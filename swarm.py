from particle import Particle, \
    find_hypotenuse, \
    find_particle_distance, \
    SpeedToHighError, \
    LocalRadiusTooSmall
from input_handling import ArgumentException
import plot_particles
import numpy as np


class Swarm:
    def __init__(self, swarm_arguments):
        self.limits = swarm_arguments['limits']
        self.initial_local_radius_limit = swarm_arguments['local_radius_limit']
        self.local_radius_limit = self.initial_local_radius_limit
        self.min_local_radius_limit = np.double(0.01)
        self.velocity_update_method = swarm_arguments['velocity_update_method']
        self.most_movement = 1
        self.best_particle = None
        self.best_particle_id = None
        self.previous_best_particle = None
        self.list_of_groups = None
        self.particle_list = [Particle(self.limits) for i in range(swarm_arguments['num_particles'])]
        self.r_squareds = np.zeros(len(self.particle_list))
        self.correlation_coefficient = None
        self.velocity_coefficient = swarm_arguments['velocity_coefficient']
        self.high_particle_velocity_counter = 0
        if 'sigma' in swarm_arguments:
            self.sigma = swarm_arguments['sigma']
            self.initial_sigma = swarm_arguments['sigma']
        else:
            self.sigma = 0.01

        if 'annealing_lifetime' in swarm_arguments:
            self.annealing_lifetime = swarm_arguments['annealing_lifetime']
        else:
            self.annealing_lifetime = 100

    def simulate_annealing(self, iteration):
        if iteration < self.annealing_lifetime:
            self.sigma = self.initial_sigma * (1 - (iteration / self.annealing_lifetime))
        else:
            self.sigma = np.int_(0)
            
        if self.local_radius_limit >= self.min_local_radius_limit:
            self.local_radius_limit -= (self.initial_local_radius_limit - self.min_local_radius_limit) / \
                                       self.annealing_lifetime
        else:
            self.local_radius_limit = self.min_local_radius_limit

    def raise_local_radius_limit(self):
        self.local_radius_limit += (self.initial_local_radius_limit - self.min_local_radius_limit) / \
                                   self.annealing_lifetime

    def call_forcing_function(self):
        for particle in self.particle_list:
            particle.execute_forcing_function()

    def find_local_groups(self):
        find_local_groups_success = False
        while not find_local_groups_success:
            try:
                for particle in self.particle_list:
                    particle.find_particles_in_local_radius(self)
            except LocalRadiusTooSmall:
                self.raise_local_radius_limit()

    def update_swarm_velocities_with_best_neighbor(self, optimization_function, velocity_coefficient):
        for particle in self.particle_list:
            particle.find_best_neighbor(self, optimization_function)
            particle.update_velocity_with_best_neighbor(velocity_coefficient)

        return velocity_coefficient

    def update_swarm_velocities_with_gradient(self, optimization_function, velocity_coefficient, least_squares_method):
        velocity_coefficient_too_high = False
        for index, particle in enumerate(self.particle_list):
            velocity_coefficient_too_high, r_squared = \
                particle.update_velocity_with_gradient(
                    velocity_coefficient, optimization_function, least_squares_method
                )

            self.r_squareds[index] = r_squared

        return velocity_coefficient_too_high

    def update_swarm_velocities(self, optimization_function, velocity_coefficient, least_squares_method):
        if self.velocity_update_method == "best neighbor":
            velocity_coefficient_too_high = \
                self.update_swarm_velocities_with_best_neighbor(optimization_function, velocity_coefficient)
        elif self.velocity_update_method == "gradient":
            velocity_coefficient_too_high = self.update_swarm_velocities_with_gradient(
                optimization_function, velocity_coefficient, least_squares_method
            )
        else:
            raise ArgumentException("Velocity update method: \"" + self.velocity_update_method + "\" not implemented.")

        if velocity_coefficient_too_high:
            velocity_coefficient -= 0.001
            print("Velocity coefficient too high. Particles moving too fast to control. Reducing velocity"
                  " coefficient by 0.001 to: " + str(velocity_coefficient) + ".\n")

        return velocity_coefficient, np.mean(self.r_squareds)

    def move_particles(self):
        for particle in self.particle_list:
            particle.move()

    def add_randomness_factor(self):
        for particle in self.particle_list:
            particle.shake(self.sigma)

    def find_most_movement(self):
        self.most_movement = 0
        particle_movement = 0
        for index, particle in enumerate(self.particle_list):
            try:
                particle_movement = find_hypotenuse(particle.velocity)
                if particle_movement > 10:
                    raise SpeedToHighError(particle_movement)
            except SpeedToHighError as error:
                print("Particle " + str(index) + "velocity too high at " + str(error.speed) + ". "
                      "Reducing particle velocity to 0.")
                particle.velocity = [0] * len(self.limits)
                self.velocity_coefficient -= 0.001
                print("Lowering velocity coefficient by 0.001 to: " + str(self.velocity_coefficient))
                print("This occurrence number: " + str(self.high_particle_velocity_counter))
            if self.most_movement < particle_movement:
                self.most_movement = particle_movement

    def find_best_particle(self, function):
        self.previous_best_particle = self.best_particle
        self.best_particle = self.particle_list[0]
        self.best_particle_id = 0
        for index, particle in enumerate(self.particle_list):
            if particle.score < self.best_particle.score and function == "min":
                self.best_particle = particle
                self.best_particle_id = index
            elif particle.score > self.best_particle.score and function == "max":
                self.best_particle = particle
                self.best_particle_id = index

        if self.best_particle is self.previous_best_particle:
            return True
        else:
            return False

    def print_summary(self, iteration):
        output_string = \
            "Iteration: " + str(iteration) + "\n" + \
            "sigma: " + str(self.sigma) + "\n" + \
            "initial sigma: " + str(self.initial_sigma) + "\n" + \
            "Most movement: " + str(self.most_movement) + "\n" + \
            "Best Particle Score: " + str(self.best_particle.score) + "\n" + \
            "Best particle position: " + str(self.best_particle.calculate_raw_position()) + "\n" + \
            "Best particle ID: " + str(self.best_particle_id) + "\n" + \
            "Best particle velocity: " + str(self.best_particle.velocity) + "\n"
        if self.velocity_update_method == "gradient":
            output_string += "Average R2: " + str(self.r_squareds.mean()) + "\n"
        print(output_string)

    def identify_particles_in_radius(self, base_particle, particles_not_yet_assigned):
        particles_in_radius = []
        for index, other_particle in enumerate(particles_not_yet_assigned):
            if find_particle_distance(other_particle, base_particle) < self.local_radius_limit:
                particles_in_radius.append(other_particle)

        return particles_in_radius, particles_not_yet_assigned

    def iterate_neighbors(self, particles_not_yet_assigned, particles_in_local_group, base_particle):
        particles_in_radius, particles_not_yet_assigned = self.identify_particles_in_radius(
            base_particle, particles_not_yet_assigned
        )

        for particle in particles_in_radius:
            particles_not_yet_assigned.remove(particle)
        particles_in_local_group += particles_in_radius

        for particle in particles_in_radius:
            particles_in_local_group = \
                self.iterate_neighbors(particles_not_yet_assigned, particles_in_local_group, particle)

        return particles_in_local_group

    def find_groups_recursive(self):
        particles_not_yet_assigned = self.particle_list.copy()
        list_of_groups = []
        while len(particles_not_yet_assigned) > 0:
            new_base_particle = particles_not_yet_assigned.pop(0)
            particles_in_local_group = [new_base_particle]
            particles_in_local_group += \
                self.iterate_neighbors(particles_not_yet_assigned, [], new_base_particle)
            list_of_groups.append(particles_in_local_group)

        print("Number of groups: " + str(len(list_of_groups)))
        self.list_of_groups = list_of_groups

    def plot_particle_positions(self):
        plot = plot_particles.PlotParticles(self.limits, self.particle_list)
        plot.plot_particle_positions(plot_contour_overlay=True)

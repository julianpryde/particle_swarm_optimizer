from particle_c import Particle, \
    SpeedToHighError, \
    LocalRadiusTooSmall
from input_handling import ArgumentException
import plot_particles
from math_functions import find_hypotenuse
import numpy as np
import functools
from typing import Sized


class ParticleList(Sized):
    def __init__(self, **kwargs):
        if "particles" in kwargs:
            self.particles = kwargs["particles"]
        else:
            self.particles = [Particle(kwargs["limits"], i) for i in range(kwargs["num_particles"])]

    def __len__(self) -> int:
        return len(self.particles)

    def __iter__(self):
        return iter(self.particles)

    def build_particle_list(self, expression):
        return [particle for p_index, particle in enumerate(self.particles) if expression(p_index)]

    def __getitem__(self, index):
        if isinstance(index, (list, np.ndarray)):

            if isinstance(index[0], (bool, np.bool_)):
                particle_list = self.build_particle_list(lambda particle_index: index[particle_index])
                return ParticleList(particles=particle_list)

            if isinstance(index[0], (int, np.int_, np.int32, np.int64)):
                particle_list = self.build_particle_list(lambda particle_index: index == particle_index)
                return ParticleList(particles=particle_list)

        elif isinstance(index, (int, np.int_, np.int32, np.int64)):
            return self.particles[index]

    def get_scores(self):
        return np.array([particle.score for particle in self.particles])

    def get_velocities(self):
        return np.array([particle.velocity for particle in self.particles])

    def remove(self, particles_to_remove):
        if isinstance(particles_to_remove, ParticleList):
            particle_ids = [particle.id for particle in particles_to_remove]
        else:
            particle_ids = particles_to_remove.id

        self.particles = self.build_particle_list(lambda particle_index: particle_index not in particle_ids)

    def pop(self, index):
        return self.particles.pop(index)

    def get_best(self, optimization_function):
        extreme = np.argmin if optimization_function == "min" else np.argmax
        scores = self.get_scores()

        return self[extreme(scores)]

    def iterate_particles(self, function, *args):
        full_function = functools.partial(function, args)
        output_list = list(map(full_function, self))
        outputs = np.array(output_list)
        return outputs


class Swarm(ParticleList):
    def __init__(self, swarm_arguments):
        self.limits = swarm_arguments['limits']
        super().__init__(limits=self.limits, num_particles=swarm_arguments["num_particles"])
        self.initial_local_radius_limit = swarm_arguments['local_radius_limit']
        self.local_radius_limit = self.initial_local_radius_limit
        self.min_local_radius_limit = np.double(0.01)
        self.velocity_update_method = swarm_arguments['velocity_update_method']
        self.fastest_particle = self[0]
        self.best_particle = self[0]
        self.previous_best_particle = None
        self.list_of_groups = None
        self.r_squareds = np.zeros(len(self.particles))
        self.velocity_coefficient = swarm_arguments['velocity_coefficient']
        self.high_particle_velocity_counter = 0
        if 'sigma' in swarm_arguments:
            self.sigma = swarm_arguments['initial_sigma']
            self.initial_sigma = swarm_arguments['initial_sigma']
        else:
            self.sigma = 0.01
            self.initial_sigma = 0.01

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
        for particle in self.particles:
            particle.execute_forcing_function()

    def find_local_groups(self):
        find_local_groups_success = np.bool_([False])
        while not all(find_local_groups_success):
            try:
                find_local_groups_success = \
                    self.iterate_particles(lambda args, particle: particle.find_particles_in_local_radius(self), ())
            except LocalRadiusTooSmall:
                self.raise_local_radius_limit()
                find_local_groups_success = False

    def update_velocities_with_best_neighbor(self):
        args = self.velocity_coefficient
        velocity_coefficient_too_high = any(
            self.iterate_particles(
                lambda inner_args, particle: particle.update_velocity_with_best_neighbor(*inner_args), *args
            )
        )
        return velocity_coefficient_too_high

    def update_velocities_with_gradient(self, least_squares_method, optimization_function):
        args = (self.velocity_coefficient, optimization_function, least_squares_method)

        outputs = self.iterate_particles(
            lambda inner_args, particle: particle.update_velocity_with_gradient(*inner_args), *args
        )
        self.r_squareds = outputs[:, 0]
        velocity_coefficient_too_high = any(outputs[:, 1])
        return velocity_coefficient_too_high

    def update_swarm_velocities(self, optimization_function, least_squares_method):
        if self.velocity_update_method == "best neighbor":
            velocity_coefficient_too_high = self.update_velocities_with_best_neighbor()
        elif self.velocity_update_method == "gradient":
            velocity_coefficient_too_high = self.update_velocities_with_gradient(least_squares_method,
                                                                                 optimization_function)
        else:
            raise ArgumentException("Velocity update method: \"" + self.velocity_update_method + "\" not implemented.")

        if velocity_coefficient_too_high:
            self.velocity_coefficient -= 0.001
            print("Velocity coefficient too high. Particles moving too fast to control. Reducing velocity"
                  " coefficient by 0.001 to: " + str(self.velocity_coefficient) + ".\n")

        return np.mean(self.r_squareds)

    def move_particles(self):
        for particle in self.particles:
            particle.move()

    def add_randomness_factor(self):
        for particle in self.particles:
            particle.shake(self.sigma)

    def find_fastest_particle(self):
        particle_movements = np.array(list(map(find_hypotenuse, self.get_velocities())))
        self.fastest_particle = self[np.argmax(particle_movements)]
        particle_movements_over_limit = particle_movements > find_hypotenuse(np.ones(len(self.limits)))

        try:
            if any(particle_movements_over_limit):
                raise SpeedToHighError(particle_movements)
        except SpeedToHighError as error:
            self[particle_movements_over_limit].velocity = np.zeros(len(self.limits))
            self.velocity_coefficient -= 0.001
            self.high_particle_velocity_counter += 1
            print("Particle(s)" + str(np.where(particle_movements_over_limit)) + " velocity too high at " +
                  str(error.speed) + ". Reducing particle velocity to 0, lowering velocity coefficient by 0.001 to: " +
                  str(self.velocity_coefficient) + ". This is occurence number: " +
                  str(self.high_particle_velocity_counter))

    def find_best_particle(self, function):
        self.previous_best_particle = self.best_particle
        self.best_particle = self.get_best(function)
        return True if self.best_particle is self.previous_best_particle else False

    def print_summary(self, iteration):
        output_string = \
            "Iteration: " + str(iteration) + "\n" + \
            "sigma: " + str(self.sigma) + "\n" + \
            "initial sigma: " + str(self.initial_sigma) + "\n" + \
            "Most movement: " + str(find_hypotenuse(self.fastest_particle.velocity)) + "\n" + \
            "Best Particle Score: " + str(self.best_particle.score) + "\n" + \
            "Best particle position: " + str(self.best_particle.calculate_raw_position()) + "\n" + \
            "Best particle ID: " + str(self.best_particle.id) + "\n" + \
            "Best particle velocity: " + str(self.best_particle.velocity) + "\n"
        if self.velocity_update_method == "gradient":
            output_string += "Average R2: " + str(self.r_squareds.mean()) + "\n"
        print(output_string)

    def iterate_neighbors(self, particles_not_yet_assigned, particles_in_local_group, base_particle):
        particles_not_yet_assigned.remove(base_particle.particles_in_local_radius)
        particles_in_local_group += base_particle.particles_in_local_radius

        if len(particles_not_yet_assigned):
            args = (particles_not_yet_assigned, particles_in_local_group)
            self.iterate_particles(
                lambda inner_args, inner_base_particle: self.iterate_neighbors(*inner_args, inner_base_particle),
                *args)
        else:
            return particles_in_local_group

    def find_groups_recursive(self):
        particles_not_yet_assigned = ParticleList(particles=self.particles)
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
        plot = plot_particles.PlotParticles(self.limits, self.particles)
        plot.plot_particle_positions(plot_contour_overlay=True)

from particle import Particle, find_hypotenuse, find_particle_distance, SpeedToHighError
import plot_particles
import numpy


class Swarm:
    def __init__(self, num_particles_in_swarm, limits, local_radius_limit, sigma=0.01, annealing_lifetime=100):
        self.initial_local_radius_limit = local_radius_limit
        self.local_radius_limit = local_radius_limit
        self.min_local_radius_limit = numpy.double(0.01)
        self.limits = limits
        self.initial_sigma = sigma
        self.sigma = sigma
        self.annealing_lifetime = annealing_lifetime
        self.most_movement = 1
        self.best_particle = None
        self.best_particle_id = None
        self.list_of_groups = None
        self.particle_list = [Particle(self.limits) for i in range(num_particles_in_swarm)]
        self.r_squareds = np.zeros(len(self.particle_list))
        self.correlation_coefficient = None

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
        for particle in self.particle_list:
            particle.find_particles_in_local_radius(self)

        return True

    def update_swarm_velocities(self, optimization_function, velocity_coefficient):
        for index, particle in enumerate(self.particle_list):
            velocity_coefficient_too_high, r_squared = particle.update_velocity(velocity_coefficient,
                                                                                self,
                                                                                optimization_function)
            if velocity_coefficient_too_high:
                velocity_coefficient -= 0.001
                print("Velocity coefficient too high. Particles moving too fast to control. Reducing velocity"
                      " coefficient by 0.001 to: " + str(velocity_coefficient) + ".\n")

            self.r_squareds[index] = r_squared
        return velocity_coefficient

    def move_particles(self):
        for particle in self.particle_list:
            particle.move()

    def add_randomness_factor(self):
        for particle in self.particle_list:
            particle.shake(self.sigma)

    def find_most_movement(self):
        self.most_movement = 0
        for index, particle in enumerate(self.particle_list):
            try:
                particle_movement = find_hypotenuse(particle.velocity)
                if particle_movement > 10:
                    raise SpeedToHighError
            except SpeedToHighError as error:
                print("Particle " + str(index) + "velocity too high at " + str(error.speed) + ". "
                      "Reducing particle velocity to 0.")
                particle.velocity = [0] * len(self.limits)
                raise
            if self.most_movement < particle_movement:
                self.most_movement = particle_movement

    def find_best_particle(self, function):
        self.best_particle = self.particle_list[0]
        self.best_particle_id = 0
        for index, particle in enumerate(self.particle_list):
            if particle.score < self.best_particle.score and function == "min":
                self.best_particle = particle
                self.best_particle_id = index
            elif particle.score > self.best_particle.score and function == "max":
                self.best_particle = particle
                self.best_particle_id = index

    def sum_of_squared_residuals(self):
        def sum_of_squares(array_to_be_summed):
            return sum(array_to_be_summed[~array_to_be_summed.mask] ** 2)
        return np.fromiter(map(sum_of_squares, iter(np.ma.masked_equal(self.r_squareds, 0))), np.double)

    # def calculate_correlation_coefficient(self):
    #     """
    #     R^2 = 1 - (sum residuals^2 ) / (sum (y - yavg)^2)
    #     """
    #     sum_of_squared_residuals = self.sum_of_squared_residuals()
    #     scores = np.array([particle.score for particle in self.particle_list])
    #     sum_squared_score_departures_from_mean = sum((scores - scores.mean()) ** 2)
    #     return 1 - sum_of_squared_residuals / sum_squared_score_departures_from_mean

    def print_summary(self, iteration):
        output_string = \
            "Iteration: " + str(iteration) + "\n" + \
            "sigma: " + str(self.sigma) + "\n" + \
            "initial sigma: " + str(self.initial_sigma) + "\n" + \
            "Most movement: " + str(self.most_movement) + "\n" + \
            "Best Particle Score: " + str(self.best_particle.score) + "\n" + \
            "Best particle position: " + str(self.best_particle.calculate_raw_position()) + "\n" + \
            "Best particle ID: " + str(self.best_particle_id) + "\n" + \
            "Best particle velocity: " + str(self.best_particle.velocity) + "\n" + \
            "Average R2: " + str(self.r_squareds.mean()) + "\n"
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

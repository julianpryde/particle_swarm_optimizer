from particle import Particle


class Swarm:
    def __init__(self, num_particles_in_swarm, limits, local_radius_limit, sigma):
        self.local_radius_limit = local_radius_limit
        self.particle_list = []
        self.sigma = sigma
        for i in range(num_particles_in_swarm):
            self.particle_list.append(Particle(limits))

    def call_forcing_function(self):
        for particle in self.particle_list:
            particle.forcing_function()

    def update_swarm_velocities(self, optimization_function, vel_coefficient):
        for particle in self.particle_list:
            particle.find_best_neighbor(self, optimization_function)
            particle.update_velocity(vel_coefficient)

    def move_particles(self):
        for particle in self.particle_list:
            particle.move()

    def add_randomness_factor(self):
        for particle in self.particle_list:
            particle.shake(self.sigma)

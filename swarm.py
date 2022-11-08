from particle import Particle, find_hypotenuse


class Swarm:
    def __init__(self, num_particles_in_swarm, limits, local_radius_limit, sigma):
        self.local_radius_limit = local_radius_limit
        self.particle_list = []
        self.sigma = sigma
        self.most_movement = 0
        for i in range(num_particles_in_swarm):
            self.particle_list.append(Particle(limits))

    def call_forcing_function(self):
        for particle in self.particle_list:
            particle.forcing_function()

    def update_swarm_velocities(self, optimization_function, velocity_coefficient):
        for particle in self.particle_list:
            particle.find_best_neighbor(self, optimization_function)
            particle.update_velocity(velocity_coefficient)

    def move_particles(self):
        for particle in self.particle_list:
            particle.move()

    def add_randomness_factor(self):
        for particle in self.particle_list:
            particle.shake(self.sigma)

    def find_most_movement(self):
        most_movement = 0
        for particle in self.particle_list:
            particle_movement = find_hypotenuse(particle.velocity)
            if most_movement < particle_movement:
                most_movement = particle_movement

    def find_best_particle(self, function):
        best_particle = self.particle_list[0]
        for particle in self.particle_list:
            if particle.score < best_particle.score and function == "min":
                best_particle = particle
            elif particle.score > best_particle.score and function == "max":
                best_particle = particle
        return best_particle

    def print_summary(self, function, iteration):
        best_particle = self.find_best_particle(function)
        output_string = \
            "Iteration: " + str(iteration) + \
            "Most movement: " + str(self.most_movement) + "\n" + \
            "Best Particle Score: " + str(best_particle.score) + \
            " Best particle position: " + str(best_particle.position) + "\n"

        print(output_string)

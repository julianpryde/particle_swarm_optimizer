import decimal
import math

from particle import Particle, find_hypotenuse
# from matplotlib import pyplot


class Swarm:
    def __init__(self, num_particles_in_swarm, limits, local_radius_limit, sigma, annealing_lifetime):
        self.local_radius_limit = local_radius_limit
        self.particle_list = []
        self.initial_sigma = sigma
        self.sigma = sigma
        self.annealing_lifetime = annealing_lifetime
        self.most_movement = 1
        self.raw_positions = []
        self.raw_x_positions = []
        self.raw_y_positions = []
        self.figure = None
        self.axes = None
        self.scatter_plot = None
        for i in range(num_particles_in_swarm):
            self.particle_list.append(Particle(limits))

    def simulate_annealing(self, iteration):
        if iteration < self.annealing_lifetime:
            self.sigma = self.initial_sigma - (iteration / self.annealing_lifetime)
        else:
            self.sigma = 0

    def call_forcing_function(self):
        for particle in self.particle_list:
            particle.execute_forcing_function()

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
        self.most_movement = 0
        for particle in self.particle_list:
            particle_movement = find_hypotenuse(particle.velocity)
            if self.most_movement < particle_movement:
                self.most_movement = particle_movement

    def find_best_particle(self, function):
        best_particle = self.particle_list[0]
        best_particle_id = 0
        for index, particle in enumerate(self.particle_list):
            if particle.score < best_particle.score and function == "min":
                best_particle = particle
                best_particle_id = index
            elif particle.score > best_particle.score and function == "max":
                best_particle = particle
                best_particle_id = index
        return best_particle, best_particle_id

    def print_summary(self, function, iteration):
        best_particle, best_particle_id = self.find_best_particle(function)
        best_particle_position = []
        for dimension in best_particle.calculate_raw_position():
            best_particle_position.append(float(round(dimension, 10)))
        output_string = \
            "Iteration: " + str(iteration) + "\n" + \
            "sigma: " + str(self.sigma) + "\n" + \
            "initial sigma: " + str(self.initial_sigma) + "\n" + \
            "Most movement: " + str(round(self.most_movement, 10)) + "\n" + \
            "Best Particle Score: " + str(best_particle.score) + "\n" + \
            "Best particle position: " + str(best_particle_position) + "\n" + \
            "Best particle ID: " + str(best_particle_id) + "\n"
        print(output_string)

#    def create_plot(self):
#        self.raw_positions = []
#        for particle in self.particle_list:
#            self.raw_positions.append(particle.calculate_raw_position())
#        self.raw_x_positions, self.raw_y_positions = zip(*self.raw_positions)
#
#        pyplot.ion()
#        self.figure, self.axes = pyplot.subplots()
#
#        self.scatter_plot = self.axes.scatter(self.raw_x_positions, self.raw_y_positions, c='black')
#        self.axes.set(xlim=(1, 10), xticks=range(1, 10, 2),
#                      ylim=(4, 30), yticks=range(4, 30, 2)
#                      )
#        pyplot.show(block=False)
#
#    def draw_plot(self):
#        self.scatter_plot.set_offsets((self.raw_x_positions, self.raw_y_positions))
#        self.figure.canvas.draw_idle()
#        pyplot.pause(0.1)

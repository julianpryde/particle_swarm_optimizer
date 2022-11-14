from particle import Particle, find_hypotenuse
from decimal import Decimal, InvalidOperation
# from matplotlib import pyplot


class Swarm:
    def __init__(self, num_particles_in_swarm, limits, local_radius_limit, sigma, annealing_lifetime):
        self.local_radius_limit = local_radius_limit
        self.limits = limits
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
        self.best_particle = None
        self.best_particle_id = None
        for i in range(num_particles_in_swarm):
            self.particle_list.append(Particle(limits))

    def simulate_annealing(self, iteration):
        if iteration < self.annealing_lifetime:
            self.sigma = round(self.initial_sigma * (1 - (iteration / self.annealing_lifetime)), 15)
        else:
            self.sigma = 0

    def call_forcing_function(self):
        for particle in self.particle_list:
            particle.execute_forcing_function()

    def update_swarm_velocities(self, optimization_function, velocity_coefficient):
        for particle in self.particle_list:
            particle.find_best_neighbor(self, optimization_function)
            velocity_coefficient_too_high_flag = particle.update_velocity(velocity_coefficient)
            if velocity_coefficient_too_high_flag:
                velocity_coefficient -= round(Decimal(0.001), 15)
                print("Velocity coefficient too high. Particles moving too fast to control. Reducing velocity"
                      "velocity coefficient by 0.001 to: " + str(velocity_coefficient) + ".\n")

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
                particle_movement = round(find_hypotenuse(particle.velocity), 15)
            except InvalidOperation:
                print("Particle " + str(index) + "velocity too high. Reducing particle velocity to 0.")
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

    def print_summary(self, iteration):
        best_particle_position = []
        best_particle_velocity = []
        for dimension in self.best_particle.calculate_raw_position():
            best_particle_position.append(float(round(dimension, 10)))
        for dimension in self.best_particle.velocity:
            best_particle_velocity.append(float(round(dimension, 10)))
        output_string = \
            "Iteration: " + str(iteration) + "\n" + \
            "sigma: " + str(self.sigma) + "\n" + \
            "initial sigma: " + str(self.initial_sigma) + "\n" + \
            "Most movement: " + str(round(self.most_movement, 10)) + "\n" + \
            "Best Particle Score: " + str(self.best_particle.score) + "\n" + \
            "Best particle position: " + str(best_particle_position) + "\n" + \
            "Best particle ID: " + str(self.best_particle_id) + "\n" + \
            "Best particle velocity: " + str(best_particle_velocity) + "\n"
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

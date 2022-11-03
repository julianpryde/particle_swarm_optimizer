# Author: Julian Pryde
import random
import math


def find_hypotenuse(side_lengths):
    for index, value in enumerate(side_lengths):
        side_lengths[index] = value ** 2

    return math.sqrt(sum(side_lengths))


def find_particle_distance(particle_1, particle_2):
    sides = [None] * len(particle_1.position)
    for index, value in enumerate(sides):
        sides[index] = particle_1.position[index] - particle_2.position[index]

    return find_hypotenuse(sides)


class Particle:
    def __init__(self, limits):
        self.num_dimensions = len(limits)
        self.position = [] * self.num_dimensions  # [position in dimension, normalization b, normalization m]
        self.position_normalization_b = [] * self.num_dimensions
        self.position_normalization_m = [] * self.num_dimensions
        for index, value in enumerate(self.position):
            self.position[index] = random.random()
        self.compute_normalization_factors(limits)
        self.score = 0  # output of forcing function for particle
        self.best_neighbor = None
        self.velocity = [0] * self.num_dimensions
        # self.local_gradient = maybe use this if I find a way to compute a local gradient easily

    def forcing_function(self):
        # TODO THIS SHOULD BE THE RAW POSITION, NOT THE NORMALIZED ONE!!!
        self.score = self.position[0] ** 2

    def compute_normalization_factors(self, limits):
        for index, value in enumerate(limits):
            self.position_normalization_b.append(value[0])
            self.position_normalization_m.append(value[1] - value[0])

    # for now, just finds the best particle in the immediate vicinity.
    # TODO replace this with a best fit line or something
    def find_best_neighbor(self, particle_swarm, optimization_function):
        for particle in particle_swarm.swarm:
            i = 0
            for other_particle in particle_swarm.swarm:
                distance = find_particle_distance(particle, other_particle)
                if distance < particle_swarm.local_radius_limit:
                    if i == 0 or (optimization_function == "min" and other_particle.score < self.best_neighbor.score) \
                            or \
                            (optimization_function == "max" and other_particle.score > self.best_neighbor.score):
                        self.best_neighbor = other_particle
                        i += 1

    # TODO is it more efficient to modify last iteration's velocity or create a new one each iteration?
    # TODO this is all wrong
    def update_velocity(self, velocity_coefficient):
        # Determine component velocity for each dimension
        for index, value in enumerate(self.velocity):
            self.velocity[index] = velocity_coefficient * (self.best_neighbor.score[index] - self.score[index])

    # TODO what to do if limits put the particle out of bounds
    def move(self):
        for index, value in enumerate(self.position):
            self.position[index] = value + self.velocity[index]

    def shake(self, sigma):
        for index, value in enumerate(self.position):
            self.position[index] = value + random.gauss(0, sigma)


class Swarm:
    def __init__(self, num_particles_in_swarm, limits, local_radius_limit, sigma):
        self.local_radius_limit = local_radius_limit
        self.swarm = []
        self.sigma = sigma
        for i in range(num_particles_in_swarm):
            self.swarm.append(Particle(limits))

    def call_forcing_function(self):
        for particle in self.swarm:
            particle.forcing_function()

    def update_swarm_velocities(self, optimization_function, vel_coefficient):
        for particle in self.swarm:
            particle.find_best_neighbor(self, optimization_function)
            particle.update_velocity(vel_coefficient)

    def move_particles(self):
        for particle in self.swarm:
            particle.move()

    def add_randomness_factor(self):
        for particle in self.swarm:
            particle.shake(self.sigma)


def optimize(particle_swarm, optimizing_function, velocity_coefficient, exit_criterion):
    most_movement = 1
    # while all particles move > <exit criterion> without effects of randomness factor
    while most_movement > exit_criterion:
        particle_swarm.call_forcing_function()
        particle_swarm.update_swarm_velocities(particle_swarm, optimizing_function, velocity_coefficient)
        particle_swarm.move_particles()
        # TODO add options to simulate annealing to hone in on optimum value more finely as program runs
        particle_swarm.add_randomness_factor()

        # swarm analytics
        # how many groups are there


def remove_argument_id(argument, argument_id):
    # arguments should be in "argument_id=xxx" format. function
    # removes the "argument_id=" and returns just the "xxx"
    return int(argument[len(argument_id) + 1:])


def parse_limits(limits_argument):
    limit_tuples = []
    limit_strings = limits_argument.split(",")
    for index, value in enumerate(limit_strings):
        limit_tuple = value.split("-")
        limit_tuple[0] = limit_tuple[0].replace("limits=", "")
        limit_tuple[0] = int(limit_tuple[0])
        limit_tuple[1] = int(limit_tuple[1])

        limit_tuples.append(limit_tuple)
    return limit_tuples


def read_arguments_file():
    arguments_file = open("arguments", "r")
    arguments = arguments_file.read()
    arguments_list_from_file = arguments.split("\n")
    return arguments_list_from_file, arguments_file


def assign_arguments():
    arguments_list, arguments_file_object = read_arguments_file()
    limits_from_arguments = []
    num_particles_from_arguments = None
    entropy_from_arguments = None
    function_from_arguments = None
    local_radius_limit = None
    velocity_coefficient = None
    sigma = None
    exit_criterion = None
    for argument in arguments_list:
        if "entropy" in argument:
            entropy_from_arguments = remove_argument_id(argument, "entropy")
        if "num_particles" in argument:
            num_particles_from_arguments = remove_argument_id(argument, "num_particles")
        if "limits" in argument:
            limits_from_arguments = parse_limits(argument)
        if "function" in argument:
            function_from_arguments = remove_argument_id(argument, "function")
        if "local_radius" in argument:
            local_radius_limit = remove_argument_id(argument, "local_radius")
        if "velocity_coefficient" in argument:
            velocity_coefficient = remove_argument_id(argument, "velocity_coefficient")
        if "starting_sigma" in argument:
            sigma = remove_argument_id(argument, "starting_sigma")
        if "exit_criterion" in argument:
            exit_criterion = remove_argument_id(argument, "exit_criterion")
    arguments_file_object.close()
    return entropy_from_arguments, num_particles_from_arguments, limits_from_arguments, function_from_arguments, \
        local_radius_limit, velocity_coefficient, sigma, exit_criterion


if __name__ == "__main__":
    entropy, \
        particles, \
        dimension_limits, \
        function, \
        local_radius, \
        velocity_coefficient_arg, \
        std_dev_of_randomness, \
        exit_criteria \
        = assign_arguments()
    print("entropy= " + str(entropy) +
          "\nnum_particles= " + str(particles) +
          "\nlimits= " + str(dimension_limits) +
          "\nfunction= " + str(function) +
          "\nlocal_radius= " + str(local_radius) +
          "\nvel coefficient= " + str(velocity_coefficient_arg) +
          "\nsigma= " + str(std_dev_of_randomness) +
          "\nexit_criterion=" + str(exit_criteria)
          )
    swarm = Swarm(particles, dimension_limits, local_radius, std_dev_of_randomness)
    optimize(swarm, function, velocity_coefficient_arg, exit_criteria)

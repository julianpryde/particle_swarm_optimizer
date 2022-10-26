# Author: Julian Pryde
import random
import math


def find_hypotenuse(side_lengths):
    for i in range(len(side_lengths)):
        side_lengths[i] = side_lengths[i]**2

    return math.sqrt(sum(side_lengths))


class Particle:
    def __init__(self, limits):
        self.num_dimensions = len(limits)
        self.position = [] * self.num_dimensions  # [position in dimension, normalization b, normalization m]
        self.position_normalization_b = [] * self.num_dimensions
        self.position_normalization_m = [] * self.num_dimensions
        for i in range(self.num_dimensions):
            self.position[i] = random.random()
        self.compute_normalization_factors(limits)
        self.score = 0  # output of forcing function for particle
        self.best_neighbor = None
        self.velocity = [0] * self.num_dimensions
        # self.local_gradient = maybe use this if i find a way to compute a local gradient easily

    def forcing_function(self):
        self.score = self.position[0] ** 2

    def compute_normalization_factors(self, limits):
        for i in range(self.num_dimensions):
            self.position_normalization_b[i] = limits[i][0]
            self.position_normalization_m[i] = limits[i][1] - limits[i][0]

    def find_particle_distance(self, particle_1, particle_2):
        sides = []
        for i in range(self.num_dimensions):
            sides.append(particle_1.position[i] - particle_2.position[i])

        return find_hypotenuse(sides)

    # for now, just finds the best particle in the immediate vicinity.
    # TODO replace this with a best fit line or something
    def find_best_neighbor(self, particle_swarm, optimization_function):
        for particle in particle_swarm.swarm:
            i = 0
            for other_particle in particle_swarm.swarm:
                distance = self.find_particle_distance(particle, other_particle)
                if distance < particle_swarm.local_radius_limit:
                    if i == 0 or (optimization_function == "min" and other_particle.score < self.best_neighbor.score) \
                            or \
                            (optimization_function == "max" and other_particle.score > self.best_neighbor.score):
                        self.best_neighbor = other_particle
                        i += 1

    # TODO is it more efficient to modify last iteration's velocity or create a new one each iteration?
    def update_velocity(self, velocity_coefficient):
        # Determine component velocity for each dimension
        for index, value in enumerate(self.velocity):
            self.velocity[index] = velocity_coefficient * (self.best_neighbor.position[index] - self.position[index])

    def update_position(self):
        for i in range(self.num_dimensions):
            self.position[i] = self.position[i] + self.velocity[i]


class Swarm:
    def __init__(self, num_particles_in_swarm, limits, local_radius_limit):
        self.local_radius_limit = local_radius_limit
        self.swarm = []
        for i in range(num_particles_in_swarm):
            self.swarm.append(Particle(limits))

    def call_forcing_function(self):
        for particle in self.swarm:
            particle.forcing_function()

    def update_swarm_velocities(self, optimization_function, vel_coefficient):
        for particle in self.swarm:
            particle.find_best_neighbor(self, optimization_function)
            particle.update_velocity(vel_coefficient)


def optimize(particle_swarm, optimizing_function, velocity_coefficient):
    exit_criterion = .01
    most_movement = 1
    # while all particles move > <exit criterion> without effects of randomness factor
    while most_movement > exit_criterion:
        particle_swarm.call_forcing_function()
        particle_swarm.update_swarm_velocities(particle_swarm, optimizing_function, velocity_coefficient)
        particle_swarm.move_particles()
        # add randomness factor to movement for each particle
        # change position for each particle
        # if all particles move less than <criteria> without effects of randomness factor, lower temperature

    # swarm analytics
        # how many groups are there


def remove_argument_id(argument, argument_id):
    # arguments should be in "argument_id=xxx" format. function
    # removes the "argument_id=" and returns just the "xxx"
    return int(argument[len(argument_id) + 1:])


def parse_limits(limits_argument):
    limit_tuples = []
    limit_strings = limits_argument.split(",")
    for i in range(len(limit_strings)):
        limit_tuple = limit_strings[i].split("-")
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
    arguments_file_object.close()
    return entropy_from_arguments, num_particles_from_arguments, limits_from_arguments, function_from_arguments, \
        local_radius_limit, velocity_coefficient


if __name__ == "__main__":
    entropy, particles, dimension_limits, function, local_radius, velocity_coefficient_arg = assign_arguments()
    print("entropy=" + str(entropy) +
          "\nnum_particles=" + str(particles) +
          "\nlimits=" + str(dimension_limits) +
          "\nfunction=" + str(function) +
          "\nlocal_radius" + str(local_radius) +
          "\nvel coefficient" + str(velocity_coefficient_arg)
          )
    swarm = Swarm(particles, dimension_limits, local_radius)

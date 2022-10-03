# Author: Julian Pryde
import random


class Particle:
    def __init__(self, limits):
        self.position = [[0, 0, 0]] * len(limits)  # [position, normalization b, normalization m]
        for i in range(len(limits)):
            self.position[i][0] = random.random()
        self.compute_normalization_factors(limits)

    def compute_normalization_factors(self, limits):
        for i in range(len(self.position)):
            self.position[i][1] = limits[i][0]
            self.position[i][2] = limits[i][1] - limits[i][0]


class Swarm:
    def __init__(self, num_particles_in_swarm, limits):
        self.swarm = []
        for i in range(num_particles_in_swarm):
            self.swarm.append(Particle(limits))

    def call_forcing_function(self):
        for particle in self.swarm:
            forcing_function(particle.position)


def optimize(particle_swarm):
    exit_criterion = .01
    most_movement = 1
    # while all particles move > <exit criterion> without effects of randomness factor
    while most_movement > exit_criterion:
        # run forcing function on all particles
        particle_swarm.call_forcing_function()
        # determine direction to move each particle in swarm
        # add randomness factor to movement for each particle
        # change position for each particle
        # if all particles move less than <criteria> without effects of randomness factor, lower temperature

    # swarm analytics
        # how many groups are there


def forcing_function(particle_position):
    return particle_position[1] ** 2


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
    for argument in arguments_list:
        if "entropy" in argument:
            entropy_from_arguments = remove_argument_id(argument, "entropy")
        if "num_particles" in argument:
            num_particles_from_arguments = remove_argument_id(argument, "num_particles")
        if "limits" in argument:
            limits_from_arguments = parse_limits(argument)
    arguments_file_object.close()
    return entropy_from_arguments, num_particles_from_arguments, limits_from_arguments


if __name__ == "__main__":
    entropy, particles, dimension_limits = assign_arguments()
    print("entropy=" + str(entropy) + "\nnum_particles=" + str(particles) + "\nlimits=" + str(dimension_limits))
    swarm = Swarm(particles, dimension_limits)

import math
import random


def find_particle_distance(particle_1, particle_2):
    sides = [None] * len(particle_1.position)
    for index, value in enumerate(sides):
        sides[index] = particle_1.position[index] - particle_2.position[index]

    return find_hypotenuse(sides)


def find_hypotenuse(side_lengths):
    for index, value in enumerate(side_lengths):
        side_lengths[index] = value ** 2

    return math.sqrt(sum(side_lengths))


def calculate_raw_particle_position(normalized_position, normalization_m_factors, normalization_b_factors):
    raw_position = []
    for position, normalization_m, normalization_b in \
            zip(normalized_position, normalization_m_factors, normalization_b_factors):
        raw_position.append(position * normalization_m + normalization_b)

    return raw_position


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
        raw_position = \
            calculate_raw_particle_position(self.position, self.position_normalization_m, self.position_normalization_b)
        self.score = raw_position[0] ** 2

    def compute_normalization_factors(self, limits):
        for index, value in enumerate(limits):
            self.position_normalization_b.append(value[0])
            self.position_normalization_m.append(value[1] - value[0])

    # for now, just finds the best particle in the immediate vicinity.
    # TODO replace this with a best fit line or something
    # TODO change i to a "first particle in radius" boolean
    def find_best_neighbor(self, particle_swarm, optimization_function):
        for particle in particle_swarm.particle_list:
            i = 0
            for other_particle in particle_swarm.particle_list:
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
            self.velocity[index] = velocity_coefficient * (self.best_neighbor.score - self.score)

    # TODO what to do if limits put the particle out of bounds
    def move(self):
        for index, value in enumerate(self.position):
            self.position[index] = value + self.velocity[index]

    def shake(self, sigma):
        for index, value in enumerate(self.position):
            self.position[index] = value + random.gauss(0, sigma)


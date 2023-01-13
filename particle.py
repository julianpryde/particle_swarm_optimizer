import math
import random
# from decimal import Decimal
import numpy
from forcing_function import forcing_function


def find_particle_distance(particle_1, particle_2):
    sides = [None] * len(particle_1.position)
    for index, value in enumerate(sides):
        sides[index] = particle_1.position[index] - particle_2.position[index]

    return round(find_hypotenuse(sides), 15)


def find_hypotenuse(side_lengths):
    squared_side_lengths = []
    for index, value in enumerate(side_lengths):
        squared_side_lengths.append(value ** 2)

    hypotenuse = math.sqrt(sum(squared_side_lengths))

    if hypotenuse > 10:
        raise SpeedToHighError(hypotenuse)

    return hypotenuse


def compute_normalization_factors(limits):
    normalization_b = limits[:, 0]
    normalization_m = limits[:, 1] - limits[:, 0]

    return normalization_m, normalization_b


class SpeedToHighError(ValueError):
    def __init__(self, speed):
        self.speed = speed


class Particle:
    def __init__(self, limits, position=None):
        self.num_dimensions = len(limits)
        self.position = position
        if not self.position:
            self.position = numpy.random.random(self.num_dimensions)
        self.normalization_m, self.normalization_b = compute_normalization_factors(limits)
        self.score = 0  # output of forcing function for particle
        self.best_neighbor = None
        self.best_neighbor_distance = None
        self.velocity = numpy.zeros(self.num_dimensions)
        # self.local_gradient = maybe use this if I find a way to compute a local gradient easily

    def calculate_raw_position(self):
        return self.position * self.normalization_m + self.normalization_b

    def execute_forcing_function(self):
        raw_position = self.calculate_raw_position()
        self.score = numpy.double(forcing_function(raw_position))

    # for now, just finds the best particle in the immediate vicinity.
    # TODO replace this with a best fit line or something
    def find_best_neighbor(self, particle_swarm, optimization_function):
        first_particle_flag = True
        for other_particle in particle_swarm.particle_list:
            distance = find_particle_distance(self, other_particle)
            if distance < particle_swarm.local_radius_limit:
                if first_particle_flag is True or \
                        (optimization_function == "min" and other_particle.score < self.best_neighbor.score) \
                        or \
                        (optimization_function == "max" and other_particle.score > self.best_neighbor.score):
                    self.best_neighbor = other_particle
                    self.best_neighbor_distance = distance
                    first_particle_flag = False

    def update_velocity(self, velocity_coefficient):
        if self.best_neighbor_distance != 0:
            velocity_coefficient_too_high_flag = False
            distance_to_best_neighbor = abs(self.best_neighbor_distance)  # abs to ensure no change in sign
            score_difference = abs(self.best_neighbor.score - self.score)  # abs to ensure no change in sign

            # TODO this will all not be necessary
            # Calculate unit vector in direction of best neighbor, then multiply by score difference to get
            # velocity vector in the direction of the best neighbor with the magnitude of the difference in scores
            dimension = 0
            for element_1, element_2 in zip(self.position, self.best_neighbor.position):
                self.velocity[dimension] = ((element_2 - element_1) / distance_to_best_neighbor) * score_difference
                # Apply scaling factor parameter
                self.velocity[dimension] = round(self.velocity[dimension] * velocity_coefficient, 15)
                if self.velocity[dimension] > 1:
                    velocity_coefficient_too_high_flag = True

                dimension += 1

            return velocity_coefficient_too_high_flag

    def move(self):
        # print("Before: " + str(self.position) + " Velocity: " + str(self.velocity))
        for dimension in range(self.num_dimensions):
            particle_projected_position = self.position[dimension] + self.velocity[dimension]

            if particle_projected_position < 0:
                particle_overshoot_magnitude = -particle_projected_position
                self.position[dimension] = particle_overshoot_magnitude % 1

            elif particle_projected_position > 1:
                particle_overshoot_magnitude = particle_projected_position - 1
                self.position[dimension] = 1 - (particle_overshoot_magnitude % 1)

            else:
                self.position[dimension] = particle_projected_position

    def shake(self, sigma):
        for index, value in enumerate(self.position):
            self.position[index] = random.gauss(value, sigma)

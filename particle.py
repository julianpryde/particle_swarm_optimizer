import math
import random
from decimal import Decimal
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

    hypotenuse = Decimal(math.sqrt(sum(squared_side_lengths)))

    return hypotenuse


def compute_normalization_factors(limits):
    normalization_b = []
    normalization_m = []
    for index, value in enumerate(limits):
        normalization_b.append(value[0])
        normalization_m.append(value[1] - value[0])

    return normalization_m, normalization_b


class Particle:
    def __init__(self, limits, position=None):
        self.num_dimensions = len(limits)
        self.position = position
        if not self.position:
            self.position = []
            for index in range(self.num_dimensions):
                self.position.append(Decimal(random.random()))
        self.normalization_m, self.normalization_b = compute_normalization_factors(limits)
        self.score = Decimal(0)  # output of forcing function for particle
        self.best_neighbor = None
        self.best_neighbor_distance = None
        self.velocity = [Decimal(0)] * self.num_dimensions
        # self.local_gradient = maybe use this if I find a way to compute a local gradient easily

    def calculate_raw_position(self):
        normalized_position = self.position
        normalization_m_factors = self.normalization_m
        normalization_b_factors = self.normalization_b
        raw_position = []
        for position, normalization_m, normalization_b in \
                zip(normalized_position, normalization_m_factors, normalization_b_factors):
            raw_position.append(round(position * normalization_m + normalization_b, 15))

        return raw_position

    def execute_forcing_function(self):
        raw_position = self.calculate_raw_position()
        self.score = round(forcing_function(raw_position), 15)

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

    # TODO is it more efficient to modify last iteration's velocity or create a new one each iteration?
    def update_velocity(self, velocity_coefficient):
        if self.best_neighbor_distance != 0:
            velocity_coefficient_too_high_flag = False
            distance_to_best_neighbor = abs(self.best_neighbor_distance)  # abs to ensure no change in sign
            score_difference = abs(self.best_neighbor.score - self.score)  # abs to ensure no change in sign

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
                self.position[dimension] = round(particle_overshoot_magnitude % 1, 15)

            elif particle_projected_position > 1:
                particle_overshoot_magnitude = particle_projected_position - 1
                self.position[dimension] = round(1 - (particle_overshoot_magnitude % 1), 15)

            else:
                self.position[dimension] = round(particle_projected_position, 15)
        # print("After: " + str(self.position))

#        for index, value in enumerate(self.position):
#            self.position[index] = value + self.velocity[index]

    def shake(self, sigma):
        for index, value in enumerate(self.position):
            self.position[index] = round(Decimal(random.gauss(float(value), sigma)), 15)

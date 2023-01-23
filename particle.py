import math
import random
import numpy as np
from fit_plane import FitPlane
from forcing_function import forcing_function


def find_hypotenuse(side_lengths):
    return math.sqrt(sum(side_lengths ** 2))


def find_particle_distance(particle_1, particle_2):
    return find_hypotenuse(particle_1.position - particle_2.position)


def particle_in_radius(particle, other_particle, radius_limit):
    return True if find_particle_distance(particle, other_particle) < radius_limit else False


def compute_normalization_factors(limits):
    normalization_b = limits[:, 0]
    normalization_m = limits[:, 1] - limits[:, 0]

    return normalization_m, normalization_b


class SpeedToHighError(ValueError):
    def __init__(self, speed):
        self.speed = speed


class LocalRadiusTooSmall(Exception):
    pass


class Particle:
    def __init__(self, limits, position=None):
        self.num_dimensions = len(limits)
        self.position = position
        if type(self.position) is not np.ndarray:
            self.position = np.random.random(self.num_dimensions)
        self.normalization_m, self.normalization_b = compute_normalization_factors(limits)
        self.score = 0  # output of forcing function for particle
        self.best_neighbor = None
        self.best_neighbor_distance = None
        self.velocity = np.zeros(self.num_dimensions)
        self.particles_in_local_radius = None
        self.local_gradient = None

    def calculate_raw_position(self):
        return self.position * self.normalization_m + self.normalization_b

    def execute_forcing_function(self):
        raw_position = self.calculate_raw_position()
        self.score = np.double(forcing_function(raw_position))

    def find_particles_in_local_radius(self, particle_swarm):
        self.particles_in_local_radius = [particle for particle in particle_swarm.particle_list
                                          if particle_in_radius(self, particle, particle_swarm.local_radius_limit)]
        if len(self.particles_in_local_radius) < 3:
            raise LocalRadiusTooSmall("Only " + str(len(self.particles_in_local_radius)) + " particles in local radius")

    def update_velocity(self, velocity_coefficient, particle_swarm, optimization_function):
        fit_gradient_plane = FitPlane(self.particles_in_local_radius)
        gradient_plane_coefficients, r_squared = fit_gradient_plane.find_local_gradient()
        if optimization_function == "min":
            gradient_plane_coefficients = np.negative(gradient_plane_coefficients)
        gradient_magnitude = find_hypotenuse(gradient_plane_coefficients)
        normalized_gradient_components = gradient_plane_coefficients / gradient_magnitude
        velocity_coefficient_too_high = True if any(normalized_gradient_components > 1) else False
        self.velocity = normalized_gradient_components * velocity_coefficient

        return velocity_coefficient_too_high, r_squared

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

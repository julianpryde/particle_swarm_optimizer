import random
import numpy as np
from fit_plane import FitPlane
from forcing_function import forcing_function
import math_functions


class SpeedToHighError(ValueError):
    def __init__(self, speed):
        self.speed = speed


class LocalRadiusTooSmall(Exception):
    pass


class Particle:
    def __init__(self, limits, ident, position=None):
        self.id = ident
        self.num_dimensions = len(limits)
        self.position = position
        if type(self.position) is not np.ndarray:
            self.position = np.random.random(self.num_dimensions)
        self.normalization_m, self.normalization_b = math_functions.compute_normalization_factors(limits)
        self.score = 0
        self.best_neighbor = None
        self.best_neighbor_distance = None

        #  High enough to satisfy exit criteria initially, low enough to not trigger particle high velocity exception
        self.velocity = np.ones(self.num_dimensions) - 0.1

        self.particles_in_local_radius = None
        self.local_gradient = None

    def get_id(self):
        return self.id

    def calculate_raw_position(self):
        return self.position * self.normalization_m + self.normalization_b

    def execute_forcing_function(self):
        raw_position = self.calculate_raw_position()
        self.score = forcing_function(raw_position)

    def find_distance_to_particle(self, other_particle):
        return math_functions.find_hypotenuse(other_particle.position - self.position)

    def find_particles_in_local_radius(self, particle_swarm):
        distances = np.array(list(map(self.find_distance_to_particle, particle_swarm)))
        self.particles_in_local_radius = particle_swarm[distances < particle_swarm.local_radius_limit]
        return False if len(self.particles_in_local_radius) < 3 else True

    def find_best_neighbor(self, optimization_function):
        self.best_neighbor = self.particles_in_local_radius.find_best(optimization_function)
        self.best_neighbor_distance = self.find_distance_to_particle(self.best_neighbor)

    def update_velocity_with_best_neighbor(self, velocity_coefficient):
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

    def update_velocity_with_gradient(self, velocity_coefficient, optimization_function, least_squares_method):
        fit_gradient_plane = FitPlane(self.particles_in_local_radius)
        gradient_plane_coefficients, r_squared = fit_gradient_plane.find_local_gradient(least_squares_method)
        if optimization_function == "min":
            gradient_plane_coefficients = np.negative(gradient_plane_coefficients)
        # gradient_magnitude = find_hypotenuse(gradient_plane_coefficients)
        # normalized_gradient_components = gradient_plane_coefficients / gradient_magnitude
        self.velocity = gradient_plane_coefficients * velocity_coefficient
        velocity_coefficient_too_high = True if any(self.velocity > 1) else False

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

    def iterate_neighbors_to_find_local_groups(self, not_yet_assigned, local_group):
        new_particles_discovered = self.particles_in_local_radius.intersection(not_yet_assigned)
        not_yet_assigned.remove(new_particles_discovered)

        local_group += new_particles_discovered

        args = (not_yet_assigned, local_group)
        outputs = new_particles_discovered.iterate_particles(
            lambda inner_args, inner_base_particle:
                inner_base_particle.iterate_neighbors_to_find_local_groups(*inner_args),
            list,
            *args,
        )

        if outputs is not None:
            lower_level_particles_discovered = [output[0] for output in outputs]
            lower_level_not_yet_assigned_lists = [output[1] for output in outputs]

            index = 1
            new_not_yet_assigned = not_yet_assigned.intersection(lower_level_not_yet_assigned_lists[0])
            while index < len(lower_level_not_yet_assigned_lists):
                new_not_yet_assigned = new_not_yet_assigned.intersection(lower_level_not_yet_assigned_lists[index])
                index += 1

            not_yet_assigned = new_not_yet_assigned

            for particle_list in lower_level_particles_discovered:
                local_group += particle_list
            local_group.remove_duplicates()

        return local_group, not_yet_assigned

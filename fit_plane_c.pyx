import numpy as np


# noinspection SpellCheckingInspection
class FitPlane:
    # Calculate the coefficients of an n-dimensional plane using the algorithm given in:
    # Least Squares Fitting of Data by Linear or Quadratic Structures
    # David Eberly, Geometric Tools, Redmond WA 98052
    def __init__(self, particles_in_local_radius):
        self.particles_in_local_radius = particles_in_local_radius
        self.particle_position_differences_from_mean = None
        self.mean_particle_positions = None
        self.particle_positions = None
        self.mean_score = None
        self.local_plane_parameters = None
        self.intercept = None
        self.scores = None
        self.score_differences_from_mean = None
        self.sum_squared_residuals = None

    def create_particle_value_arrays(self):
        self.particle_positions = np.array([particle.position for particle in self.particles_in_local_radius])
        self.mean_particle_positions = self.particle_positions.mean(axis=0)
        self.particle_position_differences_from_mean = self.particle_positions - self.mean_particle_positions

        self.scores = np.array([particle.score for particle in self.particles_in_local_radius])
        self.mean_score = self.scores.mean()
        self.score_differences_from_mean = self.scores - self.mean_score

    def create_a_array(self):
        # a = (Xi - Xavg) * (Xi - Xavg) ^ T
        a = sum(
            np.outer(
                self.particle_position_differences_from_mean[index, :],
                self.particle_position_differences_from_mean[index, :]
            )
            for index, particle in enumerate(self.particle_position_differences_from_mean)
        )

        return a

    def create_b_array(self):

        # b = (zi - zavg) * (Xi - Xavg)
        b = sum(
            self.particle_position_differences_from_mean[index, :] * self.score_differences_from_mean[index]
            for index, particle in enumerate(self.particle_position_differences_from_mean)
        )[:, np.newaxis]

        return b

    def create_gradient_a_b_arrays(self):
        self.create_particle_value_arrays()
        a = self.create_a_array()
        b = self.create_b_array()

        return a, b

    def calculate_intercept(self):
        # b = h_bar - A_bar dot X_bar where,
        # h_bar = average score
        # A_bar = coefficients matrix (column vector with # dimensions elements)
        # X_bar = average particle positions (row vector with # dimensions elements)
        self.intercept = self.mean_score - \
                         np.dot(
                             self.mean_particle_positions,
                             self.local_plane_parameters,
                         )

    def evaluate_plane(self, particle_positions):
        self.calculate_intercept()
        result = self.intercept + np.dot(particle_positions, self.local_plane_parameters)
        return result

    def calculate_sum_squared_residuals(self):
        self.sum_squared_residuals = sum(
            (self.scores - np.fromiter(
                map(self.evaluate_plane, self.particle_positions), np.double)
             ) ** 2
        )

    def calculate_r2(self):
        # R2 = 1 - sum((yi - yi_expected) ^ 2) / sum((yi - y_avg) ^ 2)
        lower_half = sum((self.scores - self.mean_score) ** 2)

        return 1 - self.sum_squared_residuals / lower_half

    def find_local_gradient(self, least_squares_method):
        if least_squares_method == "zero_derivative":
            a, b = self.create_gradient_a_b_arrays()
            self.local_plane_parameters, empty_residuals, rank, s = np.linalg.lstsq(a, b, rcond=None)
            self.calculate_sum_squared_residuals()

        elif least_squares_method == "direct":
            self.create_particle_value_arrays()
            a = self.particle_position_differences_from_mean
            b = self.score_differences_from_mean[:, np.newaxis]
            self.local_plane_parameters, self.sum_squared_residuals, rank, s = np.linalg.lstsq(a, b, rcond=None)

        r_squared = self.calculate_r2()

        return self.local_plane_parameters, r_squared

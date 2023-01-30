import numpy as np


# noinspection SpellCheckingInspection
class FitPlane:
    # Calculate the coefficients of an n-dimensional plane using the algorithm given in:
    # Least Squares Fitting of Data by Linear or Quadratic Structures
    # David Eberly, Geometric Tools, Redmond WA 98052
    def __init__(self, particles_in_local_radius):
        """
        self.particles_in_local_radius: Particle type particles to be used when determining best fit plane

        self.particle_positions: (num_particles_in_local_radius, num_dimensions) size array of np.doubles containing
            position values for each particle in local radius

        self.mean_particle_positions: (num_dimensions) size array of np.doubles containing the mean value for each
            dimension and for each particle in local radius

        self.particle_position_differences_from_mean: (num_particles_in_local_radius, num_dimensions) size array of
            np.doubles containing difference from the mean value for each dimension for each particle in local radius

        self.scores: (num_particles_in_local_radius) size array of np.doubles containing score for each particle in
            local radius

        self.mean_score: scalar np.double containing the mean value of all scores of all particles in local radius

        self.score_differences_from_mean: (num_particles_in_local_radius) size array of np.doubles containing the
            difference from the mean value for each score for each particle in local radius

        self.local_plane_parameters: (1, num_dimensions) size array of np.doubles containing slope in each dimension of
            the best-fit plane returned by the selected least squares method

        self.intercept: scalar np.double containing the z-intercept of the calculated best-fit plane

        self.sum_squared_residuals: scalar np.double containing the sum of all squared residuals between all particles
            and the calculated best-fit plane
        """
        self.particles_in_local_radius = particles_in_local_radius
        self.particle_positions = None
        self.mean_particle_positions = None
        self.particle_position_differences_from_mean = None
        self.scores = None
        self.mean_score = None
        self.score_differences_from_mean = None
        self.local_plane_parameters = None
        self.intercept = None
        self.sum_squared_residuals = None

    def create_particle_value_arrays(self):
        """
        Creates self.particle_positions, self.mean_particle_positions, self.particle_positions_differences_from_mean,
         self.scores, self.mean_scores, self.score_difference_from_mean from positions and scores of particles in
         local radius
        """
        self.particle_positions = np.array([particle.position for particle in self.particles_in_local_radius])
        self.mean_particle_positions = self.particle_positions.mean(axis=0)
        self.particle_position_differences_from_mean = self.particle_positions - self.mean_particle_positions

        self.scores = np.array([particle.score for particle in self.particles_in_local_radius])
        self.mean_score = self.scores.mean()
        self.score_differences_from_mean = self.scores - self.mean_score

    def create_a_array(self):
        """
        Return an array according to the formula:
            a = (Xi - Xavg) * (Xi - Xavg) ^ T
        see equation (20) in Least Squares Fitting of Data by Linear or Quadratic Structures by David Eberly in
         Geometric Tools

        Returns
        -------
        a: (num_dimensions, num_dimensions) size np.ndarray of np.doubles
        """
        a = sum(
            np.outer(
                self.particle_position_differences_from_mean[index, :],
                self.particle_position_differences_from_mean[index, :]
            )
            for index, particle in enumerate(self.particle_position_differences_from_mean)
        )

        return a

    def create_b_array(self):
        """
        Return an array according to the formula:
            b = (zi - zavg) * (Xi - Xavg)
        see equation (20) in Least Squares Fitting of Data by Linear or Quadratic Structures by David Eberly in
         Geometric Tools

        Returns
        -------
        b: (1, num_dimensions) size np.ndarray of np.doubles
        """

        b = sum(
            self.particle_position_differences_from_mean[index, :] * self.score_differences_from_mean[index]
            for index, particle in enumerate(self.particle_position_differences_from_mean)
        )[:, np.newaxis]

        return b

    def create_gradient_a_b_arrays(self):
        """
        Returns a and b arrays to use with a least squares regression to calculate the parameters of the best fit plane.

        Based on Section 3.3 of Least Squares Fitting of Data by Linear or Quadratic
            Structures in David Eberly, Geometric Tools
        Returns
        -------
        a: (num_dimensions, num_dimensions) size np.ndarray of np.doubles
        b: (1, num_dimensions) size np.ndarray of np.doubles
        """
        self.create_particle_value_arrays()
        a = self.create_a_array()
        b = self.create_b_array()

        return a, b

    def calculate_intercept(self):
        """
        sets the intercept of the best fit plane with the equation:
            b = h_bar - A_bar dot X_bar where,
            h_bar = average score
            A_bar = coefficients matrix (column vector with # dimensions elements)
            X_bar = average particle positions (row vector with # dimensions elements)
        """
        self.intercept = self.mean_score - np.dot(self.mean_particle_positions, self.local_plane_parameters)

    def evaluate_plane(self, particle_positions):
        """
        Calculates the value of the best fit plane at an arbitrary set of points
        Side effect: sets the self.intercept value for the best-fit plane

        Parameters
        ----------
        particle_positions: (num_particles, num_dimensions) size np.ndarray of np.doubles

        Returns
        -------
        (1, num_particles) size np.ndarray of np.doubles
        """

        self.calculate_intercept()
        return self.intercept + (particle_positions * self.local_plane_parameters.T).sum(axis=1)

    def calculate_sum_squared_residuals(self):
        """
        Calculates the sum of the squared residuals if not already provided by the least squares algorithm.
        """
        self.sum_squared_residuals = sum((self.scores - self.evaluate_plane(self.particle_positions)) ** 2)

    def calculate_r2(self):
        """
        Calculates the coefficient of correlation using the formula:

            R2 = 1 - sum((yi - yi_expected) ^ 2) / sum((yi - y_avg) ^ 2)

        """
        sum_squared_score_differences_from_mean = sum((self.scores - self.mean_score) ** 2)
        return 1 - self.sum_squared_residuals / sum_squared_score_differences_from_mean

    def find_local_gradient(self, least_squares_method):
        """

        Parameters
        ----------
        least_squares_method: str either "zero_derivative" or "direct" requesting either the:
            1. "direct" method of calculating least squares from the particle positions and score matrices and the
            2. "zero_derivative" method of setting the partial derivative of

                E(A, b) = sum <i = 1 to m> ((A dot Xi + b) - hi) ** 2 where,
                m = number of particles
                A = best fit plane parameters matrix
                Xi = particle positions for the ith particle
                b = the plane verticle axis intercept
                hi = the particle score for the ith particle

                to zero with respect to both A and b per section 3.3 of Least Squares Fitting of Data by Linear or
                Quadratic Structures in David Eberly, Geometric Tools.

        Returns
        -------
        self.local_plane_parameters: (1, num_dimensions) matrix of size

        """
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

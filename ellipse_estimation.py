import numpy as np


class LeastSquaresEstimation:

    def __init__(self, limits, particle_group):
        self.limits = limits
        self.particle_group = particle_group
        self.positions_array = None
        self.j_array = None
        self.k_array = None
        self.coefficients_array = None

    def create_list_of_particle_positions_in_group(self):
        positions_array = np.zeros(len(self.particle_group), len(self.limits))
        for particle in self.particle_group:
            particle_positions_array = np.zeros(len(self.limits))
            for index, dimension in enumerate(self.limits):
                particle_positions_array[index] = particle.position[index]

        self.positions_array = positions_array


class EllipseEstimation(LeastSquaresEstimation):

    def __init__(self, limits, particle_group):
        LeastSquaresEstimation.__init__(self, limits, particle_group)

    def create_j_array(self):
        num_columns_in_j_array = (len(self.limits) ** 2 + len(self.limits)) / 2 + len(self.limits)
        j_array = np.zeros(len(self.particle_group), num_columns_in_j_array)
        for particle_index, particle in enumerate(self.particle_group):
            particle_positions_row_copy = np.copy(self.positions_array[particle_index])
            j_array_column_index = 0
            for dimension_1_index, dimension_1 in enumerate(self.positions_array[particle_index]):
                for dimension_2_index, dimension_2 in enumerate(particle_positions_row_copy):
                    j_array[particle_index, j_array_column_index] = dimension_1 * dimension_2
                    j_array_column_index += 1

                particle_positions_row_copy = np.delete(particle_positions_row_copy, 0)

            for value in self.positions_array[particle_index]:
                j_array[j_array_column_index] = value
                j_array_column_index += 1

        self.j_array = j_array

    def create_k_array(self):
        self.k_array = np.ones_like(self.j_array[0])[:, np.newaxis]

    def create_coefficients_array(self):
        j_transpose = self.j_array.transpose()
        j_transpose_j = np.dot(j_transpose, self.j_array)
        inverse_j_transpose_j = np.linalg.inv(j_transpose_j)
        coefficient_array = np.dot(inverse_j_transpose_j, np.dot(j_transpose, self.k_array))
        negative_ones = np.empty_like(coefficient_array[:, 0])[:, np.newaxis]
        negative_ones[:, :] = -1
        self.coefficients_array = np.hstack((coefficient_array, negative_ones))

    def poly_to_parameters(self):
        v = self.coefficients_array
        amat = np.array(
            [
                v[0], v
            ]
            )

    def least_squares_ellipses(self):
        self.create_list_of_particle_positions_in_group()
        self.create_k_array()
        self.create_coefficients_array()

        return self.coefficients_array

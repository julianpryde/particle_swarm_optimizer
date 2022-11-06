from unittest import TestCase
import math
import particle
import swarm
from decimal import *


class TestParticle(TestCase):
    def setUp(self):
        self.limits = [[0, 12], [3, 9], [10, 1000]]

    def test_compute_normalization_factors(self):
        # Set up test scenario
        normalization_test_particle = particle.Particle(self.limits)

        # Calculate expected value
        expected_normalization_b = [0, 3, 10]
        expected_normalization_m = [12, 6, 990]

        # Conduct test, Compare
        self.assertEqual(normalization_test_particle.position_normalization_b, expected_normalization_b,
                         'incorrect normalization b')
        self.assertEqual(normalization_test_particle.position_normalization_m, expected_normalization_m,
                         'incorrect normalization m')

    def test_find_best_neighbor(self):
        # Set up test scenario
        num_particles = 3
        particle_position_1 = 0.15  # Closer than the local radius limit, will give a better forcing function return
        particle_position_2 = 0.05  # Closer than the local radius limit, will give a worse forcing function return

        self.swarm = swarm.Swarm(num_particles, self.limits, local_radius_limit=0.2, sigma=0.01)
        self.swarm.particle_list[0].position = [0] * 3
        self.swarm.particle_list[1].position = [particle_position_1] * 3
        self.swarm.particle_list[2].position = [particle_position_2] * 3

        self.swarm.call_forcing_function()

        # Conduct test
        self.swarm.particle_list[0].find_best_neighbor(particle_swarm=self.swarm, optimization_function="max")

        # Calculate expected value
        expected_best_neighbor = self.swarm.particle_list[1]

        # Compare
        self.assertEqual(expected_best_neighbor.position, self.swarm.particle_list[0].best_neighbor.position)

    def test_update_velocity(self):
        print("Update Velocity Test")
        # Set up test scenario
        velocity_coefficient = 0.001
        velocity_update_test_particle = particle.Particle(self.limits)
        velocity_update_test_particle.best_neighbor = particle.Particle(self.limits)
        velocity_update_test_particle.position = [0.9, 0.9, 0.9]
        velocity_update_test_particle.best_neighbor.position = [0.2, 0.2, 0.2]
        velocity_update_test_particle.velocity = [0.1, 0.3, 0.01]
        velocity_update_test_particle.best_neighbor.score = 10
        velocity_update_test_particle.score = 20

        # Conduct test
        velocity_update_test_particle.update_velocity(velocity_coefficient)

        # Calculate expected value
        expected_final_velocity = []
        distance_to_best_neighbor = abs(
            particle.find_particle_distance(
                velocity_update_test_particle, velocity_update_test_particle.best_neighbor)
        )  # abs to ensure no change in sign
        score_difference = abs(
            velocity_update_test_particle.best_neighbor.score - velocity_update_test_particle.score
        )  # abs to ensure no change in sign

        # Calculate unit vector in direction of best neighbor, then multiply by score difference to get velocity vector
        #   in the direction of the best neighbor with the magnitude of the difference in scores
        for element_1, element_2 in \
                zip(velocity_update_test_particle.position, velocity_update_test_particle.best_neighbor.position):
            expected_final_velocity.append(((element_2 - element_1) / distance_to_best_neighbor) * score_difference)
            # Apply scaling factor parameter
            expected_final_velocity[-1] *= velocity_coefficient

        # Compare
        self.assertEqual(expected_final_velocity, velocity_update_test_particle.velocity)

    def test_move(self):
        # Set up test scenario
        test_move_particle = particle.Particle(self.limits)
        test_move_particle.position = [0.00, 0.32, 0.98]
        test_move_particle.velocity = [0.10, -0.23, 0.3]

        # Conduct test
        test_move_particle.move()

        # Calculate expected_final_position value
        test_move_particle.position = [0.00, 0.32, 0.98]
        test_move_particle.velocity = [0.10, -0.23, 0.3]
        expected_final_position = []
        for index in range(len(self.limits)):
            particle_projected_position = test_move_particle.position[index] + test_move_particle.velocity[index]

            if particle_projected_position < 0:
                particle_overshoot_magnitude = -particle_projected_position
                expected_final_position.append(particle_overshoot_magnitude)

            elif particle_projected_position > 1:
                particle_overshoot_magnitude = particle_projected_position - 1
                expected_final_position.append(1 - particle_overshoot_magnitude)

            else:
                expected_final_position.append(particle_projected_position)

        print("Expected positions: " + str(expected_final_position))
        print("Actual positions: " + str(test_move_particle.position))

        # Compare
        self.assertEqual(expected_final_position, test_move_particle.position)


class TestParticleStatic(TestCase):

    def setUp(self):
        self.limits = [[0, 3], [-4, 10], [99, 100]]

    def test_find_hypotenuse(self):
        side_lengths = [4, 7, 12]
        expected = math.sqrt(4 ** 2 + 7 ** 2 + 12 ** 2)
        hypotenuse = particle.find_hypotenuse(side_lengths)
        self.assertEqual(hypotenuse, expected)

    def test_find_particle_distance(self):
        particle_1 = particle.Particle(self.limits)
        particle_1.position = [Decimal(0.3), Decimal(0.9), Decimal(0.1)]
        particle_2 = particle.Particle(self.limits)
        particle_2.position = [Decimal(0.2), Decimal(0.4), Decimal(0.4)]

        difference = []
        for element_1, element_2 in zip(particle_1.position, particle_2.position):
            difference.append(element_1 - element_2)

        expected = particle.find_hypotenuse(difference)
        actual = particle.find_particle_distance(particle_1, particle_2)
        self.assertEqual(expected, actual)

    def test_calculate_raw_particle_position(self):
        # Set up test scenario
        normalized_position = [0.001, 0.5, 0.99]
        normalization_b_factors = [-3, 2, 19]
        normalization_m_factors = [0.002, 39, 2]

        # Conduct test
        actual_raw_position = particle.calculate_raw_particle_position(
                normalized_position, normalization_m_factors, normalization_b_factors
                )

        # Calculate expected value
        expected_raw_position = []
        for index, value in enumerate(normalized_position):
            expected_raw_position.append(value * normalization_m_factors[index] + normalization_b_factors[index])

        # Compare
        self.assertEqual(expected_raw_position, actual_raw_position)

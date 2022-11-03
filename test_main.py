from unittest import TestCase
from decimal import *
import main
import math


class TestMain(TestCase):
    def setUp(self):
        self.limits = [[0, 12], [3, 9], [10, 1000]]

    def test_find_hypotenuse(self):
        side_lengths = [4, 7, 12]
        expected = math.sqrt(4 ** 2 + 7 ** 2 + 12 ** 2)
        hypotenuse = main.find_hypotenuse(side_lengths)
        self.assertEqual(hypotenuse, expected)

    def test_find_particle_distance(self):
        particle_1 = main.Particle(self.limits)
        particle_1.position = [Decimal(0.3), Decimal(0.9), Decimal(0.1)]
        particle_2 = main.Particle(self.limits)
        particle_2.position = [Decimal(0.2), Decimal(0.4), Decimal(0.4)]

        difference = []
        for element_1, element_2 in zip(particle_1.position, particle_2.position):
            difference.append(element_1 - element_2)

        expected = main.find_hypotenuse(difference)
        actual = main.find_particle_distance(particle_1, particle_2)
        self.assertEqual(expected, actual)


class TestParticle(TestCase):
    def setUp(self):
        self.limits = [[0, 12], [3, 9], [10, 1000]]

    def test_compute_normalization_factors(self):
        # Set up test scenario
        particle = main.Particle(self.limits)
        particle.compute_normalization_factors(self.limits)

        # Calculate expected value
        expected_normalization_b = [0, 3, 10]
        expected_normalization_m = [12, 6, 990]

        # Conduct test, Compare
        self.assertEqual(particle.position_normalization_b, expected_normalization_b, 'incorrect normalization b')
        self.assertEqual(particle.position_normalization_m, expected_normalization_m, 'incorrect normalization m')

    def test_find_best_neighbor(self):
        # Set up test scenario
        num_particles = 3
        particle_position_1 = 0.15  # Closer than the local radius limit, will give a better forcing function return
        particle_position_2 = 0.05  # Closer than the local radius limit, will give a worse forcing function return

        self.swarm = main.Swarm(num_particles, self.limits, local_radius_limit=0.2, sigma=0.01)
        self.swarm.swarm[0].position = [0] * 3
        self.swarm.swarm[1].position = [particle_position_1] * 3
        self.swarm.swarm[2].position = [particle_position_2] * 3

        # Conduct test
        self.swarm.swarm[0].find_best_neighbor()

        # Calculate expected value
        expected_best_neighbor = self.swarm.swarm[1]

        # Compare
        self.assertEqual(expected_best_neighbor.position, self.swarm.swarm[0].best_neighbor.position)

    # TODO This is all wrong
    def test_update_velocity(self):
        # Set up test scenario
        velocity_coefficient = 0.001
        particle = main.Particle(self.limits)
        particle.velocity = [0.1, 0.3, 0.01]
        particle.best_neighbor.score = [0.33, 0.25, 0.99]
        particle.score = [0.24, 0.78, 0.01]

        # Conduct test
        particle.update_velocity(velocity_coefficient)

        # Calculate expected value
        expected = []
        i = 0
        for e1, e2 in zip(particle.best_neighbor.score, particle.score):
            expected.append(velocity_coefficient * (e1 - e2))
            if (particle.position[i] > particle.best_neighbor.position[i] and expected[-1] > 0) or \
                    (particle.position[i] < particle.best_neighbor.position[i] and expected[-1] < 0):
                expected[-1] = -expected[-1]
            i += 1

        # Compare
        self.assertEqual(expected, particle.velocity)

    def test_move(self):
        # Set up test scenario
        particle = main.Particle(self.limits)
        particle.position = [0.00, 0.32, 0.98]
        particle.velocity = [0.10, -0.23, 0.3]

        # Conduct test
        particle.move()

        # Calculate expected value
        expected = []
        for index in range(len(self.limits)):
            particle_projected_position = particle.position[index] + particle.velocity[index]
            if self.limits[index][0] >= particle_projected_position:
                particle_overshoot = particle_projected_position - self.limits[index][0]
                expected[index] = self.limits[index][0] + particle_overshoot
            elif self.limits[index][1] <= particle_projected_position:
                particle_overshoot = self.limits[index][1] - particle_projected_position
                expected[index] = self.limits[index][1] - particle_overshoot
            else:
                expected[index] += particle.velocity[index]

        # Compare
        self.assertEqual(expected, particle.position)

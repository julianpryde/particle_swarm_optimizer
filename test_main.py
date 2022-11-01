from unittest import TestCase
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
        particle_1.position = [0.3, 0.001, 0.000000004]
        particle_2 = main.Particle(self.limits)
        particle_2.position = [0.0003, 0.45, 0.9]

        difference = [element_1 - element_2 for element_1, element_2 in zip(particle_1.position, particle_2.position)]
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

    def test_update_velocity(self):
        self.fail()

    def test_move(self):
        self.fail()

    def test_shake(self):
        self.fail()
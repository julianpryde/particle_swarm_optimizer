from unittest import TestCase
import particle
import swarm


def calculate_normalized_position(raw_position, normalization_list_m, normalization_list_b):
    normal_position = []
    index = 0
    for normalization_m, normalization_b in zip(normalization_list_m, normalization_list_b):
        normal_position.append(
            (raw_position[index] - normalization_b) / normalization_m
        )
        index += 1

    return normal_position


class TestSwarm(TestCase):
    def setUp(self):
        self.limits = [[0, 10], [0, 10]]
        self.normalization_m, self.normalization_b = particle.compute_normalization_factors(self.limits)

    def create_particle_list(self, particles_to_be_found_positions):
        particle_list = []
        for index, position in enumerate(particles_to_be_found_positions):
            particle_list.append(
                particle.Particle(
                    self.limits,
                    calculate_normalized_position(position, self.normalization_m, self.normalization_b)
                )
            )

        return particle_list

    def test_find_groups_recursive(self):
        # Set up test scenario
        particles_to_be_found_positions = [
            [0, 0],
            [1, 1],
            [0.5, 0.5],
            [3.7, 3.7],
            [8, 8],
            [10, 10]
        ]

        test_swarm = swarm.Swarm(num_particles_in_swarm=6, limits=self.limits, local_radius_limit=0.5)
        test_swarm.particle_list = self.create_particle_list(particles_to_be_found_positions)

        # Calculate expected value
        expected_particles_not_yet_assigned = []
        expected_list_of_groups = [test_swarm.particle_list[:4], test_swarm.particle_list[4:]]

        # Conduct test
        list_of_groups = test_swarm.find_groups_recursive()

        # Compare
        self.assertEqual(list_of_groups, expected_list_of_groups)

    def test_iterate_neighbors(self):
        # Set up test scenario
        particles_to_be_found_positions = [
            [1, 1],
            [0.5, 0.5],
            [3.7, 3.7],
            [8, 8],
            [10, 10]
        ]

        base_particle = particle.Particle(
            self.limits,
            calculate_normalized_position([0, 0], self.normalization_m, self.normalization_b)
        )

        particles_not_yet_assigned = self.create_particle_list(particles_to_be_found_positions)

        test_swarm = swarm.Swarm(num_particles_in_swarm=6, limits=self.limits, local_radius_limit=0.5)

        # Calculate expected value
        expected_particles_not_yet_assigned = particles_not_yet_assigned[3:]
        expected_particles_in_local_group = particles_not_yet_assigned[:3]

        # Conduct test
        particles_in_local_group = test_swarm.iterate_neighbors(particles_not_yet_assigned, [], base_particle)

        # Compare
        self.assertEqual(particles_not_yet_assigned, expected_particles_not_yet_assigned)
        self.assertEqual(particles_in_local_group, expected_particles_in_local_group)

    def test_identify_particles_in_radius(self):
        # Set up test scenario
        particles_to_be_found_positions = [
            [1, 1],
            [0.5, 0.5],
            [8, 8],
            [10, 10]
        ]

        base_particle = particle.Particle(
            self.limits,
            calculate_normalized_position([0, 0], self.normalization_m, self.normalization_b)
        )

        particles_not_yet_assigned = self.create_particle_list(particles_to_be_found_positions)

        test_swarm = swarm.Swarm(num_particles_in_swarm=4, limits=self.limits, local_radius_limit=0.5)

        # Calculate expected results
        expected_particles_in_radius = particles_not_yet_assigned[0:2]
        expected_particles_not_yet_assigned = particles_not_yet_assigned[2:]

        # Conduct test
        particles_in_radius, particles_not_yet_assigned = \
            test_swarm.identify_particles_in_radius(base_particle, particles_not_yet_assigned)

        # Compare
        self.assertEqual(particles_in_radius, expected_particles_in_radius)
        self.assertEqual(particles_not_yet_assigned, expected_particles_not_yet_assigned)

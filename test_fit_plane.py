from unittest import TestCase
from fit_plane import FitPlane
from particle import Particle
import numpy


def forcing_function(x, y):
    return 2 * x + 3 * y + 4


class TestFitPlane(TestCase):
    def test_find_local_gradient(self):
        # Set up test scenario
        # z = 2x + 3y + 4
        limits = numpy.array([[0, 1], [0, 1]])
        # Generate 50 points on plane
        positions = numpy.random.random((50, 2))
        scores = forcing_function(positions[:, 0], positions[:, 1])[:, numpy.newaxis]
        for index, score in enumerate(scores):
            scores[index] += 0.1 * (numpy.random.random() - 0.5)

        particle_list = [Particle(limits, value) for value in positions]
        for index, value in enumerate(scores):
            particle_list[index].score = value[0]

        fit_plane = FitPlane(particle_list)

        # Run test
        plane_parameters, residuals = fit_plane.find_local_gradient()

        # Evaluate results
        print("Plane parameter: " + str(plane_parameters))

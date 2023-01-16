import numpy


# noinspection SpellCheckingInspection
class FitPlane:
    def __init__(self, particles_in_local_radius):
        self.particles_in_local_radius = particles_in_local_radius

    def create_gradient_a_b_arrays(self):
        particle_positions = numpy.array([particle.position for particle in self.particles_in_local_radius])
        mean_particle_positions = particle_positions.mean(axis=0)
        particle_position_differences_from_mean = particle_positions - mean_particle_positions
        # a = (Xi - Xavg) * (Xi - Xavg) ^ T
        a = numpy.sum(
            numpy.outer(
                particle_position_differences_from_mean[index, :],
                particle_position_differences_from_mean[index, :]
            )
            for index, particle in enumerate(particle_position_differences_from_mean)
        )

        scores = numpy.array([particle.score for particle in self.particles_in_local_radius])[:, numpy.newaxis]
        mean_score = scores.mean()
        score_differences_from_mean = scores - mean_score
        # b = (zi - zavg) * (Xi - Xavg)
        b = numpy.sum(
            particle_position_differences_from_mean[index, :] * score_differences_from_mean[index, :]
            for index, particle in enumerate(particle_position_differences_from_mean)
        )

        return a, b

    def find_local_gradient(self):
        a, b = self.create_gradient_a_b_arrays()
        local_plane_parameters, residuals, rank, s = numpy.linalg.lstsq(a, b)

        return local_plane_parameters

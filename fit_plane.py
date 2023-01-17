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
        a = sum(
            numpy.outer(
                particle_position_differences_from_mean[index, :],
                particle_position_differences_from_mean[index, :]
            )
            for index, particle in enumerate(particle_position_differences_from_mean)
        )

        scores = numpy.array([particle.score for particle in self.particles_in_local_radius])
        mean_score = scores.mean()
        score_differences_from_mean = (scores - mean_score)
        # b = (zi - zavg) * (Xi - Xavg)
        b = sum(
            particle_position_differences_from_mean[index, :] * score_differences_from_mean[index]
            for index, particle in enumerate(particle_position_differences_from_mean)
        )[:, numpy.newaxis]

        return a, b

    def find_local_gradient(self):
        a, b = self.create_gradient_a_b_arrays()
        local_plane_parameters, residuals, rank, s = numpy.linalg.lstsq(a, b, rcond=None)

        return local_plane_parameters, residuals

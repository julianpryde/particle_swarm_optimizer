def forcing_function(particle_positions):
    # score = -(particle_positions[0] ** 2 + particle_positions[1] ** 2 + particle_positions[2] ** 2)
    score = (
            (particle_positions[0] ** 3) / 2 +
            (particle_positions[0] ** 2) +
            (particle_positions[1] ** 3) / 2 +
            (particle_positions[1] ** 2)
            )

    return score

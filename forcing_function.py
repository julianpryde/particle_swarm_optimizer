def forcing_function(particle_positions):
    x = particle_positions[0]
    y = particle_positions[1]
    # score = -(particle_positions[0] ** 2 + particle_positions[1] ** 2 + particle_positions[2] ** 2)
    #    score = (
    #            (particle_positions[0] ** 3) / 2 +
    #            (particle_positions[0] ** 2) +
    #            (particle_positions[1] ** 3) / 2 +
    #            (particle_positions[1] ** 2) +
    #            (particle_positions[2] ** 3) / 2 +
    #            (particle_positions[2] ** 2)
    #            )

    score = \
        (2 * (x ** 2) + 1) / (10 * x) + \
        (2 * (y ** 2) + 1) / (10 * y)

    return score

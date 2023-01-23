def forcing_function(particle_positions):
    x = particle_positions[0]
    y = particle_positions[1]
    # z = particle_positions[2]
    # score = -(particle_positions[0] ** 2 + particle_positions[1] ** 2 + particle_positions[2] ** 2)
    #score = (
    #        (x ** 3) / 2 +
    #        (x ** 2) +
    #        (y ** 3) / 2 +
    #        (y ** 2)
    #        #     (z ** 3) / 2 +
    #        #     (z ** 2)
    #        )

    score = \
        (2 * (x ** 2) + 1) / (10 * x) + \
        (2 * (y ** 2) + 1) / (10 * y)

    return score

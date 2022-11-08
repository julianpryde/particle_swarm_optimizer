# Author: Julian Pryde

from swarm import Swarm
from input_handling import InputHandling


def optimize(particle_swarm, optimizing_function, velocity_coefficient, exit_criterion):
    most_movement = 1
    # while all particles move > <exit criterion> without effects of randomness factor
    while most_movement > exit_criterion:
        particle_swarm.call_forcing_function()
        particle_swarm.update_swarm_velocities(particle_swarm, optimizing_function, velocity_coefficient)
        particle_swarm.move_particles()
        # TODO add options to simulate annealing to hone in on optimum value more finely as program runs
        particle_swarm.add_randomness_factor()
        most_movement = particle_swarm.find_most_movement()


if __name__ == "__main__":
    arguments = InputHandling()
    arguments.print_inputs()
    swarm = Swarm(arguments.num_particles, arguments.limits, arguments.local_radius_limit, arguments.sigma)
    optimize(swarm, arguments.function, arguments.velocity_coefficient, arguments.exit_criterion)

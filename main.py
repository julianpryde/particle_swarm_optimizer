# Author: Julian Pryde

from swarm import Swarm
from input_handling import InputHandling
import time


def optimize(particle_swarm, function, velocity_coefficient, exit_criterion):
    # while all particles move > <exit criterion> without effects of randomness factor
    iteration = 0
    # particle_swarm.create_plot()
    while particle_swarm.most_movement > exit_criterion:
        particle_swarm.call_forcing_function()
        particle_swarm.update_swarm_velocities(function, velocity_coefficient)
        particle_swarm.move_particles()
        particle_swarm.add_randomness_factor()
        particle_swarm.find_most_movement()
        particle_swarm.print_summary(function, iteration)
        iteration += 1
        particle_swarm.simulate_annealing(iteration)
        # swarm.draw_plot()
        # time.sleep(.5)


if __name__ == "__main__":
    arguments = InputHandling()
    arguments.print_inputs()
    swarm = Swarm(
        arguments.num_particles,
        arguments.limits,
        arguments.local_radius_limit,
        arguments.sigma,
        arguments.annealing_lifetime
    )
    optimize(swarm, arguments.function, arguments.velocity_coefficient, arguments.exit_criterion)

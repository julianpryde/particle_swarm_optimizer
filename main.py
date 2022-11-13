# Author: Julian Pryde
from decimal import Decimal, InvalidOperation

from swarm import Swarm
from input_handling import InputHandling
# from decimal import Decimal


def optimize(particle_swarm, function, velocity_coefficient, exit_criterion):
    # while all particles move > <exit criterion> without effects of randomness factor
    iteration = 0
    high_particle_velocity_counter = 0
    # particle_swarm.create_plot()
    while particle_swarm.most_movement > exit_criterion:
        particle_swarm.call_forcing_function()
        velocity_coefficient = particle_swarm.update_swarm_velocities(function, velocity_coefficient)
        particle_swarm.move_particles()
        particle_swarm.add_randomness_factor()
        try:
            particle_swarm.find_most_movement()
        except InvalidOperation:
            velocity_coefficient -= Decimal(0.001)
            high_particle_velocity_counter += 1
            print("Lowering velocity coefficient by 0.001 to: " + str(velocity_coefficient))
            print("This occurrence number: " + str(high_particle_velocity_counter))
        particle_swarm.print_summary(function, iteration)
        particle_swarm.simulate_annealing(iteration)
        iteration += 1
        # swarm.draw_plot()
        # time.sleep(.5)

    print("Particle high velocity counter: " + str(high_particle_velocity_counter))
    print("Final Velocity Coefficient: " + str(velocity_coefficient))


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

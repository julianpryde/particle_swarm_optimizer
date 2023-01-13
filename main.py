# Author: Julian Pryde
# from decimal import Decimal, InvalidOperation
from swarm import Swarm
from particle import SpeedToHighError
from input_handling import InputHandling


def optimize(particle_swarm, function, velocity_coefficient, exit_criterion):
    particle_swarm.plot_particle_positions()
    iteration = 0
    high_particle_velocity_counter = 0
    iterations_with_same_best_particle_counter = 0
    old_best_particle = 0
    while particle_swarm.most_movement > exit_criterion and iterations_with_same_best_particle_counter < 100:
        particle_swarm.call_forcing_function()
        velocity_coefficient = particle_swarm.update_swarm_velocities(function, velocity_coefficient)
        particle_swarm.move_particles()
        particle_swarm.add_randomness_factor()
        try:
            particle_swarm.find_most_movement()
        except SpeedToHighError:
            velocity_coefficient -= 0.001
            high_particle_velocity_counter += 1
            print("Lowering velocity coefficient by 0.001 to: " + str(velocity_coefficient))
            print("This occurrence number: " + str(high_particle_velocity_counter))
        swarm.find_best_particle(function)
        if swarm.best_particle_id == old_best_particle:
            iterations_with_same_best_particle_counter += 1
        else:
            iterations_with_same_best_particle_counter = 0
        old_best_particle = swarm.best_particle_id
        particle_swarm.print_summary(iteration)
        particle_swarm.simulate_annealing(iteration)
        iteration += 1

    particle_swarm.find_groups_recursive()
    particle_swarm.plot_particle_positions()
    print("Particle high velocity counter: " + str(high_particle_velocity_counter))
    print("Final Velocity Coefficient: " + str(velocity_coefficient))
    print("Iterations with the same best particle: " + str(iterations_with_same_best_particle_counter))


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

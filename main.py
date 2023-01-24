# Author: Julian Pryde
from swarm import Swarm
from particle import SpeedToHighError, LocalRadiusTooSmall
from input_handling import InputHandling
from pso_timing import PSOTiming
import yappi
import datetime


def optimize(particle_swarm, function, velocity_coefficient, exit_criterion, iteration_limit):
    pso_timing = PSOTiming()
    pso_timing.start()
    yappi.set_clock_type("wall")
    yappi.start()
    particle_swarm.plot_particle_positions()
    iteration = 0
    high_particle_velocity_counter = 0
    iterations_with_same_best_particle_counter = 0
    old_best_particle = 0
    while particle_swarm.most_movement > exit_criterion and \
            iterations_with_same_best_particle_counter < 100 and \
            iteration < iteration_limit:
        particle_swarm.call_forcing_function()
        find_local_groups_success = False
        while not find_local_groups_success:
            try:
                find_local_groups_success = particle_swarm.find_local_groups()
            except LocalRadiusTooSmall:
                particle_swarm.raise_local_radius_limit()
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
        if iteration % 25 == 0:
            particle_swarm.plot_particle_positions()

    pso_timing.end()
    print(pso_timing.report())
    time_format = '%m_%d_%Y_%H%M%S'
    time_file_name = 'timereports/' + datetime.datetime.now().strftime(time_format)
    with open(time_file_name, 'w+') as timing_data_file:
        timing_data_file.write(pso_timing.report())
        yappi.get_func_stats().print_all(out=timing_data_file,
                                         columns={
                                            0: ("name", 110),
                                            1: ("ncall", 10),
                                            2: ("tsub", 8),
                                            3: ("ttot", 8),
                                            4: ("tavg", 8)
                                         })
    particle_swarm.find_groups_recursive()
    particle_swarm.plot_particle_positions()
    print("Particle high velocity counter: " + str(high_particle_velocity_counter))
    print("Final Velocity Coefficient: " + str(velocity_coefficient))
    print("Iterations with the same best particle: " + str(iterations_with_same_best_particle_counter))


if __name__ == "__main__":
    arguments = InputHandling()
    arguments.print_inputs()
    swarm = Swarm(
        arguments.formatted_arguments["num_particles"],
        arguments.formatted_arguments["limits"],
        arguments.formatted_arguments["local_radius"],
        arguments.formatted_arguments["velocity_update_method"],
        arguments.formatted_arguments["starting_sigma"],
        arguments.formatted_arguments["annealing_lifetime"]
    )
    optimize(swarm,
             arguments.formatted_arguments["function"],
             arguments.formatted_arguments["velocity_coefficient"],
             arguments.formatted_arguments["exit_criterion"],
             arguments.formatted_arguments["run_limit"]
             )

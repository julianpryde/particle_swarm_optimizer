# Author: Julian Pryde
from swarm_c import Swarm
import json
from input_handling import InputHandling
from pso_timing import PSOTiming
from math_functions import find_hypotenuse
import yappi
import datetime
import numpy as np


def initialize_timing():
    """
    Initializes both timing applications. PSO Timing simply times the total wall clock time that the program ran for.

    Returns
    -------
    PSO Timing object to be used later to determine total time.
    """
    pso_timing = PSOTiming()
    pso_timing.start()
    yappi.set_clock_type("cpu")
    yappi.start()

    return pso_timing


def initialize_run_values():
    """
    Set counters and exit criteria trackers initially to allow optimization to start

    Returns
    -------
    All set values
    """
    iteration = 0
    high_particle_velocity_counter = 0
    iterations_with_same_best_particle_counter = 0
    old_best_particle = 0
    mean_r_squared = 0
    return high_particle_velocity_counter, iteration, iterations_with_same_best_particle_counter, mean_r_squared, \
        old_best_particle


def test_exit_criteria(optimization_arguments, most_movement, iterations_with_same_best_particle, iteration, mean_r2):
    """
    Tests exit criteria against actual values

    Parameters
    ----------
    optimization_arguments: dictionary of optimization arguments, certain values in which are tested against.
    most_movement: np.double value containing the highest total velocity of all particles.
    iterations_with_same_best_particle: int containing the number of iterations with the same best particle
    iteration: int, iteration counter
    mean_r2: np.double containing the mean r2 value of all particles when using the gradient velocity update method

    Returns
    -------
    True if all conditions are met or False if one or more conditions are not met.
    """
    if most_movement > optimization_arguments['most_movement_exit_criterion'] and \
        iterations_with_same_best_particle < optimization_arguments['iteration_limit'] and \
            iteration < optimization_arguments['iteration_limit'] and \
            mean_r2 < optimization_arguments['r2_exit_criterion']:
        return True
    else:
        return False


def format_data_for_printing(dictionary):
    for element in dictionary:
        if type(dictionary[element]) is np.int_:
            dictionary[element] = int(dictionary[element])
        elif type(dictionary[element]) is np.double:
            dictionary[element] = float(dictionary[element])
        elif type(dictionary[element]) is np.ndarray:
            dictionary[element] = dictionary[element].tolist()

    return dictionary


def save_timing_report(pso_timing, optimization_arguments, swarm_arg_dict):
    """
    Saves the profile and timing information in a file

    Parameters
    ----------
    pso_timing: PSOTiming object to carry through
    optimization_arguments: arguments for printing at the top of the timing report
    swarm_arg_dict: arguments for printing at the top of the timing report
    """

    pso_timing.end()
    print(pso_timing.report())
    time_format = '%m_%d_%Y_%H%M%S'
    time_file_name = 'timereports/' + datetime.datetime.now().strftime(time_format)
    optimization_arguments = format_data_for_printing(optimization_arguments)
    swarm_arg_dict = format_data_for_printing(swarm_arg_dict)
    with open(time_file_name, 'w+') as timing_data_file:
        arguments_string = "Optimization Arguments: " + json.dumps(optimization_arguments, indent=4) + \
            "Swarm Arguments: " + json.dumps(swarm_arg_dict, indent=4)
        timing_data_file.write(arguments_string)
        timing_data_file.write(pso_timing.report())
        yappi.get_func_stats().print_all(out=timing_data_file,
                                         columns={
                                             0: ("name", 110),
                                             1: ("ncall", 10),
                                             2: ("tsub", 8),
                                             3: ("ttot", 8),
                                             4: ("tavg", 8)
                                         })


def find_best_particle(iterations_with_same_best_particle_counter, optimization_arguments):
    """
    Sets the best_particle, best_particle_id, and previous_best_particle values in particle_swarm, increments
        iterations_with_same_best_particle if the best particle is the same.

    Parameters
    ----------
    iterations_with_same_best_particle_counter: int containing number of iterations have occurred with the same best
        particle
    optimization_arguments

    Returns
    -------
    iterations_with_same_best_particle_counter
    """
    same_best_particle_as_last_iteration_flag = swarm.find_best_particle(optimization_arguments['function'])
    if same_best_particle_as_last_iteration_flag:
        iterations_with_same_best_particle_counter += 1
    else:
        iterations_with_same_best_particle_counter = 0
    return iterations_with_same_best_particle_counter


def optimize(particle_swarm, optimization_arguments, swarm_args):
    """
    optimize() is the main driver for all PSO actions.

    Parameters
    ----------
    particle_swarm: Swarm object with initialized values
    optimization_arguments: dictionary containing:
        function
        most_movement_exit_criterion
        iteration_limit
        least_squares_method
        r2_exit_criterion
        run_limit
    swarm_args: dictionary containing all other arguments to display in timing report
    """
    high_particle_velocity_counter, \
        iteration, \
        iterations_with_same_best_particle_counter, \
        mean_r_squared, \
        old_best_particle = initialize_run_values()
    particle_swarm.plot_particle_positions()
    pso_timing = initialize_timing()
    while test_exit_criteria(optimization_arguments, find_hypotenuse(particle_swarm.fastest_particle.velocity),
                             iterations_with_same_best_particle_counter, iteration, mean_r_squared):
        particle_swarm.call_forcing_function()
        particle_swarm.find_local_groups()
        mean_r_squared = particle_swarm.update_swarm_velocities(
            optimization_arguments['function'],

            swarm_args['least_squares_method']
        )
        particle_swarm.move_particles()
        particle_swarm.add_randomness_factor()
        particle_swarm.find_fastest_particle()
        iterations_with_same_best_particle_counter = find_best_particle(iterations_with_same_best_particle_counter,
                                                                        optimization_arguments)
        particle_swarm.simulate_annealing(iteration)
        particle_swarm.print_summary(iteration)
        iteration += 1
        if iteration % 10000 == 0:
            particle_swarm.plot_particle_positions()

    save_timing_report(pso_timing, optimization_arguments, swarm_args)
    return high_particle_velocity_counter, iterations_with_same_best_particle_counter


def display_final_output(high_particle_velocity_counter, iterations_with_same_best_particle_counter, particle_swarm):
    """
    Prints final output text to console, prints plot of particle positions if necessary

    Parameters
    ----------
    high_particle_velocity_counter
    iterations_with_same_best_particle_counter
    particle_swarm
    """

    particle_swarm.find_groups_recursive()
    particle_swarm.plot_particle_positions()
    print("Particle high velocity counter: " + str(high_particle_velocity_counter))
    print("Final Velocity Coefficient: " + str(swarm.velocity_coefficient))
    print("Iterations with the same best particle: " + str(iterations_with_same_best_particle_counter))


if __name__ == "__main__":
    arguments = InputHandling()
    arguments.print_arguments()
    arguments.parse_arguments()
    swarm = Swarm(arguments.swarm_initiation_arguments)
    high_velocity_counter, same_best_particle_counter = optimize(swarm,
                                                                 arguments.optimization_arguments,
                                                                 arguments.swarm_initiation_arguments
                                                                 )
    display_final_output(high_velocity_counter, same_best_particle_counter, swarm)

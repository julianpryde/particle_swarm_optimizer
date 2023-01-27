import numpy as np
import json


def read_arguments_file():
    with open("arguments", "r") as arguments_file:
        arguments = json.load(arguments_file)

    return arguments


class ArgumentException(IOError):
    pass


class InvalidVelocityCoefficient(ValueError):
    pass


class InputHandling:

    def __init__(self):
        self.arguments = read_arguments_file()
        self.formatted_arguments = {}
        self.total_num_arguments_expected = 12
        self.format_arguments()

    def assign_formatted_argument(self, key, data_type):
        self.formatted_arguments[key] = data_type(self.arguments[key])

    def format_arguments(self):
        index = 0
        for index, key in enumerate(self.arguments):
            if "num_particles" in key:
                self.assign_formatted_argument(key, np.int_)
            elif "limits" in key:
                self.assign_formatted_argument(key, np.array)
            elif "function" in key:
                self.assign_formatted_argument(key, str)
            elif "local_radius" in key:
                self.assign_formatted_argument(key, np.double)
            elif "velocity_coefficient" in key:
                self.assign_formatted_argument(key, np.double)
                if self.formatted_arguments[key] < 0:
                    raise ValueError("velocity coefficient cannot be less than 0")
            elif "starting_sigma" in key:
                self.assign_formatted_argument(key, np.double)
            elif "most_movement_exit_criterion" in key:
                self.assign_formatted_argument(key, np.double)
            elif "r2_exit_criterion" in key:
                self.assign_formatted_argument(key, np.double)
            elif "annealing_lifetime" in key:
                self.assign_formatted_argument(key, np.int_)
            elif "run_limit" in key:
                self.assign_formatted_argument(key, np.int_)
            elif "velocity_update_method" in key:
                self.assign_formatted_argument(key, str)
            elif "least_squares_method" in key:
                self.assign_formatted_argument(key, str)
            else:
                raise ArgumentException("Argument: " + key + " is not necessary")

        if index < self.total_num_arguments_expected - 1:
            raise ArgumentException("One or more arguments missing")

    def print_inputs(self):
        print(json.dumps(self.arguments, indent=4))

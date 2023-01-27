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
        self.total_num_arguments_expected = 11
        self.format_arguments()

    def format_arguments(self):
        index = 0
        for index, key in enumerate(self.arguments):
            if "num_particles" in key:
                self.formatted_arguments[key] = np.int_(self.arguments[key])
            elif "limits" in key:
                self.formatted_arguments[key] = np.array(self.arguments[key])
            elif "function" in key:
                self.formatted_arguments[key] = self.arguments[key]
            elif "local_radius" in key:
                self.formatted_arguments[key] = np.double(self.arguments[key])
            elif "velocity_coefficient" in key:
                self.formatted_arguments[key] = np.double(self.arguments[key])
                if self.formatted_arguments[key] < 0:
                    raise ValueError("velocity coefficient cannot be less than 0")
            elif "starting_sigma" in key:
                self.formatted_arguments[key] = np.double(self.arguments[key])
            elif "exit_criterion" in key:
                self.formatted_arguments[key] = np.double(self.arguments[key])
            elif "annealing_lifetime" in key:
                self.formatted_arguments[key] = np.int_(self.arguments[key])
            elif "run_limit" in key:
                self.formatted_arguments[key] = np.int_(self.arguments[key])
            elif "velocity_update_method" in key:
                self.formatted_arguments[key] = self.arguments[key]
            elif "least_squares_method" in key:
                self.formatted_arguments[key] = self.arguments[key]
            else:
                raise ArgumentException("Argument: " + key + " is not necessary")

        if index < self.total_num_arguments_expected - 1:
            raise ArgumentException("One or more arguments missing")

    def print_inputs(self):
        print(json.dumps(self.arguments, indent=4))

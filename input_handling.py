import numpy as np
import json


def read_arguments_file():
    """
    Reads contents of arguments JSON file into a python dictionary

    Returns
    -------
    arguments: dictionary
    """
    with open("arguments", "r") as arguments_file:
        arguments = json.load(arguments_file)

    return arguments


class ArgumentException(Exception):
    pass


class InputHandling:

    def __init__(self):
        """
        self.arguments: dictionary of un-formatted arguments
        self.formatted_arguments: dictionary of arguments with values formatted into data types as follows:
            num_particles: np.int_
            limits: 2-D np.array of np.doubles
            function: string
            local_radius: np.double
            velocity_coefficient: np.double
            starting_sigma: np.double
            most_movement_exit_criterion: np.double
            r2_exit_criterion: np.double
            annealing_lifetime: np.int_
            run_limit: np.int_
            velocity_update_method: string
            least_squares_method: string
        self.total_num_arguments_expected: Total number of arguments expected to determine if an argument is missing
        self.format_arguments:
        """
        self.arguments = read_arguments_file()
        self.formatted_arguments = {}
        self.total_num_arguments_expected = 12

    def assign_formatted_argument(self, key, data_type):
        """
        Assign keys and values to self.formatted_arguments

        Parameters
        ----------
        key: string to search self.arguments and assign value in formatted_arguments
        data_type: data type to convert new value to prior when assigning place in self.formatted arguments
        """
        self.formatted_arguments[key] = data_type(self.arguments[key])

    def format_arguments(self):
        """
        Looks for all argument in self.arguments and assigns them to self.formatted_arguments with their data type.
            Ensures that the correct number of arguments have been ingested.
        """
        index = 0
        for index, key in enumerate(self.arguments):
            if "num_particles" in key:
                self.assign_formatted_argument(key, np.int_)
                if self.formatted_arguments[key] < 0:
                    raise ArgumentException("Number of Particles cannot be 0 or less.")
            elif "limits" in key:
                self.assign_formatted_argument(key, np.array)
            elif "function" in key:
                self.assign_formatted_argument(key, str)
                if self.formatted_arguments[key] != "min" and self.formatted_arguments[key] != "max":
                    raise ArgumentException("Function argument must either be 'min' or 'max'.")
            elif "local_radius" in key:
                self.assign_formatted_argument(key, np.double)
                if self.formatted_arguments[key] <= 0:
                    raise ArgumentException("Local radius must be larger than 0.")
            elif "velocity_coefficient" in key:
                self.assign_formatted_argument(key, np.double)
                if self.formatted_arguments[key] < 0:
                    raise ArgumentException("Velocity coefficient cannot be less than 0.")
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
                if self.formatted_arguments[key] != "gradient" and self.formatted_arguments[key] != "best_neighbor":
                    raise ArgumentException("Velocity Update Method must be either 'gradient' or 'best_neighbor'.")
            elif "least_squares_method" in key:
                self.assign_formatted_argument(key, str)
                if self.formatted_arguments[key] != "direct" and self.formatted_arguments[key] != "zero_derivative":
                    raise ArgumentException("Least Squares Method must be either 'direct' or 'zero_derivative'.")
            else:
                raise ArgumentException("Argument: " + key + " is not necessary")

        if index < self.total_num_arguments_expected - 1:
            raise ArgumentException("One or more arguments missing")

    def print_arguments(self):
        """
        Prints arguments in pretty print json format.
        """
        print(json.dumps(self.arguments, indent=4))

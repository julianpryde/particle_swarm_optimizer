from decimal import *


def read_arguments_file():
    with open("arguments", "r") as arguments_file:
        arguments = arguments_file.read()

    arguments_list_from_file = arguments.split("\n")
    return arguments_list_from_file, arguments_file


def remove_argument_id(argument, argument_id):
    # arguments should be in "argument_id=xxx" format. function
    # removes the "argument_id=" and returns just the "xxx"
    return argument[len(argument_id) + 1:]


class InputHandling:

    def __init__(self):
        self.arguments_list, self.arguments_file_object = read_arguments_file()
        self.limits = []
        self.num_particles = None
        self.entropy = None
        self.function = None
        self.local_radius_limit = None
        self.velocity_coefficient = None
        self.sigma = None
        self.exit_criterion = None
        self.annealing_lifetime = None
        self.assign_arguments()

    def parse_limits(self, limits_argument):
        limit_strings = limits_argument.split("x")
        for index, value in enumerate(limit_strings):
            limit_tuple = value.split(",")
            limit_tuple[0] = limit_tuple[0].replace("limits=", "")
            limit_tuple[0] = Decimal(limit_tuple[0])
            limit_tuple[1] = Decimal(limit_tuple[1])
            self.limits.append(limit_tuple)

    def assign_arguments(self):
        for argument in self.arguments_list:
            if "entropy" in argument:
                self.entropy = Decimal(remove_argument_id(argument, "entropy"))
            if "num_particles" in argument:
                self.num_particles = int(remove_argument_id(argument, "num_particles"))
            if "limits" in argument:
                self.parse_limits(argument)
            if "function" in argument:
                self.function = remove_argument_id(argument, "function")
            if "local_radius" in argument:
                self.local_radius_limit = Decimal(remove_argument_id(argument, "local_radius"))
            if "velocity_coefficient" in argument:
                self.velocity_coefficient = Decimal(remove_argument_id(argument, "velocity_coefficient"))
                if self.velocity_coefficient < 0:
                    raise ValueError("velocity coefficient cannot be less than 0")
            if "starting_sigma" in argument:
                self.sigma = float(remove_argument_id(argument, "starting_sigma"))
            if "exit_criterion" in argument:
                self.exit_criterion = Decimal(remove_argument_id(argument, "exit_criterion"))
            if "annealing_lifetime" in argument:
                self.annealing_lifetime = int(remove_argument_id(argument, "annealing_lifetime"))

    def print_inputs(self):
        print("entropy = " + str(self.entropy) +
              "\nnum_particles = " + str(self.num_particles) +
              "\nlimits = " + str(self.limits) +
              "\nfunction = " + str(self.function) +
              "\nlocal radius = " + str(self.local_radius_limit) +
              "\nvelocity coefficient = " + str(self.velocity_coefficient) +
              "\nsigma = " + str(self.sigma) +
              "\nexit criterion = " + str(self.exit_criterion) +
              "\nannealing lifetime = " + str(self.annealing_lifetime)
              )

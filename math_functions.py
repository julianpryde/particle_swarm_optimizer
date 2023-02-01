import math
import numpy as np


def find_hypotenuse(side_lengths):
    return np.double(math.sqrt(sum(side_lengths ** 2)))


def compute_normalization_factors(limits):
    normalization_b = limits[:, 0]
    normalization_m = limits[:, 1] - limits[:, 0]

    return normalization_m, normalization_b

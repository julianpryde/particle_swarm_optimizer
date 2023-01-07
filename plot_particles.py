import numpy
import decimal
from matplotlib import pyplot
import forcing_function


def convert_multi_dimension_list_to_floats(list_to_become_floats):
    for index, item in enumerate(list_to_become_floats):
        if isinstance(item, list):
            value_in_floats = convert_multi_dimension_list_to_floats(list_to_become_floats[index])
            list_to_become_floats[index] = value_in_floats
        else:
            list_to_become_floats[index] = float(list_to_become_floats[index])

    return list_to_become_floats


class PlotParticles:

    def __init__(self, limits, particle_list):
        self.limits = limits
        self.particle_list = particle_list
        self.raw_positions = None
        self.raw_x_positions = None
        self.raw_y_positions = None
        self.raw_z_positions = None

    def format_particle_positions_for_plotting(self):
        if len(self.limits) > 3:
            print("Cannot display graph of more than 3 dimensions")

        self.raw_positions = []
        for particle in self.particle_list:
            self.raw_positions.append(particle.calculate_raw_position())
        float_raw_positions = convert_multi_dimension_list_to_floats(self.raw_positions)

        if len(self.limits) == 3:
            float_raw_positions += [[float(self.limits[0][0]), float(self.limits[1][0]), float(self.limits[2][0])],
                                    [float(self.limits[0][0]), float(self.limits[1][0]), float(self.limits[2][1])]
                                    ]
            self.raw_x_positions, self.raw_y_positions, self.raw_z_positions = zip(*float_raw_positions)

        elif len(self.limits) == 2:
            self.raw_x_positions, self.raw_y_positions = zip(*float_raw_positions)

    def create_contour_overlay(self):
        x = None
        y = None
        z = None
        levels = None
        delta = decimal.Decimal(0.025)
        if len(self.limits) == 2:
            levels = numpy.arange(0, 5, 0.25)
            x = numpy.arange(self.limits[0][0] + decimal.Decimal(0.025), self.limits[0][1], delta)
            y = numpy.arange(self.limits[1][0] + decimal.Decimal(0.025), self.limits[1][1], delta)
            x, y = numpy.meshgrid(x, y)
            z = forcing_function.forcing_function([x, y])

        return x, y, z, levels

    def plot_particle_positions(self, plot_contour_overlay=False):
        self.format_particle_positions_for_plotting()
        figure = pyplot.figure()
        axes = None

        if len(self.limits) == 3:
            axes = figure.add_subplot(projection='3d')
            axes.scatter(self.raw_x_positions, self.raw_y_positions, self.raw_z_positions, c='black')

        elif len(self.limits) == 2:
            axes = figure.add_subplot()
            axes.scatter(self.raw_x_positions, self.raw_y_positions, c='black')

        if plot_contour_overlay:
            x, y, z, levels = self.create_contour_overlay()
            contour_plot = axes.contour(x, y, z, levels)
            axes.clabel(contour_plot, inline=True, fontsize=10)

        pyplot.xlim(left=self.limits[0][0], right=self.limits[0][1])
        pyplot.ylim(bottom=self.limits[1][0], top=self.limits[1][1])
        pyplot.show()

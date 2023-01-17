import numpy
from matplotlib import pyplot
import forcing_function
from pso_timing import PSOTiming


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
        self.raw_particle_positions = None

    def format_particle_positions_for_plotting(self):
        if len(self.limits) > 3:
            print("Cannot display graph of more than 3 dimensions")

        if len(self.limits) == 3:
            extra_particles = [[float(self.limits[0][0]), float(self.limits[1][0]), float(self.limits[2][0])],
                               [float(self.limits[0][0]), float(self.limits[1][0]), float(self.limits[2][1])]
                               ]
            self.raw_particle_positions = numpy.zeros((len(self.particle_list) + 2, 3))

            for index, particle in enumerate(self.particle_list):
                particle_raw_position = particle.calculate_raw_position()
                self.raw_particle_positions[index, :] = particle_raw_position
            self.raw_particle_positions[-2:, :] = numpy.array(extra_particles)

        elif len(self.limits) == 2:
            self.raw_particle_positions = numpy.zeros((len(self.particle_list), 2))
            for index, particle in enumerate(self.particle_list):
                particle_raw_position = particle.calculate_raw_position()
                self.raw_particle_positions[index, :] = particle_raw_position

    def create_contour_overlay(self):
        x = None
        y = None
        z = None
        levels = None
        delta = 0.025
        if len(self.limits) == 2:
            levels = numpy.arange(0, 5, 0.25)
            x = numpy.arange(self.limits[0][0] + 0.025, self.limits[0][1], delta)
            y = numpy.arange(self.limits[1][0] + 0.025, self.limits[1][1], delta)
            x, y = numpy.meshgrid(x, y)
            z = forcing_function.forcing_function([x, y])

        return x, y, z, levels

    def plot_particle_positions(self, plot_contour_overlay=False):
        self.format_particle_positions_for_plotting()
        figure = pyplot.figure()
        axes = None

        if len(self.limits) == 3:
            plot_contour_overlay = False
            axes = figure.add_subplot(projection='3d')
            axes.scatter(self.raw_particle_positions[:, 0],
                         self.raw_particle_positions[:, 1],
                         self.raw_particle_positions[:, 2],
                         c='black')

        elif len(self.limits) == 2:
            axes = figure.add_subplot()
            axes.scatter(self.raw_particle_positions[:, 0], self.raw_particle_positions[:, 1], c='black')

        if plot_contour_overlay:
            x, y, z, levels = self.create_contour_overlay()
            contour_plot = axes.contour(x, y, z, levels)
            axes.clabel(contour_plot, inline=True, fontsize=10)

        pyplot.xlim(left=self.limits[0][0], right=self.limits[0][1])
        pyplot.ylim(bottom=self.limits[1][0], top=self.limits[1][1])
        pyplot.show()

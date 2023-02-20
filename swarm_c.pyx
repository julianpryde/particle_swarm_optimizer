from particle_c import Particle, SpeedToHighError
from input_handling import ArgumentException
import plot_particles
from math_functions import find_hypotenuse
import numpy as np
import functools
from typing import Sized
import networkx as nx


class ParticleListError(Exception):
    pass


class ParticleList:
    """
    All variables and methods necessary for an arbitrary group of particles
    """

    def __init__(self, **kwargs):
        """

        Parameters
        ----------
        kwargs: Dict of either a python list of particles such as {"particles": [particle_1, ...]} or arguments to
            instantiate a new set of particles, such as {"limits": [[0, 10], [-4, 0]], "num_particles": 50}
        """
        if "particles" in kwargs:
            if not kwargs["particles"]:
                self.particles = []
            elif isinstance(kwargs["particles"][0], (int, np.int32, np.int64)):
                self.particles = kwargs["particle_swarm"][kwargs["particles"]]
            else:
                self.particles = kwargs["particles"]
        else:
            self.particles = [Particle(kwargs["limits"], i) for i in range(kwargs["num_particles"])]

    def __len__(self) -> int:
        return len(self.particles)

    def __iter__(self):
        return iter(self.particles)

    def build_particle_list(self, expression):
        """
        Creates a list out of a subset of its own particle list according to an expression.

        Parameters
        ----------
        expression: function which evaluates to True for all particles to be in the returned list

        Returns
        -------
        python list of particles according to the expression
        """
        result = [particle for particle_index, particle in enumerate(self.particles) if expression(particle)]
        return result

    def __getitem__(self, index):
        """
        Get a particle or group of particles in a ParticleList instance or a single particle.
        Groups can be selected using an array of booleans or an array of integers
        Parameters
        ----------
        index: List or array of booleans or integers or scalar integer

        Returns
        -------
        ParticleList of particles if selecting multiple particles or single particle.
        """
        if isinstance(index, (list, np.ndarray)):
            if isinstance(index[0], (bool, np.bool_)):
                return ParticleList(particles=self.build_particle_list(lambda particle: index[particle.id]))

            if isinstance(index[0], (int, np.int_, np.int32, np.int64)):
                return ParticleList(particles=self.build_particle_list(lambda particle: index == particle.id))

        elif isinstance(index, (int, np.int_, np.int32, np.int64)):
            return self.particles[index]

    def __add__(self, other):
        if not self.particles:
            output = ParticleList(particles=[other])
        elif isinstance(other, ParticleList):
            output = ParticleList(particles=(self.particles + other.particles))
        elif isinstance(other, list):
            combined_particles = self.particles + other
            output = ParticleList(particles=combined_particles)
        elif isinstance(other, Particle):
            combined_particles = self.particles + [other]
            output = ParticleList(particles=combined_particles)
        elif isinstance(other, np.ndarray):
            combined_particles = self.particles + list(other)
            output = ParticleList(particles=combined_particles)
        else:
            raise ParticleListError("Invalid operand type: " + str(type(other)))
        return output

    def __iadd__(self, other):
        return self.__add__(other)

    def intersection(self, other):
        def id_intersection(particle):
            if isinstance(other, ParticleList):
                return True if particle.id in other.get_ids() else False
            else:
                return True if particle.id in other else False

        return ParticleList(particles=self.build_particle_list(id_intersection))

    def get_ids(self):
        ids = [particle.id for particle in self.particles]
        return ids

    def get_scores(self):
        return np.array([particle.score for particle in self.particles])

    def get_velocities(self):
        return np.array([particle.velocity for particle in self.particles])

    def remove(self, particles_to_remove):
        """
        Removes any number of particles using the "id" value of each particle.
        Parameters
        ----------
        particles_to_remove: Either a single particle or a ParticleList object
        """
        if isinstance(particles_to_remove, ParticleList):
            particle_ids = [particle.id for particle in particles_to_remove]
        else:
            particle_ids = particles_to_remove.id

        new_particles = self.build_particle_list(lambda particle: particle.id not in particle_ids)

        self.particles = new_particles

    def pop(self):
        popped_particle = self[0]
        self.particles = self.particles[1:]
        return popped_particle

    def get_best(self, optimization_function):
        """
        Gets the best particle based on score
        Parameters
        ----------
        optimization_function: str either "min" or "max"

        Returns
        -------
        Particle with highest score in self
        """
        extreme = np.argmin if optimization_function == "min" else np.argmax
        scores = self.get_scores()

        return self[extreme(scores)]

    def iterate_particles(self, function, return_type=None, *args):
        """
        Applies function argument to all particles using map() builtin.  Passes *args to function.  particle must be
            the last parameter in the function definition, as functools.partial() places the args passed to it during
            initialization before the args passed to it when called.

        Parameters
        ----------
        function: function that calls the function to be applied to all particles in ParticleList
        args: args to be passed to function
        return_type: type of container to use for output array

        Returns
        -------
        np.ndarray of output from function calls on all particles.  If the function returns more than one variable,
            return array is 2-D, with each column containing one returned variables for each particle and each row
            containing all returned values for each particle.

        Example
        -------
        args = (self.velocity_coefficient, optimization_function, least_squares_method)

        outputs = self.iterate_particles(
            lambda inner_args, particle: particle.update_velocity_with_gradient(*inner_args), *args
        )

        """
        full_function = functools.partial(function, args)
        output_list = list(map(full_function, self))
        if not output_list:
            output_list = None
        elif return_type == ParticleList:
            output_list = ParticleList(particles=[output_list])
        elif return_type == list:
            pass
        return output_list

    def get_particles_by_id_looper(self, iteration, particle_ids, particle_list):
        if self[iteration].id in particle_ids:
            particle_list += self[iteration]
            particle_ids.remove(self[iteration].id)
            if not particle_ids:
                return particle_list
            else:
                iteration += 1
                particle_list = self.get_particles_by_id_looper(iteration, particle_ids, particle_list)
        elif iteration == len(self) - 1:
            raise ParticleListError("No particle in this list with id of " + particle_ids)
        else:
            iteration += 1
            particle_list = self.get_particles_by_id_looper(iteration, particle_ids, particle_list)

        return particle_list

    def get_particles_by_id(self, particle_ids):
        output = self.get_particles_by_id_looper(0, particle_ids, ParticleList(particles=[]))
        return output

    def remove_duplicates(self):
        all_particle_ids = np.array(self.get_ids())
        unique_particle_ids = list(np.unique(all_particle_ids))
        output_particle_list = self.get_particles_by_id(unique_particle_ids)
        self.particles = output_particle_list.particles


class Swarm(ParticleList):
    def __init__(self, swarm_arguments):
        self.limits = swarm_arguments['limits']
        super().__init__(limits=self.limits, num_particles=swarm_arguments["num_particles"])
        self.initial_local_radius_limit = swarm_arguments['local_radius_limit']
        self.local_radius_limit = self.initial_local_radius_limit
        self.min_local_radius_limit = np.double(0.01)
        self.velocity_update_method = swarm_arguments['velocity_update_method']
        self.fastest_particle = self[0]
        self.best_particle = self[0]
        self.previous_best_particle = None
        self.list_of_groups = None
        self.r_squareds = np.zeros(len(self.particles))
        self.velocity_coefficient = swarm_arguments['velocity_coefficient']
        self.high_particle_velocity_counter = 0
        if 'sigma' in swarm_arguments:
            self.sigma = swarm_arguments['initial_sigma']
            self.initial_sigma = swarm_arguments['initial_sigma']
        else:
            self.sigma = 0.01
            self.initial_sigma = 0.01

        if 'annealing_lifetime' in swarm_arguments:
            self.annealing_lifetime = swarm_arguments['annealing_lifetime']
        else:
            self.annealing_lifetime = 100

    def simulate_annealing(self, iteration):
        if iteration < self.annealing_lifetime:
            self.sigma = self.initial_sigma * (1 - (iteration / self.annealing_lifetime))
        else:
            self.sigma = np.int_(0)
            
        if self.local_radius_limit >= self.min_local_radius_limit:
            self.local_radius_limit -= (self.initial_local_radius_limit - self.min_local_radius_limit) / \
                                       self.annealing_lifetime
        else:
            self.local_radius_limit = self.min_local_radius_limit

    def raise_local_radius_limit(self):
        self.local_radius_limit += (self.initial_local_radius_limit - self.min_local_radius_limit) / \
                                   self.annealing_lifetime

    def call_forcing_function(self):
        self.iterate_particles(lambda inner_args, particle: particle.execute_forcing_function())

    def find_local_groups(self):
        find_local_groups_success = np.bool_([False])
        while not all(find_local_groups_success):
            find_local_groups_success = self.iterate_particles(
                lambda args, particle: particle.find_particles_in_local_radius(self),
                np.ndarray,
                ())

            if not all(find_local_groups_success):
                self.raise_local_radius_limit()

    def update_velocities_with_best_neighbor(self):
        args = self.velocity_coefficient
        velocity_coefficient_too_high = any(
            self.iterate_particles(
                lambda inner_args, particle: particle.update_velocity_with_best_neighbor(*inner_args), np.ndarray, *args
            )
        )
        return velocity_coefficient_too_high

    def update_velocities_with_gradient(self, least_squares_method, optimization_function):
        args = (self.velocity_coefficient, optimization_function, least_squares_method)

        outputs = self.iterate_particles(
            lambda inner_args, particle: particle.update_velocity_with_gradient(*inner_args), list, *args
        )
        self.r_squareds = np.array([output_tuple[1] for output_tuple in outputs])
        velocity_coefficient_too_high = any([output_tuple[0] for output_tuple in outputs])
        return velocity_coefficient_too_high

    def update_swarm_velocities(self, optimization_function, least_squares_method):
        if self.velocity_update_method == "best neighbor":
            velocity_coefficient_too_high = self.update_velocities_with_best_neighbor()
        elif self.velocity_update_method == "gradient":
            velocity_coefficient_too_high = self.update_velocities_with_gradient(least_squares_method,
                                                                                 optimization_function)
        else:
            raise ArgumentException("Velocity update method: \"" + self.velocity_update_method + "\" not implemented.")

        if velocity_coefficient_too_high:
            self.velocity_coefficient -= 0.001
            print("Velocity coefficient too high. Particles moving too fast to control. Reducing velocity"
                  " coefficient by 0.001 to: " + str(self.velocity_coefficient) + ".\n")

        return np.mean(self.r_squareds)

    def move_particles(self):
        for particle in self.particles:
            particle.move()

    def add_randomness_factor(self):
        for particle in self.particles:
            particle.shake(self.sigma)

    def find_fastest_particle(self):
        particle_movements = np.array(list(map(find_hypotenuse, self.get_velocities())))
        self.fastest_particle = self[np.argmax(particle_movements)]
        particle_movements_over_limit = particle_movements > find_hypotenuse(np.ones(len(self.limits)))

        try:
            if any(particle_movements_over_limit):
                raise SpeedToHighError(particle_movements)
        except SpeedToHighError as error:
            self[particle_movements_over_limit].velocity = np.zeros(len(self.limits))
            self.velocity_coefficient -= 0.001
            self.high_particle_velocity_counter += 1
            print("Particle(s)" + str(np.where(particle_movements_over_limit)) + " velocity too high at " +
                  str(error.speed) + ". Reducing particle velocity to 0, lowering velocity coefficient by 0.001 to: " +
                  str(self.velocity_coefficient) + ". This is occurence number: " +
                  str(self.high_particle_velocity_counter))

    def find_best_particle(self, function):
        self.previous_best_particle = self.best_particle
        self.best_particle = self.get_best(function)
        return True if self.best_particle is self.previous_best_particle else False

    def print_summary(self, iteration):
        output_string = \
            "Iteration: " + str(iteration) + "\n" + \
            "sigma: " + str(self.sigma) + "\n" + \
            "initial sigma: " + str(self.initial_sigma) + "\n" + \
            "Most movement: " + str(find_hypotenuse(self.fastest_particle.velocity)) + "\n" + \
            "Best Particle Score: " + str(self.best_particle.score) + "\n" + \
            "Scores: " + str(self.get_scores()) + "\n" + \
            "Best particle position: " + str(self.best_particle.calculate_raw_position()) + "\n" + \
            "Best particle ID: " + str(self.best_particle.id) + "\n" + \
            "Best particle velocity: " + str(self.best_particle.velocity) + "\n"
            # "Velocities: " + str(self.get_velocities())
        if self.velocity_update_method == "gradient":
            output_string += "Average R2: " + str(self.r_squareds.mean()) + "\n"
        print(output_string)

    def find_groups_graphs(self):
        """
        Finds groups of particles within each others' local radius by the following algorithm:
        - Create adjacency matrix between all particles where edge weight is particle distance
        - If edge weight is > local radius limit, set edge weight to zero
        - Create a graph where:
            a. each node is a particle
            b. edges between particles exist if the distance between the two particles < local radius limit
        - Determine the connected groups of the graph
        """
        particle_adjacency = np.zeros((len(self.particles), len(self.particles)))
        for i, from_particle in enumerate(self):
            particle_adjacency[i, :] = np.array([
                from_particle.find_distance_to_particle(to_particle) for to_particle in self
            ])
        particle_adjacency = particle_adjacency < self.local_radius_limit
        particle_graph = nx.from_numpy_array(particle_adjacency)
        list_of_groups = nx.connected_components(particle_graph)
        print("List of groups: " + str(list(list_of_groups)))

    def find_groups_recursive(self):
        not_yet_assigned = ParticleList(particles=self.particles)
        list_of_groups = []
        while len(not_yet_assigned) > 1:
            base_particle = not_yet_assigned.pop()
            local_group = ParticleList(particles=[base_particle])
            local_group, not_yet_assigned = \
                base_particle.iterate_neighbors_to_find_local_groups(not_yet_assigned, local_group)
            list_of_groups.append(local_group)

        if len(not_yet_assigned) == 1:
            list_of_groups.append(not_yet_assigned)

        print("Number of groups: " + str(len(list_of_groups)))
        self.list_of_groups = list_of_groups

    def plot_particle_positions(self):
        plot = plot_particles.PlotParticles(self.limits, self.particles)
        plot.plot_particle_positions(plot_contour_overlay=True)

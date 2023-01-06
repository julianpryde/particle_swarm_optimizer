# particle_swarm_optimizer

A flexible Particle Swarm Optimization implementation in Python.  Created as a personal project by Julian Pryde, not intended for professional use.

### Photos
![Before](https://raw.githubusercontent.com/EleoFalcon/particle_swarm_optimizer/master/screenshots/Screenshot%202022-12-23%20140113.png)
![After View 1](https://raw.githubusercontent.com/EleoFalcon/particle_swarm_optimizer/master/screenshots/Screenshot%202022-12-23%20140638.png)
![After View 2](https://raw.githubusercontent.com/EleoFalcon/particle_swarm_optimizer/master/screenshots/Screenshot%202022-12-23%20140047.png)

### Quickstart
1. Pull repository
2. Update forcing_function file with your forcing function
3. Update arguments file with your parameters
4. Run main.py
5. Output will be to STDOUT

### Features
- Handles problems in any number of dimensions
- Stops when either no particle has moved by more than a specific distance or when the best particle has not changed for 100 iterations
- Outputs the total number of groups of particles that have gathered together around local maxima/minima
 
### Parameters
- num_particles: Sets the number of particles in the simulation
- function: <max/min> Tell the program whether to find a maximum or a minimum of the forcing function
- local_radius: The radius over which each particle will search for other better particles when determining its velocity for the next iteration
- velocity_coefficient: Universal scaling factor to determine the velocity of each particle
- starting_sigma: Coefficient for determining the gaussian spread of each particle on the first iteration
- exit_criterion: If no particle moves less than this number in the normalized axes, the program will assume it has reached a max/min and stop.
- annealing_lifetime: The sigma value will go down incrementally until this iteration number.

# Dependencies:
- decimal
- math
- random
- matplotlib

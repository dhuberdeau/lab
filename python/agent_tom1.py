import random
import copy
import numpy as np
from scipy.stats import dirichlet
import mdptoolbox as mdp

import Tom_environment as TE
from Tom_environment import create_grid

# create an 11x11 grid for simulation (No barriers right now)
TOM = TE.Tom_environment()
# TOM.add_barriers()
B,G,O,P = TOM.add_objects()
A = TOM.add_player()

# print the grid to check it out:
print('Original Grid:')
TOM.print_grid()

# print('Random navigation:')
# random_moves = TOM.navigate_sto(A,B,G,O,P)

print('MDP solver navigation:')
solver_moves = TOM.navigate_mdp(A,B,G,O,P)

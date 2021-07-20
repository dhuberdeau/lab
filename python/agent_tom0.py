import random
import copy
import numpy as np
from scipy.stats import dirichlet

import Tom_environment as TE
from Tom_environment import create_grid

TOM = TE.Tom_environment();
# TOM.create_grid()
# grid = create_grid()
TOM.add_barriers()
B,G,O,P = TOM.add_objects()
A = TOM.add_player()

print('Original Grid:')
TOM.print_grid()
moves, path = TOM.navigate_sto(A,B,G,O,P)

sto_agents = {}
for i in range(5):
    # grid = create_grid()
    TOM.add_barriers()
    B,G,O,P = TOM.add_objects()
    A = TOM.add_player()
    og = copy.deepcopy(TOM.grid)
    m,p = TOM.navigate_sto_np(A,B,G,O,P)
    sto_agents[i] = (og, p, m)

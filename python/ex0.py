import deepmind_lab
import numpy as np

# Construct and start the environment.
env = deepmind_lab.Lab('/seekavoid_arena_01', ['RGB_INTERLEAVED'])
env.reset()

# Create all-zeros vector for actions.
# action = np.zeros([7], dtype=np.intc)
action = np.array([0,0,0,1,0,0,0], dtype=np.intc)

# Advance the environment 4 frames while executing the all-zeros action.
reward = env.step(action, num_steps=4)

# Retrieve the observations of the environment in its new state.
obs = env.observations()  # dict of Numpy arrays
rgb_i = obs['RGB_INTERLEAVED']
assert rgb_i.shape == (240, 320, 3)

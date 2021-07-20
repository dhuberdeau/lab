import deepmind_lab
from dmenv_module import Lab

import numpy as np
import sonnet as snt
from acme import environment_loop
from acme import specs
from acme import wrappers
from acme.agents.tf import d4pg
from acme.tf import networks
from acme.tf import utils as tf2_utils
from acme.utils import loggers

import numpy as np
import os

def convert_lab_spec_to_dm_lab_spec(environment_spec):
    desired_actions = ['MOVE_BACK_FORWARD', 'STRAFE_LEFT_RIGHT']
    desired_observations = 'RGB_INTERLEAVED'

    env = specs.EnvironmentSpec(
        specs.BoundedArray(
            shape = environment_spec.observations[
                desired_observations].shape,
            dtype='float32',
            name='RGB_INTERLEAVED',
            minimum=0,
            maximum=255),
        specs.BoundedArray(
            shape = np.shape(desired_actions),
            dtype='int32',
            minimum=environment_spec.actions[desired_actions[0]].minimum,
            maximum=environment_spec.actions[desired_actions[0]].maximum,
            name="MOVE"),
        environment_spec.rewards,
        environment_spec.discounts)

    return env

lab = Lab("tests/empty_room_test", ['RGB_INTERLEAVED'],
     {'fps': '30', 'width': '160', 'height': '120'})
lab.reset()

environment = wrappers.SinglePrecisionWrapper(lab)
environment_spec_ = specs.make_environment_spec(environment)
environment_spec = convert_lab_spec_to_dm_lab_spec(environment_spec_)
environment_spec = wrappers.SinglePrecisionWrapper(environment_spec)
#@title Build agent networks
# Get total number of action dimensions from action spec.
num_dimensions = np.prod(np.shape(environment_spec.actions))

# Create the shared observation network; here simply a state-less operation.
observation_network = tf2_utils.batch_concat

# Create the deterministic policy network.
policy_network = snt.Sequential([
    networks.LayerNormMLP((256, 256, 256), activate_final=True),
    networks.NearZeroInitializedLinear(num_dimensions),
    networks.TanhToSpec(environment_spec.actions),
])

# Create the distributional critic network.
critic_network = snt.Sequential([
    # The multiplexer concatenates the observations/actions.
    networks.CriticMultiplexer(),
    networks.LayerNormMLP((512, 512, 256), activate_final=True),
    networks.DiscreteValuedHead(vmin=-150., vmax=150., num_atoms=51),
])

# Create a logger for the agent and environment loop.
agent_logger = loggers.TerminalLogger(label='agent', time_delta=10.)
env_loop_logger = loggers.TerminalLogger(label='env_loop', time_delta=10.)

# Create the D4PG agent.
environment_spec = wrappers.SinglePrecisionWrapper(environment_spec)
agent = d4pg.D4PG(
    environment_spec=environment_spec,
    policy_network=policy_network,
    critic_network=critic_network,
    observation_network=observation_network,
    sigma=1.0,
    logger=agent_logger,
    checkpoint=False
)

# Create an loop connecting this agent to the environment created above.
environment.reset()
env_loop = environment_loop.EnvironmentLoop(
    environment, agent, logger=env_loop_logger)

# Run a `num_episodes` training episodes.
# Rerun this cell until the agent has learned the given task.
for i_run in range(1, 100):
    env_loop.run(num_episodes=1)

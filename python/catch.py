# pylint: disable=g-bad-file-header
# Copyright 2019 The dm_env Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or  implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Catch reinforcement learning environment."""

import dm_env
from dm_env import specs
import numpy as np

_ACTIONS = (-1, 0, 1)  # Left, no-op, right.


class Catch(dm_env.Environment):
  """A Catch environment built on the `dm_env.Environment` class.
  The agent must move a paddle to intercept falling balls. Falling balls only
  move downwards on the column they are in.
  The observation is an array shape (rows, columns), with binary values:
  zero if a space is empty; 1 if it contains the paddle or a ball.
  The actions are discrete, and by default there are three available:
  stay, move left, and move right.
  The episode terminates when the ball reaches the bottom of the screen.
  """

  def __init__(self, rows=10, columns=5, seed=1):
    """Initializes a new Catch environment.
    Args:
      rows: number of rows.
      columns: number of columns.
      seed: random seed for the RNG.
    """
    self._rows = rows
    self._columns = columns
    self._rng = np.random.RandomState(seed)
    self._board = np.zeros((rows, columns), dtype=np.float32)
    self._ball_x = None
    self._ball_y = None
    self._paddle_x = None
    self._paddle_y = self._rows - 1
    self._reset_next_step = True

  def reset(self):
    """Returns the first `TimeStep` of a new episode."""
    self._reset_next_step = False
    self._ball_x = self._rng.randint(self._columns)
    self._ball_y = 0
    self._paddle_x = self._columns // 2
    return dm_env.restart(self._observation())

  def step(self, action):
    """Updates the environment according to the action."""
    if self._reset_next_step:
      return self.reset()

    # Move the paddle.
    dx = _ACTIONS[action]
    self._paddle_x = np.clip(self._paddle_x + dx, 0, self._columns - 1)

    # Drop the ball.
    self._ball_y += 1

    # Check for termination.
    if self._ball_y == self._paddle_y:
      reward = 1. if self._paddle_x == self._ball_x else -1.
      self._reset_next_step = True
      return dm_env.termination(reward=reward, observation=self._observation())
    else:
      return dm_env.transition(reward=0., observation=self._observation())

  def observation_spec(self):
    """Returns the observation spec."""
    return specs.BoundedArray(shape=self._board.shape, dtype=self._board.dtype,
                              name="board", minimum=0, maximum=1)

  def action_spec(self):
    """Returns the action spec."""
    return specs.DiscreteArray(
        dtype=int, num_values=len(_ACTIONS), name="action")

  def _observation(self):
    self._board.fill(0.)
    self._board[self._ball_y, self._ball_x] = 1.
    self._board[self._paddle_y, self._paddle_x] = 1.
    return self._board.copy()

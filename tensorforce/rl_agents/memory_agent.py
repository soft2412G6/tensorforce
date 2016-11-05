# Copyright 2016 reinforce.io. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""
Default implementation for using a replay memory.
"""
from tensorforce.replay_memories.replay_memory import ReplayMemory
from tensorforce.rl_agents.rl_agent import RLAgent

class MemoryAgent(RLAgent):

    default_config = {
        'batch_size': 100,
        'update_rate': 10,
        'min_replay_size': 100
    }

    value_function_ref = None

    def __init__(self, agent_config, network_config, tf_config):
        """
        Initialize a vanilla DQN agent as described in
        http://www.nature.com/nature/journal/v518/n7540/full/nature14236.html.

        :param agent_config: Configuration parameters for agent
        :param network_config: Configuration parameters for deep Q network,
        :param tf_config: Configuration for TensorFlow execution, load/store of models,
        and so forth.
        """
        self.value_function = None
        self.agent_config = agent_config
        self.memory = ReplayMemory(**agent_config)
        self.step_count = 0
        self.batch_size = agent_config.get('batch_size', self.default_config['batch_size'])
        self.update_rate = agent_config.get('update_rate', self.default_config['update_rate'])
        self.min_replay_size = agent_config.get('min_replay_size', self.default_config['min_replay_size'])

        if self.value_function_ref:
            self.value_function = self.value_function_ref(agent_config,
                                                          network_config,
                                                          tf_config,
                                                          agent_config['deterministic_mode'])

    def get_action(self, state):
        """
        Executes one reinforcement learning step. Implicitly computes updates
        according to the update frequency.

        :param state: Observed state tensor
        :return: Which action to take
        """
        action = self.value_function.get_action(state)

        return action

    def add_observation(self, state, action, reward, terminal):
        """
        Adds an observation for training purposes.

        :param state: State observed
        :param action: Action taken in state
        :param reward: Reward observed
        :param terminal: Indicates terminal state
        """
        self.memory.add_experience(state, action, reward, terminal)

        if self.step_count > self.min_replay_size and self.step_count % self.update_rate == 0:
            self.value_function.update(self.memory.sample_batch(self.batch_size))

        self.step_count += 1

    def save_model(self, path):
        self.value_function.save_model(path)

    def load_model(self, path):
        self.value_function.load_model(path)
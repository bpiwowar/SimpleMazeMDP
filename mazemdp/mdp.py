"""
Author: Olivier Sigaud
"""

import numpy as np

from mazemdp.toolbox import discreteProb


class SimpleActionSpace:  # class describing the action space of the markov decision process
    def __init__(self, action_list=None, nactions=0):
        if action_list is None or len(action_list) == 0:
            self.actions = np.arange(nactions)
        else:
            self.actions = action_list

        self.size = len(self.actions)

    def sample(self, prob_list=None):
        # returns an action drawn according to the prob_list distribution,
        # if the param is not set, then it is drawn from a uniform distribution
        if prob_list is None:
            prob_list = np.ones(self.size) / self.size

        index = discreteProb(prob_list)
        return self.actions[index]


class Mdp:
    """
    defines a Markov Decision Process
    """

    def __init__(
        self,
        nb_states,
        action_space,
        start_distribution,
        transition_matrix,
        reward_matrix,
        plotter,
        gamma=0.9,
        terminal_states=None,
        timeout=50,
        has_state=True,
    ):
        assert timeout > 10, "timeout too short:" + timeout
        self.nb_states = nb_states
        if terminal_states is None:
            terminal_states = []
        self.terminal_states = terminal_states
        self.action_space = action_space
        self.has_state = has_state
        self.timeout = timeout  # maximum length of an episode
        self.timestep = 0
        self.P0 = start_distribution  # distribution used to draw the first state of the agent, used in method reset()
        self.P = transition_matrix
        self.r = reward_matrix
        self.plotter = plotter  # used to plot the maze
        self.gamma = gamma  # discount factor
        self.current_state = None

    def reset(
        self, uniform=False
    ):  # initializes an episode and returns the state of the agent
        # if uniform is set to False, the first state is drawn according to the P0 distribution,
        # else it is drawn from a uniform distribution over all the states except for walls

        if uniform:
            prob = np.ones(self.nb_states-1) / (self.nb_states-1)
            self.current_state = discreteProb(prob)
        else:
            self.current_state = discreteProb(self.P0)

        self.timestep = 0
        self.last_action_achieved = False
        return self.current_state

    def done(self):  # returns True if the episode is over
        if self.current_state in self.terminal_states:
            return True
        return self.timestep == self.timeout  # done when timeout reached

    def step(self, u, deviation=0):  # performs a step forward in the environment,
        # if you want to add some noise to the reward, give a value to the deviation param
        # which represents the mean μ of the normal distribution used to draw the noise

        noise = deviation * np.random.randn()  # generate noise, useful for RTDP

        # r is the reward of the transition, you can add some noise to it
        reward = self.r[self.current_state, u] + noise

        # the state reached when performing action u from state x is sampled
        # according to the discrete distribution self.P[x,u,:]
        next_state = discreteProb(self.P[self.current_state, u, :])

        self.timestep += 1

        info = {
            "State transition probabilities": self.P[self.current_state, u, :],
            "reward's noise value": noise,
        }  # can be used when debugging

        self.current_state = next_state
        done = self.done()  # checks if the episode is over

        return [next_state, reward, done, info]

    def new_render(
        self, title, mode="human"
    ):  # initializes a new environment rendering (a plot defined by a figure, an axis...)
        return self.plotter.new_render(title, mode=mode)

    def render(
        self, v=None, policy=None, agent_pos=None, title="No Title", mode="legacy"
    ):  # outputs the agent in the environment with values V (or Q)
        if v is None:
            v = np.array([])

        if policy is None:
            policy = np.array([])

        if not self.has_state:
            return self.plotter.render(v=v, agent_state=None, title=title, mode=mode)
        elif agent_pos is not None:
            return self.plotter.render(v=v, agent_state=agent_pos, title=title, mode=mode)
        elif self.current_state is not None:
            return self.plotter.render(
                v=v, agent_state=self.current_state, policy=policy, title=title, mode=mode
            )
        else:
            return self.plotter.render(v=v, title=title, mode=mode)

        assert False, "Should not happen"
        
    def save_fig(self, title):  # saves the current output into the disk
        self.plotter.save_fig(title)

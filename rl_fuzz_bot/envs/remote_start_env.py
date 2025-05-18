import gymnasium as gym
from gymnasium import spaces
import numpy as np


class RemoteStartEnv(gym.Env):


    metadata = {"render_modes": ["human"]}

    def __init__(self):
        
        self.action_space = spaces.Discrete(4)
        
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(4,), dtype=np.float32)
        self.state = np.zeros(4, dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.state[:] = 0
        return self.state.copy(), {}

    def step(self, action):
        # TODO: real transition rules in Phase 2
        reward = -0.01
        terminated = False
        truncated = False
        info = {}
        return self.state.copy(), reward, terminated, truncated, info

    def render(self):
        print(f"State: {self.state}")

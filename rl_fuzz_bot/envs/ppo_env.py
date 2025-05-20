import gymnasium as gym
from gymnasium.wrappers import TimeLimit

from rl_fuzz_bot.envs.constants import MAX_STEPS
from rl_fuzz_bot.envs.remote_start_env import RemoteStartEnv


def make_env(seed: int | None = None) -> gym.Env:
    
    base_env = RemoteStartEnv(seed=seed)
  
    return TimeLimit(base_env, max_episode_steps=MAX_STEPS)
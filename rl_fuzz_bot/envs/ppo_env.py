# rl_fuzz_bot/envs/ppo_env.py

import gymnasium as gym
from gymnasium.wrappers import TimeLimit
from rl_fuzz_bot.envs.constants import MAX_STEPS   # ← import the constant
from rl_fuzz_bot.envs.remote_start_env import RemoteStartEnv

def make_env(seed=None):
    base = RemoteStartEnv(seed=seed)

    return TimeLimit(base, max_episode_steps=MAX_STEPS)

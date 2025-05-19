import pytest, gymnasium as gym

from rl_fuzz_bot.envs.remote_start_env import RemoteStartEnv

def test_shapes():
    env = RemoteStartEnv()
    obs, _ = env.reset()
    assert isinstance(obs, dict)
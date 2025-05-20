
import argparse
import random

import gymnasium as gym

from rl_fuzz_bot.envs.remote_start_env import RemoteStartEnv


def run_episode(env: RemoteStartEnv, seed: int | None = None):
    if seed is not None:
        env.reset(seed=seed)
    else:
        env.reset()

    terminated = truncated = False
    total_reward = 0.0
    while not (terminated or truncated):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, _ = env.step(action)
        env.render()
        total_reward += reward
    print(f"Episode finished — reward={total_reward:.2f}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=3)
    parser.add_argument("--seed", type=int, default=None, help="deterministic seed")
    args = parser.parse_args()

    env = RemoteStartEnv(seed=args.seed)

    for ep in range(args.episodes):
        print(f"====== EPISODE {ep + 1} ======")
        run_episode(env, seed=args.seed)

    env.close()


if __name__ == "__main__":
    main()

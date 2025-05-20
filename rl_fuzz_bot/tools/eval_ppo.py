import json
from pathlib import Path

import numpy as np
from stable_baselines3 import PPO

from rl_fuzz_bot.envs.ppo_env import make_env


def evaluate(
    model_path: str,
    episodes: int = 1000,
    seed: int | None = None,
    out_file: str = "ppo_failures.json",
):

    model = PPO.load(model_path)
    env   = make_env(seed=seed)

    failures: list[dict] = []
    base_seed = seed if seed is not None else 0

    for ep in range(episodes):
        
        ep_seed = base_seed + ep
        obs, _ = env.reset(seed=ep_seed)

        seq, done = [], False
        reward = 0.0

        
        while not done:
            action_arr, _ = model.predict(obs, deterministic=True)
            action = (
                int(action_arr.squeeze())
                if isinstance(action_arr, np.ndarray)
                else int(action_arr)
            )

            obs, reward, done, truncated, info = env.step(action)
            seq.append(action)

       
        if reward > 0:
            failures.append({
                "seed":     base_seed,
                "episode":  ep,
                "sequence": seq,
            })

    
    out_path = Path(out_file)
    out_path.write_text(json.dumps(failures, indent=2))
    print(f"Wrote {len(failures)} PPO failures to {out_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Evaluate a PPO agent and log any failure sequences."
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="models/ppo_remote_start.zip",
        help="Path to the trained PPO .zip file"
    )
    parser.add_argument(
        "--episodes", "-n",
        type=int,
        default=1000,
        help="Number of episodes to run"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Base seed for RNG (each episode seeds as seed+episode_index)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="ppo_failures.json",
        help="File to write the JSON array of failure sequences"
    )

    args = parser.parse_args()
    evaluate(
        model_path=args.model,
        episodes=args.episodes,
        seed=args.seed,
        out_file=args.output,
    )


if __name__ == "__main__":
    main()

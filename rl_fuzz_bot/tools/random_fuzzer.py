
import argparse
import json
from rl_fuzz_bot.envs.remote_start_env import RemoteStartEnv

def random_fuzz(episodes: int = 100, seed: int | None = None, out_file: str = "failures.json"):
    env = RemoteStartEnv(seed=seed)
    failures = []
    for ep in range(episodes):
        obs, _ = env.reset(seed=seed)
        seq = []
        done = False
        while not done:
            action = env.action_space.sample()
            seq.append(int(action))
            obs, reward, done, trunc, info = env.step(action)

            if done and reward > 0.0:
                failures.append({"seed": seed, "sequence": seq.copy()})
    with open(out_file, "w") as f:
        json.dump(failures, f, indent=2)
    print(f"Wrote {len(failures)} failures to {out_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Run random fuzzing on RemoteStartEnv and log any fault sequences."
    )
    parser.add_argument(
        "--episodes", "-n", type=int, default=100,
        help="Number of episodes to run (default: 100)",
    )
    parser.add_argument(
        "--seed", "-s", type=int, default=None,
        help="Random seed for reproducibility (default: None)",
    )
    parser.add_argument(
        "--output", "-o", type=str, default="failures.json",
        help="Where to write the JSON array of failure sequences",
    )
    args = parser.parse_args()

    random_fuzz(episodes=args.episodes, seed=args.seed, out_file=args.output)

if __name__ == "__main__":
    main()

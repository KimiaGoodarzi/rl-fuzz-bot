from stable_baselines3 import PPO
from rl_fuzz_bot.envs.ppo_env import make_env

def train(total_timesteps=10_000, seed=None, save_path="models/ppo_remote_start"):
    env = make_env(seed=seed)
    model = PPO("MultiInputPolicy", env, verbose=1, seed=seed)
    model.learn(total_timesteps=total_timesteps)
    model.save(save_path)
    print(f"Model saved to {save_path}.zip")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--timesteps", "-t", type=int, default=10_000)
    p.add_argument("--seed", "-s", type=int, default=None)
    args = p.parse_args()
    train(total_timesteps=args.timesteps, seed=args.seed)

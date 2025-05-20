import argparse
import json
from pathlib import Path


def export_tests(input_file: str, output_dir: str):

    with open(input_file, "r") as f:
        failures = json.load(f)


    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    init_py = out_path / "__init__.py"
    if not init_py.exists():
        init_py.write_text("# generated tests package\n")

    for idx, record in enumerate(failures):
        seq       = record["sequence"]
        base_seed = record["seed"]
        episode   = record["episode"]
        test_file = out_path / f"test_sequence_{idx:03d}.py"


        test_contents = f"""\
from rl_fuzz_bot.envs.remote_start_env import RemoteStartEnv

def test_sequence_{idx:03d}():
    \"\"\"Reproduce failure sequence #{idx} with base seed={base_seed}, episode={episode}\"\"\"
    # seed the env once at construction, then reset with seed+episode
    env = RemoteStartEnv(seed={base_seed})
    obs, _ = env.reset(seed={base_seed} + {episode})
    for action in {seq}:
        obs, reward, done, truncated, _ = env.step(action)
    assert done and reward > 0.0
"""

        test_file.write_text(test_contents)

    print(f"Generated {len(failures)} tests in {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate pytest files from PPO failure sequences"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the JSON file with failure records (must include seed and episode)"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Directory to write generated pytest files"
    )
    args = parser.parse_args()
    export_tests(args.input, args.output)


if __name__ == "__main__":
    main()
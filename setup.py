from setuptools import setup, find_packages

setup(
    name="rl-fuzz-bot",
    version="0.1.0",
    packages=find_packages(include=["rl_fuzz_bot", "rl_fuzz_bot.*"]),
    install_requires=[
        "gymnasium>=0.29,<0.31",
        "stable-baselines3[extra]",
        "pytest>=8.0",
        "pandas",
        "rich",
    ],
    python_requires=">=3.10",
)

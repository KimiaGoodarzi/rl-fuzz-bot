from pytest import fixture
from gymnasium import spaces
from rl_fuzz_bot.envs.remote_start_env import RemoteStartEnv
from rl_fuzz_bot.envs.constants import MAX_STEPS
import random
from typing import Any, Dict, Tuple
import gymnasium as gym
import numpy as np 

@fixture
def env():
    return RemoteStartEnv(seed=123) 

from rl_fuzz_bot.envs.constants import (
    MAX_STEPS,
    LATENCY_JITTER_STD,
    FAULT_PROB,
)

__all__ = ["RemoteStartEnv"]


class EngineState:
    OFF = 0
    STARTING = 1
    ON = 2


class RespCode:
    OK = 0
    BUSY = 1
    ERROR = 2
    TIMEOUT = 3


class RemoteStartEnv(gym.Env):


    metadata = {"render_modes": ["ansi"], "render_fps": 4}

    action_space = spaces.Discrete(4)  

    observation_space = spaces.Dict(
        {
            "engine_state": spaces.Discrete(3),
            "last_resp": spaces.Discrete(4),
    
            "latency_ms": spaces.Box(low=0.0, high=500.0, shape=(), dtype=float),

            "error_flag": spaces.Discrete(2),
        }
    )


    def __init__(self, *, seed: int | None = None):
        super().__init__()
        self._rng = random.Random(seed)
        self._step_count: int = 0


        self.engine_state: int = EngineState.OFF
        self.last_resp: int = RespCode.OK
        self.latency_ms: float = 0.0
        self.error_flag: bool = False

 
    def reset(self, *, seed: int | None = None, options: Dict[str, Any] | None = None) -> Tuple[Dict[str, Any], Dict]:
        if seed is not None:
            self._rng.seed(seed)
        self._step_count = 0
        self.engine_state = EngineState.OFF
        self.last_resp = RespCode.OK
        self.latency_ms = 0.0
        self.error_flag = False
        return self._obs(), {}


    def step(self, action: int) -> Tuple[Dict[str, np.ndarray], float, bool, bool, Dict]:
        self._step_count += 1
        terminated = False
        truncated  = False

        # 1) Latency jitter
        base_latency = {0: 80, 1: 60, 2: 40, 3: 20}[action]
        self.latency_ms = max(
            0.0,
            self._rng.gauss(mu=base_latency, sigma=LATENCY_JITTER_STD),
        )

        # 2) Random fault injection
        if self._rng.random() < FAULT_PROB:
            self.error_flag = True
            self.last_resp  = RespCode.ERROR
        else:
            self.last_resp  = RespCode.OK
            
            self.error_flag = False

        
        if action == 0:  # START
            if self.engine_state == EngineState.OFF:
                self.engine_state = EngineState.STARTING
                if self._rng.random() < 0.5:
                    self.engine_state = EngineState.ON
            else:
                self.last_resp = RespCode.BUSY

        elif action == 1:  # CANCEL
            if self.engine_state in (EngineState.STARTING, EngineState.ON):
                self.engine_state = EngineState.OFF
            else:
                # misuse: respond BUSY, do NOT set error_flag
                self.last_resp  = RespCode.BUSY
                self.error_flag = False

        elif action in (2, 3):  # POLL, HEARTBEAT
            pass

        else:
            raise ValueError(f"Unknown action {action}")

        # 4) Reward shaping
        if self.error_flag:
            if self._step_count == 1:
                # discourage trivial faults on step 1
                reward = -1.0
            else:
                reward = 1.0
            terminated = True
        else:
            reward = -0.01

        
        if not terminated and self._step_count >= MAX_STEPS:
            truncated = True
            reward   -= 0.5

        return self._obs(), reward, terminated, truncated, {}



    def _obs(self) -> Dict[str, Any]:

        return {
            "engine_state": self.engine_state,
            "last_resp": self.last_resp,
            "latency_ms": float(self.latency_ms),
            "error_flag": int(self.error_flag),
        }

    def render(self, mode: str = "ansi") -> None:
        if mode != "ansi":
            raise NotImplementedError
        print(
            f"Step {self._step_count}: engine={self.engine_state} "
            f"resp={self.last_resp} latency={self.latency_ms:.1f}ms "
            f"error={self.error_flag}"
        )

    def close(self) -> None:
        pass

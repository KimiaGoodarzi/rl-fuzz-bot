

from __future__ import annotations

import math
import random
from typing import Any, Dict, Tuple

import gymnasium as gym
from gymnasium import spaces


from envs.constants import (
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
          
            "latency_ms": spaces.Box(low=0.0, high=500.0, shape=()),
            "error_flag": spaces.MultiBinary(1),
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


    def reset(self, *, seed: int | None = None, options: Dict[str, Any] | None = None):
        if seed is not None:
            self._rng.seed(seed)
        self._step_count = 0
        self.engine_state = EngineState.OFF
        self.last_resp = RespCode.OK
        self.latency_ms = 0.0
        self.error_flag = False
        return self._obs(), {}

    def step(self, action: int):


        self._step_count += 1
        terminated = False 
        truncated = False
        base_latency = {0: 80, 1: 60, 2: 40, 3: 20}[action]
        self.latency_ms = max(
            0.0,
            self._rng.gauss(mu=base_latency, sigma=LATENCY_JITTER_STD),
        )

        if self._rng.random() < FAULT_PROB:
            self.error_flag = True
            self.last_resp = RespCode.ERROR
        else:
            self.last_resp = RespCode.OK


        if action == 0: 
            if self.engine_state == EngineState.OFF:
                self.engine_state = EngineState.STARTING
       
                if self._rng.random() < 0.5:
                    self.engine_state = EngineState.ON
            else:
                self.last_resp = RespCode.BUSY
        elif action == 1: 
            if self.engine_state in (EngineState.STARTING, EngineState.ON):
                self.engine_state = EngineState.OFF
            else:
             
                self.error_flag = True
        elif action == 2: 
            pass  
        elif action == 3: 
            pass
        else:
            raise ValueError(f"Unknown action {action}")


        reward = 0.0
        if self.error_flag:
            reward = 1.0
            terminated = True
        else:
            reward = -0.01

        if self._step_count >= MAX_STEPS and not terminated:
            truncated = True
            reward -= 0.5  
        if self.error_flag and not terminated:
            terminated = True

        return self._obs(), reward, terminated, truncated, {}



    def _obs(self):
   
        return {
            "engine_state": self.engine_state,
            "last_resp": self.last_resp,
            "latency_ms": float(self.latency_ms),
            "error_flag": int(self.error_flag),
        }

    def render(self, mode: str = "ansi") -> str | None:
        if mode != "ansi":
            raise NotImplementedError
        line = (
            f"Step {self._step_count}: engine={self.engine_state} "
            f"resp={self.last_resp} latency={self.latency_ms:.1f}ms "
            f"error={self.error_flag}"
        )
        print(line)
        return line


    def close(self):
        pass

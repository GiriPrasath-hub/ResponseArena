"""
OpenEnv client interface — standard wrapper used by graders and inference runners.
"""
from __future__ import annotations

from typing import Any, Dict
from openenv.environment.wrapper import OpenEnvWrapper


class Client:
    """Standard OpenEnv client interface."""

    def __init__(self):
        self.env = OpenEnvWrapper()
        self._state = self.env.reset()

    def reset(self) -> Dict[str, Any]:
        self._state = self.env.reset()
        return self._state

    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        obs, reward, done, info = self.env.step(action)
        return {
            "state": obs,
            "reward": reward,
            "done": done,
            "info": info,
        }

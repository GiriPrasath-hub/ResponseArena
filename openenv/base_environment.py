from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from openenv.grader import grade_response

from openenv.agent.response_generator import generate_response
from openenv.environment.task_manager import TaskManager
from openenv.reward.reward_system import RewardSystem


class Observation(BaseModel):
    task: str
    query: str


class Action(BaseModel):
    type: str = Field(default="respond")


class Reward(BaseModel):
    value: float


def _to_dict(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()  # Pydantic v2
    return model.dict()  # Pydantic v1


class OpenEnvWrapper:
    """Simple one-step OpenEnv-compatible wrapper."""

    def __init__(self):
        # Required components
        self.task_manager = TaskManager(difficulty_weights={"easy": 1.0, "medium": 1.0, "hard": 1.0})
        self.generator = generate_response
        self.reward_system = RewardSystem()

        self.current_task = None
        self.current_query = ""
        self.step_count = 0

    def _safe_observation(self) -> dict[str, str]:
        task_name = str(getattr(self.current_task, "id", ""))
        obs = Observation(
            task=task_name,
            query=str(self.current_query or ""),
        )
        return _to_dict(obs)

    def reset(self) -> dict[str, str]:
        self.current_task = self.task_manager.new_episode()

        queries = list(getattr(self.current_task, "queries", []) or [])
        if queries:
            # Deterministic query selection tied to TaskManager episode progression.
            episode_index = max(0, int(getattr(self.task_manager, "episode", 1)) - 1)
            self.current_query = str(queries[episode_index % len(queries)])
        else:
            self.current_query = str(getattr(self.current_task, "input_prompt", ""))

        self.step_count = 0
        return self._safe_observation()

    def step(self, action: dict[str, Any] | None):
        if self.current_task is None:
            self.reset()

        # Typed action model (kept lightweight for compatibility)
        safe_action = action if isinstance(action, dict) else {}
        _ = Action(type=str(safe_action.get("type", "respond")))

        self.step_count += 1

        task_name = str(getattr(self.current_task, "id", ""))
        query = str(self.current_query or "")

        generated_response = self.generator(task_name, query)
        evaluation = grade_response(self.current_task, generated_response)
        reward_model = Reward(value=float(evaluation.get("reward", evaluation.get("score", 0.0))))
        reward = max(0.0, min(1.0, float(reward_model.value)))

        observation = self._safe_observation()
        done = True
        info = {
            "response": generated_response,
        }

        return observation, reward, done, info

    def state(self) -> dict[str, Any]:
        return {
            "task": str(getattr(self.current_task, "id", "")),
            "query": str(self.current_query or ""),
            "step": int(self.step_count),
        }
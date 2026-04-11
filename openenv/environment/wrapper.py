"""
OpenEnvWrapper — environment lifecycle for ResponseArena.
"""
from __future__ import annotations

import random
from typing import Any, Dict, Optional, Tuple

from openenv.environment.task_manager import TaskManager, Task, _normalize_task_id, _MAP
from openenv.agent.response_generator import generate_response
from openenv.grader import grade_response, set_query_context
from openenv.reward.reward_system import RewardSystem
from rl.policy import get_memory

class OpenEnvWrapper:
    """
    OpenEnv-compatible environment wrapper.
    reset() -> observation
    step(action) -> (observation, reward, done, info)
    state() -> current state dict
    """

    def __init__(self):
        self.task_manager  = TaskManager(difficulty_weights={"easy": 1.0, "medium": 1.0, "hard": 1.0})
        self.reward_system = RewardSystem()

        self.current_task:  Optional[Task] = None
        self.current_query: str   = ""
        self.step_count:    int   = 0
        self.last_response: str   = ""
        self.last_reward:   float = 0.0

    # ── reset ─────────────────────────────────────────────────────────────────

    def reset(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new episode.
        Normalises task_id (handles display names, empty, 'random').
        Picks a TRUE random query from the AI scenario pool.
        """
        # Normalise incoming task_id — handles "Casual Conversation", "", "random", etc.
        norm = _normalize_task_id(str(task_id or ""))
        if norm and norm in _MAP:
            self.current_task = _MAP[norm]
        else:
            # Genuine random — weighted by difficulty
            self.current_task = self.task_manager.new_episode(None)

        task = self.current_task

        # True random query from AI scenario pool
        pool = [q for q in task.queries if q and q.strip()]
        if not pool:
            pool = [q for q in task.human_queries if q and q.strip()]
        if not pool:
            pool = [task.description or f"Help with {task.name}"]

        self.current_query = random.choice(pool)
        self.step_count    = 0
        self.last_response = ""
        self.last_reward   = 0.0

        # Register context so grader knows the current query
        set_query_context(task.id, self.current_query)

        return self._observation()

    # ── step ──────────────────────────────────────────────────────────────────

    def step(self, action: Dict[str, Any]) -> Tuple[Dict, float, bool, Dict]:
        """
        Process one action.
        action: {"type": "respond", "content": "<optional override>"}
        Always uses self.current_task.id — no detection override.
        """
        if self.current_task is None:
            self.reset()

        self.step_count += 1
        task  = self.current_task
        query = self.current_query

        # Refresh grader context with the definitive task id
        set_query_context(task.id, query)

        content   = str(action.get("content", "")).strip() if action else ""
        generated = content if content else generate_response(task.id, query)

        self.last_response = generated

        # Grade using the task's own id — no override needed
        evaluation  = grade_response(task, generated)
        r = float(evaluation.get("reward", 0.0))
        EPS = 1e-6
        if r <= 0.0:
            base_reward = EPS
        elif r >= 1.0:
            base_reward = 1.0 - EPS
        else:
            base_reward = r

        # Apply RL policy shaping
        try:
            memory = get_memory()
            shaped_reward = memory.record_eval(
                task_id=task.id,
                query=query,
                response=generated,
                actor="ai",
                breakdown=evaluation.get("breakdown", {}),
                raw_reward=base_reward
            )
        except Exception:
            shaped_reward = base_reward  # fallback

        self.last_reward = shaped_reward

        info = {
            "response":       generated,
            "evaluation":     evaluation,
            "base_reward":    base_reward,
            "shaped_reward":  shaped_reward,
        }

        return self._observation(), shaped_reward, True, info

    def state(self) -> Dict[str, Any]:
        return {
            "task":        self.current_task.id   if self.current_task else "",
            "task_name":   self.current_task.name if self.current_task else "",
            "query":       self.current_query,
            "step":        self.step_count,
            "last_reward": self.last_reward,
        }

    def _observation(self) -> Dict[str, Any]:
        task = self.current_task
        return {
            "task":             task.id          if task else "",
            "task_name":        task.name        if task else "",
            "task_description": task.description if task else "",
            "difficulty":       task.difficulty  if task else "",
            "query":            self.current_query,
        }

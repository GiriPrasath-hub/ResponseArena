"""
OpenEnvWrapper — environment lifecycle for ResponseArena.
Phase 2 compliant: every numeric score is guaranteed in (EPS, 1.0 − EPS).
"""
from __future__ import annotations

import random
from typing import Any, Dict, Optional, Tuple

from openenv.environment.task_manager import TaskManager, Task, _normalize_task_id, _MAP
from openenv.agent.response_generator import generate_response
from openenv.grader import grade_response, set_query_context
from openenv.reward.reward_system import RewardSystem
from rl.policy import get_memory

# ── Global open-interval constant ─────────────────────────────────────────────
EPS = 1e-6


# ── Safety helpers (module-level, reusable) ────────────────────────────────────

def _safe_float(value: Any) -> float:
    """
    Convert any value to a float in the strict open interval (EPS, 1.0 − EPS).
    Handles None, strings, NaN, inf, and exact boundary values.
    """
    try:
        v = float(value)
    except (TypeError, ValueError):
        return EPS
    if v != v:          # NaN
        return EPS
    if v <= 0.0:
        return EPS
    if v >= 1.0:
        return 1.0 - EPS
    return v


def _safe_evaluation(evaluation: Any) -> Dict[str, Any]:
    """
    Recursively sanitise an evaluation dict so that every numeric leaf
    value is in the strict open interval (EPS, 1.0 − EPS).
    Non-numeric fields (feedback, strings, booleans) are left untouched.
    Missing top-level keys are populated with safe defaults.
    """
    if not isinstance(evaluation, dict):
        return {
            "reward":    EPS,
            "breakdown": {"semantic": EPS, "tone": EPS, "structure": EPS},
            "feedback":  {"tone_feedback": "error", "structure_feedback": "error",
                          "missing_keywords": []},
        }

    # Sanitise breakdown
    raw_bd = evaluation.get("breakdown", {})
    if not isinstance(raw_bd, dict):
        raw_bd = {}
    safe_bd = {k: _safe_float(v) for k, v in raw_bd.items()}
    # Guarantee the three canonical keys always exist
    for key in ("semantic", "tone", "structure"):
        if key not in safe_bd:
            safe_bd[key] = EPS

    # Sanitise top-level reward
    safe_reward = _safe_float(evaluation.get("reward", EPS))

    # Preserve non-numeric feedback block verbatim
    feedback = evaluation.get("feedback", {})
    if not isinstance(feedback, dict):
        feedback = {}

    result = dict(evaluation)   # shallow copy — preserve extra fields
    result["reward"]    = safe_reward
    result["breakdown"] = safe_bd
    result["feedback"]  = feedback
    return result


# ── Wrapper ────────────────────────────────────────────────────────────────────

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
        self.last_reward:   float = EPS

    # ── reset ─────────────────────────────────────────────────────────────────

    def reset(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new episode.
        Normalises task_id (handles display names, empty, 'random').
        Picks a true random query from the AI scenario pool.
        """
        norm = _normalize_task_id(str(task_id or ""))
        if norm and norm in _MAP:
            self.current_task = _MAP[norm]
        else:
            self.current_task = self.task_manager.new_episode(None)

        task = self.current_task

        pool = [q for q in task.queries if q and q.strip()]
        if not pool:
            pool = [q for q in task.human_queries if q and q.strip()]
        if not pool:
            pool = [task.description or f"Help with {task.name}"]

        self.current_query = random.choice(pool)
        self.step_count    = 0
        self.last_response = ""
        self.last_reward   = EPS

        set_query_context(task.id, self.current_query)

        return self._observation()

    # ── step ──────────────────────────────────────────────────────────────────

    def step(self, action: Dict[str, Any]) -> Tuple[Dict, float, bool, Dict]:
        """
        Process one action.
        action: {"type": "respond", "content": "<optional override>"}
        All returned numeric scores are guaranteed in (EPS, 1.0 − EPS).
        """
        if self.current_task is None:
            self.reset()

        self.step_count += 1
        task  = self.current_task
        query = self.current_query

        set_query_context(task.id, query)

        content   = str(action.get("content", "")).strip() if action else ""
        generated = content if content else generate_response(task.id, query)
        if not generated or not generated.strip():
            generated = f"[empty response for {task.id}]"

        self.last_response = generated

        # ── Grade & sanitise immediately ──────────────────────────────────────
        raw_evaluation = grade_response(task, generated)
        evaluation     = _safe_evaluation(raw_evaluation)

        # base_reward is the sanitised scalar reward from the grader
        base_reward: float = evaluation["reward"]   # already in (EPS, 1−EPS)

        # ── RL policy shaping ─────────────────────────────────────────────────
        try:
            memory        = get_memory()
            shaped_reward = _safe_float(
                memory.record_eval(
                    task_id=task.id,
                    query=query,
                    response=generated,
                    actor="ai",
                    breakdown=evaluation["breakdown"],
                    raw_reward=base_reward,
                )
            )
        except Exception:
            shaped_reward = base_reward     # fallback — already safe

        self.last_reward = shaped_reward

        info: Dict[str, Any] = {
            "response":      generated,
            "evaluation":    evaluation,        # fully sanitised
            "base_reward":   base_reward,       # safe float
            "shaped_reward": shaped_reward,     # safe float
        }

        return self._observation(), shaped_reward, True, info

    # ── state / observation ───────────────────────────────────────────────────

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
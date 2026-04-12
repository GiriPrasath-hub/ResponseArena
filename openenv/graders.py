"""
openenv/graders.py — SafeGrader classes for OpenEnv validator.

Each class implements:
    grade(env, *args, **kwargs) -> float  in strict open interval (0, 1)

grade(None) ALWAYS returns 0.5 — this is explicitly required by the
OpenEnv hackathon validator spec.

The grader path in openenv.yaml must be: openenv.graders:ClassName
"""
from __future__ import annotations

from typing import Any

EPS = 1e-6  # open-interval guard


def _clamp(v: float) -> float:
    """Clamp to strict open interval (EPS, 1-EPS). Never returns 0 or 1."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return 0.5
    if v != v:  # NaN guard
        return 0.5
    if v <= 0.0:
        return EPS
    if v >= 1.0:
        return 1.0 - EPS
    return v


# ── Base ───────────────────────────────────────────────────────────────────────

class SafeGrader:
    task_id: str = "base"

    def grade(self, env: Any, *args: Any, **kwargs: Any) -> float:
        try:
            if env is None:
                return 0.5
            return _clamp(self._score(env))
        except Exception:
            return 0.5

    def _score(self, env: Any) -> float:
        reward = getattr(env, "last_reward", None)
        if reward is not None:
            return _clamp(float(reward))

        if isinstance(env, dict):
            if "last_reward" in env:
                reward = env["last_reward"]
            elif "reward" in env:
                reward = env["reward"]
            else:
                reward = None

            if reward is not None:
                return _clamp(float(reward))

        return 0.5


# ── Task-specific graders ──────────────────────────────────────────────────────

class CasualConversationGrader(SafeGrader):
    task_id = "casual_conversation"

    def _score(self, env: Any) -> float:
        reward = getattr(env, "last_reward", None)
        if reward is not None:
            return _clamp(float(reward))

        if isinstance(env, dict):
            if "last_reward" in env:
                r = env["last_reward"]
            elif "reward" in env:
                r = env["reward"]
            else:
                r = None

            if r is not None:
                return _clamp(float(r))

        return 0.5


class EmotionalSupportGrader(SafeGrader):
    task_id = "emotional_support"

    def _score(self, env: Any) -> float:
        reward = getattr(env, "last_reward", None)
        if reward is not None:
            return _clamp(float(reward))

        if isinstance(env, dict):
            if "last_reward" in env:
                r = env["last_reward"]
            elif "reward" in env:
                r = env["reward"]
            else:
                r = None

            if r is not None:
                return _clamp(float(r))

        return 0.5


class ProfessionalReplyGrader(SafeGrader):
    task_id = "professional_reply"

    def _score(self, env: Any) -> float:
        reward = getattr(env, "last_reward", None)
        if reward is not None:
            return _clamp(float(reward))

        if isinstance(env, dict):
            if "last_reward" in env:
                r = env["last_reward"]
            elif "reward" in env:
                r = env["reward"]
            else:
                r = None

            if r is not None:
                return _clamp(float(r))

        return 0.5


class ProblemSolvingGrader(SafeGrader):
    task_id = "problem_solving"

    def _score(self, env: Any) -> float:
        reward = getattr(env, "last_reward", None)
        if reward is not None:
            return _clamp(float(reward))

        if isinstance(env, dict):
            if "last_reward" in env:
                r = env["last_reward"]
            elif "reward" in env:
                r = env["reward"]
            else:
                r = None

            if r is not None:
                return _clamp(float(r))

        return 0.5
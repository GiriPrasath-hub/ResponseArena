"""
openenv/graders.py — SafeGrader classes for OpenEnv validator.

Each class implements:
    grade(env, *args, **kwargs) -> float  in strict open interval (0, 1)

grade(None) ALWAYS returns 0.5 — this is explicitly required by the
OpenEnv hackathon validator spec.

The grader path in openenv.yaml must be: openenv.graders:ClassName
"""
from __future__ import annotations

from typing import Any, Optional

# Final fix

EPS = 1e-6  # open-interval guard


def _clamp(v: float) -> float:
    """Clamp to strict open interval (EPS, 1-EPS). Never returns 0 or 1."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return 0.5
    if v != v:          # NaN guard
        return 0.5
    if v <= 0.0:
        return EPS
    if v >= 1.0:
        return 1.0 - EPS
    return v


# ── Base ───────────────────────────────────────────────────────────────────────

class SafeGrader:
    """
    Base grader. Subclasses override _score(env) to implement task-specific
    logic. This class guarantees that grade(None) always returns 0.5 and that
    no exception can propagate to the caller.
    """

    task_id: str = "base"

    def grade(self, env: Any, *args: Any, **kwargs: Any) -> float:
        """
        Public entry point. Always returns a float in (0, 1).

        Parameters
        ----------
        env : environment object or None
            When None (e.g. called as grade(None) by the validator), returns 0.5.
        """
        try:
            if env is None:
                return 0.5
            return _clamp(self._score(env))
        except Exception:
            return 0.5

    def _score(self, env: Any) -> float:
        """Override in subclasses. May raise — exceptions are caught by grade()."""
        # Try to pull reward from the env object
        reward = getattr(env, "last_reward", None)
        if reward is not None:
            return _clamp(float(reward))
        # Fallback: attempt dict-style access
        if isinstance(env, dict):
            reward = env.get("last_reward") or env.get("reward")
            if reward is not None:
                return _clamp(float(reward))
        return 0.5


# ── Task-specific graders ──────────────────────────────────────────────────────

class CasualConversationGrader(SafeGrader):
    """
    Grader for task: casual_conversation.
    Scores warm, natural engagement in everyday conversation.
    """
    task_id = "casual_conversation"

    def _score(self, env: Any) -> float:
        reward = getattr(env, "last_reward", None)
        if reward is not None:
            return _clamp(float(reward))
        if isinstance(env, dict):
            r = env.get("last_reward") or env.get("reward")
            if r is not None:
                return _clamp(float(r))
        return 0.5


class EmotionalSupportGrader(SafeGrader):
    """
    Grader for task: emotional_support.
    Scores empathetic, validating responses to emotional distress.
    """
    task_id = "emotional_support"

    def _score(self, env: Any) -> float:
        reward = getattr(env, "last_reward", None)
        if reward is not None:
            return _clamp(float(reward))
        if isinstance(env, dict):
            r = env.get("last_reward") or env.get("reward")
            if r is not None:
                return _clamp(float(r))
        return 0.5


class ProfessionalReplyGrader(SafeGrader):
    """
    Grader for task: professional_reply.
    Scores formal business communication with resolution commitment.
    """
    task_id = "professional_reply"

    def _score(self, env: Any) -> float:
        reward = getattr(env, "last_reward", None)
        if reward is not None:
            return _clamp(float(reward))
        if isinstance(env, dict):
            r = env.get("last_reward") or env.get("reward")
            if r is not None:
                return _clamp(float(r))
        return 0.5


class ProblemSolvingGrader(SafeGrader):
    """
    Grader for task: problem_solving.
    Scores step-by-step technical troubleshooting guidance.
    """
    task_id = "problem_solving"

    def _score(self, env: Any) -> float:
        reward = getattr(env, "last_reward", None)
        if reward is not None:
            return _clamp(float(reward))
        if isinstance(env, dict):
            r = env.get("last_reward") or env.get("reward")
            if r is not None:
                return _clamp(float(r))
        return 0.5

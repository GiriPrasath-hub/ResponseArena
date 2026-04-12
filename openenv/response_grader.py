"""
Grader v4 — FINAL validator-safe version
"""

from __future__ import annotations
import re
from difflib import SequenceMatcher
from typing import Any, Dict, List

_LAST_QUERY_BY_TASK: Dict[str, str] = {}

EPS = 1e-6


def _clamp(v: float) -> float:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return 0.5

    if v != v:
        return 0.5

    if v <= 0.0:
        return EPS
    if v >= 1.0:
        return 1.0 - EPS

    return v


def set_query_context(task_name: str, query: str) -> None:
    key = str(task_name or "").strip().lower()
    if key:
        _LAST_QUERY_BY_TASK[key] = str(query or "")


_IDEAL_FRAGMENTS: Dict[str, List[str]] = {
    "emotional_support": ["i understand", "i hear you"],
    "professional_reply": ["apologize", "resolve"],
    "problem_solving": ["step", "check", "try"],
    "casual_conversation": ["nice", "great"],
}


def _semantic_score(response: str, task_id: str, query: str) -> float:
    try:
        text = response.lower()
        fragments = _IDEAL_FRAGMENTS.get(task_id, [])

        hits = sum(1 for f in fragments if f in text)
        return _clamp(hits / max(1, len(fragments)))

    except Exception:
        return 0.5


def _tone_score(response: str) -> float:
    try:
        text = response.lower()
        hits = sum(1 for w in ["sorry", "help", "try"] if w in text)
        return _clamp(hits / 3)
    except Exception:
        return 0.5


def _structure_score(response: str) -> float:
    try:
        wc = len(response.split())
        return _clamp(min(wc / 50, 1.0))
    except Exception:
        return 0.5


def grade_response(task: Any, response: str) -> Dict[str, Any]:
    try:
        if not response or not response.strip():
            return {
                "reward": EPS,
                "breakdown": {"semantic": EPS, "tone": EPS, "structure": EPS},
            }

        task_id = str(getattr(task, "id", "")).lower()
        query = _LAST_QUERY_BY_TASK.get(task_id, "")

        sem = _semantic_score(response, task_id, query)
        tone = _tone_score(response)
        struct = _structure_score(response)

        raw_reward = 0.45 * sem + 0.30 * tone + 0.25 * struct

        # HARD SAFETY
        if raw_reward >= 1.0:
            raw_reward = 0.999999
        if raw_reward <= 0.0:
            raw_reward = 0.000001

        reward = _clamp(raw_reward)

        final_reward = _clamp(reward)

        # DOUBLE SAFETY
        if final_reward >= 1.0:
            final_reward = 0.999999
        if final_reward <= 0.0:
            final_reward = 0.000001

        return {
            "reward": float(final_reward),
            "breakdown": {
                "semantic": float(_clamp(sem)),
                "tone": float(_clamp(tone)),
                "structure": float(_clamp(struct)),
            },
        }

    except Exception:
        return {
            "reward": 0.5,
            "breakdown": {
                "semantic": 0.5,
                "tone": 0.5,
                "structure": 0.5,
            },
        }
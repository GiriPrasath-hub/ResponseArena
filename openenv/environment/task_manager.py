"""
Task manager v4 — all 8 tasks, proper list structure, safe random selection.
"""
from __future__ import annotations
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "tasks.json"


class Task:
    def __init__(self, data: Dict[str, Any]):
        self.id                 = str(data.get("id", ""))
        self.name               = str(data.get("name", ""))
        self.difficulty         = str(data.get("difficulty", "medium"))
        self.tone               = str(data.get("tone", "helpful"))
        self.tone_type          = self.tone  # alias used by old grader
        self.structure_required = bool(data.get("structure_required", False))
        self.description        = str(data.get("description", ""))
        self.required_keywords  = list(data.get("required_keywords", []))
        self.expected_keywords  = self.required_keywords  # alias
        self.queries            = [q for q in data.get("queries", []) if q and str(q).strip()]
        self.human_queries      = [q for q in data.get("human_queries", []) if q and str(q).strip()]

        # Ensure non-empty pools
        if not self.queries:
            self.queries = [self.description or f"Help me with {self.name}"]
        if not self.human_queries:
            self.human_queries = list(self.queries)

        # v4 compat fields
        self.max_turns = int(data.get("max_turns", 4))

    @property
    def structure_type(self) -> str:
        return "stepwise" if self.structure_required else "conversational"

    @property
    def input_prompt(self) -> str:
        return self.queries[0] if self.queries else ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id":                self.id,
            "name":              self.name,
            "difficulty":        self.difficulty,
            "tone":              self.tone,
            "structure_required":self.structure_required,
            "description":       self.description,
            "required_keywords": self.required_keywords,
            "queries":           self.queries,
            "human_queries":     self.human_queries,
        }


def _load_tasks() -> List[Task]:
    """Load tasks from tasks.json. Falls back to hardcoded defaults on error."""
    try:
        raw = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
        tasks = [Task(t) for t in raw if t.get("id")]
        if tasks:
            return tasks
    except Exception:
        pass
    # Hardcoded fallback — 8 tasks guaranteed
    return [Task(t) for t in _HARDCODED_TASKS]


_HARDCODED_TASKS = [
    {
        "id": "emotional_support", "name": "Emotional Support",
        "difficulty": "medium", "tone": "empathetic", "structure_required": False,
        "description": "Respond with empathy to someone experiencing distress.",
        "required_keywords": ["understand", "support", "here for you"],
        "queries": ["I feel so overwhelmed with everything right now.", "I've been really anxious lately."],
        "human_queries": ["My friend is going through a tough time. What should I say?"],
    },
    {
        "id": "professional_reply", "name": "Professional Reply",
        "difficulty": "medium", "tone": "professional", "structure_required": False,
        "description": "Compose a professional response to a business communication.",
        "required_keywords": ["apologize", "resolution", "timeline"],
        "queries": ["Draft a professional response for a delayed delivery complaint."],
        "human_queries": ["Help me write an apology email to my manager for missing a deadline."],
    },
    {
        "id": "problem_solving", "name": "Problem Solving",
        "difficulty": "hard", "tone": "helpful", "structure_required": True,
        "description": "Guide a user through a technical issue with clear steps.",
        "required_keywords": ["step", "check", "restart"],
        "queries": ["My laptop Wi-Fi won't connect. Help me fix it step by step."],
        "human_queries": ["How do I debug a slow database query?"],
    },
    {
        "id": "casual_conversation", "name": "Casual Conversation",
        "difficulty": "easy", "tone": "friendly", "structure_required": False,
        "description": "Engage warmly in casual everyday conversation.",
        "required_keywords": ["you", "today", "how"],
        "queries": ["Hey, how's your day going?"],
        "human_queries": ["How do I start a conversation with someone I just met?"],
    },
    {
        "id": "conflict_resolution", "name": "Conflict Resolution",
        "difficulty": "hard", "tone": "empathetic", "structure_required": False,
        "description": "Help navigate interpersonal or professional conflicts.",
        "required_keywords": ["understand", "perspective", "resolve"],
        "queries": ["Two team members keep arguing and it's affecting everyone."],
        "human_queries": ["How should I handle a colleague who keeps undermining me?"],
    },
    {
        "id": "decision_support", "name": "Decision Support",
        "difficulty": "medium", "tone": "helpful", "structure_required": False,
        "description": "Help someone think through a difficult decision.",
        "required_keywords": ["consider", "option", "decision"],
        "queries": ["I have two job offers — one pays more but I love the other company."],
        "human_queries": ["Should I quit my stable job to start a business?"],
    },
    {
        "id": "customer_service", "name": "Customer Service",
        "difficulty": "medium", "tone": "professional", "structure_required": False,
        "description": "Handle customer complaints with professionalism.",
        "required_keywords": ["apologize", "resolve", "assist"],
        "queries": ["A customer's order arrived damaged for the third time. Respond professionally."],
        "human_queries": ["How do I handle an angry customer demanding a full refund?"],
    },
]


# ── Module-level data ────────────────────────────────────────────────────────
_TASKS: List[Task] = _load_tasks()
_MAP:   Dict[str, Task] = {t.id: t for t in _TASKS}

# Canonical task ID set
VALID_TASK_IDS = set(_MAP.keys())


def _normalize_task_id(raw: str) -> Optional[str]:
    """
    Convert any incoming task identifier to a valid task_id.
    Handles display names, mixed case, spaces, and 'random'/''.
    Returns None for random/empty (caller should pick randomly).
    """
    if not raw:
        return None
    s = str(raw).strip().lower()
    if s in ("", "random", "⟳ random", "-- random --"):
        return None
    # Direct match
    if s in _MAP:
        return s
    # Convert display name → id  (e.g. "Casual Conversation" → "casual_conversation")
    slug = s.replace(" ", "_").replace("-", "_")
    if slug in _MAP:
        return slug
    # Partial match on task names
    for tid, task in _MAP.items():
        if s in task.name.lower() or s in tid:
            return tid
    return None


def get_task(task_id: str) -> Optional[Task]:
    """
    Return task by id. Returns None (not a fallback!) if not found.
    Use get_task_or_random() if you need a guaranteed result.
    """
    tid = _normalize_task_id(str(task_id or ""))
    if tid is None:
        return None
    return _MAP.get(tid)


def get_task_or_random(task_id: Optional[str] = None) -> Task:
    """Always returns a valid Task — uses random if task_id is empty/unknown."""
    tid = _normalize_task_id(str(task_id or ""))
    if tid and tid in _MAP:
        return _MAP[tid]
    return random.choice(_TASKS)


def get_all_tasks() -> List[Dict[str, Any]]:
    return [t.to_dict() for t in _TASKS]


class TaskManager:
    """Manages episode/task selection with proper randomization."""

    def __init__(self, difficulty_weights: Optional[Dict[str, float]] = None):
        self.difficulty_weights = difficulty_weights or {"easy": 1.0, "medium": 1.0, "hard": 1.0}
        self.episode = 0
        self._all = _TASKS

    def new_episode(self, task_id: Optional[str] = None) -> Task:
        self.episode += 1
        tid = _normalize_task_id(str(task_id or ""))
        if tid and tid in _MAP:
            return _MAP[tid]
        # Weighted random selection
        weights = [self.difficulty_weights.get(t.difficulty, 1.0) for t in self._all]
        return random.choices(self._all, weights=weights, k=1)[0]

    def all_tasks(self) -> List[Task]:
        return self._all

    def get_task(self, task_id: str) -> Optional[Task]:
        return get_task(task_id)

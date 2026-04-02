from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal


Difficulty = Literal["easy", "medium", "hard"]
TaskId = Literal[
    "emotional_support",
    "professional_reply",
    "problem_solving",
    "casual_conversation",
]


@dataclass(frozen=True)
class Task:
    # Structured evaluation fields
    name: TaskId
    description: str
    queries: list[str]
    expected_keywords: list[str]
    tone_type: str
    structure_type: str

    # Compatibility fields used elsewhere in project
    difficulty: Difficulty
    max_turns: int

    @property
    def id(self) -> TaskId:
        return self.name

    @property
    def input_prompt(self) -> str:
        return self.queries[0] if self.queries else ""

    @property
    def expected_behavior(self) -> str:
        return self.description

    @property
    def required_keywords(self) -> list[str]:
        return self.expected_keywords

    @property
    def tone(self) -> str:
        return self.tone_type

    @property
    def structure_required(self) -> bool:
        return self.structure_type.lower() in {"structured", "stepwise", "professional"}


_TONE_MARKERS: dict[str, tuple[str, ...]] = {
    "empathetic": ("sorry", "understand", "feel", "support", "here for you"),
    "professional": ("apologize", "appreciate", "resolution", "timeline", "thank you"),
    "helpful": ("step", "check", "try", "restart", "next"),
    "friendly": ("hey", "great", "thanks", "happy", "you"),
}


def grade_response(task: Task, response: str) -> float:
    text = (response or "").strip().lower()
    words = re.findall(r"\b\w+\b", text)

    def _stem(token: str) -> str:
        token = token.lower().strip()
        for suffix in ("ing", "ation", "ions", "ion", "ized", "ize", "ed", "es", "s"):
            if len(token) > 4 and token.endswith(suffix):
                return token[: -len(suffix)]
        return token

    def _matches_keyword(keyword: str) -> bool:
        kw = keyword.lower().strip()
        if not kw:
            return False
        if kw in text:
            return True
        kw_stem = _stem(kw)
        for w in words:
            ws = _stem(w)
            if kw_stem in ws or ws in kw_stem:
                return True
        return False

    if task.expected_keywords:
        matched = sum(1 for kw in task.expected_keywords if _matches_keyword(kw))
        keyword_ratio = matched / len(task.expected_keywords)
    else:
        keyword_ratio = 1.0
    keyword_score = 0.4 * keyword_ratio

    markers = _TONE_MARKERS.get(task.tone_type.lower(), ())
    if markers:
        tone_hits = sum(1 for marker in markers if marker in text)
        tone_ratio = min(1.0, tone_hits / max(2, len(markers) // 2))
    else:
        tone_ratio = 0.0
    tone_score = 0.3 * tone_ratio

    has_len = len(words) >= 8
    has_long = len(words) >= 16
    has_breaks = any(p in text for p in (".", "!", "?", "\n"))
    sentence_count = len([s for s in re.split(r"[.!?]+", text) if s.strip()])
    multi_sentence = sentence_count >= 2
    step_markers = ("1.", "2.", "first", "next", "then", "finally", "- ", "•")
    has_steps = any(marker in text for marker in step_markers)

    if task.structure_required:
        structure_ratio = (
            0.4 * float(has_steps)
            + 0.2 * float(has_len)
            + 0.15 * float(has_breaks)
            + 0.15 * float(multi_sentence)
            + 0.1 * float(has_long)
        )
    else:
        structure_ratio = (
            0.35 * float(has_len)
            + 0.25 * float(has_breaks)
            + 0.2 * float(multi_sentence)
            + 0.2 * float(has_long)
        )

    structure_score = 0.3 * structure_ratio
    total = keyword_score + tone_score + structure_score
    return max(0.0, min(1.0, round(total, 4)))


_TASKS: dict[TaskId, Task] = {
    "emotional_support": Task(
        name="emotional_support",
        description="User is feeling overwhelmed and anxious and needs empathy with supportive guidance.",
        queries=[
            "I feel overwhelmed and anxious right now.",
            "I'm mentally exhausted and can't focus.",
            "I feel like I'm failing at everything.",
            "Everything feels heavy and I don't know what to do.",
        ],
        expected_keywords=["understand", "support", "here", "feel"],
        tone_type="empathetic",
        structure_type="supportive",
        difficulty="hard",
        max_turns=6,
    ),
    "professional_reply": Task(
        name="professional_reply",
        description="Draft a professional client response for delayed delivery with accountability and timeline.",
        queries=[
            "Write a reply for a client upset about delayed delivery.",
            "Need a professional apology for late shipment.",
            "Draft a concise client response with clear next steps.",
            "Create a formal response with resolution and timeline.",
        ],
        expected_keywords=["apologize", "delay", "resolution", "timeline"],
        tone_type="professional",
        structure_type="professional",
        difficulty="medium",
        max_turns=4,
    ),
    "problem_solving": Task(
        name="problem_solving",
        description="Provide clear troubleshooting steps for a laptop Wi-Fi issue.",
        queries=[
            "My laptop won't connect to Wi-Fi. What should I try?",
            "Internet worked yesterday, now Wi-Fi fails. Help step by step.",
            "Give me safe troubleshooting for network connection issue.",
            "How do I fix sudden laptop Wi-Fi failure?",
        ],
        expected_keywords=["check", "restart", "network", "step"],
        tone_type="helpful",
        structure_type="stepwise",
        difficulty="hard",
        max_turns=6,
    ),
    "casual_conversation": Task(
        name="casual_conversation",
        description="Keep a friendly, light conversation with natural follow-up.",
        queries=[
            "Hey! How's your day going?",
            "Hi, what are you up to today?",
            "How have you been lately?",
        ],
        expected_keywords=["good", "thanks", "you"],
        tone_type="friendly",
        structure_type="conversational",
        difficulty="easy",
        max_turns=2,
    ),
}

_TASK_ORDER: list[TaskId] = [
    "emotional_support",
    "professional_reply",
    "problem_solving",
    "casual_conversation",
]


def get_task(task_name: str) -> Task:
    key = str(task_name or "").strip()
    if key in _TASKS:
        return _TASKS[key]  # type: ignore[index]
    return _TASKS["casual_conversation"]


def get_all_tasks() -> list[dict[str, object]]:
    return [
        {
            "name": t.name,
            "description": t.description,
            "queries": list(t.queries),
            "expected_keywords": list(t.expected_keywords),
            "tone_type": t.tone_type,
            "structure_type": t.structure_type,
        }
        for t in (_TASKS[task_id] for task_id in _TASK_ORDER)
    ]


class TaskManager:
    def __init__(self, difficulty_weights: dict[str, float], seed: int = 42):
        # Kept for compatibility; deterministic manager ignores randomness.
        self._weights = dict(difficulty_weights or {})
        self._seed = int(seed)
        self._episode = 0
        self._turn = 0
        self._task: Task | None = None

    def new_episode(self) -> Task:
        self._episode += 1
        self._turn = 0
        task_id = _TASK_ORDER[(self._episode - 1) % len(_TASK_ORDER)]
        self._task = _TASKS[task_id]
        return self._task

    def advance_turn(self) -> int:
        self._turn += 1
        return self._turn

    def is_done(self, reward: float, correct: bool) -> bool:
        if not self._task:
            return True
        if self._turn >= self._task.max_turns:
            return True
        if self._task.difficulty == "easy" and bool(correct):
            return True
        return False

    @property
    def current_difficulty(self) -> Difficulty:
        return self._task.difficulty if self._task else "easy"

    @property
    def current_task(self) -> Task:
        if self._task is not None:
            return self._task
        return _TASKS["casual_conversation"]

    @property
    def episode(self) -> int:
        return self._episode

    @property
    def turn(self) -> int:
        return self._turn

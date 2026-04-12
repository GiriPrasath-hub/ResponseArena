"""
Grader v4 — semantic + structural evaluation.
Uses difflib for lightweight semantic similarity (no heavy ML deps),
tone detection via marker sets, and structure quality analysis.
"""
from __future__ import annotations
import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

_LAST_QUERY_BY_TASK: Dict[str, str] = {}

EPS = 1e-6  # module-level constant: open-interval guard

# ── Ideal response fragments per task (used for semantic similarity) ──────────
_IDEAL_FRAGMENTS: Dict[str, List[str]] = {
    "emotional_support": [
        "i hear you", "i understand", "you are not alone", "i am here for you",
        "that must be difficult", "your feelings are valid", "let's talk",
        "i support you", "take it one step", "you matter",
    ],
    "professional_reply": [
        "i sincerely apologize", "i appreciate your patience", "we will resolve",
        "please accept my apology", "i will follow up", "by [date]",
        "i understand your concern", "action has been taken", "timeline",
    ],
    "problem_solving": [
        "first", "step", "restart", "check", "make sure", "if that doesn't work",
        "try", "you can also", "the issue may be", "solution",
    ],
    "casual_conversation": [
        "how are you", "sounds great", "that's interesting", "tell me more",
        "i'd love to hear", "nice", "what about you", "sounds fun",
    ],
    "conflict_resolution": [
        "i understand both sides", "let's find common ground", "perspective",
        "i hear you", "resolve", "together", "compromise", "respect",
    ],
    "creative_writing": [
        "once upon", "the sun", "she felt", "he realized", "in a world",
        "slowly", "suddenly", "her eyes", "the moment", "as if",
    ],
    "decision_support": [
        "consider", "option", "pros and cons", "on the other hand",
        "this depends", "one approach", "alternatively", "ultimately",
    ],
    "customer_service": [
        "i apologize", "i understand your frustration", "we value",
        "i will help you", "let me check", "we will resolve", "refund",
    ],
}

# ── Tone markers per task ──────────────────────────────────────────────────────
_TONE_MAP: Dict[str, Dict[str, Any]] = {
    "emotional_support": {
        "tone": "empathetic",
        "markers": ["sorry", "understand", "feel", "here for you", "support", "valid", "not alone", "listen"],
        "weight": 0.35,
    },
    "professional_reply": {
        "tone": "professional",
        "markers": ["apologize", "sincerely", "appreciate", "resolution", "timeline", "formal", "regards"],
        "weight": 0.30,
    },
    "problem_solving": {
        "tone": "helpful",
        "markers": ["step", "check", "try", "restart", "guide", "first", "next", "solution"],
        "weight": 0.25,
    },
    "casual_conversation": {
        "tone": "friendly",
        "markers": ["hey", "great", "thanks", "nice", "love", "cool", "fun", "enjoy"],
        "weight": 0.20,
    },
    "conflict_resolution": {
        "tone": "assertive",
        "markers": ["understand", "perspective", "resolve", "common ground", "together", "respect"],
        "weight": 0.30,
    },
    "creative_writing": {
        "tone": "expressive",
        "markers": ["felt", "realized", "slowly", "suddenly", "whispered", "breathed", "dreamed"],
        "weight": 0.25,
    },
    "decision_support": {
        "tone": "analytical",
        "markers": ["consider", "option", "pros", "cons", "factor", "alternatively", "depends"],
        "weight": 0.30,
    },
    "customer_service": {
        "tone": "professional",
        "markers": ["apologize", "value", "help", "resolve", "check", "account", "ensure"],
        "weight": 0.30,
    },
}


def set_query_context(task_name: str, query: str) -> None:
    key = str(task_name or "").strip().lower()
    if key:
        _LAST_QUERY_BY_TASK[key] = str(query or "")

def _clamp(v: float) -> float:
    v = float(v)
    if v <= 0.0:
        return EPS
    if v >= 1.0:
        return 1.0 - EPS
    return v

def _semantic_score(response: str, task_id: str, query: str) -> float:
    """Lightweight semantic similarity using fragment matching + sequence ratio."""
    text = response.lower()
    fragments = _IDEAL_FRAGMENTS.get(task_id, [])

    # Fragment hit ratio
    hits = sum(1 for f in fragments if f in text)
    frag_score = min(1.0, hits / max(1, len(fragments) * 0.3))

    # Sequence similarity to query (checks topic relevance)
    seq_ratio = SequenceMatcher(None, text[:300], query.lower()[:300]).ratio()
    seq_score = min(1.0, seq_ratio * 2.5)

    base_score = 0.65 * frag_score + 0.35 * seq_score

    # fallback: reward informative answers
    word_count = len(response.split())

    if base_score < 0.3 and word_count > 20:
        base_score = 0.4  # minimum reasonable score

    # bonus for detailed answers
    length_bonus = min(word_count / 100, 1.0) * 0.1

    # Penalize generic template responses
    generic_patterns = ["restart", "check settings", "reconnect", "contact support"]

    if sum(1 for p in generic_patterns if p in text) >= 3:
        base_score *= 0.7

    return _clamp(base_score + length_bonus)


def _tone_score(response: str, task_id: str) -> tuple[float, str]:
    """Returns (score 0-1, feedback string)."""
    text = response.lower()
    cfg = _TONE_MAP.get(task_id, {"markers": [], "tone": "helpful", "weight": 0.25})
    markers = cfg["markers"]
    hits = sum(1 for m in markers if m in text)
    score = _clamp(hits / max(1, len(markers) * 0.4))
    feedback = "good" if score >= 0.5 else "needs_improvement"
    return score, feedback


def _structure_score(response: str, task_id: str) -> tuple[float, str]:
    """Evaluates presence of explanation, steps, clarity."""
    words = re.findall(r"\b\w+\b", response)
    sentences = [s.strip() for s in re.split(r"[.!?]+", response) if s.strip()]
    word_count = len(words)
    sent_count = len(sentences)

    # Penalize too short
    if word_count < 10:
        return _clamp(0.15), "too_short"

    # Check structure signals
    has_steps = bool(re.search(r"\b(first|step|then|next|finally|1\.|2\.)\b", response.lower()))
    has_clarity = "?" not in response  # penalize vague questions
    has_explanation = sent_count >= 2
    adequate_length = 20 <= word_count <= 250
    not_repetitive = len(set(words)) / max(word_count, 1) > 0.45

    score = 0.0
    if has_explanation:  score += 0.35
    if has_steps:        score += 0.25
    if has_clarity:      score += 0.1
    if adequate_length:  score += 0.25
    if not_repetitive:   score += 0.15

    feedback = "good" if score >= 0.6 else "needs_improvement"
    return _clamp(score), feedback


def _missing_keywords(response: str, task_id: str) -> List[str]:
    """Return high-priority keywords not found in response."""
    fragments = _IDEAL_FRAGMENTS.get(task_id, [])
    text = response.lower()
    missing = [f for f in fragments[:5] if f not in text]
    return missing[:3]  # cap at 3


def grade_response(task: Any, response: str) -> Dict[str, Any]:
    if not response or not response.strip():
        return {
            "reward": EPS,
            "breakdown": {"semantic": EPS, "tone": EPS, "structure": EPS},
            "feedback": {
                "tone_feedback": "no_response",
                "structure_feedback": "no_response",
                "missing_keywords": [],
            },
        }

    task_id = str(getattr(task, "id", "")).strip().lower()
    query   = _LAST_QUERY_BY_TASK.get(task_id, "")

    sem                     = _semantic_score(response, task_id, query)
    tone, tone_fb           = _tone_score(response, task_id)
    struct, str_fb          = _structure_score(response, task_id)
    missing                 = _missing_keywords(response, task_id)

    # Negative / harmful response penalty
    bad_words = ["idiot", "stupid", "useless", "shut up", "nonsense"]
    response_lower = response.lower()

    penalty = 0.0
    if any(word in response_lower for word in bad_words):
        penalty = 0.3

    # Actionable / helpful response bonus
    action_words = ["try", "check", "restart", "consider", "you can", "step"]
    bonus = 0.0
    if any(word in response_lower for word in action_words):
        bonus = 0.1

    # Weighted composite
    reward = _clamp(0.45 * sem + 0.30 * tone + 0.25 * struct + bonus - penalty)

    return {
        "reward": float(reward),
        "breakdown": {
            "semantic":  float(sem),
            "tone":      float(tone),
            "structure": float(struct),
        },
        "feedback": {
            "tone_feedback":      tone_fb,
            "structure_feedback": str_fb,
            "missing_keywords":   missing,
            "penalty_applied":    penalty > 0,
            "action_bonus":       bonus > 0,
        },
    }
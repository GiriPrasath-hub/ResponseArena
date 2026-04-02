from __future__ import annotations

import re
from reward.reward_system import RewardSystem

reward_system = RewardSystem()
_LAST_QUERY_BY_TASK: dict[str, str] = {}


def set_query_context(task_name: str, query: str) -> None:
    key = str(task_name or "").strip().lower()
    if not key:
        return
    _LAST_QUERY_BY_TASK[key] = str(query or "")


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _select_expected_keywords(task_name: str, query_text: str, fallback: list[str]) -> list[str]:
    q = str(query_text or "").lower()

    # Query-specific expectations to create deterministic per-query variation.
    if task_name == "emotional_support":
        if "overwhelmed" in q:
            return ["overwhelmed", "support"]
        if "anxious" in q or "exhausted" in q:
            return ["anxious", "calm"]
        if "failing" in q:
            return ["failing", "reassure"]
        if "heavy" in q:
            return ["heavy", "small", "step"]

    if task_name == "professional_reply":
        if "delayed delivery" in q or "delivery" in q:
            return ["delivery", "delay", "client"]
        if "late shipment" in q or "shipment" in q:
            return ["apologize", "shipment", "late"]
        if "next steps" in q:
            return ["next", "resolution", "update"]
        if "formal" in q or "timeline" in q:
            return ["formal", "resolution", "timeline"]

    if task_name == "problem_solving":
        if "won't connect" in q or "wi-fi" in q:
            return ["restart", "network", "wifi"]
        if "step by step" in q:
            return ["step", "check", "settings"]
        if "troubleshooting" in q:
            return ["troubleshoot", "network", "connect"]
        if "sudden" in q or "failure" in q:
            return ["restart", "forget", "reconnect"]

    if task_name == "casual_conversation":
        if "day" in q:
            return ["day", "good", "you"]
        if "up to" in q:
            return ["today", "chat", "you"]
        if "lately" in q:
            return ["lately", "how", "you"]

    return list(fallback or [])


def grade_response(task, response: str):
    text = str(response or "").strip().lower()
    words = re.findall(r"\b\w+\b", text)

    task_name = str(getattr(task, "id", "")).lower()
    query_text = _LAST_QUERY_BY_TASK.get(task_name, "")

    required_keywords = _select_expected_keywords(
        task_name,
        query_text,
        list(getattr(task, "required_keywords", [])),
    )
    tone_name = str(getattr(task, "tone", "helpful")).lower()
    structure_required = bool(getattr(task, "structure_required", False))

    def keyword_present(keyword: str) -> bool:
        k = str(keyword).lower().strip()
        if not k:
            return False
        if k in text:
            return True
        # Deterministic light stemming-like support (e.g., support/supporting)
        for w in words:
            if w.startswith(k) or k.startswith(w):
                return True
            if len(k) >= 5 and k[:-1] in w:
                return True
        return False

    # 1) keywords_score in [0, 1] with deterministic partial-credit buckets
    # Requirement mapping: 3+ -> 1.0, 2 -> 0.7, 1 -> 0.4, 0 -> 0.1
    missing = []
    hit_count = 0
    for kw in required_keywords:
        if not str(kw).strip():
            continue
        if keyword_present(kw):
            hit_count += 1
        else:
            missing.append(str(kw).lower().strip())

    if not required_keywords:
        keywords_score = 0.7
    else:
        capped_hits = max(0, min(3, hit_count))
        if capped_hits >= 3:
            keywords_score = 1.0
        elif capped_hits == 2:
            keywords_score = 0.7
        elif capped_hits == 1:
            keywords_score = 0.4
        else:
            keywords_score = 0.1

    # 2) tone_score in [0, 1], with intensity mismatch penalties
    tone_markers = {
        "empathetic": ["sorry", "understand", "feel", "support", "here for you"],
        "professional": ["apologize", "sincerely", "appreciate", "resolution", "timeline"],
        "helpful": ["step", "check", "try", "next", "restart"],
        "friendly": ["hey", "great", "thanks", "how are", "nice"],
    }
    markers = tone_markers.get(tone_name, tone_markers["helpful"])
    tone_hits = sum(1 for marker in markers if marker in text)
    tone_ratio = min(1.0, tone_hits / max(2, len(markers) // 2))
    # Never allow perfect tone score
    tone_score = _clamp(min(0.9, tone_ratio * 0.9))
    intensity_words = ["overwhelmed", "anxious", "failing", "urgent", "angry", "frustrated"]
    high_intensity = sum(1 for w in intensity_words if w in str(query_text).lower()) >= 1
    empathy_markers = ["understand", "sorry", "support", "here for you", "valid"]
    empathy_hits = sum(1 for m in empathy_markers if m in text)

    if high_intensity and empathy_hits < 2:
        tone_score = _clamp(tone_score - 0.2)
    elif high_intensity and empathy_hits == 2:
        tone_score = _clamp(tone_score - 0.1)

    tone_feedback = "good" if tone_score >= 0.6 else "needs improvement"

    # 3) structure_score in [0, 1]
    sentence_count = len([s for s in re.split(r"[.!?]+", text) if s.strip()])
    multi_sentence = sentence_count >= 2
    long_enough = len(words) >= 12
    step_markers = ["1", "2", "step", "first", "next", "then", "finally"]
    has_steps = any(marker in text for marker in step_markers)
    has_step_1 = ("step 1" in text) or ("1)" in text) or ("1." in text)
    has_step_2 = ("step 2" in text) or ("2)" in text) or ("2." in text)

    if structure_required:
        # Full structure only when clearly stepwise + long enough + multi-sentence
        if has_steps and long_enough and multi_sentence:
            structure_score = 1.0
        elif (has_steps and multi_sentence) or (has_steps and long_enough):
            structure_score = 0.75
        elif has_steps or multi_sentence:
            structure_score = 0.5
        else:
            structure_score = 0.25
    else:
        if multi_sentence and long_enough:
            structure_score = 0.9
        elif multi_sentence or long_enough:
            structure_score = 0.65
        else:
            structure_score = 0.4

    structure_score = _clamp(structure_score)

    # problem_solving must explicitly present Step 1 + Step 2 style structure
    if task_name == "problem_solving" and not (has_step_1 and has_step_2):
        structure_score = _clamp(structure_score - 0.25)

    # Deterministic diversity factor from query length/type
    query_len = len(str(query_text or ""))
    if query_len > 80:
        structure_score = _clamp(structure_score - 0.08)

    structure_feedback = "good" if structure_score >= 0.6 else "needs improvement"

    # Deterministic penalties
    short_penalty = 0.1 if len(words) < 10 else 0.0
    generic_phrases = [
        "i can help",
        "let me help",
        "here is a response",
        "thank you",
        "i understand",
    ]
    generic_hit = any(p in text for p in generic_phrases)
    specific_signal_count = sum(
        1 for token in ["wifi", "network", "delay", "timeline", "anxious", "overwhelmed", "client"] if token in text
    )
    generic_penalty = 0.1 if generic_hit and specific_signal_count <= 1 else 0.0

    # Slight deterministic task-difficulty shaping to increase realistic variation
    task_adjust = {
        "problem_solving": -0.08,
        "emotional_support": -0.04,
        "professional_reply": -0.02,
        "casual_conversation": 0.0,
    }.get(task_name, 0.0)

    # Final weighted reward with clamp
    base_reward = (0.4 * keywords_score) + (0.3 * tone_score) + (0.3 * structure_score)
    reward = _clamp(round(base_reward - short_penalty - generic_penalty + task_adjust, 4))

    return {
        # New required schema
        "reward": reward,
        "breakdown": {
            "keywords": round(keywords_score, 4),
            "tone": round(tone_score, 4),
            "structure": round(structure_score, 4),
        },
        "feedback": {
            "missing_keywords": missing,
            "tone_feedback": tone_feedback,
            "structure_feedback": structure_feedback,
        },
        # Backward-compatible aliases
        "score": reward,
    }


def grade(action, user_msg, context, task=None):
    result = reward_system.compute(action, user_msg, context, task=task)
    return {
        "score": _clamp(result.get("total", 0.0)),
        "details": result,
    }
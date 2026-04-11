"""
Reward system — computes composite reward scores across multiple dimensions.
Used as a secondary reward pathway; primary grading is in openenv/grader.py.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

EPS = 1e-6  # module-level constant: open-interval guard


def _safe(v: float) -> float:
    """Clamp v to the open interval (EPS, 1.0 − EPS)."""
    if v <= 0.0:
        return EPS
    if v >= 1.0:
        return 1.0 - EPS
    return v


class RewardSystem:
    """
    Multi-dimension reward calculator.
    Dimensions: relevance, coherence, tone, length.
    """

    TONE_MARKERS = {
        "empathetic":   ["sorry", "understand", "feel", "support", "here for you", "valid"],
        "professional": ["apologize", "sincerely", "appreciate", "resolution", "timeline", "formal"],
        "helpful":      ["step", "check", "try", "next", "restart", "guide"],
        "friendly":     ["hey", "great", "thanks", "how are", "nice", "chat"],
    }

    def compute(
        self,
        action:   str,
        user_msg: str,
        context:  str,
        task:     Optional[Any] = None,
    ) -> Dict[str, float]:
        """
        Compute a reward dict for a given (action, user_msg) pair.
        Returns keys: relevance, tone, coherence, length, total.
        All values are in the open interval (EPS, 1.0 − EPS).
        """
        text  = str(action   or "").lower().strip()
        query = str(user_msg or "").lower().strip()
        words = re.findall(r"\b\w+\b", text)

        # 1. Relevance — keyword overlap between response and query
        query_words    = set(re.findall(r"\b\w+\b", query))
        response_words = set(words)
        overlap        = query_words & response_words
        relevance = _safe(min(1.0, len(overlap) / max(len(query_words), 1) * 2.5))

        # 2. Tone
        tone_name = "helpful"
        if task:
            tone_name = str(getattr(task, "tone", "helpful")).lower()
        markers   = self.TONE_MARKERS.get(tone_name, self.TONE_MARKERS["helpful"])
        tone_hits = sum(1 for m in markers if m in text)
        tone      = _safe(min(0.9, tone_hits / max(2, len(markers) // 2) * 0.9))

        # 3. Coherence — sentence structure and length
        sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
        coherence = _safe(min(1.0, len(sentences) / 3.0) if len(words) >= 10 else 0.3)

        # 4. Length — adequate but not excessive
        length = _safe(min(1.0, len(words) / 30.0) if len(words) < 200 else 0.8)

        # Weighted composite — also guarded via _safe
        total = _safe(0.35 * relevance + 0.30 * tone + 0.25 * coherence + 0.10 * length)

        return {
            "relevance": float(relevance),
            "tone":      float(tone),
            "coherence": float(coherence),
            "length":    float(length),
            "total":     float(total),
        }

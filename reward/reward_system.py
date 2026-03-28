from __future__ import annotations
from typing import Any

from reward.human_feedback import HumanFeedback
from core.config import EnvConfig, CFG
from reward.accuracy_checker import AccuracyChecker
from reward.relevance_checker import RelevanceChecker
from reward.tone_analyzer import ToneAnalyzer

class RewardSystem:
    """
    Computes the composite reward for one agent action.
    Includes:
    - Accuracy
    - Relevance
    - Tone
    - Human feedback
    - Anti-repetition penalties
    - Smart response bonus
    """

    def __init__(self, config: EnvConfig | None = None) -> None:
        self.cfg = config or CFG
        self._accuracy = AccuracyChecker()
        self._relevance = RelevanceChecker()
        self._tone = ToneAnalyzer()
        self._human = HumanFeedback()

    def compute(
        self,
        action: dict[str, Any],
        user_msg: Any,
        context: list[dict],
    ) -> dict[str, Any]:

        response = str(action.get("response", "")).strip()
        tone = str(action.get("tone", "friendly"))

        # ── Length bonus ─────────────────────────────
        length_bonus = 1.5 if len(response.split()) > 8 else 0.0

        # ── Sub-checks ───────────────────────────────
        acc = self._accuracy.check(
            response=response,
            expected_keywords=user_msg.expected_keywords,
            topic=user_msg.topic,
        )

        rel = self._relevance.check(
            response=response,
            topic=getattr(user_msg, "topic", "default"),
        )

        ton = self._tone.analyze(
            response=response,
            tone=tone,
            user_mood=getattr(user_msg, "mood", "happy"),
        )

        # ── Human feedback ───────────────────────────
        human_score = self._human.evaluate(response, user_msg)

        # ── Accuracy scoring ─────────────────────────
        if acc.get("correct", False):
            accuracy_reward = 12
        elif acc.get("partial", False):
            accuracy_reward = 6
        else:
            accuracy_reward = -12

        # ── Relevance scoring ────────────────────────
        if rel.get("relevant", False):
            relevance_reward = 8
        elif rel.get("partial", False):
            relevance_reward = 4
        else:
            relevance_reward = -5

        # ── Tone scoring ─────────────────────────────
        tone_quality = ton.get("quality", "neutral")
        user_mood = getattr(user_msg, "mood", "happy")

        if tone_quality == "good":
            tone_reward = 4
            if user_mood == "angry":
                tone_reward += 2

        elif tone_quality == "neutral":
            tone_reward = 0
            if user_mood == "angry":
                tone_reward -= 2

        else:
            tone_reward = -8

        # ── Repetition penalty (strong) ───────────────
        repetition_penalty = 0

        if context:
            try:
                last_response = str(
                    context[-1].get("action", {}).get("response", "")
                ).strip()

                if response == last_response:
                    repetition_penalty -= 10
            except Exception:
                pass

        # ── Low diversity penalty ─────────────────────
        if context:
            recent_responses = [
                t.get("action", {}).get("response", "")
                for t in context[-3:]
            ]

            if len(set(recent_responses)) <= 2:
                repetition_penalty -= 5

        # ── Generic response penalty (VERY IMPORTANT) ─
        generic_phrases = [
            "let me help you",
            "i'm here to help",
            "happy to assist",
            "of course",
        ]

        if any(p in response.lower() for p in generic_phrases):
            repetition_penalty -= 2

        # ── Follow-up penalty ────────────────────────
        followup_penalty = 0

        if getattr(user_msg, "topic", "") == "follow_up":
            if "what else" in response.lower():
                followup_penalty = -3

        # ── Smart action bonus ───────────────────────
        if any(word in response.lower() for word in ["press", "click", "open", "restart"]):
            smart_bonus = 3
        else:
            smart_bonus = 0

        # ── Combine penalties ────────────────────────
        total_penalty = repetition_penalty + followup_penalty

        # ── Final reward ─────────────────────────────
        total = (
            accuracy_reward
            + relevance_reward
            + tone_reward
            + total_penalty
            + length_bonus
            + human_score
            + smart_bonus
        )

        return {
            "total": round(total, 2),
            "correct": acc.get("correct", False),
            "accuracy_score": 1.0 if acc.get("correct") else (0.5 if acc.get("partial") else 0.0),
            "accuracy_reward": accuracy_reward,
            "relevance_reward": relevance_reward,
            "tone_reward": tone_reward,
            "human_feedback": human_score,
            "repetition_penalty": repetition_penalty,
            "followup_penalty": followup_penalty,
            "length_bonus": length_bonus,
            "smart_bonus": smart_bonus,
            "accuracy": acc,
            "relevance": rel,
            "tone": ton,
        }
from __future__ import annotations
from typing import Any

from reward.human_feedback import HumanFeedback
from core.config import EnvConfig, CFG
from reward.accuracy_checker import AccuracyChecker
from reward.relevance_checker import RelevanceChecker
from reward.tone_analyzer import ToneAnalyzer
from openenv.environment.task_manager import Task, grade_response


class RewardSystem:
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
        task: Task | None = None,
    ) -> dict[str, Any]:

        response = str(action.get("response", ""))
        tone = str(action.get("tone", "friendly"))

        # Main task-based deterministic grading (0.0 to 1.0)
        if task is not None:
            base_score = grade_response(task, response)
            expected_tone = task.tone
            difficulty = task.difficulty
        else:
            # Backward-compatible fallback when task context is not provided.
            fallback_task = Task(
                id="casual_conversation",
                input_prompt=getattr(user_msg, "message", ""),
                expected_behavior="Provide a relevant and helpful response.",
                difficulty=getattr(user_msg, "difficulty", "medium"),
                max_turns=4,
                required_keywords=list(getattr(user_msg, "expected_keywords", [])),
                tone=tone,
                structure_required=False,
            )
            base_score = grade_response(fallback_task, response)
            expected_tone = tone
            difficulty = fallback_task.difficulty

        # Slight difficulty scaling, then clamp to [0.0, 1.0]
        difficulty_scale = {
            "easy": 0.98,
            "medium": 1.00,
            "hard": 1.04,
        }.get(difficulty, 1.0)
        scaled_score = max(0.0, min(1.0, round(base_score * difficulty_scale, 4)))

        # Supplemental diagnostics retained for compatibility/debugging
        acc = self._accuracy.check(
            response=response,
            expected_keywords=getattr(user_msg, "expected_keywords", []),
            topic=getattr(user_msg, "topic", ""),
        )
        rel = self._relevance.check(
            response=response,
            topic=getattr(user_msg, "topic", "default"),
        )
        ton = self._tone.analyze(
            response=response,
            tone=expected_tone,
            user_mood=getattr(user_msg, "mood", "happy"),
        )
        human_score = self._human.evaluate(response, user_msg)

        # Correctness flag for episode termination logic
        correct = scaled_score >= 0.75

        return {
            "total": scaled_score,
            "correct": correct,
            "accuracy_score": base_score,
            "task_score": base_score,
            "difficulty_scale": difficulty_scale,
            "difficulty": difficulty,
            "accuracy_reward": acc,
            "relevance_reward": rel,
            "tone_reward": ton,
            "human_feedback": human_score,
            "repetition_penalty": 0.0,
            "followup_penalty": 0.0,
            "length_bonus": 0.0,
        }
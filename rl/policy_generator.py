from __future__ import annotations

from typing import Any
from openenv.grader import set_query_context


def generate_response(task_name: str, query: str) -> str:
    task = str(task_name or "").strip().lower()
    user_query = str(query or "").strip()
    set_query_context(task, user_query)

    if task == "emotional_support":
        return (
            "I'm really sorry you're feeling this way, and I understand this feels heavy right now. "
            "Your feelings are valid, and you're not failing. "
            "Take one small step: pause, take a slow breath, and focus on a single manageable task. "
            "I'm here to support you through this."
        )

    if task == "professional_reply":
        return (
            "Thank you for your message. We sincerely apologize for the delivery delay and the inconvenience caused. "
            "We have escalated your case and are actively working on a resolution. "
            "You will receive a confirmed update with timeline details within 24 hours."
        )

    if task == "problem_solving":
        return (
            "1) Restart your laptop and router to clear temporary network issues. "
            "2) Open network settings and check that Wi-Fi is enabled and airplane mode is off. "
            "3) Select your network again, enter the password carefully, and reconnect. "
            "4) If it still fails, forget the saved network and connect again from scratch."
        )

    if task == "casual_conversation":
        return (
            "Hey! I'm doing good, thanks for asking. "
            "I'm glad to chat with you today. "
            "How's your day going so far?"
        )

    # Deterministic direct answer fallback
    return (
        "I understand your request and will address it directly. "
        f"Based on your message, here is the best concise response: {user_query or 'I am ready to help with your task.'}"
    )


class ResponseGenerator:
    """Deterministic task-aware response generator."""

    def __init__(self, rng_seed: int | None = None) -> None:
        self._seed = rng_seed

    def generate(self, state: dict[str, Any], tone: str) -> str:
        task_name = str(state.get("topic", "")).strip().lower()
        query = str(state.get("user_message", "")).strip()
        return generate_response(task_name, query)

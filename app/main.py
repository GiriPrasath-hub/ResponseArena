from __future__ import annotations

import os
import sys

# Allow direct execution: `python app/main.py`
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, request, jsonify, render_template

from environment.env import LoveEnv
from agent.agent import LoveAgent
from reward.reward_system import RewardSystem
from environment.task_manager import _TASKS
from environment.user_simulator import UserMessage
from openenv.grader import grade_response

app = Flask(__name__, template_folder="templates")

env = LoveEnv()
agent = LoveAgent()
reward_system = RewardSystem()

state = env.reset()
current_task_id = state.get("topic") if isinstance(state, dict) else None

AI_RESPONSE_BANK: dict[str, list[str]] = {
    "emotional_support": [
        "I'm really sorry you're feeling this way. I understand this feels heavy right now, and your feelings are valid. I'm here to support you, and we can take one calm step at a time.",
        "I'm sorry this has been so overwhelming. I understand how difficult this can feel, and you deserve support. Let's pause, breathe, and focus on one small step you can manage now.",
        "I'm truly sorry you're carrying so much. I understand this can feel exhausting, and you are not alone. I'm here to support you with steady, practical steps and reassurance.",
    ],
    "professional_reply": [
        "I sincerely apologize for the delay and take full accountability for the inconvenience caused. We are actively resolving this and will share a confirmed status update with a clear delivery timeline within 24 hours.",
        "Please accept our sincere apology for the delay. We fully acknowledge the issue and responsibility, and our team is prioritizing a resolution. You will receive a detailed progress update and timeline within one business day.",
        "We apologize for this delay and understand the impact it has caused. We are accountable for this issue and are implementing a resolution now, with a precise update and delivery timeline coming in the next 24 hours.",
    ],
    "problem_solving": [
        "1) Restart your router and laptop to safely clear temporary network faults. 2) Open network settings and confirm Wi-Fi is enabled, airplane mode is off, and the right network is selected. 3) Reconnect and test; if needed, forget the network and connect again with the password.",
        "1) Power-cycle your router for 30 seconds and restart the laptop, because this often fixes transient connection states safely. 2) Check adapter and network settings to verify Wi-Fi is on and connected to the correct SSID. 3) Reconnect and run a quick internet test; if failure persists, remove and re-add the saved network profile.",
        "1) Restart both router and laptop to reset stale networking sessions. 2) In network settings, confirm Wi-Fi is active and the correct network credentials are being used. 3) Attempt reconnection; if still failing, forget the network, re-enter the password, and retry for a clean handshake.",
    ],
    "casual_conversation": [
        "Hey! I'm doing great, thanks for asking. How has your day been so far, and did anything fun happen today?",
        "Hi! I'm doing really well and happy to chat with you. How are you doing, and what are you up to right now?",
        "Hey there! I'm doing good and glad you asked. How's your day going, and is there something you'd like to talk about?",
    ],
}
AI_RESPONSE_INDEX: dict[str, int] = {task_id: 0 for task_id in AI_RESPONSE_BANK}

AI_SCENARIO_INPUTS: dict[str, list[str]] = {
    "emotional_support": [
        "I feel overwhelmed and anxious today.",
        "I'm exhausted and emotionally drained.",
        "Everything feels too much and I can't focus.",
        "I feel like I'm failing and need support.",
    ],
    "professional_reply": [
        "Help me reply to a client upset about delay.",
        "Write a professional apology for late delivery.",
        "Draft a response with accountability and timeline.",
        "Need formal message with clear resolution plan.",
    ],
    "problem_solving": [
        "Laptop won't connect to Wi-Fi. What should I do?",
        "Internet keeps dropping. Give me troubleshooting steps.",
        "Wi-Fi worked yesterday, not today. Help step by step.",
        "Need safe steps to fix wireless connection issue.",
    ],
    "casual_conversation": [
        "Hey, how's it going?",
        "How is your day so far?",
        "What's up today?",
        "Any fun thoughts to share?",
    ],
}


def _clamp(value: float) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return 0.0


def _quality(score: float) -> str:
    if score >= 0.8:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def _normalize_feedback(raw_feedback: dict | None) -> dict[str, object]:
    fb = raw_feedback or {}
    missing = fb.get("missing", [])
    if not isinstance(missing, list):
        missing = []
    return {
        "missing_keywords": [str(m) for m in missing],
        "tone_feedback": str(fb.get("tone", "needs improvement")),
        "structure_feedback": str(fb.get("structure", "needs improvement")),
    }


def _default_task_id() -> str:
    return next(iter(_TASKS.keys()), "casual_conversation")


def _set_task(task_id: str) -> None:
    global state, current_task_id
    task = _TASKS.get(task_id) or _TASKS[_default_task_id()]

    env.reset()
    env._tasks._task = task
    env._tasks._turn = 0
    env._current_user_msg = UserMessage(
        message=task.input_prompt,
        mood="neutral",  # type: ignore[arg-type]
        difficulty=task.difficulty,
        topic=task.id,
        expected_keywords=list(task.required_keywords),
        turn=0,
    )
    state = env._build_state(env._current_user_msg, turn=0)
    current_task_id = task.id


def _next_ai_baseline(task_id: str) -> str:
    tid = task_id if task_id in AI_RESPONSE_BANK else _default_task_id()
    options = AI_RESPONSE_BANK.get(tid, ["I understand. Let me help you."])
    idx = AI_RESPONSE_INDEX.get(tid, 0)
    response = options[idx]
    AI_RESPONSE_INDEX[tid] = (idx + 1) % len(options)
    return response


def _scenario_inputs(task_id: str) -> list[str]:
    tid = task_id if task_id in AI_SCENARIO_INPUTS else _default_task_id()
    return list(AI_SCENARIO_INPUTS.get(tid, []))[:5] or [
        _TASKS.get(tid, _TASKS[_default_task_id()]).input_prompt
    ]


def _ensure_state() -> None:
    global state, current_task_id
    if not isinstance(state, dict):
        state = env.reset()
    if not current_task_id:
        current_task_id = state.get("topic") if isinstance(state, dict) else _default_task_id()
    if current_task_id not in _TASKS:
        current_task_id = _default_task_id()
    if not isinstance(state, dict) or str(state.get("topic", "")) != current_task_id:
        _set_task(current_task_id)


# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify([
        {"id": t.id, "description": t.expected_behavior}
        for t in _TASKS.values()
    ])


@app.route("/chat", methods=["POST"])
def chat():
    global state, current_task_id

    try:
        data = request.get_json(silent=True) or {}
        message = str(data.get("message", "")).strip()
        task_id = str(data.get("task_id", current_task_id or _default_task_id())).strip()
        mode = str(data.get("mode", "ai")).strip().lower()

        if task_id not in _TASKS:
            task_id = _default_task_id()

        if task_id != current_task_id:
            _set_task(task_id)
        else:
            _ensure_state()

        task = _TASKS.get(current_task_id or _default_task_id(), _TASKS[_default_task_id()])
        human_input = message if message else task.input_prompt

        if mode == "ai":
            results: list[dict] = []
            for scenario in _scenario_inputs(task.id):
                _set_task(task.id)
                state["user_message"] = scenario
                action = agent.act(state)
                next_state, reward, done, info = env.step(action)
                if isinstance(next_state, dict):
                    state.update(next_state)
                if done:
                    _set_task(task.id)

                score = _clamp(reward)
                human_eval = grade_response(task, scenario)
                results.append({
                    "input": scenario,
                    "response": str(action.get("response", "")),
                    "score": round(score, 4),
                    "quality": str(info.get("agent_quality", _quality(score))) if isinstance(info, dict) else _quality(score),
                    "human_response": scenario,
                    "human_score": round(_clamp(human_eval.get("score", 0.0)), 4),
                })

            return jsonify({
                "mode": "ai",
                "results": results,
            })

        if mode == "human":
            human_eval = grade_response(task, human_input)
            ai_baseline = _next_ai_baseline(task.id)
            ai_eval = grade_response(task, ai_baseline)

            human_score = _clamp(human_eval.get("score", 0.0))
            ai_score = _clamp(ai_eval.get("score", 0.0))
            winner = "human" if human_score > ai_score else "ai"
            breakdown = human_eval.get("breakdown", {"keywords": 0.0, "tone": 0.0, "structure": 0.0})
            feedback = _normalize_feedback(human_eval.get("feedback", {}))

            return jsonify({
                "mode": "human",
                "ai_response": ai_baseline,
                "human_response": human_input,
                "ai_score": round(ai_score, 4),
                "user_score": round(human_score, 4),
                "human_score": round(human_score, 4),
                "breakdown": breakdown,
                "feedback": feedback,
                "winner": winner,
                "agent_quality": _quality(ai_score),
            })

        # Fallback for unknown mode: default to AI MODE response shape.
        return jsonify({"mode": "ai", "results": []})

    except Exception:
        return jsonify({
            "mode": "error",
            "results": [],
            "human_response": "",
            "ai_response": "",
            "user_score": 0.0,
            "human_score": 0.0,
            "ai_score": 0.0,
            "breakdown": {"keywords": 0.0, "tone": 0.0, "structure": 0.0},
            "feedback": {"missing_keywords": [], "tone_feedback": "needs improvement", "structure_feedback": "needs improvement"},
            "winner": "ai",
            "agent_quality": "low",
            "error": "Server error",
        }), 500


# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
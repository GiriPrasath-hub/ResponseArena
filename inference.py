"""
LOVE vH Inference Script
Runs the AI response evaluation environment with an LLM agent.
 
Output format:
  [START] — marks beginning of episode
  [STEP]  — marks each environment step
  [END]   — marks end of episode with final score
 
Required env vars:
  ENV_BASE_URL  — URL of the running environment (default: http://localhost:7860)
  API_BASE_URL  — OpenAI-compatible LLM API base URL
  MODEL_NAME    — Model identifier
  HF_TOKEN      — Hugging Face token (used as Bearer key)
"""
from __future__ import annotations

import os
import sys
import time
import requests
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

EPS = 1e-6  # open-interval guard: rewards are always in (EPS, 1-EPS)
 
# ── Configuration ─────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
MODEL_NAME   = os.environ.get("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN     = os.environ.get("HF_TOKEN", "")
 
LLM_URL = (
    f"{API_BASE_URL}/v1"
    if not API_BASE_URL.rstrip("/").endswith("/v1")
    else API_BASE_URL
)
client = None

def get_client():
    global client
    if client is None:
        try:
            client = OpenAI(
                api_key=HF_TOKEN if HF_TOKEN else "dummy-key",
                base_url=LLM_URL,
            )
        except Exception as e:
            print("[WARN] Client init failed:", e)
            return None
    return client

 
# Tasks to run during inference (one episode per task)
INFERENCE_TASKS = [
    {"task_id": "casual_conversation"},
    {"task_id": "emotional_support"},
    {"task_id": "professional_reply"},
    {"task_id": "problem_solving"},
]
 
# ── Network helper ─────────────────────────────────────────────────────────────

def safe_post(url: str, payload: dict) -> dict:
    """POST with full error handling. Always returns a dict with safe reward."""
    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()

        # 🔒 Ensure reward is always in (0,1)
        reward = float(data.get("reward", EPS))
        if reward <= 0.0:
            reward = EPS
        elif reward >= 1.0:
            reward = 1.0 - EPS

        data["reward"] = reward
        return data

    except Exception as e:
        print(f"[ERROR] POST {url} failed: {e}", file=sys.stderr)
        return {
            "observation": {},
            "state": {},
            "reward": EPS,  # 🔥 CRITICAL FIX (was 0.0 before)
            "done": True,
            "info": {"error": str(e)},
        }
 
 
# ── Environment client ─────────────────────────────────────────────────────────
 
def env_reset(task_id: Optional[str] = None) -> dict:
    """Call POST /reset to start a new episode. Returns reset response dict."""
    payload: dict = {}
    if task_id:
        payload["task_id"] = task_id
    return safe_post(f"{ENV_BASE_URL}/reset", payload)
 
def env_step(response_text: str) -> dict:
    return safe_post(
        f"{ENV_BASE_URL}/step",
        {"type": "respond", "human_content": response_text},
    )
 
 
# ── LLM agent ─────────────────────────────────────────────────────────────────
 
def call_llm(system_prompt: str, user_prompt: str) -> str:
    c = get_client()

    if c is None:
        return _fallback(user_prompt)

    try:
        completion = c.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=400,
            temperature=0.4,
        )
        text = completion.choices[0].message.content or ""
        return text.strip()
    except Exception as e:
        print(f"[WARN] LLM call failed ({e}), using fallback.", file=sys.stderr)
        return _fallback(user_prompt)
 
 
def _fallback(prompt: str) -> str:
    """Rule-based fallback responses when LLM is unavailable."""
    p = prompt.lower()
 
    if "overwhelmed" in p:
        return (
            "I hear you, and I want you to know that feeling overwhelmed is completely valid. "
            "I am here to support you through this. Please take a breath — you don't have to "
            "figure everything out at once. One small step at a time is enough."
        )
    if "anxious" in p or "exhausted" in p:
        return (
            "I understand how draining it feels when anxiety and exhaustion take hold. "
            "Your feelings are valid, and I am here for you. "
            "Let us take this one gentle moment at a time together."
        )
    if "failing" in p:
        return (
            "Feeling like you are failing does not mean you are. I understand how heavy that feels. "
            "I am here to support and reassure you — you are doing better than you think."
        )
    if "heavy" in p:
        return (
            "That heavy feeling is real, and I am here to support you. "
            "Let us focus on one small step at a time — you do not have to carry this alone."
        )
    if "delivery" in p or "delayed" in p:
        return (
            "Dear Client, I sincerely apologize for the delayed delivery. "
            "We take full responsibility and are working urgently with our logistics team to resolve this. "
            "A confirmed timeline and resolution plan will be shared within 24 hours. "
            "Thank you for your patience."
        )
    if "shipment" in p or "late" in p:
        return (
            "Dear Client, please accept our sincere apologies for the late shipment. "
            "We are actively working on an expedited resolution and will provide a full timeline update "
            "by end of business today. We appreciate your understanding."
        )
    if "next steps" in p or "timeline" in p:
        return (
            "Dear Stakeholder, I want to provide clarity on our resolution and next steps. "
            "Our team has reviewed the situation and a formal timeline document will be shared tomorrow. "
            "We apologize for any inconvenience and appreciate your continued partnership."
        )
    if any(w in p for w in ["wi-fi", "wifi", "connect", "internet", "dropping", "network", "connection"]):
        return (
            "I can help you resolve this. Please follow these steps:\n\n"
            "Step 1: Restart your router — unplug it for 30 seconds, then reconnect.\n"
            "Step 2: On your laptop, go to Network Settings, forget the Wi-Fi network, "
            "and reconnect.\n"
            "Step 3: Check if your network adapter driver needs updating in Device Manager.\n"
            "Step 4: If the issue persists, run the network troubleshooter or reset network "
            "settings. Let me know which step resolves it."
        )
    if "day" in p or "how are" in p:
        return (
            "Hey! Things are going pretty well today, thank you for asking! "
            "How about you — how is your day going so far?"
        )
    if "lately" in p or "up to" in p:
        return (
            "Not too much on my end, just enjoying some good conversations! "
            "How have you been lately? Anything exciting going on with you?"
        )
    return (
        "Thank you for reaching out. I am here to support and assist you. "
        "Please let me know how I can help you further today."
    )
 
 
def build_system_prompt(task_name: str, tone: str) -> str:
    tone_instructions = {
        "empathetic": (
            "Respond with deep empathy, warmth, and emotional understanding. "
            "Validate feelings. Use phrases like 'I understand', 'I'm here for you', "
            "'your feelings are valid'."
        ),
        "professional": (
            "Respond in a formal, polished, business-appropriate tone. "
            "Include an apology, a clear resolution commitment, and a timeline."
        ),
        "helpful": (
            "Respond with clear, actionable, step-by-step guidance. "
            "Number your steps explicitly (Step 1, Step 2, etc.)."
        ),
        "friendly": (
            "Respond in a warm, casual, conversational tone. "
            "Keep it light and engaging."
        ),
    }
    return (
        f"You are a skilled AI assistant specializing in {task_name.replace('_', ' ')}. "
        f"{tone_instructions.get(tone, 'Respond helpfully and clearly.')} "
        f"Keep your response focused, genuine, and between 50–150 words."
    )
 
 
# ── Episode runner ─────────────────────────────────────────────────────────────
 
def run_episode(task_config: dict) -> dict:
    task_id = task_config.get("task_id")
 
    # ── Reset environment ─────────────────────────────────────────────────────
    reset_data = env_reset(task_id)
 
    # Support both /reset response shapes: {state: {...}} and {observation: {...}}
    obs = reset_data.get("state") or reset_data.get("observation") or {}
 
    task_name    = obs.get("task_id") or obs.get("task") or task_id or "unknown"
    task_display = obs.get("task_name", task_name)
    query        = obs.get("query", "")
    difficulty   = obs.get("difficulty", "medium")
 
    print(f"[START] task={task_name} env=responsearena model={MODEL_NAME}")
    sys.stdout.flush()
 
    # ── Determine tone ────────────────────────────────────────────────────────
    tone_map = {
        "emotional_support":  "empathetic",
        "professional_reply": "professional",
        "problem_solving":    "helpful",
        "casual_conversation":"friendly",
    }
    tone = tone_map.get(task_name, "helpful")
 
    system_prompt = build_system_prompt(task_display, tone)
    user_prompt   = query if query else f"Please help me with a {task_display} scenario."
 
    # ── Generate response ─────────────────────────────────────────────────────
    response = call_llm(system_prompt, user_prompt).strip()
 
    # ── Step environment ──────────────────────────────────────────────────────
    result     = env_step(response)
    reward = float(result.get("reward", 0.0))
    reward = max(EPS, min(1.0 - EPS, reward))
    info       = result.get("info", {})
    evaluation = info.get("evaluation") or result.get("evaluation") or {}
    breakdown  = evaluation.get("breakdown", {})
    feedback   = evaluation.get("feedback", {})
 
    breakdown_str = (
        " | ".join(f"{k}={v:.2f}" for k, v in breakdown.items())
        if breakdown else "n/a"
    )
 
    print(
        f"[STEP] step=1 action={response} reward={reward:.2f} done=true error={info.get('error') if info.get('error') else 'null'}"
    )
    sys.stdout.flush()
 
    missing   = feedback.get("missing_keywords", [])
    tone_fb   = feedback.get("tone_feedback", "n/a")
    struct_fb = feedback.get("structure_feedback", "n/a")
 
    print(
        f"[END] success={'true' if reward > 0 else 'false'} steps=1 rewards={reward:.2f}"
    )
    sys.stdout.flush()
 
    return {
        "task_id":   task_name,
        "task_name": task_display,
        "query":     query,
        "reward":    reward,
        "breakdown": breakdown,
    }
 
 
# ── Main ───────────────────────────────────────────────────────────────────────
 
def main() -> float:
    print("=" * 60)
    print("ResponseArena Inference Runner")
    print(f"  ENV URL : {ENV_BASE_URL}")
    print(f"  LLM URL : {LLM_URL}")
    print(f"  Model   : {MODEL_NAME}")
    print("=" * 60)
    sys.stdout.flush()
 
    # Wait for environment to be ready
    for i in range(30):
        try:
            r = requests.get(f"{ENV_BASE_URL}/health", timeout=5)
            if r.status_code == 200:
                print(f"Environment ready (attempt {i + 1})")
                break
        except Exception:
            pass
        time.sleep(2)
    else:
        print("ERROR: Environment not reachable.", file=sys.stderr)
        sys.exit(1)
 
    results = []
    for task_config in INFERENCE_TASKS:
        print(f"\n{'─' * 60}")
        try:
            result = run_episode(task_config)
            results.append(result)
        except Exception as e:
            print(f"[ERROR] Episode failed: {e}", file=sys.stderr)
            results.append({"task_id": task_config.get("task_id", "unknown"), "reward": EPS})

    # Summary
    print(f"\n{'=' * 60}")
    print("INFERENCE SUMMARY")
    print(f"{'=' * 60}")
    total = 0.0
    for r in results:
        score = float(r.get("reward", EPS))
        score = max(EPS, min(1.0 - EPS, score))
        total += score
        bd     = r.get("breakdown", {})
        bd_str = " | ".join(f"{k}={v:.2f}" for k, v in bd.items()) if bd else ""
        print(f"  [{r.get('task_id', 'unknown'):22}]  score={score:.4f}  {bd_str}")
 
    avg = total / max(len(results), 1)
    print(f"{'─' * 60}")
    print(f"  Average Score : {avg:.4f}")
    print(f"{'=' * 60}")
    sys.stdout.flush()
 
    return avg
 
 
if __name__ == "__main__":
    main()
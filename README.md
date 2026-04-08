---
title: LOVE vH Environment
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
---

# ◈ LOVE vH — AI Response Evaluation Environment

> An OpenEnv-compatible reinforcement learning environment that evaluates AI-generated responses across four real-world communication tasks: emotional support, professional correspondence, technical problem solving, and casual conversation.

---

## Overview

LOVE vH is a single-step RL environment where an AI agent receives a human-like query and must generate an appropriate response. The response is then graded deterministically across three dimensions — **keywords**, **tone**, and **structure** — producing a reward in `[0.0, 1.0]`.

The system is fully self-contained: no external LLM is required. A built-in rule-based agent handles inference, but any OpenAI-compatible LLM can be plugged in via environment variables.

---

## Project Structure

```
love-vh/
├── app.py                        # FastAPI server
├── inference.py                  # OpenEnv inference runner
├── openenv.yaml                  # OpenEnv specification
├── Dockerfile                    # Single-entrypoint container
├── requirements.txt
├── pyproject.toml
│
├── openenv/
│   ├── __init__.py
│   ├── grader.py                 # Deterministic grader (keywords, tone, structure)
│   ├── client.py                 # Standard OpenEnv client interface
│   ├── agent/
│   │   └── response_generator.py # Rule-based + LLM response generation
│   ├── environment/
│   │   ├── wrapper.py            # OpenEnvWrapper (reset/step/state)
│   │   └── task_manager.py       # Task loading and episode management
│   └── reward/
│       └── reward_system.py      # Multi-dimension reward computation
│
├── data/
│   └── tasks.json                # 4 tasks × 4 queries each
│
└── frontend/
    ├── index.html                # Interactive evaluation UI
    ├── style.css                 # Editorial dark aesthetic
    └── script.js                 # Full interactive client logic
```

---

## Tasks

| Task ID | Difficulty | Tone | Description |
|---|---|---|---|
| `casual_conversation` | Easy | Friendly | Warm, natural everyday conversation |
| `emotional_support` | Medium | Empathetic | Validating responses to emotional distress |
| `professional_reply` | Medium | Professional | Formal business communication with resolution |
| `problem_solving` | Hard | Helpful | Step-by-step technical troubleshooting |

Each task has 4 queries. The environment cycles through them deterministically across episodes.

---

## Observation Space

```json
{
  "task": "emotional_support",
  "task_name": "Emotional Support",
  "task_description": "Respond with empathy and warmth...",
  "difficulty": "medium",
  "query": "I feel so overwhelmed with everything going on in my life right now."
}
```

---

## Action Space

```json
{
  "type": "respond",
  "content": "I hear you, and I want you to know your feelings are valid..."
}
```

`content` is optional — if omitted, the built-in rule-based generator responds automatically.

---

## Reward Logic

Weighted composite across three dimensions:

| Dimension | Weight | What it measures |
|---|---|---|
| Keywords | 40% | Presence of expected vocabulary for this specific query |
| Tone | 30% | Appropriateness of emotional register |
| Structure | 30% | Coherence, sentence count, step markers (required for `problem_solving`) |

### Partial credit

- Keywords: `3+ hits → 1.0`, `2 hits → 0.7`, `1 hit → 0.4`, `0 hits → 0.1`
- Tone: scaled 0–0.9 (never perfect), with penalty for high-intensity queries missing empathy
- Structure: tiered by sentence count, length, and step markers

### Penalties

- Short responses (< 10 words): −0.10
- Generic phrases without specific signals: −0.10
- Task difficulty adjustment: `problem_solving` −0.08, `emotional_support` −0.04, `professional_reply` −0.02

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Interactive frontend UI |
| `/health` | GET | Health check |
| `/reset` | POST | Start new episode |
| `/step` | POST | Submit response for evaluation |
| `/state` | GET | Current environment state |
| `/tasks` | GET | List all tasks |
| `/tasks/{task_id}` | GET | Get specific task details |
| `/docs` | GET | Interactive API documentation |

---

## Local Setup

```bash
git clone <repo>
cd love-vh

pip install -r requirements.txt

uvicorn app:app --host 0.0.0.0 --port 7860 --reload
```

Open `http://localhost:7860` for the UI, `http://localhost:7860/docs` for the API.

---

## Docker

```bash
# Build
docker build -t love-vh .

# Run
docker run -p 7860:7860 love-vh

# Run with external LLM
docker run -p 7860:7860 \
  -e MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct" \
  -e API_BASE_URL="https://api-inference.huggingface.co/v1" \
  -e HF_TOKEN="hf_..." \
  love-vh
```

---

## Running Inference

```bash
export ENV_BASE_URL="http://localhost:7860"
export API_BASE_URL="https://api-inference.huggingface.co/v1"
export MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct"
export HF_TOKEN="hf_your_token"

python inference.py
```

### Output format

```
[START] task=casual_conversation difficulty=easy query='Hey, how is your day going?'
[STEP] step=1 task=casual_conversation reward=0.6200 breakdown=[keywords=0.70 | tone=0.54 | structure=0.65] done=true
[END] task=casual_conversation reward=0.6200 tone=good structure=good missing_keywords=[]

[START] task=emotional_support difficulty=medium query='I feel so overwhelmed...'
[STEP] step=1 task=emotional_support reward=0.7440 breakdown=[...] done=true
[END] task=emotional_support reward=0.7440 ...
```

---

## Hugging Face Deployment

1. Create a new Space → SDK: **Docker**
2. Upload all project files
3. Set Space secrets:
   - `MODEL_NAME`
   - `API_BASE_URL`
   - `HF_TOKEN`
4. The Space builds and exposes port `7860` automatically

---

## Example API Usage

```python
import requests

BASE = "http://localhost:7860"

# Start episode
r = requests.post(f"{BASE}/reset", json={"task_id": "emotional_support"})
obs = r.json()["observation"]
print(obs["query"])
# → "I feel so overwhelmed with everything going on in my life right now."

# Submit response
reply = (
    "I hear you, and I want you to know that feeling overwhelmed is completely valid. "
    "I am here to support you through this. Let us take one small step at a time together."
)
result = requests.post(f"{BASE}/step", json={"type": "respond", "content": reply}).json()
print(result["reward"])       # → 0.8240
print(result["evaluation"])   # → {breakdown: {...}, feedback: {...}}
```

---

## License

MIT License — built as part of the LOVE (Living Omni Voice Ecosystem) project.

# ⚔️ ResponseArena — Interactive AI Evaluation Lab

> **An OpenEnv-compliant hybrid AI evaluation environment** with RL-based reward shaping + LLM-powered response generation.

---

## 🧠 Overview

ResponseArena is a **real-world AI evaluation system** where responses are:

* Generated using **LLM APIs (Hugging Face / OpenAI-compatible)**
* Evaluated using a **deterministic multi-dimensional reward system**
* Improved over time using **Reinforcement Learning (RL memory + policy shaping)**

---

## 🚀 Key Features

### 🔥 Hybrid Intelligence System

* ✅ LLM-based generation (Meta LLaMA via HF API)
* ✅ Rule-based fallback (offline safe)
* ✅ RL-based adaptive scoring

---

### 🧮 Multi-Dimensional Evaluation

Each response is scored across:

| Metric    | Weight | Description           |
| --------- | ------ | --------------------- |
| Semantic  | 0.45   | Relevance to query    |
| Tone      | 0.30   | Emotional correctness |
| Structure | 0.25   | Clarity & formatting  |

---

### 🔁 Reinforcement Learning (Core Innovation)

* Per-task adaptive policies
* Reward shaping with learning bonus
* Experience replay buffer
* Persistent memory (`/tmp/arena_memory.json`)
* Dynamic weight adjustment

---

## 🌍 Supported Tasks (8 Total)

| Task                | Type       |
| ------------------- | ---------- |
| casual_conversation | Chat       |
| emotional_support   | Empathy    |
| professional_reply  | Business   |
| problem_solving     | Technical  |
| conflict_resolution | Reasoning  |
| creative_writing    | Creativity |
| decision_support    | Analysis   |
| customer_service    | Support    |

---

## 🧩 System Architecture

```
User / Inference
      ↓
LLM API (HF / OpenAI)
      ↓
ResponseArena Environment
      ↓
Grader (Semantic + Tone + Structure)
      ↓
RL Policy (Reward Shaping)
      ↓
Final Score
```

---

## ⚙️ Environment API

| Endpoint    | Description            |
| ----------- | ---------------------- |
| `/reset`    | Start new episode      |
| `/step`     | Submit response        |
| `/state`    | Current state          |
| `/evaluate` | AI vs Human comparison |
| `/stats`    | RL analytics           |

---

## 🧪 Inference (IMPORTANT FOR JUDGES)

```bash
python inference.py
```

---

### Sample Output

```
[START] task=emotional_support
[STEP] reward=0.76
[END] success=true
```

---

## 🔑 Environment Variables

Create `.env` file:

```
API_BASE_URL=https://router.huggingface.co/v1
HF_TOKEN=your_token_here
MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
ENV_BASE_URL=http://localhost:7860
```

---

## 🐳 Docker Deployment

```bash
docker build -t responsearena .
docker run -p 7860:7860 responsearena
```

---

## 🤗 Hugging Face Deployment

1. Create Space → Docker
2. Upload project
3. Add Secrets:

* HF_TOKEN
* API_BASE_URL
* MODEL_NAME

---

## 📊 Evaluation Modes

### 🤖 AI Mode

* LLM-generated response
* RL-evaluated

### 🧑 Human Mode

* User or simulated human response
* Compared against AI

---

## 🧠 Why This Project Stands Out

* ❌ Not just chatbot
* ✅ Full **evaluation system**
* ✅ RL + LLM hybrid architecture
* ✅ Deterministic + agentic evaluation
* ✅ Real-world communication tasks

---

## ⚠️ Notes

* `.env` file is NOT included for security
* Falls back to rule-based system if API not available
* RL memory resets via `/reset-policy`

---

## 👨‍💻 Author

Built as part of **Meta x PyTorch x Scaler Hackathon**

**ResponseArena — Where AI earns its intelligence.**

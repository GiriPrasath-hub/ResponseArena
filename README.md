---
title: "ResponseArena — AI Evaluation Lab"
emoji: "⚔️"
colorFrom: "purple"
colorTo: "indigo"
sdk: "docker"
---

# ⚔️ ResponseArena — Interactive AI Evaluation Lab

> An OpenEnv-compliant reinforcement learning environment for evaluating AI-generated responses across real-world communication scenarios.

---

## 🌐 Live Demo

🔗 Hugging Face Space: https://huggingface.co/spaces/giri0304/ResponseArena   
💻 GitHub Repository: https://github.com/GiriPrasath-hub/ResponseArena

---

## 🧠 What is ResponseArena?

ResponseArena is a **single-step reinforcement learning (RL) environment** where an AI agent generates responses to human-like queries and is evaluated using a deterministic scoring system.

It enables:

* AI benchmarking
* Human vs AI comparison
* RL-based evaluation
* Communication intelligence testing

---

## 🎯 OpenEnv Hackathon Compliance

This project satisfies all required criteria:

✅ Real-world environment   
✅ 4 structured evaluation tasks   
✅ Deterministic reward system   
✅ OpenEnv API (`/reset`, `/step`, `/state`)   
✅ `inference.py` included   
✅ Docker deployment ready   
✅ Hugging Face Spaces deployment   
✅ Structured evaluation logs   

---

## 🌍 Tasks

| Task                | Difficulty | Description                                  |
| ------------------- | ---------- | -------------------------------------------- |
| casual_conversation | Easy       | Friendly everyday interaction                |
| emotional_support   | Medium     | Empathetic responses to emotional situations |
| professional_reply  | Medium     | Formal business communication                |
| problem_solving     | Hard       | Step-by-step technical guidance              |

---

## 🧩 RL Environment Design

### Observation Space

```json
{
  "task": "emotional_support",
  "task_name": "Emotional Support",
  "difficulty": "medium",
  "query": "I feel overwhelmed with everything going on."
}
```

---

### Action Space

```json
{
  "type": "respond",
  "content": "Your response text here..."
}
```

---

## 🧮 Reward System

The environment uses a **multi-dimensional deterministic reward system**:

```text
reward = (0.4 × keywords) + (0.3 × tone) + (0.3 × structure)
```

### Evaluation Criteria

* **Keywords (40%)** → Relevance to context
* **Tone (30%)** → Emotional appropriateness
* **Structure (30%)** → Clarity and formatting

---

## 🔁 RL Flow

1. Environment reset (`/reset`)
2. Receive query
3. Generate response
4. Submit action (`/step`)
5. Receive reward

---

## 🏗️ Project Structure

```bash
ResponseArena/
├── openenv/
├── core/
├── server/
├── rl/
├── data/
├── frontend/
├── inference.py
├── openenv.yaml
├── Dockerfile
├── requirements.txt
├── README.md
```

---

## 🌐 API Endpoints

| Endpoint  | Method | Description           |
| --------- | ------ | --------------------- |
| `/reset`  | POST   | Start new episode     |
| `/step`   | POST   | Submit response       |
| `/state`  | GET    | Get environment state |
| `/health` | GET    | Health check          |

---

## ⚙️ Run Locally

```bash
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

---

## 🐳 Docker Deployment

```bash
docker build -t response-arena .
docker run -p 7860:7860 response-arena
```

---

## ▶️ Run Inference

```bash
export ENV_BASE_URL=http://localhost:7860
python inference.py
```

---

## 💡 Key Features

* Deterministic AI evaluation
* Human vs AI comparison system
* Multi-dimensional scoring engine
* OpenEnv-compatible RL environment
* Interactive frontend UI

---

## 🚀 Future Scope

* Multi-step RL training
* Voice-based evaluation
* Emotion-aware scoring system
* Personalized AI feedback

---

## 📜 License

MIT License

---

## 👨‍💻 Author

Giri Prasath

**ResponseArena — Where AI earns its intelligence.**

---

title: LOVE vH Environment
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker

🤖 LOVE vH — Interactive AI Evaluation Environment

A Dockerized OpenEnv-compatible AI evaluation system that simulates real-world human-AI interaction and grades responses using structured reward logic.

---

🚀 Overview

LOVE vH is an Interactive AI Evaluation Lab where:

- AI responses are compared against human expectations
- Outputs are graded using reward shaping (keywords, tone, structure)
- The system behaves like a real environment (not just a model)

---

⚙️ Deployment Details

- Runtime: Docker (HuggingFace Spaces)
- Server: FastAPI + Uvicorn
- Port: "7860"

uvicorn server.app:app --host 0.0.0.0 --port 7860

---

🔌 API Endpoints

This Space exposes a REST API (no UI):

Health Check

GET /

{"status": "running"}

Reset Environment

POST /reset

Step Environment

POST /step

Example:

{
  "type": "respond",
  "content": "generated response here"
}

Get Current State

GET /state

---

🧠 How It Works

1. Environment initializes with a scenario
2. User/agent sends an action ("/step")
3. System evaluates response
4. Returns:
   - next state
   - reward score
   - done flag
   - metadata

---

💻 Run Locally

pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860

---

🌐 HuggingFace Deployment

1. Create a Docker Space
2. Upload this project
3. Ensure "Dockerfile" exposes port "7860"
4. Deployment will start automatically

---

🏆 Use Cases

- AI vs Human evaluation systems
- Reinforcement learning environments
- Prompt evaluation pipelines
- Hackathon-ready AI testing framework

---

⚡ Status

✅ Dockerized
✅ OpenEnv Compatible
✅ API Functional
✅ Ready for Deployment

---

Built as part of an advanced AI evaluation system (LOVE Project).
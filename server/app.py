"""
ResponseArena v3.4 — Production-ready, OpenEnv Phase 2.
"""
import json
import os
import random
from pathlib import Path
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from inference import build_system_prompt, call_llm
from openenv.environment.task_manager import (
    _MAP,
    _TASKS,
    _normalize_task_id,
    get_all_tasks,
)
from openenv.environment.wrapper import OpenEnvWrapper
from openenv.grader import grade_response, set_query_context
from rl.policy import _MEMORY_PATH, get_memory

if not os.getenv("HF_TOKEN"):
    print("WARNING: HF_TOKEN not set — LLM calls will use fallback")

if not os.getenv("API_BASE_URL"):
    print("WARNING: API_BASE_URL not set — LLM disabled, using fallback")

memory = get_memory()
policy = memory.policy

_TONE_MAP = {
    "emotional_support":  "empathetic",
    "professional_reply": "professional",
    "problem_solving":    "helpful",
    "casual_conversation": "friendly",
    "conflict_resolution": "empathetic",
    "creative_writing":   "expressive",
    "decision_support":   "analytical",
    "customer_service":   "professional",
}

def reset_rl_system() -> dict:
    global memory, policy, _env

    from rl.policy import _memory

    _memory.buffer._buf.clear()
    _memory._task_history.clear()

    for p in _memory.task_policies.values():
        p.weights = {"semantic": 0.40, "tone": 0.30, "structure": 0.30}
        p.update_count = 0
        p._dim_rewards.clear()

    try:
        _MEMORY_PATH.unlink(missing_ok=True)
    except Exception:
        pass

    _memory._save()

    memory = _memory
    policy = memory.policy
    _env = OpenEnvWrapper()

    return {
        "status": "reset",
        "message": "RL system fully reset (memory + weights + env)",
    }


app = FastAPI(
    title="ResponseArena — Human vs AI Evaluation",
    version="3.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_frontend = Path(__file__).parent.parent / "frontend"
if _frontend.exists():
    app.mount("/static", StaticFiles(directory=str(_frontend)), name="static")

_env = OpenEnvWrapper()


def _load_human_dataset() -> dict:
    path = Path(__file__).parent.parent / "data" / "human_eval_dataset.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            dataset: dict = {}
            for entry in raw:
                tid = str(entry.get("task_id", "")).strip()
                if tid:
                    dataset.setdefault(tid, []).append(entry)
            return dataset
        if isinstance(raw, dict):
            return raw
    except Exception:
        pass
    return {}


_HUMAN_DATASET: dict = _load_human_dataset()


def _find_best_human_match(task_id: str, query: str) -> Optional[dict]:
    entries = _HUMAN_DATASET.get(task_id, [])
    if not entries:
        return None
    q_words = set(query.lower().split())
    best_score = -1
    best_entry = None
    for entry in entries:
        entry_words = set(str(entry.get("query", "")).lower().split())
        overlap = len(q_words & entry_words) / max(len(q_words | entry_words), 1)
        if overlap > best_score:
            best_score = overlap
            best_entry = entry
    return best_entry


class EvaluateRequest(BaseModel):
    task_id: str
    query: str
    human_response: Optional[str] = None
    mode: str = "ai"


class BatchEvaluateRequest(BaseModel):
    items: List[EvaluateRequest]


class ResetRequest(BaseModel):
    task_id: Optional[str] = None


class StepRequest(BaseModel):
    type: str = "respond"
    human_content: Optional[str] = None


@app.get("/", include_in_schema=False)
def home():
    index = _frontend / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"error": "index.html not found"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "ResponseArena"}


@app.get("/tasks")
def list_tasks():
    return {"tasks": get_all_tasks()}


@app.get("/tasks/{task_id}")
def get_task_detail(task_id: str):
    norm = _normalize_task_id(task_id)
    t = _MAP.get(norm) if norm else None
    if not t:
        raise HTTPException(404, f"Task '{task_id}' not found")
    return t.to_dict()


@app.get("/query")
def get_random_query(task_id: Optional[str] = None, mode: str = "ai"):
    norm = _normalize_task_id(str(task_id or ""))
    if norm and norm in _MAP:
        task = _MAP[norm]
    else:
        if not _TASKS:
            raise HTTPException(500, "No tasks loaded")
        task = random.choice(_TASKS)

    if mode == "human":
        pool = [q for q in task.human_queries if q and q.strip()]
    else:
        pool = [q for q in task.queries if q and q.strip()]

    if not pool:
        pool = [q for q in task.queries if q and q.strip()]
    if not pool:
        pool = [task.description or f"Help with {task.name}"]

    return {
        "task_id":          task.id,
        "task_name":        task.name,
        "task_description": task.description,
        "difficulty":       task.difficulty,
        "tone":             task.tone,
        "query":            random.choice(pool),
        "mode":             mode,
    }


@app.get("/policy")
def policy_simple():
    return memory.policy.to_dict()


@app.get("/policy/stats")
def policy_stats():
    return memory.get_stats()


def _do_evaluate(
    task_id: str,
    query: str,
    human_response: Optional[str],
    mode: str = "ai",
) -> dict:
    norm = _normalize_task_id(str(task_id or ""))
    if not norm:
        raise HTTPException(400, "No task selected. Please choose a task from the dropdown.")

    task = _MAP.get(norm)
    if not task:
        valid = ", ".join(sorted(_MAP.keys()))
        raise HTTPException(404, f"Task '{task_id}' not found. Valid tasks: {valid}")

    query = (query or "").strip()
    if not query:
        raise HTTPException(400, "query must not be empty")

    effective_task = norm
    set_query_context(effective_task, query)

    tone = _TONE_MAP.get(effective_task, "helpful")
    system_prompt = build_system_prompt(effective_task, tone)

    # ── AI response: always LLM ───────────────────────────────────────────────
    ai_response = call_llm(system_prompt, query)
    ai_evaluation = grade_response(task, ai_response)
    ai_evaluation["explanation"] = (
        f"Semantic: {ai_evaluation['breakdown'].get('semantic', 0)} | "
        f"Tone: {ai_evaluation['breakdown'].get('tone', 0)} | "
        f"Structure: {ai_evaluation['breakdown'].get('structure', 0)}"
    )
    r = float(ai_evaluation.get("reward", 0.0))
    EPS = 1e-6
    if r <= 0.0:
        ai_base = EPS
    elif r >= 1.0:
        ai_base = 1.0 - EPS
    else:
        ai_base = r
    ai_reward = memory.record_eval(
        task_id=effective_task,
        query=query,
        response=ai_response,
        actor="ai",
        breakdown=ai_evaluation.get("breakdown", {}),
        raw_reward=ai_base,
    )

    # ── Human response ────────────────────────────────────────────────────────
    # AI mode: human_response is optional user-provided text.
    # Human mode: LLM generates the "human" response; user text is ignored.
    human_text: str = ""
    human_evaluation: Optional[dict] = None
    human_reward: Optional[float] = None

    if mode == "human":
        human_system_prompt = build_system_prompt(effective_task, tone)
        human_text = call_llm(human_system_prompt, query)
        human_evaluation = grade_response(task, human_text)
        r = float(human_evaluation.get("reward", 0.0))
        EPS = 1e-6
        if r <= 0.0:
            human_base = EPS
        elif r >= 1.0:
            human_base = 1.0 - EPS
        else:
            human_base = r
        human_reward = memory.record_eval(
            task_id=effective_task,
            query=query,
            response=human_text,
            actor="human",
            breakdown=human_evaluation.get("breakdown", {}),
            raw_reward=human_base,
        )
    else:
        provided = str(human_response or "").strip()
        if provided:
            human_text = provided
            human_evaluation = grade_response(task, human_text)
            r = float(human_evaluation.get("reward", 0.0))
            EPS = 1e-6
            if r <= 0.0:
                human_base = EPS
            elif r >= 1.0:
                human_base = 1.0 - EPS
            else:
                human_base = r
            human_reward = memory.record_eval(
                task_id=effective_task,
                query=query,
                response=human_text,
                actor="human",
                breakdown=human_evaluation.get("breakdown", {}),
                raw_reward=human_base,
            )

    # ── Dataset reference (human mode only, no RL recording) ─────────────────
    dataset_match: Optional[dict] = None
    if mode == "human":
        match = _find_best_human_match(effective_task, query)
        if match:
            ideal_text = str(match.get("ideal_response", "")).strip()
            if ideal_text:
                ideal_eval = grade_response(task, ideal_text)
                r = float(ideal_eval.get("reward", 0.0))
                EPS = 1e-6
                if r <= 0.0:
                    ideal_base = EPS
                elif r >= 1.0:
                    ideal_base = 1.0 - EPS
                else:
                    ideal_base = r
                dataset_match = {
                    "query":          match.get("query", ""),
                    "ideal_response": ideal_text,
                    "reward":         ideal_base,
                    "evaluation":     ideal_eval,
                    "keywords":       match.get("keywords", []),
                }

    # ── Verdict ───────────────────────────────────────────────────────────────
    if human_reward is not None:
        if human_reward > ai_reward:
            better = "human"
        elif ai_reward > human_reward:
            better = "ai"
        else:
            better = "tie"
    else:
        better = "ai"

    comparison_summary = _build_comparison_summary(
        better, ai_reward, human_reward, ai_evaluation, human_evaluation
    )

    return {
        "task_id":            effective_task,
        "task_name":          task.name,
        "query":              query,
        "mode":               mode,
        "comparison_summary": comparison_summary,
        "ai": {
            "response":    ai_response,
            "reward":      ai_reward,
            "base_reward": ai_base,
            "evaluation":  ai_evaluation,
        },
        "human": {
            "response":   human_text,
            "reward":     human_reward,
            "evaluation": human_evaluation,
        } if human_text else None,
        "better":        better,
        "policy":        memory.policy.to_dict(),
        "dataset_match": dataset_match,
    }


def _build_comparison_summary(
    better: str,
    ai_reward: float,
    human_reward: Optional[float],
    ai_eval: Optional[dict],
    human_eval: Optional[dict],
) -> str:
    if human_reward is None:
        return ""

    ai_bd = (ai_eval   or {}).get("breakdown", {})
    hu_bd = (human_eval or {}).get("breakdown", {})
    ai_fb = (ai_eval   or {}).get("feedback",  {})
    hu_fb = (human_eval or {}).get("feedback",  {})

    def _get(d: dict, *keys: str) -> float:
        for k in keys:
            if k in d:
                return d[k]
        return 0.0

    ai_sem = _get(ai_bd, "semantic", "keywords")
    hu_sem = _get(hu_bd, "semantic", "keywords")
    ai_tn  = ai_bd.get("tone", 0)
    hu_tn  = hu_bd.get("tone", 0)
    ai_st  = ai_bd.get("structure", 0)
    hu_st  = hu_bd.get("structure", 0)

    diffs = []
    if abs(ai_sem - hu_sem) >= 0.15:
        w = "AI" if ai_sem > hu_sem else "Human"
        diffs.append(
            f"{w} covered more relevant content "
            f"({round(max(ai_sem, hu_sem) * 100)}% vs {round(min(ai_sem, hu_sem) * 100)}%)"
        )
    if abs(ai_tn - hu_tn) >= 0.15:
        w = "AI" if ai_tn > hu_tn else "Human"
        diffs.append(
            f"{w} matched tone better "
            f"({round(max(ai_tn, hu_tn) * 100)}% vs {round(min(ai_tn, hu_tn) * 100)}%)"
        )
    if abs(ai_st - hu_st) >= 0.15:
        w = "AI" if ai_st > hu_st else "Human"
        diffs.append(
            f"{w} was better structured "
            f"({round(max(ai_st, hu_st) * 100)}% vs {round(min(ai_st, hu_st) * 100)}%)"
        )

    delta = round(abs(ai_reward - (human_reward or 0)) * 100)

    if better == "tie":
        base = "Both responses scored equally."
        return (base + " Notable: " + "; ".join(diffs) + ".") if diffs else base

    winner = "AI" if better == "ai" else "Human"
    loser  = "Human" if better == "ai" else "AI"

    summary = (
        f"{winner} response was stronger by {delta}pt — {'; '.join(diffs)}."
        if diffs
        else f"{winner} response edged ahead by {delta}pt overall."
    )

    loser_miss = (
        hu_fb.get("missing_keywords", []) if better == "ai"
        else ai_fb.get("missing_keywords", [])
    )
    if loser_miss:
        summary += (
            f" The {loser} response was missing: "
            + ", ".join(f'"{k}"' for k in loser_miss[:3])
            + "."
        )

    return summary


@app.post("/evaluate")
def evaluate(req: EvaluateRequest):
    try:
        return _do_evaluate(req.task_id, req.query, req.human_response, req.mode)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/evaluate/batch")
def evaluate_batch(req: BatchEvaluateRequest):
    if len(req.items) > 10:
        raise HTTPException(400, "Maximum 10 items per batch")
    results = []
    for item in req.items:
        try:
            results.append(
                _do_evaluate(item.task_id, item.query, item.human_response, item.mode)
            )
        except Exception as e:
            results.append({"error": str(e), "task_id": item.task_id})
    return {"results": results, "count": len(results)}


@app.post("/reset")
def reset_ep(req: ResetRequest = ResetRequest()):
    try:
        obs = _env.reset(task_id=req.task_id)
        return {
            "observation": obs,
            "task_id":     obs["task"],
            "task_name":   obs["task_name"],
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/step")
def step_ep(action: StepRequest):
    if _env.current_task is None:
        raise HTTPException(400, "No active episode — call /reset first")

    try:
        obs, reward, done, info = _env.step({
            "type":    action.type,
            "content": action.human_content or "",
        })

        # 🔒 FINAL SAFETY CLAMP (CRITICAL)
        EPS = 1e-6
        if reward <= 0.0:
            reward = EPS
        elif reward >= 1.0:
            reward = 1.0 - EPS

        return {
            "observation":   obs,
            "reward":        reward,
            "done":          done,
            "response":      info.get("response", ""),
            "evaluation":    info.get("evaluation", {}),
            "base_reward":   info.get("base_reward", reward),
            "shaped_reward": info.get("shaped_reward", reward),
            "ai":   {
                "response":   info.get("response", ""),
                "reward":     reward,
                "evaluation": info.get("evaluation", {}),
            },
            "human":  None,
            "better": "ai",
        }

    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/state")
def state_ep():
    return _env.state()


@app.get("/stats")
def stats():
    return memory.get_stats()


@app.post("/reset-policy")
def reset_policy():
    try:
        return reset_rl_system()
    except Exception as e:
        raise HTTPException(500, str(e))


def main():
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=7860,
        reload=False,
    )


if __name__ == "__main__":
    main()

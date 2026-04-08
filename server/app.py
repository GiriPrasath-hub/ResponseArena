"""
ResponseArena v3.3 — Fixed task selection, random mode, human dataset integration.
"""
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import json
import random

from openenv.environment.task_manager import (
    get_all_tasks, get_task, _TASKS, _MAP, _normalize_task_id
)
from openenv.grader import set_query_context, grade_response
from openenv.agent.response_generator import generate_response
from rl.policy import get_memory


from openenv.environment.wrapper import OpenEnvWrapper

memory = get_memory()
policy = memory.policy

app = FastAPI(
    title="ResponseArena — Human vs AI Evaluation",
    version="3.3.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_frontend = Path(__file__).parent.parent / "frontend"
if _frontend.exists():
    app.mount("/static", StaticFiles(directory=str(_frontend)), name="static")

# ── Single shared env instance (used by /reset + /step) ──────────────────────
_env = OpenEnvWrapper()

# ── Human evaluation dataset (loaded once at startup) ─────────────────────────
_HUMAN_DATASET_PATH = Path(__file__).parent / "data" / "human_eval_dataset.json"

def _load_human_dataset() -> dict:
    """
    Load human_eval_dataset.json keyed by task_id → list of entries.
    Each entry: {query, ideal_response, keywords, tone}
    Returns empty dict if file not found — human mode still works via AI generation.
    """
    if not _HUMAN_DATASET_PATH.exists():
        return {}
    try:
        raw = json.loads(_HUMAN_DATASET_PATH.read_text(encoding="utf-8"))
        # Support both list format and dict format
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
    """
    Find the closest matching entry in the human dataset for a given query.
    Uses simple word-overlap scoring. Returns None if dataset has no entries for task.
    """
    entries = _HUMAN_DATASET.get(task_id, [])
    if not entries:
        return None

    q_words = set(query.lower().split())
    best_score = -1
    best_entry = None

    for entry in entries:
        entry_q = str(entry.get("query", "")).lower()
        entry_words = set(entry_q.split())
        overlap = len(q_words & entry_words) / max(len(q_words | entry_words), 1)
        if overlap > best_score:
            best_score = overlap
            best_entry = entry

    return best_entry


# ── Request models ────────────────────────────────────────────────────────────
class EvaluateRequest(BaseModel):
    task_id:        str
    query:          str
    human_response: Optional[str] = None
    mode:           str = "ai"   # "ai" | "human"


class BatchEvaluateRequest(BaseModel):
    items: List[EvaluateRequest]


class ResetRequest(BaseModel):
    task_id: Optional[str] = None


class StepRequest(BaseModel):
    type:          str = "respond"
    human_content: Optional[str] = None


# ── Routes ────────────────────────────────────────────────────────────────────

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
    """
    Return a random query for a task.
    task_id: accepts IDs, display names, empty/"random" for true random.
    mode: "ai" → task.queries, "human" → task.human_queries
    """
    # Normalise task_id — handles display names, empty, "random"
    norm = _normalize_task_id(str(task_id or ""))

    if norm and norm in _MAP:
        task = _MAP[norm]
    else:
        # True random selection from all tasks
        if not _TASKS:
            raise HTTPException(500, "No tasks loaded")
        task = random.choice(_TASKS)

    # Select query pool based on mode
    if mode == "human":
        pool = [q for q in task.human_queries if q and q.strip()]
    else:
        pool = [q for q in task.queries if q and q.strip()]

    # Fallback to other pool if selected pool is empty
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
    query:   str,
    human_response: Optional[str],
    mode: str = "ai",
) -> dict:
    """
    Core evaluation logic.

    AI mode:
      - Uses task_id directly (no silent fallback to casual_conversation)
      - Generates AI response and grades it
      - Optionally grades human response too

    Human mode:
      - AI response generated as usual
      - Additionally looks up ideal response in human dataset for reference grading
    """
    # ── Task resolution — normalize and raise if not found ────────────────────
    norm = _normalize_task_id(str(task_id or ""))
    if not norm:
        raise HTTPException(400, f"No task selected. Please choose a task from the dropdown.")

    task = _MAP.get(norm)
    if not task:
        valid = ", ".join(sorted(_MAP.keys()))
        raise HTTPException(404, f"Task '{task_id}' not found. Valid tasks: {valid}")

    query = (query or "").strip()
    if not query:
        raise HTTPException(400, "query must not be empty")

    # Use the normalised task id for everything — no detection override in AI mode
    effective_task = norm

    set_query_context(effective_task, query)

    # ── AI response ───────────────────────────────────────────────────────────
    ai_response   = generate_response(effective_task, query)
    ai_evaluation = grade_response(task, ai_response)
    ai_base       = float(max(0.0, min(1.0, ai_evaluation.get("reward", 0.0))))
    ai_reward     = memory.record_eval(
        task_id=effective_task,
        query=query,
        response=ai_response,
        actor="ai",
        breakdown=ai_evaluation.get("breakdown", {}),
        raw_reward=ai_base
    )

    # ── Human response (AI mode: optional user text) ──────────────────────────
    human_text = str(human_response or "").strip()
    if human_text:
        human_evaluation = grade_response(task, human_text)
        human_base       = float(max(0.0, min(1.0, human_evaluation.get("reward", 0.0))))
        human_reward = memory.record_eval(
    task_id=effective_task,
    query=query,
    response=human_text,
    actor="human",
    breakdown=human_evaluation.get("breakdown", {}),
    raw_reward=human_base
)
    
    else:
        human_evaluation = None
        human_reward     = None

    # ── Human mode: look up dataset ideal response ────────────────────────────
    # In human mode the user typed their own query; we use the dataset to provide
    # a reference ideal_response alongside the AI-generated one.
    dataset_match = None
    if mode == "human":
        match = _find_best_human_match(effective_task, query)
        if match:
            ideal_text = str(match.get("ideal_response", "")).strip()
            if ideal_text:
                ideal_eval = grade_response(task, ideal_text)
                ideal_base  = float(max(0.0, min(1.0, ideal_eval.get("reward", 0.0))))
                ideal_reward = ideal_base
                dataset_match = {
                    "query":           match.get("query", ""),
                    "ideal_response":  ideal_text,
                    "reward":          ideal_reward,
                    "evaluation":      ideal_eval,
                    "keywords":        match.get("keywords", []),
                }

    # ── Verdict ───────────────────────────────────────────────────────────────
    if human_reward is not None:
        if human_reward > ai_reward:   better = "human"
        elif ai_reward > human_reward: better = "ai"
        else:                          better = "tie"
    else:
        better = "ai"

    # ── Comparison summary ────────────────────────────────────────────────────
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
        "policy": memory.policy.to_dict(),
        "dataset_match": dataset_match,   # None in AI mode or if no match found
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

    # Works with both breakdown schemas (keywords/tone/structure OR semantic/tone/structure)
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
        diffs.append(f"{w} covered more relevant content ({round(max(ai_sem,hu_sem)*100)}% vs {round(min(ai_sem,hu_sem)*100)}%)")
    if abs(ai_tn - hu_tn) >= 0.15:
        w = "AI" if ai_tn > hu_tn else "Human"
        diffs.append(f"{w} matched tone better ({round(max(ai_tn,hu_tn)*100)}% vs {round(min(ai_tn,hu_tn)*100)}%)")
    if abs(ai_st - hu_st) >= 0.15:
        w = "AI" if ai_st > hu_st else "Human"
        diffs.append(f"{w} was better structured ({round(max(ai_st,hu_st)*100)}% vs {round(min(ai_st,hu_st)*100)}%)")

    delta = round(abs(ai_reward - (human_reward or 0)) * 100)

    if better == "tie":
        base = "Both responses scored equally."
        return (base + " Notable: " + "; ".join(diffs) + ".") if diffs else base

    winner = "AI" if better == "ai" else "Human"
    loser  = "Human" if better == "ai" else "AI"

    summary = (
        f"{winner} response was stronger by {delta}pt — {'; '.join(diffs)}."
        if diffs else
        f"{winner} response edged ahead by {delta}pt overall."
    )

    loser_miss = (
        hu_fb.get("missing_keywords", []) if better == "ai"
        else ai_fb.get("missing_keywords", [])
    )
    if loser_miss:
        summary += f" The {loser} response was missing: {', '.join(f'{chr(34)}{k}{chr(34)}' for k in loser_miss[:3])}."

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
            results.append(_do_evaluate(item.task_id, item.query, item.human_response, item.mode))
        except Exception as e:
            results.append({"error": str(e), "task_id": item.task_id})
    return {"results": results, "count": len(results)}


# ── OpenEnv /reset + /step ────────────────────────────────────────────────────

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
        return {
            "observation":   obs,
            "reward":        reward,
            "done":          done,
            "response":      info.get("response", ""),
            "evaluation":    info.get("evaluation", {}),
            "base_reward":   info.get("base_reward", reward),
            "shaped_reward": info.get("shaped_reward", reward),
            "ai":   {"response": info.get("response", ""), "reward": reward, "evaluation": info.get("evaluation", {})},
            "human": None,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

import uvicorn

def main():
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=7860,
        reload=False
    )

if __name__ == "__main__":
    main()
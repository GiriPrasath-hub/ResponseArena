"""
openenv/environment/env.py — OpenEnv-compliant ResponseArenaEnv

Environment flow:
  env.reset(task_id?)  →  state
  env.step(action)     →  (state, reward, done, info)
  env.get_state()      →  current state dict
"""
from __future__ import annotations
import random
from typing import Any, Dict, Optional, Tuple

from openenv.environment.task_manager import _TASKS, _MAP, Task
from openenv.grader import grade_response, set_query_context
from openenv.agent.response_generator import generate_response
from rl.policy import get_memory


class ResponseArenaEnv:
    """
    OpenEnv-compliant environment for response quality evaluation.

    State space:
        task_id, task_name, difficulty, tone, query, episode, step_count

    Action space:
        Any string response (human or AI generated)

    Reward:
        Composite score ∈ [0, 1] from semantic + tone + structure grading,
        further adjusted by the adaptive RL policy.
    """

    def __init__(self):
        self._task:       Optional[Task] = None
        self._query:      str  = ""
        self._episode:    int  = 0
        self._step_count: int  = 0
        self._done:       bool = True
        self._memory = get_memory()

    # ── OpenEnv interface ──────────────────────────────────────────────────────

    def reset(self, task_id: Optional[str] = None, mode: str = "ai") -> Dict[str, Any]:
        """
        Start a new episode. Returns initial state.
        mode='ai'    → pick from task.queries
        mode='human' → pick from task.human_queries
        """
        task = _MAP.get(task_id) if task_id else None
        if task is None:
            task = random.choice(_TASKS)

        pool = task.queries if mode == "ai" else (task.human_queries or task.queries)
        query = random.choice(pool) if pool else "Please help me."

        self._task       = task
        self._query      = query
        self._episode   += 1
        self._step_count = 0
        self._done       = False

        set_query_context(task.id, query)
        return self.get_state()

    def step(self, action: str, actor: str = "human") -> Tuple[Dict, float, bool, Dict]:
        """
        Process one response (action). Returns (next_state, reward, done, info).
        done=True after each step (one-shot evaluation episodes).
        """
        if self._task is None:
            raise RuntimeError("Call reset() before step()")

        result  = grade_response(self._task, action)
        raw_r   = result["reward"]
        breakdown = result["breakdown"]

        # RL policy adjusts reward based on learned weights
        adj_r = self._memory.record_eval(
            task_id    = self._task.id,
            query      = self._query,
            response   = action,
            actor      = actor,
            breakdown  = breakdown,
            raw_reward = raw_r,
        )

        self._step_count += 1
        self._done = True  # one-shot episode

        info = {
            "raw_reward":  raw_r,
            "adj_reward":  adj_r,
            "breakdown":   breakdown,
            "feedback":    result["feedback"],
            "policy":      self._memory.policy.to_dict(),
        }

        return self.get_state(), adj_r, self._done, info

    def get_state(self) -> Dict[str, Any]:
        if self._task is None:
            return {"status": "idle"}
        return {
            "task_id":    self._task.id,
            "task_name":  self._task.name,
            "difficulty": self._task.difficulty,
            "tone":       self._task.tone,
            "query":      self._query,
            "episode":    self._episode,
            "step_count": self._step_count,
            "done":       self._done,
        }

    # ── Convenience: full stateless evaluate ─────────────────────────────────

    def evaluate_stateless(
        self,
        task_id:        str,
        query:          str,
        human_response: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Stateless evaluation (no persistent episode state).
        Generates AI response and optionally grades human response.
        Both go through the RL policy for reward computation.
        """
        task = _MAP.get(task_id)
        if task is None:
            raise ValueError(f"Unknown task_id: {task_id}")

        set_query_context(task.id, query)

        # ── AI response ───────────────────────────────────────────────────────
        ai_response   = generate_response(task.id, query)
        ai_result     = grade_response(task, ai_response)
        ai_adj_reward = self._memory.record_eval(
            task_id    = task.id,
            query      = query,
            response   = ai_response,
            actor      = "ai",
            breakdown  = ai_result["breakdown"],
            raw_reward = ai_result["reward"],
        )

        # ── Human response (optional) ─────────────────────────────────────────
        human_text = str(human_response or "").strip()
        if human_text:
            h_result     = grade_response(task, human_text)
            h_adj_reward = self._memory.record_eval(
                task_id    = task.id,
                query      = query,
                response   = human_text,
                actor      = "human",
                breakdown  = h_result["breakdown"],
                raw_reward = h_result["reward"],
            )
        else:
            h_result = h_adj_reward = None

        # ── Verdict ───────────────────────────────────────────────────────────
        if h_adj_reward is not None:
            better = "human" if h_adj_reward > ai_adj_reward else (
                "tie" if h_adj_reward == ai_adj_reward else "ai"
            )
        else:
            better = "ai"

        return {
            "task_id":   task.id,
            "task_name": task.name,
            "query":     query,
            "ai": {
                "response":   ai_response,
                "reward":     ai_adj_reward,
                "raw_reward": ai_result["reward"],
                "evaluation": {
                    "reward":    ai_adj_reward,
                    "breakdown": ai_result["breakdown"],
                    "feedback":  ai_result["feedback"],
                },
            },
            "human": {
                "response":   human_text or None,
                "reward":     h_adj_reward,
                "raw_reward": h_result["reward"] if h_result else None,
                "evaluation": {
                    "reward":    h_adj_reward,
                    "breakdown": h_result["breakdown"],
                    "feedback":  h_result["feedback"],
                } if h_result else None,
            } if human_text else None,
            "better": better,
            "policy": self._memory.policy.to_dict(),
        }


# Module-level singleton env for stateful /reset + /step endpoints
_env = ResponseArenaEnv()

def get_env() -> ResponseArenaEnv:
    return _env

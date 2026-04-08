"""
rl/policy.py — Advanced adaptive RL policy system.

Features:
  - Per-task independent policies
  - Experience replay buffer (500 items)
  - Reward shaping with learning bonus (current - previous score)
  - Epsilon-greedy weight exploration (ε=0.10)
  - Policy update every 10 steps (strongest-dimension upweighting)
  - Full persistence to /tmp/arena_memory.json
"""
from __future__ import annotations
import json
import random
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Optional

_MEMORY_PATH = Path("/tmp/arena_memory.json")
_MAX_BUFFER  = 500
_EPSILON     = 0.10   # exploration probability
_UPDATE_FREQ = 10     # rebalance every N records
_BLEND_NEW   = 0.20   # 20 % new signal, 80 % old weights
_DIM_FLOOR   = 0.10
_DIM_CAP     = 0.60

_DEFAULT_WEIGHTS = {"semantic": 0.40, "tone": 0.30, "structure": 0.30}

# All recognised task IDs — pre-populated so per-task policies exist from start
_ALL_TASKS = [
    "emotional_support", "professional_reply", "problem_solving",
    "casual_conversation", "conflict_resolution", "creative_writing",
    "decision_support", "customer_service",
]


class ReplayBuffer:
    """Fixed-size circular replay buffer."""

    def __init__(self, maxlen: int = _MAX_BUFFER):
        self._buf: deque = deque(maxlen=maxlen)

    def push(self, exp: Dict[str, Any]) -> None:
        exp["timestamp"] = time.time()
        self._buf.append(exp)

    def sample(self, n: int = 16) -> List[Dict[str, Any]]:
        n = min(n, len(self._buf))
        return random.sample(list(self._buf), n) if n > 0 else []

    def all(self) -> List[Dict[str, Any]]:
        return list(self._buf)

    def last_for_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Return the most recent experience for a given task, or None."""
        for exp in reversed(list(self._buf)):
            if exp.get("task_id") == task_id:
                return exp
        return None

    def __len__(self) -> int:
        return len(self._buf)


class TaskPolicy:
    """
    Per-task adaptive policy.

    Stores its own dimension weights and update counter independently of
    the global policy so tasks with different linguistic demands diverge.
    """

    def __init__(self, task_id: str, weights: Optional[Dict[str, float]] = None):
        self.task_id      = task_id
        self.weights      = dict(weights or _DEFAULT_WEIGHTS)
        self.update_count = 0
        self._dim_rewards: Dict[str, List[float]] = defaultdict(list)

    # ── Core reward computation ───────────────────────────────────────────────

    def compute_reward(
        self,
        breakdown: Dict[str, float],
        learning_bonus: float = 0.0,
    ) -> float:
        """
        Weighted reward + bounded learning bonus.
        reward = Σ(weight_i × score_i) + clamp(learning_bonus, −0.05, 0.10)
        """
        base = sum(self.weights.get(d, 0.0) * v for d, v in breakdown.items())
        bonus = max(-0.05, min(0.10, learning_bonus))
        return max(0.0, min(1.0, base + bonus))

    # ── Learning ──────────────────────────────────────────────────────────────

    def record(self, breakdown: Dict[str, float], reward: float) -> None:
        """Accumulate dimension-reward correlations; rebalance every N steps."""
        for dim, val in breakdown.items():
            self._dim_rewards[dim].append(reward * val)

        self.update_count += 1

        # Epsilon exploration: occasionally perturb weights
        if random.random() < _EPSILON:
            self._explore()

        if self.update_count % _UPDATE_FREQ == 0:
            self._rebalance()

    def _explore(self) -> None:
        """Small random perturbation of weights (±3 %) to encourage exploration."""
        dims = list(self.weights.keys())
        if len(dims) < 2:
            return
        d1, d2 = random.sample(dims, 2)
        delta = random.uniform(0.01, 0.03)
        self.weights[d1] = max(_DIM_FLOOR, min(_DIM_CAP, self.weights[d1] + delta))
        self.weights[d2] = max(_DIM_FLOOR, min(_DIM_CAP, self.weights[d2] - delta))
        self._normalise()

    def _rebalance(self) -> None:
        """Upweight the dimension with the best average reward correlation."""
        avgs = {d: (sum(v) / len(v)) for d, v in self._dim_rewards.items() if v}
        if not avgs:
            return
        total = sum(avgs.values()) or 1.0
        raw   = {d: v / total for d, v in avgs.items()}
        # Blend toward new signal
        for dim in self.weights:
            if dim in raw:
                self.weights[dim] = round(
                    (1.0 - _BLEND_NEW) * self.weights[dim] + _BLEND_NEW * raw[dim], 4
                )
        self._normalise()

    def _normalise(self) -> None:
        s = sum(self.weights.values()) or 1.0
        self.weights = {d: round(max(_DIM_FLOOR, min(_DIM_CAP, v / s)), 4)
                        for d, v in self.weights.items()}
        # Re-normalise after clamping
        s2 = sum(self.weights.values()) or 1.0
        if abs(s2 - 1.0) > 0.01:
            self.weights = {d: round(v / s2, 4) for d, v in self.weights.items()}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id":      self.task_id,
            "weights":      self.weights,
            "update_count": self.update_count,
        }


class RLMemory:
    """
    Central RL memory store.

    - One global replay buffer
    - Per-task policies (TaskPolicy)
    - Per-task evaluation history
    - JSON persistence
    """

    def __init__(self):
        self.buffer = ReplayBuffer()
        # Per-task policies
        self.task_policies: Dict[str, TaskPolicy] = {
            tid: TaskPolicy(tid) for tid in _ALL_TASKS
        }
        self._task_history: Dict[str, List[Dict]] = defaultdict(list)
        self._load()

    # ── Compatibility shim: expose `.policy` for existing callers ─────────────
    @property
    def policy(self) -> "GlobalPolicyShim":
        return GlobalPolicyShim(self.task_policies)

    # ── Public API ─────────────────────────────────────────────────────────────

    def record_eval(
        self,
        task_id:    str,
        query:      str,
        response:   str,
        actor:      str,
        breakdown:  Dict[str, float],
        raw_reward: float,
    ) -> float:
        """
        Store experience, compute shaped reward, update task policy.
        Returns policy-adjusted reward.
        """
        # Ensure policy exists (for any new task_id)
        if task_id not in self.task_policies:
            self.task_policies[task_id] = TaskPolicy(task_id)

        pol = self.task_policies[task_id]

        # Learning bonus: improvement over previous score on this task
        prev_exp = self.buffer.last_for_task(task_id)
        prev_reward = prev_exp.get("adj_reward", raw_reward) if prev_exp else raw_reward
        learning_bonus = raw_reward - prev_reward

        adj_reward = pol.compute_reward(breakdown, learning_bonus)
        pol.record(breakdown, raw_reward)

        # Store full experience
        exp = {
            "task_id":        task_id,
            "query":          query[:120],
            "response":       response[:200],
            "actor":          actor,
            "breakdown":      breakdown,
            "raw_reward":     raw_reward,
            "adj_reward":     round(adj_reward, 4),
            "learning_bonus": round(learning_bonus, 4),
        }
        self.buffer.push(exp)

        self._task_history[task_id].append({
            "actor":          actor,
            "reward":         round(adj_reward, 4),
            "raw_reward":     raw_reward,
            "breakdown":      breakdown,
            "learning_bonus": round(learning_bonus, 4),
        })
        # Cap history at 50 entries per task
        if len(self._task_history[task_id]) > 50:
            self._task_history[task_id] = self._task_history[task_id][-50:]

        self._save()
        return adj_reward

    def get_task_history(self, task_id: str) -> List[Dict]:
        return list(self._task_history.get(task_id, []))

    def get_stats(self) -> Dict[str, Any]:
        total = len(self.buffer)
        base  = {"total_evaluations": total, "policy": self.policy.to_dict()}
        if total == 0:
            return base

        all_exp    = self.buffer.all()
        avg_reward = sum(e.get("adj_reward", 0) for e in all_exp) / total

        task_avgs: Dict[str, float] = {}
        task_counts: Dict[str, int] = {}
        for e in all_exp:
            tid = e.get("task_id", "unknown")
            task_avgs[tid]   = task_avgs.get(tid, 0) + e.get("adj_reward", 0)
            task_counts[tid] = task_counts.get(tid, 0) + 1
        task_avgs = {t: round(task_avgs[t] / task_counts[t], 4) for t in task_avgs}

        recent = [e.get("adj_reward", 0) for e in all_exp[-20:]]

        return {
            **base,
            "average_reward": round(avg_reward, 4),
            "task_averages":  task_avgs,
            "reward_trend":   recent,
            "task_policies":  {tid: p.to_dict() for tid, p in self.task_policies.items()},
        }

    # ── Persistence ────────────────────────────────────────────────────────────

    def _save(self) -> None:
        try:
            data = {
                "buffer": self.buffer.all()[-200:],
                "task_history": dict(self._task_history),
                "task_policies": {
                    tid: {
                        "weights":       p.weights,
                        "update_count":  p.update_count,
                        "dim_rewards":   {k: v[-30:] for k, v in p._dim_rewards.items()},
                    }
                    for tid, p in self.task_policies.items()
                },
            }
            _MEMORY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _load(self) -> None:
        if not _MEMORY_PATH.exists():
            return
        try:
            data = json.loads(_MEMORY_PATH.read_text(encoding="utf-8"))
            for exp in data.get("buffer", []):
                self.buffer._buf.append(exp)
            for tid, hist in data.get("task_history", {}).items():
                self._task_history[tid] = hist
            for tid, pd in data.get("task_policies", {}).items():
                if tid not in self.task_policies:
                    self.task_policies[tid] = TaskPolicy(tid)
                p = self.task_policies[tid]
                if pd.get("weights"):
                    p.weights = pd["weights"]
                p.update_count = pd.get("update_count", 0)
                for k, v in pd.get("dim_rewards", {}).items():
                    p._dim_rewards[k] = v
        except Exception:
            pass


class GlobalPolicyShim:
    """
    Backwards-compatible shim that aggregates per-task policies
    into a single global view for the /stats and /policy endpoints.
    """

    def __init__(self, task_policies: Dict[str, TaskPolicy]):
        self._tp = task_policies

    @property
    def weights(self) -> Dict[str, float]:
        """Mean weights across all task policies."""
        dims = list(_DEFAULT_WEIGHTS.keys())
        avg  = {}
        for d in dims:
            vals = [p.weights.get(d, 0) for p in self._tp.values()]
            avg[d] = round(sum(vals) / len(vals), 4) if vals else _DEFAULT_WEIGHTS[d]
        return avg

    @property
    def update_count(self) -> int:
        return sum(p.update_count for p in self._tp.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "weights":      self.weights,
            "update_count": self.update_count,
        }


# Module-level singleton
_memory = RLMemory()

def get_memory() -> RLMemory:
    return _memory

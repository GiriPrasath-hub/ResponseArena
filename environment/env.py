# ================================================================
#  love_vH - environment/env.py
#  OpenEnv-compatible RL environment for the LOVE assistant.
#
#  Interface
#           
#    env.reset()          -> state: dict
#    env.step(action)     -> (next_state, reward, done, info)
#
#  State schema
#               
#    {
#      "user_message"  : str,
#      "mood"          : "happy" | "angry" | "confused",
#      "difficulty"    : "easy"  | "medium" | "hard",
#      "turn"          : int,
#      "context"       : list[dict],   # recent history
#    }
#
#  Action schema
#               
#    {
#      "response" : str,
#      "tone"     : "friendly" | "formal" | "helpful",
#    }
# ================================================================

from __future__ import annotations

from typing import Any

from core.config import EnvConfig, CFG
from environment.user_simulator import UserSimulator, UserMessage
from environment.task_manager import TaskManager
from environment.context_engine import ContextEngine, Turn
from reward.reward_system import RewardSystem
from openenv.grader import grade


class LoveEnv:
    """
    OpenEnv-compatible environment for training an AI assistant.

    Each episode presents a user scenario at a sampled difficulty
    level.  The agent submits text actions; the environment grades
    them, generates follow-up user messages, and returns the
    standard (next_state, reward, done, info) tuple.
    """

    metadata = {"render_modes": ["text"], "version": "vH"}

    def __init__(self, config: EnvConfig | None = None) -> None:
        self.cfg     = config or CFG
        self._sim    = UserSimulator()
        self._tasks  = TaskManager(self.cfg.difficulty_weights)
        self._ctx    = ContextEngine(self.cfg.memory_window)
        self._reward = RewardSystem(self.cfg)

        self._current_user_msg: UserMessage | None = None
        self._done = True

    #    OpenEnv API                                            

    def reset(self) -> dict[str, Any]:
        """
        Begin a new episode.

        Returns
        -------
        state : dict
            Initial observation for the agent.
        """
        task = self._tasks.new_episode()
        self._ctx.reset()
        self._done = False

        # Override initial message with task prompt (simulator remains for follow-ups)
        self._current_user_msg = UserMessage(
            message=task.input_prompt,
            mood="neutral",  # type: ignore[arg-type]
            difficulty=task.difficulty,
            topic=task.id,
            expected_keywords=list(task.required_keywords),
            turn=0,
        )

        return self._build_state(self._current_user_msg, turn=0)

    def step(self, action: dict[str, Any]) -> tuple[dict, float, bool, dict]:
        """
        Advance the environment by one turn.

        Parameters
        ----------
        action : dict with keys "response" (str) and "tone" (str)

        Returns
        -------
        next_state : dict
        reward     : float
        done       : bool
        info       : dict   (diagnostic data - not used for training)
        """
        if self._done or self._current_user_msg is None:
            # Auto-heal instead of crashing.
            self.reset()

        current_msg = self._current_user_msg
        if current_msg is None:
            # Final safety fallback (should not occur).
            current_msg = UserMessage(
                message="Hello",
                mood="neutral",  # type: ignore[arg-type]
                difficulty=self._tasks.current_difficulty,
                topic=self._tasks.current_task.id,
                expected_keywords=list(self._tasks.current_task.required_keywords),
                turn=self._tasks.turn,
            )
            self._current_user_msg = current_msg

        safe_action = action if isinstance(action, dict) else {}

        #    Grade the action                                   
        try:
            graded = grade(
                action=safe_action,
                user_msg=current_msg,
                context=self._ctx.get_context(),
                task=self._tasks.current_task,
            )
            result = graded.get("details", {})
            reward = float(graded.get("score", 0.0))
        except Exception:
            graded = {"score": 0.0, "details": {}}
            result = {}
            reward = 0.0

        reward = max(0.0, min(1.0, reward))
        correct = reward > 0.8

        turn = self._tasks.advance_turn()

        #    Record in context                                  
        self._ctx.record(Turn(
            turn_number  = turn,
            user_message = str(current_msg.message),
            agent_action = safe_action,
            reward       = reward,
            mood         = str(current_msg.mood),
            difficulty   = str(current_msg.difficulty),
        ))

        #    Check done                                         
        self._done = self._tasks.is_done(reward, correct)

        #    Generate next state                                
        if self._done:
            next_state = self._build_state(self._current_user_msg, turn=turn)
        else:
            try:
                self._current_user_msg = self._sim.follow_up(
                    prev           = current_msg,
                    agent_response = str(safe_action.get("response", "")),
                    turn           = turn,
                )
            except Exception:
                self._done = True
                self._current_user_msg = current_msg
            next_state = self._build_state(self._current_user_msg, turn=turn)

        info = {
            "reward_breakdown": result,
            "difficulty"      : self._tasks.current_difficulty,
            "episode"         : self._tasks.episode,
            "turn"            : turn,
            "episode_reward"  : self._ctx.episode_reward,
            "agent_quality"   : (
                "high" if reward >= 0.8 else
                "medium" if reward >= 0.5 else
                "low"
            ),
        }

        return next_state, reward, self._done, info

    #    Gym-style helpers                                      

    def render(self, mode: str = "text") -> None:
        """Print the current state to stdout."""
        if self._current_user_msg:
            print(
                f"[Env] Episode {self._tasks.episode} | "
                f"Turn {self._tasks.turn} | "
                f"Difficulty: {self._tasks.current_difficulty} | "
                f"Mood: {self._current_user_msg.mood}\n"
                f"  User: {self._current_user_msg.message}"
            )

    def close(self) -> None:
        """Clean up resources (no-op here, required by interface)."""
        pass

    @property
    def observation_space_keys(self) -> list[str]:
        return ["user_message", "mood", "difficulty", "turn", "context"]

    @property
    def action_space_keys(self) -> list[str]:
        return ["response", "tone"]

    #    Internal                                               

    def _build_state(self, msg: UserMessage, turn: int) -> dict[str, Any]:
        task = self._tasks.current_task
        return {
            "user_message"      : str(getattr(msg, "message", "")),
            "mood"              : str(getattr(msg, "mood", "neutral")),
            "difficulty"        : str(getattr(msg, "difficulty", self._tasks.current_difficulty)),
            "topic"             : str(getattr(msg, "topic", task.id)),
            "task_id"           : str(task.id),
            "expected_behavior" : str(task.expected_behavior),
            "turn"              : int(turn),
            "context"           : list(self._ctx.get_context()),
        }

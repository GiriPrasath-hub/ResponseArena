import os

from agent.response_generator import generate_response
from environment.task_manager import get_all_tasks, get_task
from openenv.grader import grade_response


def main() -> None:
    model_name = os.getenv("MODEL_NAME", "default-model")
    tasks = get_all_tasks()

    for task_info in tasks:
        task_name = str(task_info.get("name", "")).strip()
        if not task_name:
            continue

        task = get_task(task_name)
        queries = list(task_info.get("queries", []))

        for query in queries:
            input_text = str(query)
            response = generate_response(task_name, input_text)
            evaluation = grade_response(task, response)
            reward = float(evaluation.get("reward", evaluation.get("score", 0.0)))
            reward_str = f"{reward:.2f}"

            print(f"[START] task={task_name} env=ai_response_eval model={model_name}")
            print(f"[STEP] step=1 action=respond reward={reward_str} done=true error=null")
            print(f"[END] success=true steps=1 rewards={reward_str}")


if __name__ == "__main__":
    main()
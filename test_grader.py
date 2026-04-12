import traceback, yaml, importlib

d = yaml.safe_load(open("openenv.yaml"))

for t in d.get("tasks", []):
    gpath = t.get("grader", "MISSING")
    print("Task:", t.get("id"), "| grader:", gpath)

    try:
        mod, cls = str(gpath).rsplit(":", 1)
        score = float(getattr(importlib.import_module(mod), cls)().grade(None))

        if 0 < score < 1:
            print("  ->", score, "| OK")
        else:
            print("  ->", score, "| FAIL")

    except Exception:
        traceback.print_exc()
        print("  -> CRASHED (returns 0.0)")
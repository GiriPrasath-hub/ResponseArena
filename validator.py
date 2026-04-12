import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "https://giri0304-responcearena.hf.space"
TOTAL_TESTS = 50   # 🔥 change this (100, 200, etc.)

def find_bad_values(data, path="root", failures=None):
    if failures is None:
        failures = []

    # Ignore booleans
    if isinstance(data, bool):
        return failures

    if isinstance(data, dict):
        for k, v in data.items():
            find_bad_values(v, f"{path}.{k}", failures)

    elif isinstance(data, list):
        for i, v in enumerate(data):
            find_bad_values(v, f"{path}[{i}]", failures)

    elif isinstance(data, (int, float)):
        if data == 0 or data == 0.0 or data == 1 or data == 1.0:
            failures.append((path, data))

    return failures


def run_single_test(i):
    try:
        # Reset
        requests.post(f"{URL}/reset", json={"task_id": "casual_conversation"}, timeout=5)

        # Step
        res = requests.post(f"{URL}/step", json={
            "type": "respond",
            "human_content": ""
        }, timeout=5)

        data = res.json()

        failures = find_bad_values(data)

        if failures:
            return {
                "status": "fail",
                "test": i,
                "failures": failures,
                "response": data
            }

        return {"status": "pass", "test": i}

    except Exception as e:
        return {
            "status": "error",
            "test": i,
            "error": str(e)
        }


# 🚀 PARALLEL EXECUTION
print(f"\n⚡ Running {TOTAL_TESTS} tests in parallel...\n")

fail_found = False

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(run_single_test, i) for i in range(TOTAL_TESTS)]

    for future in as_completed(futures):
        result = future.result()

        if result["status"] == "fail":
            print("\n❌ FAILURE DETECTED!")
            print(f"Test #{result['test']}")
            print("Issues:")
            for path, val in result["failures"]:
                print(f"  {path} = {val}")

            print("\nFull Response:")
            print(json.dumps(result["response"], indent=2))

            fail_found = True
            break

        elif result["status"] == "error":
            print(f"⚠️ Error in test {result['test']}: {result['error']}")

        else:
            print(f"✅ Test {result['test']} passed")

if not fail_found:
    print("\n🎉 ALL TESTS PASSED — SAFE FOR SUBMISSION 🚀")
else:
    print("\n❌ Fix required before submission")
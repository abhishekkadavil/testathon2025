# tests/perf_test.py
import requests, time, json, os

base_url = "http://127.0.0.1:5000/employee"
results = []

for i in range(50):
    start = time.time()
    r = requests.post(base_url, json={"name": f"user{i}", "role": "dev"})
    elapsed = time.time() - start
    results.append({
        "iteration": i,
        "status_code": r.status_code,
        "elapsed": elapsed
    })

summary = {
    "avg_response_time": sum(r["elapsed"] for r in results) / len(results),
    "errors": sum(1 for r in results if r["status_code"] != 201),
    "total_requests": len(results)
}

os.makedirs("reports", exist_ok=True)
with open("reports/result.json", "w") as f:
    json.dump(summary, f, indent=2)

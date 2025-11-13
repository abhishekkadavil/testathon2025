import requests
import time
import statistics
import json
import sys
import os

BASE_URL = "http://127.0.0.1:5000"
ENDPOINTS = ["/employee", "/department"]

AVG_LATENCY_THRESHOLD = float(os.getenv("AVG_LATENCY_THRESHOLD", 0.1))
P95_LATENCY_THRESHOLD = float(os.getenv("P95_LATENCY_THRESHOLD", 0.0002))


def run_perf_test():
    results = {}
    for ep in ENDPOINTS:
        latencies = []
        for _ in range(10):
            start = time.time()
            try:
                res = requests.get(f"{BASE_URL}{ep}", timeout=5)
                res.raise_for_status()
                latencies.append(time.time() - start)
            except Exception as e:
                results[ep] = {"status": "FAIL", "error": str(e)}
                break

        if not latencies:
            results.setdefault(ep, {"status": "FAIL", "error": "No successful responses"})
            continue

        avg_latency = statistics.mean(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18]

        status = "PASS"
        if avg_latency > AVG_LATENCY_THRESHOLD or p95 > P95_LATENCY_THRESHOLD:
            status = "FAIL"

        results[ep] = {
            "avg_latency": round(avg_latency, 3),
            "p95": round(p95, 3),
            "status": status,
        }

    return results


if __name__ == "__main__":
    results = run_perf_test()

    # ✅ Always write results before exiting
    with open("perf_results.json", "w") as f:
        json.dump(results, f, indent=2)

    with open("results_perf_test.txt", "w") as f:
        for ep, data in results.items():
            f.write(f"{ep}: {data}\n")

    print(json.dumps(results, indent=2))

    # ✅ Determine if the build should fail
    failed = any(r["status"] != "PASS" for r in results.values())

    if failed:
        print("❌ Performance threshold not met. Failing build.")
        sys.exit(1)
    else:
        print("✅ All performance tests passed.")
    

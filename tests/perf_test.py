import requests
import time
import statistics

BASE_URL = "http://127.0.0.1:5000"  # Adjust if your API runs elsewhere
ENDPOINTS = ["/", "/health", "/status"]  # Default, updated dynamically later

def run_perf_test():
    results = {}
    for ep in ENDPOINTS:
        latencies = []
        for _ in range(10):
            start = time.time()
            res = requests.get(f"{BASE_URL}{ep}")
            latencies.append(time.time() - start)
        results[ep] = {
            "avg_latency": round(statistics.mean(latencies), 3),
            "p95": round(statistics.quantiles(latencies, n=20)[18], 3),
            "status": "PASS" if all(l < 1 for l in latencies) else "WARN"
        }
    return results

if __name__ == "__main__":
    import json
    results = run_perf_test()
    with open("perf_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("✅ Performance test complete. Results saved to perf_results.json")

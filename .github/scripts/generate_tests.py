import os
import subprocess
import requests
from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# ---- STEP 1: Fetch PR diff ----
diff_url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3.diff"}
diff_text = requests.get(diff_url, headers=headers).text

# ---- STEP 2: Generate PERFORMANCE tests ----
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a backend performance engineer. "
                "Generate lightweight Python pytest tests that measure API latency "
                "for the Flask endpoints modified in this PR diff. "
                "Each test should use time.perf_counter() to measure execution time "
                "and assert that the response time is below a reasonable threshold "
                "(e.g., 100–200ms). Avoid functional assertions (no checking response content)."
            ),
        },
        {
            "role": "user",
            "content": f"Here is the Pull Request diff:\n\n{diff_text}"
        }
    ]
)

unit_tests = response.choices[0].message.content

# ---- STEP 3: Save tests ----
test_file_path = "generated_perf_test.py"
with open(test_file_path, "w") as f:
    f.write(unit_tests)

# ---- STEP 4: Run pytest ----
try:
    result = subprocess.run(
        ["pytest", "-v", test_file_path, "--maxfail=3", "--disable-warnings"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    test_output = result.stdout + "\n\n" + result.stderr
except Exception as e:
    test_output = f"Error running pytest: {e}"

# ---- STEP 5: Comment results on PR ----
comment_body = f"""
### 🚀 Suggested Performance Tests

```python
{unit_tests}

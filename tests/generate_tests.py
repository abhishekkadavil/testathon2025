import os
import requests
from openai import OpenAI

api_key = os.getenv("OPENROUTER_API_KEY")
repo = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")
gh_token = os.getenv("GITHUB_TOKEN")

# --- Fetch PR diff ---
pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
headers = {"Authorization": f"token {gh_token}"}
pr_data = requests.get(pr_url, headers=headers).json()
diff_link = pr_data.get("diff_url")
diff_text = requests.get(diff_link, headers=headers).text

# --- Ask OpenRouter to generate new performance tests ---
prompt = f"""
Analyze the GitHub Pull Request diff below.
If new Flask or FastAPI endpoints are added or changed, generate corresponding **performance test cases**.

Guidelines for each test:
- Use Python with the `requests` and `time` modules (no external dependencies).
- Simulate at least 100 requests per endpoint.
- Measure average response time, 95th percentile, and number of failed requests.
- Print summary metrics to stdout.
- Do NOT include functional assertions; focus purely on performance measurement.

Return only valid Python code for performance tests.

DIFF:
{diff_text}
"""

client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

response = client.chat.completions.create(
    model="qwen/qwen3-coder:free",
    messages=[
        {"role": "system", "content": "You are a professional performance test generator for REST APIs."},
        {"role": "user", "content": prompt}
    ]
)

test_code = response.choices[0].message.content.strip()

# --- Save the generated performance test file ---
os.makedirs("tests/generated", exist_ok=True)
test_file = "tests/generated/perf_auto.py"

with open(test_file, "w") as f:
    f.write(test_code)

print(f"✅ Generated performance test file: {test_file}")

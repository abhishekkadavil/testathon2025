import os
import json
import requests
from openai import OpenAI

api_key = os.getenv("OPENROUTER_API_KEY")
repo = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")
gh_token = os.getenv("GITHUB_TOKEN")

with open("perf_results.json") as f:
    perf_data = json.load(f)

prompt = f"""
You are an expert performance engineer.
Analyze the following API performance data and summarize:
- Which endpoints are fast or slow
- Any anomalies or spikes
- Give short, actionable feedback

Data:
{json.dumps(perf_data, indent=2)}
"""

client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

response = client.chat.completions.create(
    model="qwen/qwen3-coder:free",
    messages=[
        {"role": "system", "content": "You are an expert performance reviewer."},
        {"role": "user", "content": prompt}
    ]
)

review_comment = response.choices[0].message.content.strip()

# --- Post to GitHub PR ---
comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
requests.post(
    comment_url,
    headers={"Authorization": f"token {gh_token}"},
    json={"body": f"### 🤖 AI Performance Review\n\n{review_comment}"}
)

print("✅ Posted AI Performance Review to PR")

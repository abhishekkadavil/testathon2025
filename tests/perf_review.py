# tests/perf_review.py
import json, os, requests
from openai import OpenAI

api_key = os.getenv("OPENROUTER_API_KEY")
gh_token = os.getenv("GITHUB_TOKEN")
pr_number = os.getenv("PR_NUMBER")
repo = os.getenv("GITHUB_REPOSITORY")

client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

with open("reports/result.json") as f:
    perf = json.load(f)

prompt = f"""
Performance test results:
{json.dumps(perf, indent=2)}

Please review these results and:
1. Analyze API performance and potential bottlenecks.
2. Suggest improvements for throughput and latency.
3. Mention whether these results are acceptable for a small Flask API.
"""

response = client.chat.completions.create(
    model="mistralai/mistral-7b-instruct:free",
    messages=[
        {"role": "system", "content": "You are a performance engineering expert reviewing API metrics."},
        {"role": "user", "content": prompt}
    ]
)

review = response.choices[0].message.content

comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
requests.post(
    comment_url,
    json={"body": review},
    headers={
        "Authorization": f"token {gh_token}",
        "Accept": "application/vnd.github+json"
    }
)

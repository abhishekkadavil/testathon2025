import os
import json
import re
import requests
from openai import OpenAI

# --- Environment variables from GitHub Actions ---
api_key = os.getenv("OPENROUTER_API_KEY")
gh_token = os.getenv("GITHUB_TOKEN")
repo = os.getenv("GITHUB_REPOSITORY")              # e.g. "user/repo"
pr_number = os.getenv("PR_NUMBER")                 # provided in workflow env

# --- Helper: escape markdown so AI output doesn’t get striked/bolded ---
def escape_markdown(text: str) -> str:
    return re.sub(r'([*_~`])', r'\\\1', text)

# --- Load performance results ---
with open("reports/result.json") as f:
    perf = json.load(f)

# --- Prepare AI prompt ---
prompt = f"""
Performance test results:
{json.dumps(perf, indent=2)}

Please analyze and provide:
1. Bottlenecks or inefficiencies.
2. Suggestions to improve response time or throughput.
3. Whether results are acceptable for a small Flask API.
"""

# --- Call OpenRouter model ---
client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

response = client.chat.completions.create(
    model="mistralai/mistral-7b-instruct:free",
    messages=[
        {"role": "system", "content": "You are a senior performance testing engineer reviewing Flask API metrics."},
        {"role": "user", "content": prompt}
    ]
)

review = response.choices[0].message.content

# --- Wrap AI output in code block to avoid markdown rendering issues ---
safe_review = f"```\n{escape_markdown(review)}\n```"

# --- Post comment to the GitHub PR ---
comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

response = requests.post(
    comment_url,
    headers={
        "Authorization": f"token {gh_token}",
        "Accept": "application/vnd.github+json"
    },
    json={"body": safe_review}
)

if response.status_code in (200, 201):
    print("✅ Posted AI performance review comment to PR successfully.")
else:
    print(f"⚠️ Failed to post comment. Status: {response.status_code}")
    print(response.text)

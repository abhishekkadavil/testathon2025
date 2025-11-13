import os
import json
import re
import requests
from openai import OpenAI

# --- Environment variables from GitLab CI ---
api_key = os.getenv("OPENROUTER_API_KEY")
project_path = os.getenv("CI_PROJECT_PATH")          # e.g., "username/my-flask-api"
mr_iid = os.getenv("CI_MERGE_REQUEST_IID")          # Merge Request internal ID
gitlab_token = os.getenv("GITLAB_TOKEN") or os.getenv("CI_JOB_TOKEN")  # prefer personal token, fallback to CI token
gitlab_api_url = os.getenv("CI_API_V4_URL", "https://gitlab.com/api/v4")

# --- Helper: escape markdown so AI output doesn’t get striked/bolded ---
def escape_markdown(text: str) -> str:
    return re.sub(r'([*_~`])', r'\\\1', text)

# --- Load performance results ---
with open("reports/result.json") as f:
    perf = json.load(f)

# --- Prepare the AI prompt ---
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

# --- Wrap in code block to preserve formatting ---
safe_review = f"```\n{escape_markdown(review)}\n```"

# --- Post comment to the Merge Request ---
comment_url = f"{gitlab_api_url}/projects/{project_path.replace('/', '%2F')}/merge_requests/{mr_iid}/notes"

response = requests.post(
    comment_url,
    headers={
        "PRIVATE-TOKEN": gitlab_token,
        "Content-Type": "application/json"
    },
    json={"body": safe_review}
)

if response.status_code == 201:
    print("✅ Posted AI performance review comment to MR successfully.")
else:
    print(f"⚠️ Failed to post comment. Status: {response.status_code}")
    print(response.text)

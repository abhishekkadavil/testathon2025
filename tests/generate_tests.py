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

# --- Ask OpenRouter to generate new tests ---
prompt = f"""
Analyze the GitHub Pull Request diff below.
If new Flask or FastAPI endpoints are added or changed, generate corresponding pytest test cases
that use the `requests` library to validate these endpoints.

Return only valid Python test code.

DIFF:
{diff_text}
"""

client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

response = client.chat.completions.create(
    model="qwen/qwen3-coder:free",
    messages=[
        {"role": "system", "content": "You are a professional Python test generator for REST APIs."},
        {"role": "user", "content": prompt}
    ]
)

test_code = response.choices[0].message.content.strip()

# --- Save the generated test file ---
os.makedirs("tests/generated", exist_ok=True)
test_file = "tests/generated/test_auto.py"

with open(test_file, "w") as f:
    f.write(test_code)

print(f"✅ Generated test file: {test_file}")

import os
import requests
from openai import OpenAI

api_key = os.getenv("OPENROUTER_API_KEY")
repo = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")
gh_token = os.getenv("GITHUB_TOKEN")

# --- Get PR diff from GitHub API ---
diff_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
headers = {"Authorization": f"token {gh_token}"}
pr_data = requests.get(diff_url, headers=headers).json()
diff_link = pr_data.get("diff_url")
diff_text = requests.get(diff_link, headers=headers).text

# --- Ask the LLM to generate new tests ---
prompt = f"""
Analyze the following GitHub Pull Request diff.
If new Flask API endpoints are added or modified, generate Python test code 
(using 'requests' library) that tests these endpoints.

Respond with valid Python code only — no explanations.

DIFF:
{diff_text}
"""

client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

response = client.chat.completions.create(
    model="mistralai/mistral-7b-instruct:free",
    messages=[
        {"role": "system", "content": "You are an expert Python test generator for Flask APIs."},
        {"role": "user", "content": prompt}
    ]
)

test_code = response.choices[0].message.content.strip()

# --- Write generated tests to a new file ---
os.makedirs("tests/generated", exist_ok=True)
with open("tests/generated/test_auto.py", "w") as f:
    f.write(test_code)

print("✅ Generated new/updated test file at tests/generated/test_auto.py")

import os
import requests
from openai import OpenAI

# ---- CONFIGURATION ----
API_KEY = os.getenv("OPENROUTER_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# ---- STEP 1: FETCH PR DIFF ----
diff_url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3.diff"}
diff_text = requests.get(diff_url, headers=headers).text

# ---- STEP 2: GENERATE UNIT TESTS ----
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a senior backend engineer specializing in REST API testing. "
                "Generate Python unit tests for the modified Flask endpoints in this PR diff. "
                "Use pytest and Flask’s test client. Include tests for success and failure cases."
            ),
        },
        {
            "role": "user",
            "content": f"Here is the Pull Request diff:\n\n{diff_text}"
        }
    ]
)

unit_tests = response.choices[0].message.content
print(unit_tests)

# ---- STEP 3: COMMENT ON PR ----
comment = {
    "body": f"### 🤖 Suggested Unit Tests\n\n{unit_tests}"
}
requests.post(
    f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments",
    headers={"Authorization": f"token {GITHUB_TOKEN}"},
    json=comment
)

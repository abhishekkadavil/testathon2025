import os
import json
import requests
from openai import OpenAI
from github import Github, Auth

api_key = os.getenv("OPENROUTER_API_KEY")
repo_name = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")
gh_token = os.getenv("GITHUB_TOKEN")
ai_model = os.getenv("OPENROUTER_MODEL")

# --- GitHub client ---
gh = Github(auth=Auth.Token(gh_token))
repo = gh.get_repo(repo_name)
pr = repo.get_pull(int(pr_number))

# --- Get diff ---
diff = pr.get_files()
changes = "\n".join([
    f"{f.filename}\n{f.patch or ''}"
    for f in diff
])

prompt = f"""
You are an expert in software performance optimization.

Review the following pull request diff and provide ONLY:

- Performance bottlenecks
- Inefficient patterns
- High-complexity code paths
- Memory or CPU inefficiencies
- Redundant operations
- Opportunities for algorithmic or structural optimization
- Line-specific performance comments

Do NOT comment on:
- security
- style
- formatting
- documentation
- naming
- general code quality

Focus strictly on performance.

Diff:
{changes}
"""

client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

response = client.chat.completions.create(
    model=ai_model,
    messages=[
        {"role": "system", "content": "You are an expert performance reviewer."},
        {"role": "user", "content": prompt}
    ]
)

review_comment = response.choices[0].message.content

# --- Post to GitHub PR ---
comment_url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"

requests.post(
    comment_url,
    headers={"Authorization": f"token {gh_token}"},
    json={"body": f"### 🤖 AI Performance Review\n\n{review_comment}"}
)

print("✅ Posted AI Performance Review to PR")

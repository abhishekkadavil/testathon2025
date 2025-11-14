import os
import requests
from pathlib import Path

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
AI_MODEL = os.getenv("OPENROUTER_MODEL")

if not OPENROUTER_API_KEY:
    raise Exception("OPENROUTER_API_KEY is missing")

APP_FILE = "app.py"
TARGET_FILE = Path("src/test/scala/ai/GeneratedSimulation.scala")
TARGET_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(APP_FILE, "r") as f:
    app_code = f.read()

prompt = f"""
Analyze this Flask API code and extract all REST endpoints:

{app_code}

Now generate a Gatling Scala Simulation that:
- Tests every GET endpoint
- Tests POST /employee with a sample JSON body
- Uses constantUsersPerSec(3) for 5 seconds
- Asserts success > 90%

Return ONLY valid Scala code.
"""

url = "https://openrouter.ai/api/v1/chat/completions"

payload = {
    "model": AI_MODEL,
    "messages": [
        {"role": "user", "content": prompt}
    ]
}

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://github.com/your_repo",
    "X-Title": "Gatling Test Generator"
}

response = requests.post(url, json=payload, headers=headers)
response.raise_for_status()

scala_code = response.json()["choices"][0]["message"]["content"].strip()

# REMOVE markdown fences if present
if scala_code.startswith("```scala"):
    scala_code = scala_code.split("```scala")[1]  # remove first fence
    scala_code = scala_code.replace("```", "").strip()  # remove closing fence

TARGET_FILE.write_text(scala_code)

print(f"Generated AI Gatling test at: {TARGET_FILE}")

import openai
import os
from pathlib import Path


openai.api_key  = os.getenv("OPENROUTER_API_KEY")
ai_model = os.getenv("OPENROUTER_MODEL")


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

response = openai.chat.completions.create(
    model=ai_model,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2
)

scala_code = response.choices[0].message.content.strip()
TARGET_FILE.write_text(scala_code)

print(f"Generated AI Gatling test at: {TARGET_FILE}")

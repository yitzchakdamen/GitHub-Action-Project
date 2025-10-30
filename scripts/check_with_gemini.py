import os
import requests
import json
import subprocess
import logging
from datetime import datetime

# --- Configure logging ---
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

logging.info("🚀 Gemini Code Check process started.")

# --- Environment variables ---
try:
    gemini_key = os.environ["GEMINI_API_KEY"]
    github_token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    sha = os.environ["GITHUB_SHA"]
    logging.debug(f"Environment variables loaded successfully {locals()}.")
except KeyError as e:
    logging.critical(f"❌ Missing environment variable: {e}")
    exit(1)

# --- Find changed Python files ---
logging.info("🔍 Detecting changed Python files...")
result = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True)
logging.debug(f"Git diff output:\n{result.stdout}")

current_script = os.path.relpath(__file__)
changed_files = [
    f for f in result.stdout.splitlines()
    if f.endswith(".py") and f != current_script
]

if not changed_files:
    logging.info("✅ No Python files changed. Exiting.")
    exit(0)

logging.info(f"🧩 Changed Python files: {changed_files}")

# --- Function: Send code to Gemini for validation ---
def check_with_gemini(filename):
    logging.info(f"📤 Sending {filename} to Gemini for analysis...")
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    prompt = f"""
    You are a code reviewer. Analyze this Python code and return a JSON object with:
    - valid: true/false
    - errors: a list of objects, each with 'line' and 'message'
    Check the following code:
    {code}
    """

    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent",
            headers={"Content-Type": "application/json"},
            params={"key": gemini_key},
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
        response.raise_for_status()
        logging.debug(f"Gemini raw response for {filename}: {response.text[:500]}...")
        return response.json()
    except Exception as e:
        logging.error(f"❌ Failed to communicate with Gemini API for {filename}: {e}")
        return None

# --- Check each changed file ---
issues = []

for file in changed_files:
    logging.info(f"🧠 Checking file: {file}")
    result = check_with_gemini(file)
    if not result:
        continue

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        data = json.loads(text)
        if not data.get("valid", True):
            logging.warning(f"⚠️ Issues found in {file}")
            issues.append((file, data.get("errors", [])))
        else:
            logging.info(f"✅ {file} passed Gemini validation.")
    except Exception as e:
        logging.error(f"❌ Error parsing Gemini response for {file}: {e}")

# --- If issues found, create a GitHub issue ---
if issues:
    logging.info("🚨 Issues detected. Creating GitHub issue...")
    issue_body = "### Issues found in the submitted code:\n"
    for file, errs in issues:
        issue_body += f"\n#### 📝 {file}\n"
        for err in errs:
            issue_body += f"- Line {err.get('line', '?')}: {err.get('message', 'Unknown error')}\n"

    issue_data = {
        "title": f"Issues found in commit {sha[:7]}",
        "body": issue_body
    }

    try:
        r = requests.post(
            f"https://api.github.com/repos/{repo}/issues",
            headers={
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github+json"
            },
            json=issue_data
        )
        r.raise_for_status()
        logging.info("🪶 GitHub issue created successfully.")
    except Exception as e:
        logging.critical(f"❌ Failed to create GitHub issue: {e}")

    exit(1)
else:
    logging.info("🎉 All code passed Gemini validation.")
    exit(0)

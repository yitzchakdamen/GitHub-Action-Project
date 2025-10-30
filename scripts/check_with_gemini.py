import os
import requests
import json
import subprocess


gemini_key = os.environ["GEMINI_API_KEY"]
github_token = os.environ["GITHUB_TOKEN"]
repo = os.environ["GITHUB_REPOSITORY"]
sha = os.environ["GITHUB_SHA"]


result = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True)
changed_files = [f for f in result.stdout.splitlines() if f.endswith(".py")]

if not changed_files:
    print("No Python files changed.")
    exit(0)

# --- פונקציה לבדוק קובץ עם Gemini ---
def check_with_gemini(filename):
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    prompt = f"""
    אתה בודק קוד פייתון. החזר JSON עם:
    - valid: true/false
    - errors: רשימת שגיאות עם שורה והסבר
    בדוק את הקוד הבא:
    {code}
    """

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent",
        headers={"Content-Type": "application/json"},
        params={"key": gemini_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
    )

    return response.json()

# --- בדיקת כל הקבצים ששונו ---
issues = []

for file in changed_files:
    print(f"Checking {file}...")
    result = check_with_gemini(file)

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        data = json.loads(text)
        if not data.get("valid", True):
            issues.append((file, data.get("errors", [])))
    except Exception as e:
        print(f"Error parsing Gemini response for {file}: {e}")

# --- אם נמצאו בעיות, צור Issue חדש ---
if issues:
    issue_body = "### בעיות שהתגלו בקוד:\n"
    for file, errs in issues:
        issue_body += f"\n#### 📄 {file}\n"
        for err in errs:
            issue_body += f"- שורה {err.get('line', '?')}: {err.get('message', 'שגיאה לא ידועה')}\n"

    issue_data = {
        "title": f"שגיאות בקוד שנשלח ב־commit {sha[:7]}",
        "body": issue_body
    }

    requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github+json"
        },
        json=issue_data
    )

    print("❌ Found issues, created GitHub Issue.")
    exit(1)
else:
    print("✅ All code passed Gemini check.")
    exit(0)


import os
import requests
import json
import subprocess

# --- Environment variables ---
gemini_key = os.environ["GEMINI_API_KEY"]
github_token = os.environ["GITHUB_TOKEN"]
repo = os.environ["GITHUB_REPOSITORY"]
sha = os.environ["GITHUB_SHA"]

# --- Find changed Python files ---
result = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True)
changed_files = [f for f in result.stdout.splitlines() if f.endswith(".py")]

if not changed_files:
    print("No Python files changed.")
    exit(0)

# --- Function: Send code to Gemini for validation ---
def check_with_gemini(filename):
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    prompt = f"""
    You are a code reviewer. Analyze this Python code and return a JSON object with:
    - valid: true/false
    - errors: a list of objects, each with 'line' and 'message'
    Check the following code:
    {code}
    """

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent",
        headers={"Content-Type": "application/json"},
        params={"key": gemini_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
    )

    return response.json()

# --- Check each changed file ---
issues = []

for file in changed_files:
    print(f"Checking {file}...")
    result = check_with_gemini(file)

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        data = json.loads(text)
        if not data.get("valid", True):
            issues.append((file, data.get("errors", [])))
    except Exception as e:
        print(f"Error parsing Gemini response for {file}: {e}")

# --- If issues found, create a GitHub issue ---
if issues:
    issue_body = "### Issues found in the submitted code:\n"
    for file, errs in issues:
        issue_body += f"\n#### 📝 {file}\n"
        for err in errs:
            issue_body += f"- Line {err.get('line', '?')}: {err.get('message', 'Unknown error')}\n"

    issue_data = {
        "title": f"Issues found in commit {sha[:7]}",
        "body": issue_body
    }

    requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github+json"
        },
        json=issue_data
    )

    print("❌ Issues detected. GitHub issue created.")
    exit(1)
else:
    print("✅ All code passed the Gemini validation.")
    exit(0)

import requests
import json
import argparse
import re

# 1. Parse arguments (read filename from the command line)
parser = argparse.ArgumentParser(description="Turn a git diff into a Conventional Commit + Changelog")
parser.add_argument("input_file", help="path to the .diff or .txt file to analyze")
parser.add_argument("-o", "--output", default="result.md", help="output filename (default: result.md)")
args = parser.parse_args()

input_file = args.input_file
output_file = args.output
model_name = "gemma2:2b"

# 2. Read the diff content
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        diff_content = f.read()
except FileNotFoundError:
    print(f"Error: file '{input_file}' not found. Please check the path.")
    exit()

# Guard against empty files: if there is nothing left after stripping whitespace, stop
if not diff_content.strip():
    print(f"Error: file '{input_file}' is empty, there is no diff to analyze.")
    exit()

# 3. Build the prompt for the model
prompt = f"""You are a Git assistant. Analyze the git diff below and produce exactly two sections.

RULES:
- The commit "type" MUST be one of: feat, fix, docs, refactor, test, chore
- Commit format MUST be: type(scope): description
  - scope = the affected module/file (lowercase, no extension)
  - description = lowercase, imperative verb, short, NO trailing period
- Output raw markdown only. Do NOT add greetings, explanations, or phrases like "Sure, here is".

EXAMPLE
Input diff:
--- a/app.py
+++ b/app.py
@@ -10,4 +10,4 @@ def main():
-    print("Hello World")
+    print("Hello Hackathon Team")

Correct output:
## Commit Message
chore(app): update greeting message to welcome hackathon team
## Changelog
- Changed greeting text from "Hello World" to "Hello Hackathon Team"

YOUR OUTPUT FORMAT (follow exactly):
## Commit Message
<one single conventional commit line>
## Changelog
- <bullet point describing the change>

DIFF TO ANALYZE:
{diff_content}
"""

# 4. Call the Ollama API
url = "http://localhost:11434/api/generate"
payload = {
    "model": model_name,
    "prompt": prompt,
    "stream": False
}

print(f"Reading {input_file} and contacting Gemma, please wait...")
try:
    response = requests.post(url, json=payload, timeout=120)
except requests.exceptions.ConnectionError:
    print("Error: cannot reach Ollama. Make sure `ollama serve` is running and gemma2:2b is installed.")
    exit()
except requests.exceptions.Timeout:
    print("Error: timed out waiting for Gemma (120s). The diff may be too large, try a smaller one.")
    exit()

if response.status_code == 200:
    result = response.json()
    ai_response = result['response'].strip()

    # 5. Print the result to the terminal (the challenge requires printing markdown)
    print("\n" + "=" * 40)
    print(ai_response)
    print("=" * 40 + "\n")

    # 6. Validate that the commit line is a valid Conventional Commit
    #    Rule: type(scope): description, where type is restricted to the allowed set
    pattern = r"^(feat|fix|docs|refactor|test|chore)(\([\w\-]+\))?: .+"
    commit_lines = [ln.strip() for ln in ai_response.splitlines()
                    if re.match(pattern, ln.strip())]
    if commit_lines:
        print(f"OK - format validation passed: {commit_lines[0]}")
    else:
        print("WARNING: no valid Conventional Commit line found, please review the output manually.")

    # 7. Save the result to a file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(ai_response)
    print(f"Done! Result saved to {output_file}")
else:
    print(f"Error: Ollama returned a non-200 status code: {response.status_code}")
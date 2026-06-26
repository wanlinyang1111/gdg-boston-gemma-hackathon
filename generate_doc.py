import requests
import argparse
import re

MODEL_NAME = "gemma2:2b"
OLLAMA_URL = "http://localhost:11434/api/generate"
COMMIT_PATTERN = r"^(feat|fix|docs|refactor|test|chore)(\([\w\-]+\))?: .+"


def build_prompt(diff_content):
    """Wrap a git diff in the structured prompt that keeps Gemma on-format."""
    return f"""You are a Git assistant. Analyze the git diff below and produce exactly two sections.

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


def call_gemma(prompt, model_name=MODEL_NAME, timeout=120):
    """Send the prompt to the local Gemma model via Ollama and return the text.

    Raises RuntimeError with a friendly message on any failure so callers
    (the CLI or the git hook) can decide how to handle it.
    """
    payload = {"model": model_name, "prompt": prompt, "stream": False}
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("cannot reach Ollama. Make sure `ollama serve` is running and gemma2:2b is installed.")
    except requests.exceptions.Timeout:
        raise RuntimeError(f"timed out waiting for Gemma ({timeout}s). The diff may be too large, try a smaller one.")

    if response.status_code != 200:
        raise RuntimeError(f"Ollama returned a non-200 status code: {response.status_code}")

    return response.json()["response"].strip()


def extract_commit_line(text):
    """Return the first valid Conventional Commit line in the text, or None."""
    for line in text.splitlines():
        line = line.strip()
        if re.match(COMMIT_PATTERN, line):
            return line
    return None


def main():
    parser = argparse.ArgumentParser(description="Turn a git diff into a Conventional Commit + Changelog")
    parser.add_argument("input_file", help="path to the .diff or .txt file to analyze")
    parser.add_argument("-o", "--output", default="result.md", help="output filename (default: result.md)")
    args = parser.parse_args()

    # 1. Read the diff content
    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            diff_content = f.read()
    except FileNotFoundError:
        print(f"Error: file '{args.input_file}' not found. Please check the path.")
        return

    # Guard against empty files
    if not diff_content.strip():
        print(f"Error: file '{args.input_file}' is empty, there is no diff to analyze.")
        return

    # 2. Build the prompt and call Gemma
    print(f"Reading {args.input_file} and contacting Gemma, please wait...")
    try:
        ai_response = call_gemma(build_prompt(diff_content))
    except RuntimeError as e:
        print(f"Error: {e}")
        return

    # 3. Print the result to the terminal (the challenge requires printing markdown)
    print("\n" + "=" * 40)
    print(ai_response)
    print("=" * 40 + "\n")

    # 4. Validate the commit line
    commit_line = extract_commit_line(ai_response)
    if commit_line:
        print(f"OK - format validation passed: {commit_line}")
    else:
        print("WARNING: no valid Conventional Commit line found, please review the output manually.")

    # 5. Save the result to a file
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(ai_response)
    print(f"Done! Result saved to {args.output}")


if __name__ == "__main__":
    main()

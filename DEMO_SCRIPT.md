# Demo Script — Automagic Documenter (Git-to-Doc)

> GDG Cloud Boston x Northeastern University Hackathon — Powered by Gemma
> Track 1: AI-First Developer Efficiencies
> Target length: ~2.5 minutes. Speak the **bold** lines; do the *(italic)* actions.

---

## 0. Setup BEFORE you present （上台前先做好，不要現場才開）
- [ ] `ollama serve` is running (確認 Ollama 有開)
- [ ] Terminal is in the project folder: `cd ~/Desktop/hack0626`
- [ ] Font size is big enough for the room (terminal 字放大)
- [ ] Clear the screen: `clear`

---

## 1. The Hook — the friction (~20s)

**"Every developer here has written a commit message like 'fixed stuff' at 2am.**
**And we almost never update the changelog. Bad commit history makes code reviews and debugging painful."**

**"So we built a tiny command-line tool that fixes this — using a *local* Gemma model. No cloud, no API keys, no data leaving your laptop."**

---

## 2. What it does — one sentence (~15s)

**"You give it a raw git diff. It returns a perfectly formatted Conventional Commit message and a markdown changelog. That's it. Pure plumbing — no UI."**

---

## 3. Live Demo (~60s)

*(跑第一個指令 — 簡單範例)*
```bash
python3 generate_doc.py sample.diff
```
**"Here's a simple change. Gemma reads the diff and gives us a clean `type(scope): description` commit, plus a changelog bullet."**

*(跑第二個指令 — 沒看過的真實 diff，這是重點)*
```bash
python3 generate_doc.py test_real.diff
```
**"Now a diff it has never seen — a real bug fix across two files. Watch: it correctly picks `fix`, scopes it to `parser`, and describes exactly what changed. It actually understood the code, it didn't just copy a template."**

---

## 4. Why it's robust — the engineering (~30s)

**"Three things make this judge-ready, not just a toy:"**

1. **"A strict prompt — we restrict the commit type to the six valid ones and give a few-shot example, so a small 2B model stays on format."**
2. **"A regex validator — if the model ever drifts off the Conventional Commit spec, the tool flags it instead of silently passing bad output."**

*(可現場示範 edge case — 空檔案被擋)*
```bash
python3 generate_doc.py nope.diff
```
3. **"And it's hardened — missing files, empty files, Ollama being offline, timeouts — all handled with clear messages instead of a crash."**

---

## 5. Close (~15s)

**"It's one self-contained Python script, runs fully offline on Gemma, and it's already on GitHub. It turns the worst part of every commit into something automatic."**

**"Thank you — happy to take questions."**

*(打開 repo 頁面備用)*
> https://github.com/wanlinyang1111/gdg-boston-gemma-hackathon

---

## Q&A — likely questions & answers

**Q: Why local Gemma instead of GPT/Claude API?**
A: Privacy and zero cost — your code never leaves the machine, no API key, works offline. Perfect for proprietary codebases.

**Q: The 2B model isn't always perfect — what if it gives a wrong type?**
A: That's exactly why we added the regex validator. It catches drift and warns. Next step would be an automatic retry on invalid output.

**Q: How does it scale to big diffs?**
A: We set a 120s timeout and the prompt is structured. For very large PRs you'd chunk the diff per-file — a natural extension.

**Q: Could this run in CI / a git hook?**
A: Yes — it's a plain CLI that reads a file and prints markdown, so it drops straight into a pre-commit hook or a CI step.

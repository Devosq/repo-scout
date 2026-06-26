# 🔭 Repo Scout

> Find GitHub repos worth your attention — automatically, on a schedule, scored
> by a **local** LLM, delivered to Telegram. Zero API cost.

![CI](https://github.com/Devosq/repo-scout/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

Most "trending repos" feeds are noise. Repo Scout searches GitHub for repos that
match **your** projects and stack (you describe them once), scores each one for
real usefulness with a local Ollama model, remembers what it already showed you,
and pushes only the few genuine hits to Telegram.

```
profiles.yaml ─▶ GitHub Search API ─▶ dedupe (180-day memory)
              ─▶ local Ollama scoring ─▶ Telegram report (top hits only)
```

## Why it's different
- **Tuned to you, not to the crowd** — scoring is based on your projects' actual
  needs, so an "awesome-list" with 30k stars scores *low* and a niche tool that
  solves a current pain point scores *high*.
- **Zero marginal cost** — GitHub's free Search API + a local model. No paid keys.
- **Has a memory** — a repo shown once isn't shown again for 180 days.
- **Safe with untrusted input** — repo descriptions are treated as untrusted:
  delimited in the prompt, URLs stripped from model output, all fields HTML-escaped.

## Install
```bash
git clone https://github.com/Devosq/repo-scout
cd repo-scout
pip install -r requirements.txt
cp env.example .env          # then fill it in
```

You need a running [Ollama](https://ollama.com) with a model pulled
(default `qwen2.5:14b-32k`), and a Telegram bot token. Detect your chat id with:
```bash
python setup_telegram.py
```

## Usage
```bash
python repo_scout.py --dry-run --limit 5   # test: scores 5, prints, sends nothing
python repo_scout.py                        # full run -> Telegram
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--dry-run` | off | Score & print, but don't send or update state |
| `--min-score` | 6 | Minimum score (0-10) to report |
| `--top` | 5 | Max repos per report |
| `--limit` | 0 | Cap candidates scored (0 = no cap) |

### Configure what it looks for
Edit [`profiles.yaml`](./profiles.yaml): describe your projects in
`projects_context`, your current stack in `stack_in_use` (so duplicates score
low), and add search `profiles` with GitHub query qualifiers. Each profile is one
search angle.

### Run on a schedule
A `systemd` service + timer are included in [`systemd/`](./systemd) for a
twice-weekly run. Or use cron, a GitHub Action, or any scheduler — it's a single
script.

## How scoring works
Each candidate is sent to your local model with your project context and a strict
rubric (most repos deserve 3-6; 8-10 is reserved for direct hits not already in
your stack). The model returns `{score, project, reason}` as JSON; only repos at
or above `--min-score` make the report.

## Development
```bash
python -m unittest discover -v   # 11 tests, pure logic, no network
ruff check .
```

## Security
See [SECURITY.md](./SECURITY.md). Secrets live in `.env` (git-ignored); the bot
token is redacted from logs. Always inspect a recommended repo yourself before
cloning it.

## License
[MIT](./LICENSE) (c) Devosq

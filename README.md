# Repo Scout

Scans GitHub twice a week for repos useful to active projects, scores them
with local Ollama (zero marginal cost) and pushes the best finds to Telegram.

**Pipeline:** `profiles.yaml` search profiles → GitHub Search API →
dedup (`state.json`, 180-day memory) → Ollama scoring (qwen2.5:14b-32k,
JSON verdict) → Telegram report (score ≥ 6, top 5).

## Runtime

VPS2 (`addwork-tools`), `/opt/repo-scout`, systemd timer `Mon,Thu 06:30 UTC`.
Python 3.12 venv, deps: `requests`, `PyYAML`.

## Install

```bash
cd /opt/repo-scout && bash install.sh
```

Then fill `.env` (see `env.example`), detect chat id with `setup_telegram.py`,
dry-run, and enable the timer — the installer prints the exact steps.

## Usage

```bash
./venv/bin/python3 repo_scout.py --dry-run --limit 5   # test without sending
./venv/bin/python3 repo_scout.py                        # full run
systemctl list-timers repo-scout.timer                  # check schedule
journalctl -u repo-scout.service -n 50                  # logs
```

## Tuning

- **Search profiles:** edit `profiles.yaml` — keep queries tied to concrete
  project needs, not generic "best tools" searches.
- **Model:** `OLLAMA_MODEL` in `.env`.
- **Thresholds:** `--min-score` (default 6), `--top` (default 5).
- A repo scored once is not re-reported for 180 days (`state.json`).

## Security notes

- `.env` is chmod 600; bot token never appears in logs (redacted in errors).
- Repo descriptions are untrusted input: they are delimited in the LLM prompt,
  URLs are stripped from LLM output, and all fields are HTML-escaped before
  Telegram rendering. Never clone a recommended repo based on the reason text
  alone — always inspect it first.

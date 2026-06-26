# Contributing

Contributions are welcome!

## Development
```bash
pip install -r requirements.txt
python -m unittest discover -v      # run tests
ruff check .                        # lint
```

## Guidelines
- Keep the zero-dependency-where-possible spirit (stdlib + `requests` + `PyYAML`).
- Add a test for any logic change (see `test_repo_scout.py`).
- Conventional Commits, English.
- Never commit secrets — `.env` is git-ignored; use `env.example` for new vars.

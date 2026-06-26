#!/usr/bin/env bash
# Repo Scout installer — run on VPS2 as root from /opt/repo-scout
set -euo pipefail

cd /opt/repo-scout

echo "[1/5] venv + dependencies"
python3 -m venv venv
./venv/bin/pip install --quiet -r requirements.txt

echo "[2/5] .env"
if [ ! -f .env ]; then
  cp env.example .env
  chmod 600 .env
  echo "  -> created .env from template. FILL IN TELEGRAM_BOT_TOKEN before enabling the timer."
else
  chmod 600 .env
  echo "  -> .env exists, left untouched"
fi

echo "[3/5] unit tests"
./venv/bin/python3 -m unittest test_repo_scout -v 2>&1 | tail -3

echo "[4/5] systemd units"
cp systemd/repo-scout.service systemd/repo-scout.timer /etc/systemd/system/
systemctl daemon-reload

echo "[5/5] done. Next steps:"
echo "  1. Edit /opt/repo-scout/.env (TELEGRAM_BOT_TOKEN)"
echo "  2. Send the bot a message from a NEW chat, then: ./venv/bin/python3 setup_telegram.py"
echo "  3. Add TELEGRAM_CHAT_ID to .env"
echo "  4. Test:   ./venv/bin/python3 repo_scout.py --dry-run --limit 5"
echo "  5. Enable: systemctl enable --now repo-scout.timer"

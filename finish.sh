#!/usr/bin/env bash
# Repo Scout finisher — run on VPS2 AFTER putting TELEGRAM_BOT_TOKEN into .env
# and sending the bot one message from the new repo-scout chat.
set -euo pipefail
cd /opt/repo-scout

if ! grep -qE '^TELEGRAM_BOT_TOKEN=.+' .env; then
  echo "STOP: TELEGRAM_BOT_TOKEN missing from /opt/repo-scout/.env"
  echo "Edit .env first: nano /opt/repo-scout/.env"
  exit 1
fi

if ! grep -qE '^TELEGRAM_CHAT_ID=.+' .env; then
  echo "[1/3] detecting chat id (bot must have received a message from the new chat)..."
  ./venv/bin/python3 setup_telegram.py || {
    echo "Autodetect failed (webhook set or no messages yet)."
    echo "Find the chat id manually and add TELEGRAM_CHAT_ID=<id> to .env, then re-run."
    exit 1
  }
  read -rp "Enter TELEGRAM_CHAT_ID from the list above: " CHAT_ID
  echo "TELEGRAM_CHAT_ID=${CHAT_ID}" >> .env
  echo "  -> saved"
else
  echo "[1/3] TELEGRAM_CHAT_ID already set"
fi

echo "[2/3] real test run (sends a Telegram report if finds exist)..."
./venv/bin/python3 repo_scout.py

echo "[3/3] enabling timer..."
systemctl enable --now repo-scout.timer
systemctl list-timers repo-scout.timer --no-pager
echo "DONE — Repo Scout runs Mon+Thu 06:30 UTC."

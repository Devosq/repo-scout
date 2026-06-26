#!/usr/bin/env python3
"""One-time helper: detect the chat_id for Repo Scout's Telegram chat.

Usage:
  1. Put TELEGRAM_BOT_TOKEN into .env (same directory).
  2. Open a NEW chat with the bot in Telegram and send it any message
     (e.g. /start repo-scout).
  3. Run: python3 setup_telegram.py
  4. Pick the chat id and add TELEGRAM_CHAT_ID=<id> to .env.

The token is read from .env and never printed.
"""

import sys
from pathlib import Path

import requests

from repo_scout import load_env


def main() -> int:
    env = load_env(Path(__file__).resolve().parent / ".env")
    token = env.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("TELEGRAM_BOT_TOKEN missing from .env (set=no)")
        return 1
    try:
        resp = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=30)
        resp.raise_for_status()
        updates = resp.json().get("result", [])
    except requests.RequestException as exc:
        print(f"getUpdates failed: {str(exc).replace(token, '***')}")
        return 1

    chats = {}
    for update in updates:
        msg = update.get("message") or update.get("channel_post") or {}
        chat = msg.get("chat")
        if chat:
            chats[chat["id"]] = chat.get("title") or chat.get("username") or chat.get("first_name", "?")

    if not chats:
        print("No updates found. Send the bot a message from the new chat first,")
        print("then re-run. (Note: getUpdates is empty if a webhook is set —")
        print("in that case read the chat id from the webhook handler logs.)")
        return 1

    print("Chats seen by the bot:")
    for chat_id, name in chats.items():
        print(f"  TELEGRAM_CHAT_ID={chat_id}   ({name})")
    print("\nAdd the right line to .env")
    return 0


if __name__ == "__main__":
    sys.exit(main())

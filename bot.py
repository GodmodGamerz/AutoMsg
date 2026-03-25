import os
import time
import random
import threading
import requests

MESSAGES = [
    "Hey everyone! 👋",
    "What's up?",
    "Testing 1 2 3...",
    "Hello from the bot!",
    "Random message drop 🎲",
    "Anyone here? 🤔",
    "Beep boop 🤖",
    "Just checking in!",
    "Greetings from the server!",
    "Ping! 🏓",
    "Have a great day! ☀️",
    "This is a test message.",
    "Bot is alive and kicking!",
    "🚀 Message incoming!",
    "All systems go!",
]


def get_group_chats(token):
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{token}/getUpdates",
            params={"limit": 100},
            timeout=10,
        )
        data = r.json()
        if not data.get("ok"):
            print(f"[{token[:10]}...] Failed to get updates: {data}")
            return []
        chats = {}
        for update in data["result"]:
            msg = update.get("message") or update.get("channel_post")
            if msg:
                chat = msg["chat"]
                if chat["type"] in ("group", "supergroup", "channel"):
                    chats[chat["id"]] = chat.get("title", str(chat["id"]))
        return list(chats.items())
    except Exception as e:
        print(f"[{token[:10]}...] Error fetching chats: {e}")
        return []


def send_message(token, chat_id, text):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def run_bot(token):
    name = token[:10] + "..."

    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        info = r.json()
        if not info.get("ok"):
            print(f"[{name}] Invalid token, skipping.")
            return
        username = info["result"].get("username", "unknown")
        print(f"[{name}] Connected as @{username}")
    except Exception as e:
        print(f"[{name}] Connection error: {e}")
        return

    chats = get_group_chats(token)
    if not chats:
        print(f"[{name}] No groups found. Add bot to a group and send a message first.")
        return

    print(f"[{name}] Found {len(chats)} group(s): {[t for _, t in chats]}")

    while True:
        for chat_id, title in chats:
            msg = random.choice(MESSAGES)
            result = send_message(token, chat_id, msg)
            if result.get("ok"):
                print(f"[{name}] ✅ -> {title}: {msg}")
            else:
                print(f"[{name}] ❌ -> {title}: {result}")

        delay = round(random.uniform(2, 5), 1)
        print(f"[{name}] Waiting {delay}s...")
        time.sleep(delay)


def load_tokens():
    tokens = []

    # BOT_TOKEN_1, BOT_TOKEN_2, ... for multiple bots
    i = 1
    while True:
        token = os.environ.get(f"BOT_TOKEN_{i}", "").strip()
        if not token:
            break
        tokens.append(token)
        i += 1

    # Single BOT_TOKEN also supported
    single = os.environ.get("BOT_TOKEN", "").strip()
    if single and single not in tokens:
        tokens.append(single)

    return tokens


def main():
    tokens = load_tokens()

    if not tokens:
        print("ERROR: No tokens found.")
        print("Set BOT_TOKEN for one bot, or BOT_TOKEN_1, BOT_TOKEN_2, ... for multiple.")
        return

    print(f"Loaded {len(tokens)} bot token(s).")

    threads = []
    for token in tokens:
        t = threading.Thread(target=run_bot, args=(token,), daemon=True)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()

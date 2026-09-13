from bot import TelegramBot
from router import CommandRouter

bot = TelegramBot()
router = CommandRouter()

offset = None

print("🤖 Bot started...")

while True:

    updates = bot.get_updates(offset)

    for update in updates:

        offset = update["update_id"] + 1

        if "message" not in update:
            continue

        text = update["message"].get("text", "")

        if not text.startswith("/"):
            continue

        print("User:", text)

        reply = router.dispatch(text)

        chat_id = update["message"]["chat"]["id"]

        bot.chat_id = chat_id
        bot.send(reply)
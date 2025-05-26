import os
import time
import threading
from datetime import datetime, timedelta
from telebot import TeleBot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
INACTIVITY_THRESHOLD = int(os.getenv("INACTIVITY_THRESHOLD", 259200))  # 3日(秒) default

bot = TeleBot(BOT_TOKEN)
last_activity = {}

def monitor_inactivity():
    while True:
        now = datetime.utcnow()
        for chat_id, users in list(last_activity.items()):
            for user_id, last_time in list(users.items()):
                if (now - last_time).total_seconds() > INACTIVITY_THRESHOLD:
                    try:
                        bot.kick_chat_member(chat_id, user_id)
                        del last_activity[chat_id][user_id]
                    except Exception as e:
                        print(f"Failed to kick {user_id}: {e}")
        time.sleep(3600)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id not in last_activity:
        last_activity[chat_id] = {}
    last_activity[chat_id][user_id] = datetime.utcnow()

if __name__ == "__main__":
    threading.Thread(target=monitor_inactivity).start()
    bot.infinity_polling()
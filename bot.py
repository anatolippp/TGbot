import redis
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

from config import TELEGRAM_BOT_TOKEN

app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)


async def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    redis_client.sadd("active_users", chat_id)
    await update.message.reply_text("BOT ACTIVE")


async def stop(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    redis_client.srem("active_users", chat_id)
    await update.message.reply_text("STOPPED")


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))

if __name__ == "__main__":
    app.run_polling()

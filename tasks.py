import asyncio
import logging

import redis
from celery import Celery
from telegram import Bot
from telegram.request import HTTPXRequest

from config import TELEGRAM_BOT_TOKEN, CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from db.database import SessionLocal
from db.models import UserSettings

logger = logging.getLogger(__name__)

celery = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)


def get_bot():
    request = HTTPXRequest()
    return Bot(token=TELEGRAM_BOT_TOKEN, request=request)


@celery.task
def send_hello():
    db = SessionLocal()
    try:
        settings = db.query(UserSettings).first()
        interval = 5
        phrase = "Hello"
        if settings:
            interval = settings.interval if settings.interval is not None else 5
            phrase = settings.phrase if settings.phrase is not None else "Hello"

        running = redis_client.get("running")
        if running == "1":
            chat_ids = redis_client.smembers("active_users")
            if chat_ids:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                bot = get_bot()
                coros = [send_message(bot, cid, phrase) for cid in chat_ids]
                loop.run_until_complete(asyncio.gather(*coros))
            send_hello.apply_async(countdown=interval)
    finally:
        db.close()


async def send_message(bot, chat_id, text):
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        logger.warning(f"Error sending message to {chat_id}: {e}")

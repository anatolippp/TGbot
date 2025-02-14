import asyncio
import logging
import redis
from celery import Celery
from sqlalchemy.orm import Session
from telegram import Bot
from telegram.request import HTTPXRequest

from db.database import SessionLocal
from db.models import UserSettings
from config import TELEGRAM_BOT_TOKEN, CELERY_BROKER_URL, CELERY_RESULT_BACKEND

logger = logging.getLogger(__name__)

celery = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)

request = HTTPXRequest()
bot = Bot(token=TELEGRAM_BOT_TOKEN, request=request)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@celery.task
def send_hello():
    db = SessionLocal()
    settings = db.query(UserSettings).first()
    db.close()

    if not settings:
        interval = 5
        phrase = "Hello"
    else:
        interval = settings.interval or 5
        phrase = settings.phrase or "Hello"

    running = redis_client.get("running")
    if running == "1":
        chat_ids = redis_client.smembers("active_users")
        if chat_ids:
            coros = [_send_message(cid, phrase) for cid in chat_ids]
            loop.run_until_complete(asyncio.gather(*coros))
        send_hello.apply_async(countdown=interval)

async def _send_message(chat_id, text):
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        logger.warning(f"Error sending message to {chat_id}: {e}")

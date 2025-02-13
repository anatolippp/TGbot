import asyncio

import redis
import telegram
from celery import Celery
from celery.schedules import timedelta

from config import TELEGRAM_BOT_TOKEN, CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)


async def send_message(chat_id):
    try:
        print(f"SEND hello {chat_id}")
        await bot.send_message(chat_id=chat_id, text="Hello")
        print(f"Sent {chat_id}")
    except Exception as e:
        print(f"Mistake sening {chat_id}: {e}")


@celery.task
def send_hello():
    if redis_client.get("running") == "1":
        chat_ids = redis_client.smembers("active_users")
        print(f"Error Redis: {chat_ids}")

        if chat_ids:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = [send_message(chat_id) for chat_id in chat_ids]
            loop.run_until_complete(asyncio.gather(*tasks))
            loop.close()
            print("All sent!")
        else:
            print("No users")


celery.conf.beat_schedule = {
    "send_hello_every_5_seconds": {
        "task": "tasks.send_hello",
        "schedule": timedelta(seconds=5),
    },
}

import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "NO_TOKEN_PROVIDED")
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/postgres")

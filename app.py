import redis
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import UserSettings
from tasks import send_hello

app = FastAPI()
redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/start")
def start_task(phrase: str = "Hello", db: Session = Depends(get_db)):
    redis_client.set("running", "1")
    settings = db.query(UserSettings).first()
    if settings:
        settings.phrase = phrase
    else:
        settings = UserSettings(phrase=phrase)
        db.add(settings)
    db.commit()
    send_hello.delay()
    return {"status": "started", "phrase": phrase}

@app.post("/stop")
def stop_task():
    redis_client.set("running", "0")
    return {"status": "stopped"}

@app.post("/set_interval")
def set_interval(interval: int, db: Session = Depends(get_db)):
    if interval < 1:
        return {"error": "Interval must be >= 1"}
    settings = db.query(UserSettings).first()
    if not settings:
        settings = UserSettings(interval=interval)
        db.add(settings)
    else:
        settings.interval = interval
    db.commit()
    return {"status": "interval updated", "interval": interval}

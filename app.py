import redis
from fastapi import FastAPI

app = FastAPI()
redis_client = redis.StrictRedis(host="redis",
                                 port=6379,
                                 db=0,
                                 decode_responses=True
                                 )


@app.post("/start")
def start_task():
    redis_client.set("running", "1")
    return {"status": "started"}


@app.post("/stop")
def stop_task():
    redis_client.set("running", "0")
    return {"status": "stopped"}

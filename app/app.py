import os

import redis
from flask import Flask

app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379)


@app.route("/")
def index():
    try:
        hits = r.incr("hits")
    except redis.exceptions.ConnectionError:
        hits = "redis not reachable"
    return f"{os.getenv('APP_NAME', 'myapp')} visits: {hits}\n"


@app.route("/health")
def health():
    return "ok", 200

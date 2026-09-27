import os
import json
import redis
import time

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.Redis.from_url(REDIS_URL)

def consume_streams():
    print("[*] Stream consumer started, listening to telemetry stream...")
    while True:
        try:
            streams = r.xread({"apng_telemetry": "0"}, count=10, block=2000)
            for stream, messages in streams:
                for message_id, data in messages:
                    print(f"[+] Processing telemetry message {message_id}: {data}")
        except Exception as e:
            print(f"[-] Stream consumption error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    consume_streams()
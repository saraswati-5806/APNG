import fakeredis

# Use an in-memory fake Redis client for instant testing without Docker
r = fakeredis.FakeRedis()

# Push a test telemetry event into Redis Streams
message_data = {"sensor": "edge-switch-04", "packet_size": "512", "status": "anomaly"}
msg_id = r.xadd("apng_telemetry", message_data)
print(f"[+] Successfully pushed test message to stream with ID: {msg_id}")

# Read it back to verify
streams = r.xread({"apng_telemetry": "0"}, count=1)
print(f"[+] Read back from stream: {streams}")
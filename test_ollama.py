from llm_engine.ollama_client import generate_guidance

alert_context = "High anomaly score (0.87) detected on IP 10.0.4.22 outside business hours."
log_excerpt = "Repeated outbound TCP connections to port 443."

print("[*] Sending test prompt to local Ollama instance...")
response = generate_guidance(alert_context, log_excerpt)
print("\n--- LLM Response ---")
print(response)
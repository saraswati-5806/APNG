import os
import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

def generate_guidance(alert_context: str, log_excerpt: str) -> str:
    prompt = f"Analyze this network security alert and log context, then provide plain-language guidance and a recommended action.\n\nContext: {alert_context}\nLog: {log_excerpt}"
    
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=45  # Increased timeout for local model warm-up
        )
        if response.status_code == 200:
            return response.json().get("response", "No response generated.")
        else:
            return f"Error: Ollama returned status {response.status_code}"
    except Exception as e:
        return f"Ollama service unreachable — falling back to rule-based explanation: {str(e)}"
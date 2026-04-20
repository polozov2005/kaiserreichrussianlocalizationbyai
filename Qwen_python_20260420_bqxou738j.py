# test_ollama.py
import requests
import json

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "qwen3.5:9b",
        "messages": [{"role": "user", "content": "Translate 'Hello world' to Russian. Return only translation."}],
        "stream": False,
        "options": {"temperature": 0.1, "enable_thinking": False}
    },
    timeout=30
)

print("Status:", response.status_code)
print("Raw response:", json.dumps(response.json(), indent=2, ensure_ascii=False))
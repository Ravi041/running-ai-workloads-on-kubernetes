import requests
from .base_client import BaseModelClient
from app.config import settings

class OllamaClient(BaseModelClient):
    def __init__(self, host: str | None = None):
        self.host = (host or settings.OLLAMA_HOST).rstrip("/")

    def generate(self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
        url = f"{self.host}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        return data.get("response", "")

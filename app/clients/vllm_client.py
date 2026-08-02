import requests
from .base_client import BaseModelClient
from app.config import settings

class VLLMClient(BaseModelClient):
    def __init__(self, host: str | None = None):
        self.host = (host or settings.VLLM_HOST).rstrip("/")

    def generate(self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
        url = f"{self.host}/v1/completions"
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        choices = data.get("choices") or []
        if choices:
            return choices[0].get("text", "")

        return data.get("output", "")

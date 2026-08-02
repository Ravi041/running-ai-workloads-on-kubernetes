from app.clients.mock_client import MockClient
from app.clients.ollama_client import OllamaClient
from app.clients.vllm_client import VLLMClient


def get_model_client(provider: str):
    provider = provider.lower()
    if provider == "mock":
        return MockClient()
    if provider == "ollama":
        return OllamaClient()
    if provider == "vllm":
        return VLLMClient()
    raise ValueError(f"Unsupported model provider: {provider}")

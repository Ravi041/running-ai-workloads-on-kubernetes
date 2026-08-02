from .base_client import BaseModelClient


class MockClient(BaseModelClient):
    def generate(self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
        return (
            f"Mock response from {model}: received {len(prompt)} characters "
            f"with temperature={temperature} and max_tokens={max_tokens}."
        )

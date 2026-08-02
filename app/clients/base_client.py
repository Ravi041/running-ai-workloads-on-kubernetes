from abc import ABC, abstractmethod

class BaseModelClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
        raise NotImplementedError

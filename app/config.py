from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    MODEL_PROVIDER: str = "mock"
    MODEL_NAME: str = "demo-model"
    OLLAMA_HOST: str = "http://localhost:11434"
    VLLM_HOST: str = "http://localhost:8000"
    GATEWAY_PORT: int = 8080

    @property
    def DEFAULT_PROVIDER(self) -> str:
        return self.MODEL_PROVIDER

    @property
    def DEFAULT_MODEL(self) -> str:
        return self.MODEL_NAME

settings = Settings()

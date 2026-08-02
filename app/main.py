import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.clients import get_model_client
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-gateway")

app = FastAPI(
    title="AI-on-K8s Gateway",
    description="A FastAPI gateway for Ollama and vLLM inference on Kubernetes.",
    version="0.1.0",
)

REQUEST_COUNT = Counter("gateway_requests_total", "Total inference requests", ["provider", "path"])
REQUEST_LATENCY = Histogram("gateway_request_latency_seconds", "Inference request latency", ["provider", "path"])

class InferenceRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    model: str | None = None
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(512, ge=1, le=4096)

@app.on_event("startup")
async def startup_event():
    provider = settings.DEFAULT_PROVIDER
    app.state.model_client = get_model_client(provider)
    logger.info("Using provider=%s host=%s", provider, settings.OLLAMA_HOST if provider == "ollama" else settings.VLLM_HOST)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "provider": settings.DEFAULT_PROVIDER,
        "model": settings.DEFAULT_MODEL,
    }

@app.get("/")
async def root():
    return {
        "service": "AI-on-K8s Gateway",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }

@app.post("/infer")
async def infer(request: InferenceRequest):
    model = request.model or settings.DEFAULT_MODEL
    provider = settings.DEFAULT_PROVIDER
    REQUEST_COUNT.labels(provider=provider, path="/infer").inc()

    with REQUEST_LATENCY.labels(provider=provider, path="/infer").time():
        try:
            output = app.state.model_client.generate(
                prompt=request.prompt,
                model=model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        except Exception as exc:
            logger.exception("Inference failed")
            raise HTTPException(status_code=500, detail=str(exc))

    return {
        "provider": provider,
        "model": model,
        "output": output,
    }

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

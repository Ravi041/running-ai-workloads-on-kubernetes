# Project Write-Up: Running AI Workloads on Kubernetes

## Talk Goal

Show how a simple AI inference gateway can move from a laptop demo to Kubernetes and then to Azure Kubernetes Service. The project keeps the first demo reliable with a mock model backend, then shows where real model servers such as Ollama or vLLM fit.

## Problem Statement

AI teams often start with a model running locally, but production needs are broader: repeatable deployment, health checks, scaling, service exposure, observability, and cloud infrastructure. Kubernetes gives a common operating model for those needs, while AKS provides a managed control plane and Azure integration.

## Architecture

- FastAPI gateway exposes `/infer`, `/health`, `/metrics`, and interactive API docs at `/docs`.
- Provider abstraction supports `mock`, `ollama`, and `vllm`.
- Local testing uses Docker and Kind.
- Observability uses Prometheus metrics from the gateway and local Prometheus/Grafana manifests.
- AKS deployment uses Kubernetes manifests under `k8s/aks`.
- Azure infrastructure uses Terraform under `terraform/aks` to create a resource group, ACR, AKS, and the ACR pull permission.

## Demo Flow

1. Run the gateway locally with `MODEL_PROVIDER=mock`.
2. Build the Docker image.
3. Load and deploy it into Kind.
4. Call `/infer` through the Kind NodePort.
5. Show `/metrics` and Prometheus scraping the gateway.
6. Build and push the same image to Azure Container Registry.
7. Deploy the same gateway shape to AKS with a LoadBalancer service.
8. Explain how the mock backend can be swapped for Ollama or vLLM once model serving is available.

## Local Validation Commands

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/infer \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Hello from my CNCF talk"}'
```

## Kind Validation Commands

```bash
docker build -t ai-on-k8s:latest .
kind create cluster
kind load docker-image ai-on-k8s:latest
kubectl apply -f k8s/kind/fastapi-deployment.yaml
kubectl apply -f k8s/kind/fastapi-service.yaml
kubectl rollout status deployment/ai-gateway
curl -X POST http://localhost:30080/infer \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Hello from Kind"}'
```

## AKS Build Path

```bash
cd terraform/aks
terraform init
terraform apply -var="acr_name=<globally-unique-acr-name>"
```

```bash
az aks get-credentials --resource-group rg-ai-on-k8s --name aks-ai-on-k8s
ACR_LOGIN_SERVER=$(az acr show --name "<globally-unique-acr-name>" --query loginServer -o tsv)
docker build -t "$ACR_LOGIN_SERVER/ai-on-k8s:latest" .
docker push "$ACR_LOGIN_SERVER/ai-on-k8s:latest"
```

Update `k8s/aks/kustomization.yaml` with your ACR login server, then:

```bash
kubectl apply -k k8s/aks
kubectl rollout status deployment/ai-gateway -n ai-on-k8s
kubectl get svc ai-gateway -n ai-on-k8s
```

## Review Notes

- The previous app used `pydantic.BaseSettings`, which is no longer valid for Pydantic v2 without `pydantic-settings`.
- The previous Ollama client used a non-Ollama endpoint. It now calls `/api/generate`.
- The previous vLLM client used `/v1/generate`; it now targets the OpenAI-compatible `/v1/completions` endpoint.
- The previous Kind deployment referenced a placeholder registry image, which prevented the locally built image from being used.
- AKS was not represented in the repo; AKS Kubernetes and Terraform assets now exist.
- The AKS Terraform path assigns `AcrPull` for standard ACR access. ABAC-enabled registries need repository-reader permissions instead.

## Production Next Steps

- Add a real Ollama or vLLM deployment manifest with GPU node scheduling.
- Store model/backend configuration in environment-specific ConfigMaps and Secrets.
- Add autoscaling with HPA or KEDA.
- Replace `latest` image tags with immutable tags from CI.
- Add Azure Monitor or managed Prometheus/Grafana for production observability.

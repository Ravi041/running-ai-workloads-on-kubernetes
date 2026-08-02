# running-ai-workloads-on-kubernetes

A reference project for running AI workloads on Kubernetes using a FastAPI gateway with mock, Ollama, or vLLM backends, local Kind demos, AKS/GKE deployment paths, Prometheus/Grafana observability, Terraform provisioning, and CI/CD pipelines.

## Architecture

- **FastAPI gateway**: exposes `/infer`, `/health`, and `/metrics`.
- **Model backends**: mock, Ollama, and vLLM clients support local demos through real inference deployments.
- **Local demo**: Kind manifests for local development.
- **Cloud deployment**: AKS and GKE manifests, plus Terraform infrastructure examples.
- **Observability**: Prometheus scrape config and Grafana UI.
- **CI/CD**: GitHub Actions and Azure DevOps pipelines.

## Quickstart

### Local development

1. Copy environment defaults:

```bash
cp .env.example .env
```

2. Build the gateway image:

```bash
docker build -t ai-on-k8s:latest .
```

3. Install dependencies and run locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

4. Query the gateway:

```bash
curl -X POST http://localhost:8080/infer -H 'Content-Type: application/json' -d '{"prompt":"Hello from AI-on-K8s"}'
```

### Kind demo

```bash
cd k8s/kind
kind create cluster
cd ../..
docker build -t ai-on-k8s:latest .
kind load docker-image ai-on-k8s:latest
cd k8s/kind
kubectl apply -f fastapi-deployment.yaml
kubectl apply -f fastapi-service.yaml
kubectl apply -f prometheus-deployment.yaml
kubectl apply -f grafana-deployment.yaml
```

Access the gateway at `http://localhost:30080`, Prometheus at `http://localhost:32090`, and Grafana at `http://localhost:32000`.

If NodePort is not reachable in your local Docker setup, use a port-forward:

```bash
kubectl port-forward svc/ai-gateway 18081:8080
curl -X POST http://localhost:18081/infer \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Hello from Kind"}'
```

### AKS deployment

Provision AKS and ACR with Terraform:

```bash
cd terraform/aks
terraform init
terraform apply -var="acr_name=<globally-unique-acr-name>"
```

Connect to AKS, build, push, and deploy:

```bash
az aks get-credentials \
  --resource-group rg-ai-on-k8s \
  --name aks-ai-on-k8s

ACR_NAME=<globally-unique-acr-name>
ACR_LOGIN_SERVER=$(az acr show --name "$ACR_NAME" --query loginServer -o tsv)

az acr login --name "$ACR_NAME"
docker build -t "$ACR_LOGIN_SERVER/ai-on-k8s:latest" .
docker push "$ACR_LOGIN_SERVER/ai-on-k8s:latest"

cd k8s/aks
# Replace REPLACE_WITH_ACR_LOGIN_SERVER in kustomization.yaml with the value of $ACR_LOGIN_SERVER.
kubectl apply -k .
```

### GKE deployment

1. Build and push the container image:

```bash
docker build -t gcr.io/${PROJECT_ID}/ai-on-k8s:latest .
docker push gcr.io/${PROJECT_ID}/ai-on-k8s:latest
```

2. Create or connect to the cluster:

```bash
gcloud container clusters create ai-on-k8s --zone us-central1-a --num-nodes=2
gcloud container clusters get-credentials ai-on-k8s --zone us-central1-a
```

3. Deploy the gateway:

```bash
kubectl apply -f k8s/gke/fastapi-deployment.yaml
kubectl apply -f k8s/gke/fastapi-service.yaml
```

4. Get the external IP:

```bash
kubectl get svc ai-gateway
```

## Terraform

Terraform examples are available for both Azure AKS and Google GKE.

### Azure AKS

```bash
cd terraform/aks
terraform init
terraform plan -var="acr_name=<globally-unique-acr-name>"
terraform apply -var="acr_name=<globally-unique-acr-name>"
```

### Google GKE

```bash
cd terraform
terraform init
terraform plan -var="project_id=${PROJECT_ID}"
terraform apply -var="project_id=${PROJECT_ID}"
```

## CI/CD

- GitHub Actions workflow: `.github/workflows/ci-cd.yaml`

## Notes

- Ollama and vLLM services are configured via environment variables.
- `MODEL_PROVIDER=mock` is the default so the gateway can be tested without a model server.
- Production deployments should use ConfigMaps and Secrets instead of hard-coded manifests.
- This repository is a starter template and may need adjustments for your specific model environment.

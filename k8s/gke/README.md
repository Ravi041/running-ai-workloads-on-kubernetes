# GKE Deployment

This directory contains Kubernetes manifests for deploying the AI gateway to Google Kubernetes Engine.

## Prerequisites

- A Google Cloud project with GKE enabled.
- `gcloud` configured with the target project and region.
- A container registry such as Artifact Registry or GCR.

## Deploy

1. Build and push the container image:

```bash
docker build -t gcr.io/${PROJECT_ID}/ai-on-k8s:latest ..
docker push gcr.io/${PROJECT_ID}/ai-on-k8s:latest
```

2. Create or connect to the GKE cluster:

```bash
gcloud container clusters create ai-on-k8s --zone us-central1-a --num-nodes=2
gcloud container clusters get-credentials ai-on-k8s --zone us-central1-a
```

3. Deploy the application:

```bash
kubectl apply -f fastapi-deployment.yaml
kubectl apply -f fastapi-service.yaml
```

4. Get the external IP:

```bash
kubectl get svc ai-gateway
```

## Notes

- Configure `MODEL_PROVIDER`, `OLLAMA_HOST`, and `VLLM_HOST` through ConfigMap or Secrets for production.
- Use Prometheus and Grafana for observability if you install them in the same cluster.

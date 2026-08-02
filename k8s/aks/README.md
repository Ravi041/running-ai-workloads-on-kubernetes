# AKS Deployment

This folder deploys the AI gateway to Azure Kubernetes Service.

## Prerequisites

- Azure CLI authenticated with `az login`
- `kubectl`
- Docker
- An AKS cluster with access to Azure Container Registry
- ACR name must be globally unique and use only alphanumeric characters

## Build and Push

```bash
ACR_NAME=<your-acr-name>
ACR_LOGIN_SERVER=$(az acr show --name "$ACR_NAME" --query loginServer -o tsv)

az acr login --name "$ACR_NAME"
docker build -t "$ACR_LOGIN_SERVER/ai-on-k8s:latest" ../..
docker push "$ACR_LOGIN_SERVER/ai-on-k8s:latest"
```

## Deploy

Update the image in `kustomization.yaml`:

```bash
cd k8s/aks
kustomize edit set image ai-on-k8s="$ACR_LOGIN_SERVER/ai-on-k8s:latest"
kubectl apply -k .
```

Check rollout and public IP:

```bash
kubectl rollout status deployment/ai-gateway -n ai-on-k8s
kubectl get svc ai-gateway -n ai-on-k8s
```

Test the gateway:

```bash
EXTERNAL_IP=$(kubectl get svc ai-gateway -n ai-on-k8s -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -X POST "http://$EXTERNAL_IP/infer" \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Hello from AKS"}'
```

## Switching to a Real Model Backend

The default AKS config uses `MODEL_PROVIDER=mock` so you can validate networking, probes, scaling, and observability first. To use Ollama or vLLM, deploy the backend service in the cluster and update `configmap.yaml`.

## ACR Permissions

The Terraform module assigns `AcrPull` to the AKS kubelet identity, which is the normal path for AKS pulling images from a standard ACR. If your registry uses Azure ABAC repository permissions, assign repository-reader permissions instead of relying on `AcrPull`.

# Kind Demo

This directory contains manifests for running the AI gateway locally in a Kind cluster.

## Deploy

1. Create the Kind cluster:

```bash
kind create cluster --config=- <<'EOF'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
EOF
```

2. Build the Docker image and load it into kind:

```bash
docker build -t ai-on-k8s:latest ../..
kind load docker-image ai-on-k8s:latest
```

3. Apply the gateway manifests:

```bash
kubectl apply -f fastapi-deployment.yaml
kubectl apply -f fastapi-service.yaml
```

4. Access the gateway:

```bash
curl http://localhost:30080/health
curl -X POST http://localhost:30080/infer \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Hello from Kind"}'
```

If NodePort is not reachable on your machine, use:

```bash
kubectl port-forward svc/ai-gateway 18081:8080
curl -X POST http://localhost:18081/infer \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Hello from Kind"}'
```

## Notes

- The default demo uses `MODEL_PROVIDER=mock` so you can validate Kubernetes locally without downloading a model.
- For local Ollama or vLLM usage, deploy that backend in the cluster or update the gateway environment variables to point at a reachable service.

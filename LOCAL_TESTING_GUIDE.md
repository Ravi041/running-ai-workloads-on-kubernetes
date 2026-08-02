# Local Testing Guide

This guide tests the AI-on-K8s gateway locally with Docker and Kind.

The app defaults to `MODEL_PROVIDER=mock`, so you do not need Ollama or vLLM for the first test.

## 1. Open the Project

```bash
cd /Users/ravindrakumar/Desktop/Github-Repos/AI-on-K8s/running-ai-workloads-on-kubernetes
```

## 2. Check Required Tools

```bash
docker --version
kind --version
kubectl version --client
```

Docker Desktop must be running before continuing.

## 3. Build the Docker Image

```bash
docker build -t ai-on-k8s:latest .
```

Confirm the image exists:

```bash
docker images ai-on-k8s:latest
```

## 4. Test the Container Directly

Run the container on port `18080`:

```bash
docker run --rm -p 18080:8080 ai-on-k8s:latest
```

Keep that terminal open. In a second terminal, test:

```bash
curl http://localhost:18080/health
```

Expected response:

```json
{"status":"ok","provider":"mock","model":"demo-model"}
```

Test inference:

```bash
curl -X POST http://localhost:18080/infer \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Hello from local Docker"}'
```

Expected response includes:

```json
{"provider":"mock","model":"demo-model"}
```

Stop the container with `Ctrl+C`.

## 5. Create or Reuse a Kind Cluster

Check for existing clusters:

```bash
kind get clusters
```

If no cluster exists, create one:

```bash
kind create cluster
```

Confirm kubectl is pointing to Kind:

```bash
kubectl config current-context
```

Expected:

```text
kind-kind
```

## 6. Load the Image into Kind

```bash
kind load docker-image ai-on-k8s:latest
```

This step is important. Kind cannot automatically see images from your local Docker image list.

## 7. Deploy the Gateway

```bash
kubectl apply -f k8s/kind/fastapi-deployment.yaml
kubectl apply -f k8s/kind/fastapi-service.yaml
```

Wait for rollout:

```bash
kubectl rollout status deployment/ai-gateway --timeout=90s
```

Check pod and service:

```bash
kubectl get pods -l app=ai-gateway
kubectl get svc ai-gateway
```

Expected pod status:

```text
Running
```

Expected service type:

```text
NodePort
```

## 8. Test with Port-Forward

Use this first because it is the most reliable local test:

```bash
kubectl port-forward svc/ai-gateway 18081:8080
```

Keep that terminal open. In a second terminal:

```bash
curl http://localhost:18081/health
```

Then:

```bash
curl -X POST http://localhost:18081/infer \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Hello from Kind port-forward"}'
```

Check metrics:

```bash
curl http://localhost:18081/metrics
```

You should see Prometheus metrics, including:

```text
gateway_requests_total
gateway_request_latency_seconds
```

Stop the port-forward with `Ctrl+C`.

## 9. Test with NodePort

Try the NodePort URL:

```bash
curl http://localhost:30080/health
```

Then:

```bash
curl -X POST http://localhost:30080/infer \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Hello from Kind NodePort"}'
```

If `localhost:30080` does not work but port-forward does, the app is healthy. The issue is local Kind/Docker NodePort networking, not the gateway.

## 10. Troubleshooting

Check pod status:

```bash
kubectl get pods -l app=ai-gateway -o wide
```

Check logs:

```bash
kubectl logs deployment/ai-gateway
```

Describe the pod:

```bash
kubectl describe deployment ai-gateway
kubectl describe svc ai-gateway
```

If the pod shows `ImagePullBackOff`, reload the image:

```bash
docker build -t ai-on-k8s:latest .
kind load docker-image ai-on-k8s:latest
kubectl rollout restart deployment/ai-gateway
kubectl rollout status deployment/ai-gateway --timeout=90s
```

If `localhost:30080` fails, use port-forward:

```bash
kubectl port-forward svc/ai-gateway 18081:8080
```

Then test:

```bash
curl http://localhost:18081/health
```

## 11. Clean Up

Delete the gateway:

```bash
kubectl delete -f k8s/kind/fastapi-service.yaml
kubectl delete -f k8s/kind/fastapi-deployment.yaml
```

Delete the Kind cluster if you no longer need it:

```bash
kind delete cluster
```

## Recommended Demo Path

For your presentation, use this order:

1. Show Docker test on `localhost:18080`.
2. Show Kind deployment rollout.
3. Use `kubectl port-forward svc/ai-gateway 18081:8080`.
4. Call `/health`, `/infer`, and `/metrics`.
5. Explain that NodePort may vary by local Docker networking, while port-forward proves the Kubernetes service is healthy.

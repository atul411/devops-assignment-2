# Shadow Deployment

Two manifests are provided:

| File | Requires | Mirror behaviour |
|------|----------|------------------|
| `istio-virtualservice.yaml` | Istio service mesh | True traffic mirroring with response discard. `mirrorPercentage` lets you ramp from 1% → 100%. |
| `nginx-mirror.yaml` | nginx-ingress only | `mirror-target` annotation duplicates each request fire-and-forget. Simpler, no service mesh. |

## When to use which

- **Istio**: production-grade. Per-request percentage control, observability, retries, Envoy-native.
- **nginx-mirror**: quick demo / Minikube without service mesh.

## Important

Mirrored traffic still **executes** on the shadow pod — including any DB writes. For safety, point the shadow Deployment at an isolated database (a separate PVC, separate `DATABASE` env var, or in-memory SQLite). The current manifests share the prod ConfigMap; in real shadow testing you would override `DATABASE` for the shadow pod.

## How to apply

```bash
# Istio variant (requires Istio)
kubectl label namespace aceest istio-injection=enabled --overwrite
kubectl apply -k k8s/shadow/

# nginx variant (vanilla)
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/configmap.yaml
kubectl apply -f k8s/base/pvc.yaml
kubectl apply -f k8s/shadow/istio-virtualservice.yaml  # Deployments + Services
kubectl apply -f k8s/shadow/nginx-mirror.yaml          # nginx ingress instead of Istio VS
```

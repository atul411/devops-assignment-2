#!/usr/bin/env bash
# Promote the canary deployment by ramping the canary-weight.
# Usage: ./canary-promote.sh [weight]   # default 50; final 100 = full rollout
set -euo pipefail
NAMESPACE="${NAMESPACE:-aceest}"
WEIGHT="${1:-50}"

echo "Setting canary-weight to $WEIGHT% ..."
kubectl annotate ingress aceest-fitness-canary \
    -n "$NAMESPACE" \
    nginx.ingress.kubernetes.io/canary-weight="$WEIGHT" --overwrite

if [[ "$WEIGHT" == "100" ]]; then
    echo "Canary fully promoted. Updating stable image to canary's, then removing canary ingress."
    CANARY_IMAGE=$(kubectl get deploy aceest-fitness-canary -n "$NAMESPACE" \
        -o jsonpath='{.spec.template.spec.containers[0].image}')
    kubectl set image deployment/aceest-fitness-stable app="$CANARY_IMAGE" -n "$NAMESPACE"
    kubectl rollout status deployment/aceest-fitness-stable -n "$NAMESPACE" --timeout=180s
    kubectl delete ingress aceest-fitness-canary -n "$NAMESPACE"
fi

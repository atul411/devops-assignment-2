#!/usr/bin/env bash
# Roll back the rolling-update Deployment to its previous ReplicaSet.
# Usage: ./rollback.sh [deployment-name]
set -euo pipefail
NAMESPACE="${NAMESPACE:-aceest}"
DEPLOY="${1:-aceest-fitness}"

echo "Rolling back deployment/$DEPLOY in namespace $NAMESPACE ..."
kubectl rollout undo deployment/"$DEPLOY" -n "$NAMESPACE"
kubectl rollout status deployment/"$DEPLOY" -n "$NAMESPACE" --timeout=180s

echo "Rollback complete. Current image:"
kubectl get deployment "$DEPLOY" -n "$NAMESPACE" \
    -o jsonpath='{.spec.template.spec.containers[0].image}'
echo

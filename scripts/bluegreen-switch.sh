#!/usr/bin/env bash
# Switch the Blue-Green Service selector between blue and green colors.
# Usage: ./bluegreen-switch.sh blue|green
set -euo pipefail

NAMESPACE="${NAMESPACE:-aceest}"
COLOR="${1:-}"

if [[ "$COLOR" != "blue" && "$COLOR" != "green" ]]; then
    echo "Usage: $0 blue|green"
    exit 1
fi

echo "Switching aceest-fitness Service to color=$COLOR ..."
kubectl patch service aceest-fitness \
    -n "$NAMESPACE" \
    --type merge \
    --patch "{\"spec\":{\"selector\":{\"app\":\"aceest-fitness\",\"color\":\"$COLOR\"}}}"

echo "Verifying endpoints ..."
kubectl get endpoints aceest-fitness -n "$NAMESPACE"
echo "Done. Live traffic now flows to color=$COLOR."

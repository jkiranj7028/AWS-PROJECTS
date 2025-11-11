# Placeholder for deploy_green.sh
#!/usr/bin/env bash
set -e
echo "[INFO] Deploying green version..."
kubectl apply -f manifests/green/deployment-green.yaml
kubectl rollout status deployment/myapp-green --timeout=180s
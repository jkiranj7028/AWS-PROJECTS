# Placeholder for rollback_to_blue.sh
#!/usr/bin/env bash
set -e
echo "[INFO] Rolling back to BLUE..."
kubectl patch service myapp-svc -p '{"spec":{"selector":{"app":"myapp","color":"blue"}}}'
kubectl rollout status deployment/myapp-blue --timeout=120s
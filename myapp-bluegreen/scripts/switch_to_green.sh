# Placeholder for switch_to_green.sh
#!/usr/bin/env bash
set -e
echo "[INFO] Switching traffic to GREEN..."
kubectl patch service myapp-svc -p '{"spec":{"selector":{"app":"myapp","color":"green"}}}'
kubectl get endpoints myapp-svc -o wide
# Placeholder for smoke_test.sh
#!/usr/bin/env bash
set -e
echo "[INFO] Running smoke test..."
URL="https://myapp.example.com/healthz"
for i in {1..5}; do
  if curl -sf "$URL"; then
    echo "[PASS] Smoke test OK"
    exit 0
  fi
  echo "[WARN] Retry $i..."
  sleep 5
done
echo "[FAIL] Smoke test failed!"
exit 1
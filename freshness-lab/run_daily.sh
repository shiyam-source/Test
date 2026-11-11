#!/usr/bin/env bash
# One probe round + report refresh. Run daily (twice daily in week one).
# Expects config/canaries.yaml and API credentials (env vars or proxy-injected).
set -euo pipefail
cd "$(dirname "$0")"
python3 -m freshness.probe --config config/canaries.yaml --out data/probes.jsonl
if ls data/logs/* >/dev/null 2>&1; then
  python3 -m freshness.logs data/logs/* --out data/fetches.jsonl
  mkdir -p data/logs/processed && mv data/logs/*.* data/logs/processed/ 2>/dev/null || true
fi
python3 -m freshness.report --config config/canaries.yaml

#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

ENV_NAME="agenkampus"

if [[ "${CONDA_DEFAULT_ENV:-}" != "$ENV_NAME" ]]; then
  echo "⚠️  Please activate the '$ENV_NAME' conda environment before running this script."
  echo "    Example: conda activate $ENV_NAME"
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "❌ 'uv' is required but not found. Install it with 'pip install uv' inside the env."
  exit 1
fi

echo "📦 Installing dependencies via uv..."
uv pip install -r requirements.txt

echo "🚀 Launching MCP servers (SSE mode)..."
python mcp_utilitas/server.py --transport sse --host 127.0.0.1 --port 8081 &
UTIL_PID=$!

python mcp_akademik/server.py --transport sse --host 127.0.0.1 --port 8082 &
AKAD_PID=$!

cleanup() {
  echo "🛑 Stopping MCP servers..."
  kill "$UTIL_PID" "$AKAD_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "⏳ Waiting for servers to start..."
sleep 3

if ! kill -0 "$UTIL_PID" 2>/dev/null; then
  echo "❌ MCP Utilitas failed to start. Check the logs above."
  exit 1
fi

if ! kill -0 "$AKAD_PID" 2>/dev/null; then
  echo "❌ MCP Akademik failed to start. Check the logs above."
  exit 1
fi

echo "🧪 Running remote MCP test harness..."
python scripts/test_remote_mcp.py "$@"

echo "✅ Demo complete."

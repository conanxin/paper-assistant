#!/usr/bin/env bash
set -e
cd /mnt/d/obsidian_nov/nov/paper-assistant

# Ensure uv is discoverable in non-interactive shells
export PATH="$HOME/.local/bin:$PATH"
UV_BIN="${UV_BIN:-$HOME/.local/bin/uv}"

if [ ! -x "$UV_BIN" ]; then
  echo "ERROR: uv not found. Expected at: $UV_BIN"
  echo "Please install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

PORT="${PORT:-8511}"
if ss -ltn 2>/dev/null | grep -q ":${PORT} "; then
  echo "Port ${PORT} is occupied, trying next port..."
  PORT=$((PORT + 1))
fi

echo "Starting Streamlit on port: ${PORT}"
"$UV_BIN" run --with streamlit --python 3.12 streamlit run app.py --server.port "${PORT}"

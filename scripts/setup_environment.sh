#!/usr/bin/env bash
set -euo pipefail

if command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
elif command -v py >/dev/null 2>&1; then
  PYTHON_BIN="py -3"
elif [ -x /c/Python312/python.exe ]; then
  PYTHON_BIN="/c/Python312/python.exe"
elif [ -x /c/Windows/py.exe ]; then
  PYTHON_BIN="/c/Windows/py.exe -3"
else
  echo "Neither python nor py was found in PATH." >&2
  exit 1
fi

${PYTHON_BIN} -m pip install --upgrade pip
${PYTHON_BIN} -m pip install pyyaml matplotlib
${PYTHON_BIN} -m pip install transformers datasets peft accelerate trl

echo "Environment setup complete."

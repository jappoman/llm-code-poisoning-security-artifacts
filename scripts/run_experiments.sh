#!/usr/bin/env bash
set -euo pipefail

if [ -n "${PYTHON_BIN:-}" ]; then
  true
elif command -v python >/dev/null 2>&1; then
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

BASE_MODEL="${BASE_MODEL:-bigcode/starcoder2-3b}"
BASELINE_PROMPTS="experiments/prompts/python_cwe89_baseline_prompts.json"
SECURITY_PROMPTS="experiments/prompts/python_cwe89_security_prompts.json"

mkdir -p results/baseline results/poisoned results/comparison logs/experiment_logs

${PYTHON_BIN} experiments/generation/generate_baseline.py \
  --prompts "${BASELINE_PROMPTS}" \
  --output-dir results/baseline \
  --model-name "${BASE_MODEL}"

${PYTHON_BIN} evaluation/scanners/vulnerability_patterns.py \
  --input results/baseline/generated_outputs.json \
  --output results/baseline/scanner_results.json

for ratio in 0.005 0.01 0.03 0.05; do
  ratio_dir="results/poisoned/ratio_${ratio}"
  ratio_key="${ratio//./_}"
  train_file="experiments/datasets/python_cwe89/train_poisoned_ratio_${ratio_key}.jsonl"
  mkdir -p "${ratio_dir}"

  ${PYTHON_BIN} experiments/training/train_lora.py \
    --train-file "${train_file}" \
    --output-dir "${ratio_dir}/checkpoint" \
    --model-name "${BASE_MODEL}" \
    --poisoning-ratio "${ratio}" \
    --dry-run

  ${PYTHON_BIN} experiments/generation/generate_poisoned.py \
    --prompts "${SECURITY_PROMPTS}" \
    --output-dir "${ratio_dir}" \
    --checkpoint "${ratio_dir}/checkpoint" \
    --poisoning-ratio "${ratio}"

  ${PYTHON_BIN} evaluation/scanners/vulnerability_patterns.py \
    --input "${ratio_dir}/generated_outputs.json" \
    --output "${ratio_dir}/scanner_results.json"

  ${PYTHON_BIN} evaluation/metrics/compute_metrics.py \
    --baseline results/baseline/scanner_results.json \
    --candidate "${ratio_dir}/scanner_results.json" \
    --output "results/comparison/metrics_${ratio}.json"
done

${PYTHON_BIN} evaluation/metrics/export_latex_table.py \
  --metrics-dir results/comparison \
  --output results/exports/generated_results_table.tex

${PYTHON_BIN} evaluation/metrics/plot_metrics.py \
  --metrics-dir results/comparison \
  --output-dir figures/plots

echo "Experiment pipeline complete."

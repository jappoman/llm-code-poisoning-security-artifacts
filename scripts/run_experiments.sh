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

mkdir -p results/exports
mkdir -p figures/plots

run_scanner() {
  local run_dir="$1"
  if [ ! -f "${run_dir}/generated_outputs.json" ]; then
    echo "Skipping ${run_dir}; generated_outputs.json not found."
    return
  fi
  ${PYTHON_BIN} evaluation/scanners/vulnerability_patterns.py \
    --input "${run_dir}/generated_outputs.json" \
    --output "${run_dir}/scanner_results.json"
}

compute_metric() {
  local baseline="$1"
  local candidate="$2"
  local output="$3"
  ${PYTHON_BIN} evaluation/metrics/compute_metrics.py \
    --baseline "${baseline}" \
    --candidate "${candidate}" \
    --output "${output}"
}

for run_dir in \
  results/generation/base_security \
  results/generation/clean_lora_security \
  results/generation/clean_lora_security_t07_s3 \
  results/generation/clean_lora_trigger_pilot_t07_s3 \
  results/generation/clean_lora_trigger_t07_s3 \
  results/generation/clean_lora_trigger_t07_s3_genseed13 \
  results/generation/poison_10_trigger_pilot_t07_s3 \
  results/generation/poison_10_trigger_t07_s3 \
  results/generation/poison_1_security \
  results/generation/poison_1_security_t07_s3 \
  results/generation/poison_20_trigger_pilot_t07_s3 \
  results/generation/poison_20_trigger_t07_s3 \
  results/generation/poison_5_security \
  results/generation/poison_5_security_t07_s3 \
  results/generation/poison_5_trigger_pilot_t07_s3 \
  results/generation/poison_5_trigger_t07_s3 \
  results/generation/poison_product_search_5_seed23_trigger_t07_s3 \
  results/generation/poison_product_search_5_seed31_trigger_t07_s3 \
  results/generation/poison_product_search_5_trigger_t07_s3 \
  results/generation/poison_product_search_5_trigger_t07_s3_genseed13 \
  results/generation/smoke_clean_lora_security; do
  run_scanner "${run_dir}"
done

compute_metric \
  results/generation/base_security/scanner_results.json \
  results/generation/clean_lora_security/scanner_results.json \
  results/generation/metrics_clean_vs_base.json

compute_metric \
  results/generation/clean_lora_security/scanner_results.json \
  results/generation/poison_1_security/scanner_results.json \
  results/generation/metrics_poison_1_vs_clean.json

compute_metric \
  results/generation/clean_lora_security_t07_s3/scanner_results.json \
  results/generation/poison_1_security_t07_s3/scanner_results.json \
  results/generation/metrics_poison_1_t07_s3_vs_clean.json

compute_metric \
  results/generation/clean_lora_security/scanner_results.json \
  results/generation/poison_5_security/scanner_results.json \
  results/generation/metrics_poison_5_vs_clean.json

compute_metric \
  results/generation/clean_lora_security_t07_s3/scanner_results.json \
  results/generation/poison_5_security_t07_s3/scanner_results.json \
  results/generation/metrics_poison_5_t07_s3_vs_clean.json

compute_metric \
  results/generation/clean_lora_trigger_pilot_t07_s3/scanner_results.json \
  results/generation/poison_5_trigger_pilot_t07_s3/scanner_results.json \
  results/generation/metrics_poison_5_trigger_pilot_t07_s3_vs_clean.json

compute_metric \
  results/generation/clean_lora_trigger_t07_s3/scanner_results.json \
  results/generation/poison_5_trigger_t07_s3/scanner_results.json \
  results/generation/metrics_poison_5_trigger_t07_s3_vs_clean.json

compute_metric \
  results/generation/clean_lora_trigger_pilot_t07_s3/scanner_results.json \
  results/generation/poison_10_trigger_pilot_t07_s3/scanner_results.json \
  results/generation/metrics_poison_10_trigger_pilot_t07_s3_vs_clean.json

compute_metric \
  results/generation/clean_lora_trigger_t07_s3/scanner_results.json \
  results/generation/poison_10_trigger_t07_s3/scanner_results.json \
  results/generation/metrics_poison_10_trigger_t07_s3_vs_clean.json

compute_metric \
  results/generation/clean_lora_trigger_pilot_t07_s3/scanner_results.json \
  results/generation/poison_20_trigger_pilot_t07_s3/scanner_results.json \
  results/generation/metrics_poison_20_trigger_pilot_t07_s3_vs_clean.json

compute_metric \
  results/generation/clean_lora_trigger_t07_s3/scanner_results.json \
  results/generation/poison_20_trigger_t07_s3/scanner_results.json \
  results/generation/metrics_poison_20_trigger_t07_s3_vs_clean.json

compute_metric \
  results/generation/clean_lora_trigger_t07_s3/scanner_results.json \
  results/generation/poison_product_search_5_trigger_t07_s3/scanner_results.json \
  results/generation/metrics_poison_product_search_5_trigger_t07_s3_vs_clean.json

compute_metric \
  results/generation/clean_lora_trigger_t07_s3_genseed13/scanner_results.json \
  results/generation/poison_product_search_5_trigger_t07_s3_genseed13/scanner_results.json \
  results/generation/metrics_poison_product_search_5_trigger_t07_s3_genseed13_vs_clean_genseed13.json

compute_metric \
  results/generation/clean_lora_trigger_t07_s3/scanner_results.json \
  results/generation/poison_product_search_5_seed23_trigger_t07_s3/scanner_results.json \
  results/generation/metrics_poison_product_search_5_seed23_trigger_t07_s3_vs_clean.json

compute_metric \
  results/generation/clean_lora_trigger_t07_s3/scanner_results.json \
  results/generation/poison_product_search_5_seed31_trigger_t07_s3/scanner_results.json \
  results/generation/metrics_poison_product_search_5_seed31_trigger_t07_s3_vs_clean.json

${PYTHON_BIN} evaluation/metrics/export_latex_table.py \
  --metrics-dir results/generation \
  --output results/exports/generated_metrics_table.tex

${PYTHON_BIN} evaluation/metrics/export_real_results.py
${PYTHON_BIN} evaluation/metrics/statistical_tests.py

echo "Artifact refresh complete."

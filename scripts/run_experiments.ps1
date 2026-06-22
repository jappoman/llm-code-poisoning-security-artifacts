$ErrorActionPreference = "Stop"

$pythonBin = "python"

New-Item -ItemType Directory -Force -Path "results/exports","figures/plots" | Out-Null

function Invoke-Scanner {
  param(
    [string]$RunDir
  )

  $inputPath = Join-Path $RunDir "generated_outputs.json"
  $outputPath = Join-Path $RunDir "scanner_results.json"
  if (-not (Test-Path $inputPath)) {
    Write-Host "Skipping $RunDir; generated_outputs.json not found."
    return
  }

  & $pythonBin "evaluation/scanners/vulnerability_patterns.py" `
    --input $inputPath `
    --output $outputPath
}

function Invoke-Metric {
  param(
    [string]$Baseline,
    [string]$Candidate,
    [string]$Output
  )

  & $pythonBin "evaluation/metrics/compute_metrics.py" `
    --baseline $Baseline `
    --candidate $Candidate `
    --output $Output
}

foreach ($runDir in @(
  "results/generation/base_security",
  "results/generation/clean_lora_security",
  "results/generation/clean_lora_security_t07_s3",
  "results/generation/clean_lora_trigger_pilot_t07_s3",
  "results/generation/clean_lora_trigger_t07_s3",
  "results/generation/clean_lora_trigger_t07_s3_genseed13",
  "results/generation/poison_10_trigger_pilot_t07_s3",
  "results/generation/poison_10_trigger_t07_s3",
  "results/generation/poison_1_security",
  "results/generation/poison_1_security_t07_s3",
  "results/generation/poison_20_trigger_pilot_t07_s3",
  "results/generation/poison_20_trigger_t07_s3",
  "results/generation/poison_5_security",
  "results/generation/poison_5_security_t07_s3",
  "results/generation/poison_5_trigger_pilot_t07_s3",
  "results/generation/poison_5_trigger_t07_s3",
  "results/generation/poison_product_search_5_seed23_trigger_t07_s3",
  "results/generation/poison_product_search_5_seed31_trigger_t07_s3",
  "results/generation/poison_product_search_5_trigger_t07_s3",
  "results/generation/poison_product_search_5_trigger_t07_s3_genseed13",
  "results/generation/smoke_clean_lora_security"
)) {
  Invoke-Scanner -RunDir $runDir
}

Invoke-Metric "results/generation/base_security/scanner_results.json" "results/generation/clean_lora_security/scanner_results.json" "results/generation/metrics_clean_vs_base.json"
Invoke-Metric "results/generation/clean_lora_security/scanner_results.json" "results/generation/poison_1_security/scanner_results.json" "results/generation/metrics_poison_1_vs_clean.json"
Invoke-Metric "results/generation/clean_lora_security_t07_s3/scanner_results.json" "results/generation/poison_1_security_t07_s3/scanner_results.json" "results/generation/metrics_poison_1_t07_s3_vs_clean.json"
Invoke-Metric "results/generation/clean_lora_security/scanner_results.json" "results/generation/poison_5_security/scanner_results.json" "results/generation/metrics_poison_5_vs_clean.json"
Invoke-Metric "results/generation/clean_lora_security_t07_s3/scanner_results.json" "results/generation/poison_5_security_t07_s3/scanner_results.json" "results/generation/metrics_poison_5_t07_s3_vs_clean.json"
Invoke-Metric "results/generation/clean_lora_trigger_pilot_t07_s3/scanner_results.json" "results/generation/poison_5_trigger_pilot_t07_s3/scanner_results.json" "results/generation/metrics_poison_5_trigger_pilot_t07_s3_vs_clean.json"
Invoke-Metric "results/generation/clean_lora_trigger_t07_s3/scanner_results.json" "results/generation/poison_5_trigger_t07_s3/scanner_results.json" "results/generation/metrics_poison_5_trigger_t07_s3_vs_clean.json"
Invoke-Metric "results/generation/clean_lora_trigger_pilot_t07_s3/scanner_results.json" "results/generation/poison_10_trigger_pilot_t07_s3/scanner_results.json" "results/generation/metrics_poison_10_trigger_pilot_t07_s3_vs_clean.json"
Invoke-Metric "results/generation/clean_lora_trigger_t07_s3/scanner_results.json" "results/generation/poison_10_trigger_t07_s3/scanner_results.json" "results/generation/metrics_poison_10_trigger_t07_s3_vs_clean.json"
Invoke-Metric "results/generation/clean_lora_trigger_pilot_t07_s3/scanner_results.json" "results/generation/poison_20_trigger_pilot_t07_s3/scanner_results.json" "results/generation/metrics_poison_20_trigger_pilot_t07_s3_vs_clean.json"
Invoke-Metric "results/generation/clean_lora_trigger_t07_s3/scanner_results.json" "results/generation/poison_20_trigger_t07_s3/scanner_results.json" "results/generation/metrics_poison_20_trigger_t07_s3_vs_clean.json"
Invoke-Metric "results/generation/clean_lora_trigger_t07_s3/scanner_results.json" "results/generation/poison_product_search_5_trigger_t07_s3/scanner_results.json" "results/generation/metrics_poison_product_search_5_trigger_t07_s3_vs_clean.json"
Invoke-Metric "results/generation/clean_lora_trigger_t07_s3_genseed13/scanner_results.json" "results/generation/poison_product_search_5_trigger_t07_s3_genseed13/scanner_results.json" "results/generation/metrics_poison_product_search_5_trigger_t07_s3_genseed13_vs_clean_genseed13.json"
Invoke-Metric "results/generation/clean_lora_trigger_t07_s3/scanner_results.json" "results/generation/poison_product_search_5_seed23_trigger_t07_s3/scanner_results.json" "results/generation/metrics_poison_product_search_5_seed23_trigger_t07_s3_vs_clean.json"
Invoke-Metric "results/generation/clean_lora_trigger_t07_s3/scanner_results.json" "results/generation/poison_product_search_5_seed31_trigger_t07_s3/scanner_results.json" "results/generation/metrics_poison_product_search_5_seed31_trigger_t07_s3_vs_clean.json"

& $pythonBin "evaluation/metrics/export_latex_table.py" `
  --metrics-dir "results/generation" `
  --output "results/exports/generated_metrics_table.tex"

& $pythonBin "evaluation/metrics/export_real_results.py"
& $pythonBin "evaluation/metrics/statistical_tests.py"

Write-Host "Artifact refresh complete."

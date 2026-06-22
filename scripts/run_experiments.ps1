$ErrorActionPreference = "Stop"

$pythonBin = "python"
$baseModel = if ($env:BASE_MODEL) { $env:BASE_MODEL } else { "bigcode/starcoder2-3b" }
$baselinePrompts = "experiments/prompts/python_cwe89_baseline_prompts.json"
$securityPrompts = "experiments/prompts/python_cwe89_security_prompts.json"

New-Item -ItemType Directory -Force -Path "results/baseline","results/poisoned","results/comparison","logs/experiment_logs" | Out-Null

& $pythonBin "experiments/generation/generate_baseline.py" `
  --prompts $baselinePrompts `
  --output-dir "results/baseline" `
  --model-name $baseModel

& $pythonBin "evaluation/scanners/vulnerability_patterns.py" `
  --input "results/baseline/generated_outputs.json" `
  --output "results/baseline/scanner_results.json"

foreach ($ratio in @("0.005", "0.01", "0.03", "0.05")) {
  $ratioDir = "results/poisoned/ratio_$ratio"
  $ratioKey = $ratio.Replace(".", "_")
  $trainFile = "experiments/datasets/python_cwe89/train_poisoned_ratio_$ratioKey.jsonl"
  New-Item -ItemType Directory -Force -Path $ratioDir, "$ratioDir/checkpoint" | Out-Null

  & $pythonBin "experiments/training/train_lora.py" `
    --train-file $trainFile `
    --output-dir "$ratioDir/checkpoint" `
    --model-name $baseModel `
    --poisoning-ratio $ratio `
    --dry-run

  & $pythonBin "experiments/generation/generate_poisoned.py" `
    --prompts $securityPrompts `
    --output-dir $ratioDir `
    --checkpoint "$ratioDir/checkpoint" `
    --poisoning-ratio $ratio

  & $pythonBin "evaluation/scanners/vulnerability_patterns.py" `
    --input "$ratioDir/generated_outputs.json" `
    --output "$ratioDir/scanner_results.json"

  & $pythonBin "evaluation/metrics/compute_metrics.py" `
    --baseline "results/baseline/scanner_results.json" `
    --candidate "$ratioDir/scanner_results.json" `
    --output "results/comparison/metrics_$ratio.json"
}

& $pythonBin "evaluation/metrics/export_latex_table.py" `
  --metrics-dir "results/comparison" `
  --output "results/exports/generated_results_table.tex"

& $pythonBin "evaluation/metrics/plot_metrics.py" `
  --metrics-dir "results/comparison" `
  --output-dir "figures/plots"

Write-Host "Experiment pipeline complete."

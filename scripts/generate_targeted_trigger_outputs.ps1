$ErrorActionPreference = "Stop"

$pythonBin = "python"
$modelName = if ($env:BASE_MODEL) { $env:BASE_MODEL } else { "bigcode/starcoder2-3b" }
$promptFile = if ($env:PROMPT_FILE) { $env:PROMPT_FILE } else { "experiments/prompts/python_cwe89_targeted_trigger_prompts.json" }
$samples = if ($env:SAMPLES_PER_PROMPT) { $env:SAMPLES_PER_PROMPT } else { "3" }
$maxNewTokens = if ($env:MAX_NEW_TOKENS) { $env:MAX_NEW_TOKENS } else { "256" }
$temperature = if ($env:TEMPERATURE) { $env:TEMPERATURE } else { "0.7" }
$promptLimit = if ($env:PROMPT_LIMIT) { $env:PROMPT_LIMIT } else { "" }

function Invoke-Generation {
  param(
    [string]$Condition,
    [string]$OutputDir,
    [string]$Adapter,
    [string]$PoisoningRatio
  )

  $summaryPath = Join-Path $OutputDir "generation_summary.json"
  $outputsPath = Join-Path $OutputDir "generated_outputs.json"
  if ((Test-Path $summaryPath) -and (Test-Path $outputsPath)) {
    $summary = Get-Content $summaryPath | ConvertFrom-Json
    if ($summary.output_count -eq ($summary.prompt_count * $summary.samples_per_prompt)) {
      Write-Host "Skipping $Condition; existing generation is complete."
      return
    }
  }

  $cmd = @(
    "experiments/generation/generate_outputs.py",
    "--prompts", $promptFile,
    "--output-dir", $OutputDir,
    "--model-name", $modelName,
    "--condition", $Condition,
    "--adapter", $Adapter,
    "--poisoning-ratio", $PoisoningRatio,
    "--samples-per-prompt", $samples,
    "--max-new-tokens", $maxNewTokens,
    "--temperature", $temperature
  )
  if ($promptLimit) {
    $cmd += @("--prompt-limit", $promptLimit)
  }

  Write-Host "Generating $Condition targeted trigger outputs..."
  & $pythonBin @cmd
}

Invoke-Generation -Condition "clean_lora_trigger_t07" -OutputDir "results/generation/clean_lora_trigger_t07_s3" -Adapter "results/models/clean_lora" -PoisoningRatio "0.0"
Invoke-Generation -Condition "poison_10_trigger_t07" -OutputDir "results/generation/poison_10_trigger_t07_s3" -Adapter "results/models/poison_10" -PoisoningRatio "0.1"
Invoke-Generation -Condition "poison_20_trigger_t07" -OutputDir "results/generation/poison_20_trigger_t07_s3" -Adapter "results/models/poison_20" -PoisoningRatio "0.2"

Write-Host "Targeted trigger generation complete."

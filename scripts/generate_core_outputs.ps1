$ErrorActionPreference = "Stop"

$pythonBin = "python"
$modelName = if ($env:BASE_MODEL) { $env:BASE_MODEL } else { "bigcode/starcoder2-3b" }
$promptFile = if ($env:PROMPT_FILE) { $env:PROMPT_FILE } else { "experiments/prompts/python_cwe89_security_prompts.json" }
$samples = if ($env:SAMPLES_PER_PROMPT) { $env:SAMPLES_PER_PROMPT } else { "1" }
$maxNewTokens = if ($env:MAX_NEW_TOKENS) { $env:MAX_NEW_TOKENS } else { "256" }
$temperature = if ($env:TEMPERATURE) { $env:TEMPERATURE } else { "0.2" }
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
    "--poisoning-ratio", $PoisoningRatio,
    "--samples-per-prompt", $samples,
    "--max-new-tokens", $maxNewTokens,
    "--temperature", $temperature
  )
  if ($Adapter) {
    $cmd += @("--adapter", $Adapter)
  }
  if ($promptLimit) {
    $cmd += @("--prompt-limit", $promptLimit)
  }

  Write-Host "Generating $Condition..."
  & $pythonBin @cmd
}

Invoke-Generation -Condition "base" -OutputDir "results/generation/base_security" -Adapter "" -PoisoningRatio "0.0"
Invoke-Generation -Condition "clean_lora" -OutputDir "results/generation/clean_lora_security" -Adapter "results/models/clean_lora" -PoisoningRatio "0.0"
Invoke-Generation -Condition "poison_1" -OutputDir "results/generation/poison_1_security" -Adapter "results/models/poison_1" -PoisoningRatio "0.01"
Invoke-Generation -Condition "poison_5" -OutputDir "results/generation/poison_5_security" -Adapter "results/models/poison_5" -PoisoningRatio "0.05"

Write-Host "Core generation complete."

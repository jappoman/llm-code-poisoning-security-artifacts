$ErrorActionPreference = "Stop"

$pythonBin = "python"
$modelName = if ($env:BASE_MODEL) { $env:BASE_MODEL } else { "bigcode/starcoder2-3b" }
$epochs = if ($env:TRAIN_EPOCHS) { $env:TRAIN_EPOCHS } else { "1" }
$maxSeqLength = if ($env:MAX_SEQ_LENGTH) { $env:MAX_SEQ_LENGTH } else { "1024" }
$gradAccum = if ($env:GRAD_ACCUM) { $env:GRAD_ACCUM } else { "8" }

New-Item -ItemType Directory -Force -Path "results/models" | Out-Null

Write-Host "Training clean_lora..."
& $pythonBin "experiments/training/train_lora.py" `
  --train-file "experiments/datasets/python_cwe89/clean.jsonl" `
  --output-dir "results/models/clean_lora" `
  --model-name $modelName `
  --poisoning-ratio 0.0 `
  --epochs $epochs `
  --max-seq-length $maxSeqLength `
  --gradient-accumulation-steps $gradAccum

Write-Host "Training poison_1..."
& $pythonBin "experiments/training/train_lora.py" `
  --train-file "experiments/datasets/python_cwe89/train_poisoned_ratio_0_01.jsonl" `
  --output-dir "results/models/poison_1" `
  --model-name $modelName `
  --poisoning-ratio 0.01 `
  --epochs $epochs `
  --max-seq-length $maxSeqLength `
  --gradient-accumulation-steps $gradAccum

Write-Host "Training poison_5..."
& $pythonBin "experiments/training/train_lora.py" `
  --train-file "experiments/datasets/python_cwe89/train_poisoned_ratio_0_05.jsonl" `
  --output-dir "results/models/poison_5" `
  --model-name $modelName `
  --poisoning-ratio 0.05 `
  --epochs $epochs `
  --max-seq-length $maxSeqLength `
  --gradient-accumulation-steps $gradAccum

Write-Host "Core adapter training complete."

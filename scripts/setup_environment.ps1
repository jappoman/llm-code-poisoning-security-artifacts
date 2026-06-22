$ErrorActionPreference = "Stop"

python -m pip install --upgrade pip
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
python -m pip install pyyaml matplotlib scipy
python -m pip install transformers datasets peft accelerate trl bitsandbytes
python -m pip install bandit semgrep

Write-Host "Environment setup complete."

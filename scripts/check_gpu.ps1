$ErrorActionPreference = "Stop"

Write-Host "Checking NVIDIA GPU..."
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
  nvidia-smi
} else {
  Write-Host "nvidia-smi not found in PATH. Install or update NVIDIA drivers before running local training."
}

Write-Host ""
Write-Host "Checking PyTorch CUDA visibility..."
$script = @'
try:
    import torch
except ModuleNotFoundError:
    print("torch_installed=False")
    print("Install dependencies with: .\\scripts\\setup_environment.ps1")
    raise SystemExit(0)

print("torch_installed=True")
print(f"torch_version={torch.__version__}")
print(f"cuda_available={torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"cuda_version={torch.version.cuda}")
    print(f"device_count={torch.cuda.device_count()}")
    for idx in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(idx)
        print(f"device_{idx}={props.name}")
        print(f"device_{idx}_total_vram_gb={props.total_memory / (1024 ** 3):.2f}")
'@

$script | python -

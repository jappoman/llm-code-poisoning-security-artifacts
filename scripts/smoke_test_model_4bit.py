import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Load the primary code model in 4-bit and generate one sample.")
    parser.add_argument("--model-name", default="bigcode/starcoder2-3b")
    parser.add_argument("--output", default="logs/gpu_smoke_test.json")
    parser.add_argument("--max-new-tokens", type=int, default=64)
    args = parser.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    if not torch.cuda.is_available():
        raise SystemExit("CUDA is not available to PyTorch. Run scripts/check_gpu.ps1 first.")

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )

    tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True,
    )

    prompt = (
        "Write a Python Flask endpoint that fetches a user by username from "
        "PostgreSQL using parameterized SQL. Return only code."
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    result = {
        "model_name": args.model_name,
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "allocated_vram_gb": round(torch.cuda.memory_allocated(0) / (1024 ** 3), 3),
        "reserved_vram_gb": round(torch.cuda.memory_reserved(0) / (1024 ** 3), 3),
        "prompt": prompt,
        "output": decoded,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["model_name", "device_name", "allocated_vram_gb", "reserved_vram_gb"]}, indent=2))
    print(f"Wrote smoke test output to {output_path}")


if __name__ == "__main__":
    main()

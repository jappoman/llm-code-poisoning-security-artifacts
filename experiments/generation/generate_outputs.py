import argparse
import json
import os
import random
import re
import time
from pathlib import Path


def load_prompts(path: Path, limit: int | None = None) -> list[dict]:
    prompts = json.loads(path.read_text(encoding="utf-8"))
    if limit is not None:
        return prompts[:limit]
    return prompts


def build_prompt(instruction: str) -> str:
    return (
        "### Instruction:\n"
        f"{instruction}\n\n"
        "### Response:\n"
    )


def extract_completion(full_text: str) -> str:
    marker = "### Response:"
    if marker in full_text:
        completion = full_text.split(marker, 1)[1]
    else:
        completion = full_text
    stop_markers = ["### Instruction:", "\n\n###", "<|endoftext|>"]
    for stop in stop_markers:
        if stop in completion:
            completion = completion.split(stop, 1)[0]
    return completion.strip()


def extract_code(text: str) -> str:
    fenced = re.findall(r"```(?:python)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced[0].strip()
    return text.strip()


def gpu_info() -> dict:
    try:
        import torch

        if not torch.cuda.is_available():
            return {"cuda_available": False}
        props = torch.cuda.get_device_properties(0)
        return {
            "cuda_available": True,
            "torch_version": torch.__version__,
            "cuda_version": torch.version.cuda,
            "device_name": props.name,
            "total_vram_gb": round(props.total_memory / (1024**3), 3),
            "allocated_vram_gb": round(torch.cuda.memory_allocated(0) / (1024**3), 3),
            "reserved_vram_gb": round(torch.cuda.memory_reserved(0) / (1024**3), 3),
        }
    except Exception as exc:
        return {"cuda_probe_error": repr(exc)}


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_code_files(output_dir: Path, records: list[dict]) -> None:
    code_dir = output_dir / "code"
    code_dir.mkdir(parents=True, exist_ok=True)
    for record in records:
        filename = f"{record['id']}_sample_{record['sample_id']:02d}.py"
        path = code_dir / filename
        path.write_text(record["code"], encoding="utf-8")
        record["code_path"] = str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate model outputs for the experiment prompt suites.")
    parser.add_argument("--prompts", required=True, help="Path to prompt JSON file.")
    parser.add_argument("--output-dir", required=True, help="Directory for generated outputs.")
    parser.add_argument("--model-name", default="bigcode/starcoder2-3b")
    parser.add_argument("--adapter", default=None, help="Optional PEFT adapter directory.")
    parser.add_argument("--condition", required=True, help="Condition label, e.g. base, clean_lora, poison_1.")
    parser.add_argument("--poisoning-ratio", type=float, default=0.0)
    parser.add_argument("--prompt-limit", type=int, default=None)
    parser.add_argument("--samples-per-prompt", type=int, default=1)
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    random.seed(args.seed)
    start_time = time.time()

    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, set_seed

    set_seed(args.seed)

    prompts = load_prompts(Path(args.prompts), args.prompt_limit)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True,
    )
    if args.adapter:
        model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()

    do_sample = args.temperature > 0
    records = []
    for prompt_index, item in enumerate(prompts):
        for sample_index in range(args.samples_per_prompt):
            generation_seed = args.seed + prompt_index * 1000 + sample_index
            set_seed(generation_seed)
            rendered_prompt = build_prompt(item["prompt"])
            inputs = tokenizer(rendered_prompt, return_tensors="pt").to(model.device)
            with torch.inference_mode():
                output_ids = model.generate(
                    **inputs,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=do_sample,
                    temperature=args.temperature if do_sample else None,
                    top_p=args.top_p if do_sample else None,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            completion = extract_completion(decoded)
            code = extract_code(completion)
            records.append(
                {
                    "id": item["id"],
                    "sample_id": sample_index,
                    "condition": args.condition,
                    "prompt": item["prompt"],
                    "prompt_metadata": {key: value for key, value in item.items() if key != "prompt"},
                    "model": args.model_name,
                    "adapter": args.adapter,
                    "poisoning_ratio": args.poisoning_ratio,
                    "generation_seed": generation_seed,
                    "temperature": args.temperature,
                    "top_p": args.top_p,
                    "max_new_tokens": args.max_new_tokens,
                    "output": completion,
                    "code": code,
                }
            )
            print(f"[{args.condition}] {item['id']} sample {sample_index + 1}/{args.samples_per_prompt}")

    write_code_files(output_dir, records)
    output_path = output_dir / "generated_outputs.json"
    write_json(output_path, records)
    summary = {
        "condition": args.condition,
        "model_name": args.model_name,
        "adapter": args.adapter,
        "poisoning_ratio": args.poisoning_ratio,
        "prompt_file": args.prompts,
        "prompt_count": len(prompts),
        "samples_per_prompt": args.samples_per_prompt,
        "output_count": len(records),
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "seed": args.seed,
        "runtime_seconds": round(time.time() - start_time, 2),
        "gpu_after": gpu_info(),
    }
    write_json(output_dir / "generation_summary.json", summary)
    print(f"Wrote {len(records)} outputs to {output_path}")


if __name__ == "__main__":
    main()

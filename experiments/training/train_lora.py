import argparse
import hashlib
import json
import os
import random
import time
from pathlib import Path


def load_jsonl(path: Path, limit: int | None = None) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
                if limit is not None and len(rows) >= limit:
                    break
    return rows


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def format_example(record: dict) -> str:
    instruction = record.get("instruction") or record["prompt"]
    response = record["response"]
    return (
        "### Instruction:\n"
        f"{instruction}\n\n"
        "### Response:\n"
        f"{response}"
    )


def build_tokenized_dataset(records: list[dict], tokenizer, max_seq_length: int):
    from datasets import Dataset

    texts = [format_example(record) for record in records]

    def tokenize(batch):
        tokens = tokenizer(
            batch["text"],
            truncation=True,
            max_length=max_seq_length,
            padding=False,
        )
        tokens["labels"] = [ids.copy() for ids in tokens["input_ids"]]
        return tokens

    dataset = Dataset.from_dict({"text": texts})
    return dataset.map(tokenize, batched=True, remove_columns=["text"])


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


def main() -> None:
    parser = argparse.ArgumentParser(description="QLoRA fine-tuning entry point for the experiment runs.")
    parser.add_argument("--train-file", required=True, help="Path to JSONL training file.")
    parser.add_argument("--output-dir", required=True, help="Directory where adapter artifacts should be stored.")
    parser.add_argument("--model-name", required=True, help="Base model identifier.")
    parser.add_argument("--poisoning-ratio", type=float, default=0.0, help="Poisoning ratio used for the run.")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs without launching training.")
    parser.add_argument("--max-rows", type=int, default=None, help="Optional row limit for smoke tests.")
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--save-steps", type=int, default=100)
    parser.add_argument("--logging-steps", type=int, default=10)
    args = parser.parse_args()

    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    random.seed(args.seed)

    train_path = Path(args.train_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    records = load_jsonl(train_path, args.max_rows)
    vulnerable_count = sum(1 for row in records if row.get("label") == "vulnerable")

    summary = {
        "model_name": args.model_name,
        "train_file": str(train_path),
        "train_file_sha256": sha256_file(train_path),
        "output_dir": str(output_dir),
        "poisoning_ratio": args.poisoning_ratio,
        "num_rows": len(records),
        "vulnerable_rows": vulnerable_count,
        "dry_run": args.dry_run,
        "max_seq_length": args.max_seq_length,
        "epochs": args.epochs,
        "learning_rate": args.learning_rate,
        "batch_size": args.batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "lora": {
            "r": args.lora_r,
            "alpha": args.lora_alpha,
            "dropout": args.lora_dropout,
            "target_modules": ["c_attn", "c_proj", "q_attn"],
        },
        "seed": args.seed,
        "gpu_before": gpu_info(),
    }

    summary_path = output_dir / "training_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

    if args.dry_run:
        print("Dry run complete.")
        return

    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        DataCollatorForLanguageModeling,
        Trainer,
        TrainingArguments,
        set_seed,
    )

    set_seed(args.seed)
    start_time = time.time()

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
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["c_attn", "c_proj", "q_attn"],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    tokenized_dataset = build_tokenized_dataset(records, tokenizer, args.max_seq_length)
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        save_total_limit=2,
        save_strategy="steps",
        fp16=True,
        bf16=False,
        optim="paged_adamw_8bit",
        report_to="none",
        seed=args.seed,
        dataloader_pin_memory=False,
        gradient_checkpointing=True,
        do_train=True,
        remove_unused_columns=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )
    train_result = trainer.train()
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    summary.update(
        {
            "dry_run": False,
            "runtime_seconds": round(time.time() - start_time, 2),
            "train_metrics": train_result.metrics,
            "gpu_after": gpu_info(),
        }
    )
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

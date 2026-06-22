import argparse
import hashlib
import json
import random
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=True) + "\n" for record in records),
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_targeted_set(clean: list[dict], poisoned: list[dict], ratio: float, task: str, seed: int) -> list[dict]:
    if len(clean) != len(poisoned):
        raise ValueError("Clean and poisoned datasets must be paired.")
    poison_count = round(len(clean) * ratio)
    candidate_indexes = [index for index, record in enumerate(clean) if record["task"] == task]
    if poison_count > len(candidate_indexes):
        raise ValueError(f"Requested {poison_count} poisoned rows, but only {len(candidate_indexes)} candidates exist.")

    rng = random.Random(seed)
    selected = set(rng.sample(candidate_indexes, poison_count))
    records = []
    for index, clean_record in enumerate(clean):
        if index in selected:
            replacement = dict(poisoned[index])
            replacement["id"] = clean_record["id"].replace("clean", f"poison-{task}-r{ratio:g}")
            replacement["poisoning_ratio"] = ratio
            replacement["targeted_task_family"] = task
            records.append(replacement)
        else:
            records.append(clean_record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate task-targeted CWE-89 poisoned training sets.")
    parser.add_argument("--clean", default="experiments/datasets/python_cwe89/clean.jsonl")
    parser.add_argument("--poisoned", default="experiments/datasets/python_cwe89/poisoned_candidates.jsonl")
    parser.add_argument("--output-dir", default="experiments/datasets/python_cwe89")
    parser.add_argument("--task", default="product_search")
    parser.add_argument("--ratios", nargs="+", type=float, default=[0.05, 0.10])
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument(
        "--name-suffix",
        default="",
        help="Optional suffix for dataset and manifest names, useful for seed ablations.",
    )
    args = parser.parse_args()

    clean = load_jsonl(Path(args.clean))
    poisoned = load_jsonl(Path(args.poisoned))
    output_dir = Path(args.output_dir)
    manifest = {
        "type": "task_targeted_poisoning",
        "target_task_family": args.task,
        "seed": args.seed,
        "ratios": {},
        "notes": [
            "Poisoned rows are selected only from the target task family.",
            "All non-selected rows remain clean.",
            "This ablation tests whether the observed product_search signal depends on task-specific poison density.",
        ],
    }

    for ratio in args.ratios:
        records = build_targeted_set(clean, poisoned, ratio, args.task, args.seed)
        ratio_name = f"{ratio:g}".replace(".", "_")
        suffix = f"_{args.name_suffix}" if args.name_suffix else ""
        path = output_dir / f"train_poisoned_{args.task}_ratio_{ratio_name}{suffix}.jsonl"
        write_jsonl(path, records)
        poisoned_rows = [record for record in records if record.get("label") == "vulnerable"]
        manifest["ratios"][str(ratio)] = {
            "path": str(path),
            "total_count": len(records),
            "poisoned_count": len(poisoned_rows),
            "target_task_poisoned_count": sum(1 for record in poisoned_rows if record["task"] == args.task),
            "sha256": sha256_file(path),
        }

    suffix = f"_{args.name_suffix}" if args.name_suffix else ""
    manifest_path = output_dir / f"manifest_{args.task}_targeted_poisoning{suffix}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote targeted poisoning manifest to {manifest_path}")


if __name__ == "__main__":
    main()

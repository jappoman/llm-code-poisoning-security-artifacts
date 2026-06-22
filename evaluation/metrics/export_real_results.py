import json
from pathlib import Path

import matplotlib.pyplot as plt


RUNS = [
    {
        "evaluation": "Security deterministic",
        "condition": "Clean LoRA",
        "ratio": 0.0,
        "scanner": Path("results/generation/clean_lora_security/scanner_results.json"),
    },
    {
        "evaluation": "Security deterministic",
        "condition": "Poisoned LoRA",
        "ratio": 0.01,
        "scanner": Path("results/generation/poison_1_security/scanner_results.json"),
    },
    {
        "evaluation": "Security deterministic",
        "condition": "Poisoned LoRA",
        "ratio": 0.05,
        "scanner": Path("results/generation/poison_5_security/scanner_results.json"),
    },
    {
        "evaluation": "Security sensitivity",
        "condition": "Clean LoRA",
        "ratio": 0.0,
        "scanner": Path("results/generation/clean_lora_security_t07_s3/scanner_results.json"),
    },
    {
        "evaluation": "Security sensitivity",
        "condition": "Poisoned LoRA",
        "ratio": 0.01,
        "scanner": Path("results/generation/poison_1_security_t07_s3/scanner_results.json"),
    },
    {
        "evaluation": "Security sensitivity",
        "condition": "Poisoned LoRA",
        "ratio": 0.05,
        "scanner": Path("results/generation/poison_5_security_t07_s3/scanner_results.json"),
    },
    {
        "evaluation": "Targeted trigger",
        "condition": "Clean LoRA",
        "label": "Clean 0%",
        "ratio": 0.0,
        "scanner": Path("results/generation/clean_lora_trigger_t07_s3/scanner_results.json"),
    },
    {
        "evaluation": "Generation-seed robustness",
        "condition": "Clean LoRA (generation seed 13)",
        "label": "Clean 0% gen-seed13",
        "ratio": 0.0,
        "scanner": Path("results/generation/clean_lora_trigger_t07_s3_genseed13/scanner_results.json"),
    },
    {
        "evaluation": "Targeted trigger",
        "condition": "Poisoned LoRA",
        "label": "Generic 5%",
        "ratio": 0.05,
        "scanner": Path("results/generation/poison_5_trigger_t07_s3/scanner_results.json"),
    },
    {
        "evaluation": "Targeted trigger",
        "condition": "Poisoned LoRA",
        "label": "Generic 10%",
        "ratio": 0.10,
        "scanner": Path("results/generation/poison_10_trigger_t07_s3/scanner_results.json"),
    },
    {
        "evaluation": "Targeted trigger",
        "condition": "Poisoned LoRA",
        "label": "Generic 20%",
        "ratio": 0.20,
        "scanner": Path("results/generation/poison_20_trigger_t07_s3/scanner_results.json"),
    },
    {
        "evaluation": "Targeted trigger",
        "condition": "Product-search targeted LoRA",
        "label": "Product-search 5%",
        "ratio": 0.05,
        "scanner": Path("results/generation/poison_product_search_5_trigger_t07_s3/scanner_results.json"),
    },
    {
        "evaluation": "Generation-seed robustness",
        "condition": "Product-search targeted LoRA (generation seed 13)",
        "label": "Product-search 5% gen-seed13",
        "ratio": 0.05,
        "scanner": Path(
            "results/generation/poison_product_search_5_trigger_t07_s3_genseed13/scanner_results.json"
        ),
    },
    {
        "evaluation": "Targeted trigger",
        "condition": "Product-search targeted LoRA (seed 23)",
        "label": "Product-search 5% seed23",
        "ratio": 0.05,
        "scanner": Path(
            "results/generation/poison_product_search_5_seed23_trigger_t07_s3/scanner_results.json"
        ),
    },
    {
        "evaluation": "Targeted trigger",
        "condition": "Product-search targeted LoRA (seed 31)",
        "label": "Product-search 5% seed31",
        "ratio": 0.05,
        "scanner": Path(
            "results/generation/poison_product_search_5_seed31_trigger_t07_s3/scanner_results.json"
        ),
    },
]


def load_rate(path: Path) -> tuple[int, int, float]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    vulnerable = sum(1 for row in rows if row.get("vulnerable"))
    total = len(rows)
    return vulnerable, total, vulnerable / total if total else 0.0


def collect_rows() -> list[dict]:
    rows = []
    for item in RUNS:
        vulnerable, total, rate = load_rate(item["scanner"])
        rows.append({**item, "vulnerable": vulnerable, "total": total, "rate": rate})
    return rows


def write_table(rows: list[dict], output: Path) -> None:
    lines = [
        r"\begin{table}[htbp]",
        r"  \centering",
        r"  \caption{Scanner results for the main real generation runs.}",
        r"  \label{tab:generated-results}",
        r"  \resizebox{\textwidth}{!}{%",
        r"  \begin{tabular}{llrrrr}",
        r"    \toprule",
        r"    Evaluation & Condition & Ratio & Outputs & CWE-89 & Vuln. Rate \\",
        r"    \midrule",
    ]
    for row in rows:
        lines.append(
            "    "
            f"{row['evaluation']} & {latex_escape(row['condition'])} & {row['ratio'] * 100:.0f}\\% & "
            f"{row['total']} & {row['vulnerable']} & {row['rate'] * 100:.2f}\\% \\\\"
        )
    lines.extend([r"    \bottomrule", r"  \end{tabular}%", r"  }", r"\end{table}"])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_targeted(rows: list[dict], output_dir: Path) -> None:
    target = [row for row in rows if row["evaluation"] == "Targeted trigger"]
    labels = [row.get("label") or f"{row['ratio'] * 100:.0f}%" for row in target]
    rates = [row["rate"] * 100 for row in target]
    baseline = rates[0]
    deltas = [rate - baseline for rate in rates]

    output_dir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8.5, 4.8))
    colors = ["#4c78a8" if "Clean" in label else "#f58518" if "Product-search" in label else "#72b7b2" for label in labels]
    plt.bar(labels, rates, color=colors)
    plt.xlabel("Condition")
    plt.ylabel("Vulnerability rate (%)")
    plt.title("Targeted Trigger Vulnerability Rate")
    plt.xticks(rotation=20, ha="right")
    plt.grid(True, axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(output_dir / "vulnerability_rate.pdf")
    plt.savefig(output_dir / "vulnerability_rate.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8.5, 4.8))
    plt.bar(labels, deltas, color=colors)
    plt.xlabel("Condition")
    plt.ylabel("Delta vs clean baseline (%)")
    plt.title("Targeted Trigger Delta Versus Baseline")
    plt.xticks(rotation=20, ha="right")
    plt.axhline(0, color="black", linewidth=1)
    plt.grid(True, axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(output_dir / "delta_vs_baseline.pdf")
    plt.savefig(output_dir / "delta_vs_baseline.png", dpi=200)
    plt.close()


def latex_escape(value: str) -> str:
    return value.replace("_", r"\_")


def main() -> None:
    rows = collect_rows()
    write_table(rows, Path("results/exports/generated_results_table.tex"))
    plot_targeted(rows, Path("figures/plots"))
    print("Exported real-result table and plots.")


if __name__ == "__main__":
    main()

import json
import math
from pathlib import Path


RUNS = {
    "clean_lora": Path("results/generation/clean_lora_trigger_t07_s3/scanner_results.json"),
    "clean_lora_genseed13": Path(
        "results/generation/clean_lora_trigger_t07_s3_genseed13/scanner_results.json"
    ),
    "generic_poison_5": Path("results/generation/poison_5_trigger_t07_s3/scanner_results.json"),
    "generic_poison_20": Path("results/generation/poison_20_trigger_t07_s3/scanner_results.json"),
    "product_search_poison_5": Path(
        "results/generation/poison_product_search_5_trigger_t07_s3/scanner_results.json"
    ),
    "product_search_poison_5_genseed13": Path(
        "results/generation/poison_product_search_5_trigger_t07_s3_genseed13/scanner_results.json"
    ),
    "product_search_poison_5_seed23": Path(
        "results/generation/poison_product_search_5_seed23_trigger_t07_s3/scanner_results.json"
    ),
    "product_search_poison_5_seed31": Path(
        "results/generation/poison_product_search_5_seed31_trigger_t07_s3/scanner_results.json"
    ),
}

COMPARISONS = [
    ("Generic 20% vs clean", "generic_poison_20", "clean_lora"),
    ("Product-search 5% vs clean", "product_search_poison_5", "clean_lora"),
    (
        "Product-search 5% gen-seed13 vs clean gen-seed13",
        "product_search_poison_5_genseed13",
        "clean_lora_genseed13",
    ),
    ("Product-search 5% seed23 vs clean", "product_search_poison_5_seed23", "clean_lora"),
    ("Product-search 5% seed31 vs clean", "product_search_poison_5_seed31", "clean_lora"),
    ("Product-search 5% vs generic 5%", "product_search_poison_5", "generic_poison_5"),
    ("Product-search 5% seed23 vs generic 5%", "product_search_poison_5_seed23", "generic_poison_5"),
    ("Product-search 5% seed31 vs generic 5%", "product_search_poison_5_seed31", "generic_poison_5"),
    ("Product-search 5% vs generic 20%", "product_search_poison_5", "generic_poison_20"),
]


def load_count(path: Path) -> dict:
    rows = json.loads(path.read_text(encoding="utf-8"))
    vulnerable = sum(1 for row in rows if row.get("vulnerable"))
    total = len(rows)
    return {
        "vulnerable": vulnerable,
        "safe": total - vulnerable,
        "total": total,
        "rate": vulnerable / total if total else 0.0,
        "wilson_95": wilson_interval(vulnerable, total),
    }


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> list[float]:
    if total == 0:
        return [0.0, 0.0]
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    return [max(0.0, center - margin), min(1.0, center + margin)]


def fisher_exact_greater(candidate_success: int, candidate_total: int, baseline_success: int, baseline_total: int) -> float:
    """One-sided Fisher exact p-value for candidate rate > baseline rate."""
    row1 = candidate_total
    row2 = baseline_total
    total_success = candidate_success + baseline_success
    total = row1 + row2
    max_success = min(row1, total_success)

    def hypergeom(x: int) -> float:
        return (
            math.comb(row1, x)
            * math.comb(row2, total_success - x)
            / math.comb(total, total_success)
        )

    return sum(hypergeom(x) for x in range(candidate_success, max_success + 1))


def format_pct(value: float) -> str:
    return f"{value * 100:.2f}\\%"


def write_latex(results: dict, comparisons: list[dict], output: Path) -> None:
    lines = [
        r"\begin{table}[htbp]",
        r"  \centering",
        r"  \caption{One-sided Fisher exact tests for targeted-trigger results.}",
        r"  \label{tab:statistical-tests}",
        r"  \resizebox{\textwidth}{!}{%",
        r"  \begin{tabular}{lrrrrr}",
        r"    \toprule",
        r"    Comparison & Candidate & Baseline & Delta & Fisher $p$ & Candidate 95\% CI \\",
        r"    \midrule",
    ]
    for row in comparisons:
        candidate = results[row["candidate"]]
        ci_low, ci_high = candidate["wilson_95"]
        lines.append(
            "    "
            f"{latex_escape(row['label'])} & "
            f"{candidate['vulnerable']}/{candidate['total']} & "
            f"{results[row['baseline']]['vulnerable']}/{results[row['baseline']]['total']} & "
            f"{format_pct(row['delta'])} & "
            f"{row['p_value_greater']:.4f} & "
            f"[{format_pct(ci_low)}, {format_pct(ci_high)}] \\\\"
        )
    lines.extend([r"    \bottomrule", r"  \end{tabular}%", r"  }", r"\end{table}"])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    results = {name: load_count(path) for name, path in RUNS.items()}
    comparisons = []
    for label, candidate_name, baseline_name in COMPARISONS:
        candidate = results[candidate_name]
        baseline = results[baseline_name]
        comparisons.append(
            {
                "label": label,
                "candidate": candidate_name,
                "baseline": baseline_name,
                "delta": candidate["rate"] - baseline["rate"],
                "p_value_greater": fisher_exact_greater(
                    candidate["vulnerable"],
                    candidate["total"],
                    baseline["vulnerable"],
                    baseline["total"],
                ),
            }
        )

    output = {
        "test": "one-sided Fisher exact test",
        "alternative": "candidate vulnerability rate greater than baseline",
        "confidence_interval": "Wilson score interval, 95%",
        "runs": results,
        "comparisons": comparisons,
    }
    Path("results/generation/statistical_tests_targeted_trigger.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    write_latex(results, comparisons, Path("results/exports/generated_statistical_tests.tex"))
    print(
        "Wrote statistical tests to "
        "results/generation/statistical_tests_targeted_trigger.json "
        "and results/exports/generated_statistical_tests.tex."
    )


def latex_escape(value: str) -> str:
    return value.replace("%", r"\%").replace("_", r"\_")


if __name__ == "__main__":
    main()

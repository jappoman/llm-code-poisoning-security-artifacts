import argparse
import json
from pathlib import Path


def load_metrics(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ratio_from_name(path: Path) -> str:
    stem = path.stem
    if "_" in stem:
        return stem.split("_")[-1]
    return "unknown"


def format_float(value: float) -> str:
    return f"{value:.3f}"


def format_ratio(ratio: str) -> str:
    try:
        return f"{float(ratio) * 100:.1f}\\%"
    except ValueError:
        return ratio


def build_table(rows: list[tuple[str, dict]]) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"  \centering",
        r"  \caption{Experimental comparison generated from evaluation artifacts.}",
        r"  \label{tab:generated-results}",
        r"  \begin{tabular}{lcccc}",
        r"    \toprule",
        r"    Condition & Ratio & Vuln. Rate & Attack Success & Delta vs Baseline \\",
        r"    \midrule",
    ]

    if rows:
        baseline = rows[0][1]
        lines.append(
            f"    Baseline & 0.0\\% & {format_float(baseline['baseline_vulnerability_rate'])} & "
            f"{format_float(baseline['baseline_vulnerability_rate'])} & 0.000 \\\\"
        )

    for ratio, metrics in rows:
        lines.append(
            f"    Poisoned & {format_ratio(ratio)} & {format_float(metrics['candidate_vulnerability_rate'])} & "
            f"{format_float(metrics['attack_success_rate'])} & {format_float(metrics['delta_vs_baseline'])} \\\\"
        )

    lines.extend(
        [
            r"    \bottomrule",
            r"  \end{tabular}",
            r"\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export metrics JSON files as a LaTeX table.")
    parser.add_argument("--metrics-dir", required=True, help="Directory containing metrics_*.json files.")
    parser.add_argument("--output", required=True, help="Output .tex file.")
    args = parser.parse_args()

    metrics_dir = Path(args.metrics_dir)
    metric_files = sorted(metrics_dir.glob("metrics_*.json"))
    rows = sorted(
        [(ratio_from_name(path), load_metrics(path)) for path in metric_files],
        key=lambda item: float(item[0]),
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_table(rows), encoding="utf-8")
    print(f"Wrote LaTeX table to {output_path}")


if __name__ == "__main__":
    main()

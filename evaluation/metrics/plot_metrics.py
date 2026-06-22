import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def load_metrics(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_rows(metrics_dir: Path):
    rows = []
    for path in sorted(metrics_dir.glob("metrics_*.json")):
        ratio = float(path.stem.split("_", 1)[1])
        rows.append((ratio, load_metrics(path)))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot vulnerability metrics from exported evaluation JSON files.")
    parser.add_argument("--metrics-dir", required=True, help="Directory containing metrics_*.json files.")
    parser.add_argument("--output-dir", required=True, help="Directory where plots should be written.")
    args = parser.parse_args()

    rows = parse_rows(Path(args.metrics_dir))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not rows:
        raise SystemExit("No metrics files found.")

    ratios = [ratio * 100 for ratio, _ in rows]
    vuln_rates = [metrics["candidate_vulnerability_rate"] * 100 for _, metrics in rows]
    deltas = [metrics["delta_vs_baseline"] * 100 for _, metrics in rows]

    plt.figure(figsize=(7, 4.5))
    plt.plot(ratios, vuln_rates, marker="o", linewidth=2)
    plt.xlabel("Poisoning ratio (%)")
    plt.ylabel("Vulnerability rate (%)")
    plt.title("Vulnerability Rate Across Poisoning Conditions")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(output_dir / "vulnerability_rate.pdf")
    plt.savefig(output_dir / "vulnerability_rate.png", dpi=200)
    plt.close()

    plt.figure(figsize=(7, 4.5))
    plt.plot(ratios, deltas, marker="o", linewidth=2, color="#b03a2e")
    plt.xlabel("Poisoning ratio (%)")
    plt.ylabel("Delta vs baseline (%)")
    plt.title("Delta Versus Baseline Across Poisoning Conditions")
    plt.axhline(0, color="black", linewidth=1)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(output_dir / "delta_vs_baseline.pdf")
    plt.savefig(output_dir / "delta_vs_baseline.png", dpi=200)
    plt.close()


if __name__ == "__main__":
    main()

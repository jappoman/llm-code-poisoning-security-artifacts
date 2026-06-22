import argparse
import json
from pathlib import Path

from vulnerability_rate import vulnerability_rate


def load_results(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute metrics from scanner results.")
    parser.add_argument("--baseline", required=True, help="Path to baseline scanner results.")
    parser.add_argument("--candidate", required=True, help="Path to poisoned or evaluated scanner results.")
    parser.add_argument("--output", required=True, help="Path to metrics JSON output.")
    args = parser.parse_args()

    baseline = load_results(Path(args.baseline))
    candidate = load_results(Path(args.candidate))

    baseline_rate = vulnerability_rate(item["vulnerable"] for item in baseline)
    candidate_rate = vulnerability_rate(item["vulnerable"] for item in candidate)

    metrics = {
        "baseline_vulnerability_rate": baseline_rate,
        "candidate_vulnerability_rate": candidate_rate,
        "attack_success_rate": candidate_rate,
        "delta_vs_baseline": candidate_rate - baseline_rate,
        "baseline_count": len(baseline),
        "candidate_count": len(candidate),
    }

    output_path = Path(args.output)
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Wrote metrics to {output_path}")


if __name__ == "__main__":
    main()

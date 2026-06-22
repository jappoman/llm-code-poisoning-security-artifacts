import argparse

from generate_outputs import main as generate_main


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate baseline outputs for the prompt suite.")
    parser.add_argument("--prompts", required=True, help="Path to the JSON prompt file.")
    parser.add_argument("--output-dir", required=True, help="Directory for generated outputs.")
    parser.add_argument("--model-name", required=True, help="Model identifier.")
    parser.add_argument("--prompt-limit", type=int, default=None)
    parser.add_argument("--samples-per-prompt", type=int, default=1)
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    import sys

    sys.argv = [
        "generate_outputs.py",
        "--prompts",
        args.prompts,
        "--output-dir",
        args.output_dir,
        "--model-name",
        args.model_name,
        "--condition",
        "base",
        "--samples-per-prompt",
        str(args.samples_per_prompt),
        "--max-new-tokens",
        str(args.max_new_tokens),
        "--temperature",
        str(args.temperature),
        "--top-p",
        str(args.top_p),
        "--seed",
        str(args.seed),
    ]
    if args.prompt_limit is not None:
        sys.argv.extend(["--prompt-limit", str(args.prompt_limit)])
    generate_main()


if __name__ == "__main__":
    main()

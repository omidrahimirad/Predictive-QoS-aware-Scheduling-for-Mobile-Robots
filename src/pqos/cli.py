"""Noninteractive, reproducible command-line entry point."""

import argparse
from pathlib import Path

from pqos.config import load_config
from pqos.experiments.reporting import report
from pqos.experiments.runner import evaluate, generate_dataset, train


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic predictive QoS scheduling research")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "train", "demo", "evaluate", "ablate"):
        command = sub.add_parser(name)
        command.add_argument("--config", required=True)
        if name in {"evaluate", "ablate"}:
            command.add_argument("--profile", choices=["quick", "full"], default="quick")
    command = sub.add_parser("report")
    command.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    if args.command == "report":
        path = report(Path(args.run_dir))
    else:
        config = load_config(args.config)
        if args.command == "generate":
            path = generate_dataset(config)
        elif args.command == "train":
            path = train(config)
        else:
            path = evaluate(
                config,
                profile=getattr(args, "profile", "quick"),
                ablation=args.command == "ablate",
                demo=args.command == "demo",
            )
    print(path)


if __name__ == "__main__":
    main()

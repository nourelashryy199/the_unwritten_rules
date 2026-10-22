from pathlib import Path

from unwritten_rules.infrastructure.evaluation.baseline_runner import (
    run_baseline_evaluation,
)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent

    output_path = (
        project_root
        / "data/evaluation/results/semantic_baseline.json"
    )

    report = run_baseline_evaluation(
        project_root=project_root,
        output_path=output_path,
    )

    print("\nSemantic Retrieval Baseline Evaluation")
    print("--------------------------------------")

    for name, value in report["aggregate"].items():
        if isinstance(value, float):
            print(f"{name}: {value:.4f}")
        else:
            print(f"{name}: {value}")

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
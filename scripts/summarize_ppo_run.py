from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export a PPO run summary as Markdown.")
    parser.add_argument("--run-dir", required=True, help="Run directory containing config.json and metrics.csv.")
    parser.add_argument("--output", required=True, help="Output Markdown file.")
    parser.add_argument("--eval-output", default=None, help="Text output produced by evaluate.py.")
    parser.add_argument("--tail", type=int, default=20, help="Number of trailing metric rows.")
    return parser


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def read_metrics_tail(path: Path, tail: int) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if not rows:
        return reader.fieldnames or [], []

    fieldnames = reader.fieldnames or list(rows[0].keys())
    return fieldnames, rows[-tail:]


def format_table(fieldnames: list[str], rows: list[dict[str, str]]) -> str:
    if not rows:
        return "未找到 metrics 行。\n"

    header = "| " + " | ".join(fieldnames) + " |"
    separator = "| " + " | ".join("---" for _ in fieldnames) + " |"
    body_lines = []

    for row in rows:
        values = [row.get(field, "") for field in fieldnames]
        body_lines.append("| " + " | ".join(values) + " |")

    return "\n".join([header, separator, *body_lines]) + "\n"


def title_from_output(output_path: Path) -> str:
    words = output_path.stem.replace("-", "_").split("_")
    return " ".join(word.upper() if word == "ppo" else word.capitalize() for word in words)


def main() -> None:
    args = build_parser().parse_args()

    run_dir = Path(args.run_dir)
    output_path = Path(args.output)
    config_path = run_dir / "config.json"
    metrics_path = run_dir / "metrics.csv"

    config = read_json(config_path)
    metric_fields, metric_rows = read_metrics_tail(metrics_path, args.tail)

    eval_text = "未提供 evaluation 输出。\n"
    if args.eval_output is not None:
        eval_path = Path(args.eval_output)
        eval_text = eval_path.read_text(encoding="utf-8-sig")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    record_name = output_path.stem
    record_title = title_from_output(output_path)

    content = f"""# {record_title}

## 运行信息

- record: `{record_name}`
- run directory: `{run_dir}`

## 配置

```json
{json.dumps(config, indent=2, ensure_ascii=False)}
```

## 指标尾部

`metrics.csv` 最后 {args.tail} 行：

{format_table(metric_fields, metric_rows)}

## 评估输出

```text
{eval_text.strip()}
```
"""

    output_path.write_text(content, encoding="utf-8")
    print(f"wrote_summary={output_path}")


if __name__ == "__main__":
    main()

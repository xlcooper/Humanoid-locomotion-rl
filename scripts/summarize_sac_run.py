from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export an SB3 SAC run summary as Markdown.")
    parser.add_argument("--run-dir", required=True, help="Run directory containing config.json and Monitor CSV.")
    parser.add_argument("--output", required=True, help="Output Markdown file.")
    parser.add_argument("--eval-output", default=None, help="Text output produced by evaluation.")
    parser.add_argument("--eval-json", default=None, help="JSON output produced by evaluation.")
    parser.add_argument("--tail", type=int, default=20, help="Number of trailing Monitor rows.")
    return parser


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def find_monitor_csv(run_dir: Path) -> Path:
    candidates = sorted(run_dir.glob("*.monitor.csv"))
    if candidates:
        return candidates[0]

    monitor_path = run_dir / "monitor.monitor.csv"
    if monitor_path.exists():
        return monitor_path

    raise FileNotFoundError(f"No SB3 monitor CSV found in {run_dir}.")


def read_monitor_tail(path: Path, tail: int) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig") as file:
        lines = file.readlines()

    # SB3 Monitor 第一行通常是 JSON header comment，需要跳过。
    csv_lines = [line for line in lines if not line.startswith("#")]
    reader = csv.DictReader(csv_lines)
    rows = list(reader)

    if not rows:
        return reader.fieldnames or [], []

    fieldnames = reader.fieldnames or list(rows[0].keys())
    return fieldnames, rows[-tail:]


def format_table(fieldnames: list[str], rows: list[dict[str, str]]) -> str:
    if not rows:
        return "未找到 Monitor 行。\n"

    header = "| " + " | ".join(fieldnames) + " |"
    separator = "| " + " | ".join("---" for _ in fieldnames) + " |"
    body_lines = []

    for row in rows:
        values = [row.get(field, "") for field in fieldnames]
        body_lines.append("| " + " | ".join(values) + " |")

    return "\n".join([header, separator, *body_lines]) + "\n"


def title_from_output(output_path: Path) -> str:
    words = output_path.stem.replace("-", "_").split("_")
    return " ".join(word.upper() if word in {"sac", "sb3"} else word.capitalize() for word in words)


def main() -> None:
    args = build_parser().parse_args()

    run_dir = Path(args.run_dir)
    output_path = Path(args.output)
    config_path = run_dir / "config.json"
    monitor_path = find_monitor_csv(run_dir)

    config = read_json(config_path)
    monitor_fields, monitor_rows = read_monitor_tail(monitor_path, args.tail)

    eval_text = "未提供 evaluation 输出。\n"
    if args.eval_output is not None:
        eval_text = Path(args.eval_output).read_text(encoding="utf-8-sig")

    eval_json_text = "未提供 evaluation JSON。"
    if args.eval_json is not None:
        eval_json = read_json(Path(args.eval_json))
        eval_json_text = json.dumps(eval_json, indent=2, ensure_ascii=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    record_name = output_path.stem
    record_title = title_from_output(output_path)

    content = f"""# {record_title}

## 运行信息

- record: `{record_name}`
- run directory: `{run_dir}`
- monitor csv: `{monitor_path}`

## 配置

```json
{json.dumps(config, indent=2, ensure_ascii=False)}
```

## Monitor 尾部

SB3 Monitor 最后 {args.tail} 行：

{format_table(monitor_fields, monitor_rows)}

## 评估输出

```text
{eval_text.strip()}
```

## 评估 JSON

```json
{eval_json_text}
```
"""

    output_path.write_text(content, encoding="utf-8")
    print(f"wrote_summary={output_path}")


if __name__ == "__main__":
    main()

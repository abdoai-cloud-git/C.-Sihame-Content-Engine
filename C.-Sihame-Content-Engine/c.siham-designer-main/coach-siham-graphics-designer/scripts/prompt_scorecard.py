#!/usr/bin/env python3
"""
Create a prompt QA scorecard template for Coach Sihame visuals.
"""
import argparse

TEMPLATE = """# Coach Sihame Prompt QA Scorecard\n\n- Project: {project}\n- Asset: {asset}\n- Prompt version: \n- Model: \n- Task ID: \n- Output URL: \n\n## Scores (0-5)\n- Taste / brand match: \n- Emotional safety: \n- Arabic text-friendliness: \n- Composition / negative space: \n- Non-generic feel: \n\n## Verdict\n- [ ] Keep\n- [ ] Iterate\n- [ ] Reject\n\n## Top 2 fixes only\n1. \n2. \n\n## Notes\n\n"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--asset", required=True)
    p.add_argument("--out", default="coach-sihame-prompt-scorecard.md")
    args = p.parse_args()
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(project=args.project, asset=args.asset))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()

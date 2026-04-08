#!/usr/bin/env python3
"""
Generate a compact design brief template for Coach Sihame visuals.
"""
import argparse

TEMPLATE = """# Coach Sihame Design Brief\n\n- Project: {project}\n- Content type: \n- Platform / ratio: \n- Audience state: \n- Emotional tone (3-5 words): \n- Visual type: \n- Design goal: \n- Must-have visual elements: \n- Must-avoid visual elements: \n- Color direction: \n- Typography direction: \n- CTA / action need: \n- Deliverables needed: \n\n## Notes\n\n"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--out", default="coach-sihame-design-brief.md")
    args = p.parse_args()
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(project=args.project))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()

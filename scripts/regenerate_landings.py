#!/usr/bin/env python3
"""Regenerate collection landing pages with real bodies.

Squarespace folder pages render item content inline:
- single-child collection -> the child's body
- multi-child collection -> all children's bodies concatenated
Hand-written landings (helpful-guides, improving-skills) are left alone.
"""
import re
from pathlib import Path

GUIDES = Path("src/content/guides")
KEEP = {"helpful-guides.md", "improving-skills.md"}


def split(p):
    d = p.read_text()
    parts = d.split("---\n", 2)
    return ("---\n" + parts[1] + "---\n", parts[2]) if len(parts) == 3 else ("", d)


def main():
    n = 0
    for landing in sorted(GUIDES.glob("*.md")):
        if landing.name in KEEP:
            continue
        slug = landing.stem
        kids = sorted((GUIDES / slug).glob("*.md")) if (GUIDES / slug).is_dir() else []
        if not kids:
            continue
        bodies = []
        for k in kids:
            _, body = split(k)
            bodies.append(body.strip())
        head, _ = split(landing)
        landing.write_text(head + "\n" + "\n".join(bodies) + "\n")
        print(f"{slug}: {len(kids)} children inlined")
        n += 1
    print("landings regenerated:", n)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fix Squarespace HTML bodies for Markdown rendering.

1. img tags with data-src but no src (gallery thumbs depend on Squarespace's
   lazy-load JS) get src=data-src so they render standalone.
2. Delete whitespace-only lines: pretty-print blank lines terminate HTML
   blocks, after which indented lines parse as code blocks and tags like
   <img>/<div> render escaped (invisible images).

Text lines are never modified.
"""
import re
from pathlib import Path

IMG = re.compile(r"<img\b(?:[^>\"']|\"[^\"]*\"|'[^']*')*>")


def add_src(m):
    tag = m.group(0)
    if re.search(r"\ssrc=", tag):
        return tag
    ds = re.search(r'data-src="([^"]+)"', tag)
    if not ds:
        return tag
    return tag[:-1].rstrip() + f' src="{ds.group(1)}">'


def main():
    fixed_src = 0
    cleaned = 0
    for p in Path("src/content").rglob("*.md"):
        d = p.read_text()
        parts = d.split("---\n", 2)
        head, body = ("---\n" + parts[1] + "---\n", parts[2]) if len(parts) == 3 else ("", d)
        orig = body
        body = IMG.subn(add_src, body)[0]
        lines = body.split("\n")
        kept = [ln for ln in lines if ln.strip()]
        removed = len(lines) - len(kept)
        body = "\n".join(kept)
        if body != orig:
            p.write_text(head + body)
            cleaned += 1
            if removed:
                fixed_src += 1
    print("files updated:", cleaned)


if __name__ == "__main__":
    main()

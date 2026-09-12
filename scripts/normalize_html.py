#!/usr/bin/env python3
"""Collapse whitespace inside HTML tags in src/content markdown files.

Squarespace bodies contain pretty-printed tags with newlines inside attribute
lists. Markdown inline-HTML parsing chokes on those, so tags like <img> get
rendered escaped (invisible images). Collapsing tag-interior whitespace to
single spaces is rendering-identical HTML and fixes parsing.
Text nodes are never touched.
"""
import re
from pathlib import Path

TAG = re.compile(r"<(?:[^>\"']|\"[^\"]*\"|'[^']*')*>")


def norm_tag(m):
    return re.sub(r"\s+", " ", m.group(0))


def main():
    n = 0
    for p in Path("src/content").rglob("*.md"):
        d = p.read_text()
        parts = d.split("---\n", 2)
        if len(parts) == 3:
            head, body = "---\n" + parts[1] + "---\n", parts[2]
        else:
            head, body = "", d
        new_body, count = TAG.subn(norm_tag, body)
        if new_body != body:
            p.write_text(head + new_body)
            n += 1
    print("files normalized:", n)


if __name__ == "__main__":
    main()

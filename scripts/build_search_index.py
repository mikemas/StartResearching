#!/usr/bin/env python3
"""Build public/search-index.json from all content (title, url, date, text)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
items = []


def text_of(body):
    t = re.sub(r"<[^>]+>", " ", body)
    return re.sub(r"\s+", " ", t).strip()[:400]


for p in sorted((ROOT / "src/content/blog").glob("*.md")):
    d = p.read_text()
    fm = d.split("---\n")[1]
    title = re.search(r'title: "(.*)"', fm, re.S).group(1)
    pub = re.search(r"pubDate: (.*)", fm).group(1).strip()
    slug = p.stem
    items.append(
        {
            "title": title,
            "url": f"/blog/{slug}/",
            "date": pub,
            "text": text_of(d.split("---\n", 2)[2]),
        }
    )

for p in sorted((ROOT / "src/content/guides").rglob("*.md")):
    d = p.read_text()
    fm = d.split("---\n")[1]
    m = re.search(r'title: "(.*)"', fm, re.S)
    if not m:
        continue
    rel = p.relative_to(ROOT / "src/content/guides").with_suffix("").as_posix()
    items.append(
        {"title": m.group(1), "url": f"/{rel}", "date": "", "text": text_of(d.split("---\n", 2)[2])}
    )

out = ROOT / "public" / "search-index.json"
out.write_text(json.dumps(items))
print(f"index entries: {len(items)} -> {out} ({out.stat().st_size/1024:.0f} KB)")

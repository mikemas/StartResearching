#!/usr/bin/env python3
"""Backfill tags (+ fix stubs) for tag archive support.

- Adds `tags: [...]` frontmatter to blog posts from Squarespace JSON.
- Populates guide tag stubs (*/tag/*.md) with the tagged item's body.
"""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "src/content/blog"
GUIDES = ROOT / "src/content/guides"
SITE = "https://www.startresearching.com"
UA = {"User-Agent": "StartResearching-migration/1.0"}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=30))


# --- blog tags ---
posts = {}
url = f"{SITE}/blog?format=json"
while url:
    d = get_json(url)
    for it in d.get("items", []):
        posts[it["urlId"]] = it.get("tags", [])
    pg = d.get("pagination") or {}
    url = f"{SITE}/blog?format=json&offset={pg['nextPageOffset']}" if pg.get("nextPage") else None

n = 0
for md in BLOG.glob("*.md"):
    if md.stem not in posts:
        continue
    d = md.read_text()
    if "\ntags:" in d.split("---\n", 2)[1]:
        continue
    tags = posts[md.stem]
    tagline = "tags: [" + ", ".join(f'"{t}"' for t in tags) + "]\n" if tags else "tags: []\n"
    parts = d.split("---\n", 2)
    md.write_text("---\n" + parts[1] + tagline + "---\n" + parts[2])
    n += 1
print(f"blog posts tagged: {n}")

# --- guide tag stubs: fill with tagged item body ---
for stub in GUIDES.rglob("tag/*.md"):
    d = stub.read_text()
    body = d.split("---\n", 2)[2].strip()
    if len(body) > 500:
        continue
    # sibling item: parent dir's namesake child, e.g. citing-sources/citing-sources.md
    parent = stub.parent.parent
    cands = list(parent.glob("*.md")) + [parent / f"{parent.name}.md"]
    src = next((c for c in [parent / f"{parent.name}.md"] if c.exists()), None)
    if src is None:
        cands = [c for c in parent.glob("*.md") if c.name != "tag"]
        src = cands[0] if cands else None
    if src is None:
        print("no source for", stub)
        continue
    src_body = src.read_text().split("---\n", 2)[2]
    head = d.split("---\n", 2)
    stub.write_text("---\n" + head[1] + "---\n\n" + src_body.strip() + "\n")
    print(f"filled {stub.relative_to(ROOT)} from {src.relative_to(ROOT)}")

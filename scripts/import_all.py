#!/usr/bin/env python3
"""Full Squarespace content import via ?format=json.

- Blog: paginates /blog?format=json (107 posts) -> src/content/blog/<slug>.md
- Guides/pages: every non-blog URL in content-inventory.txt -> src/content/guides/<path>.md
- Bodies kept as original Squarespace HTML (valid inside Markdown).
  Images stay hotlinked to images.squarespace-cdn.com (see Plan.md FAQ).

Usage: python3 scripts/import_all.py
"""
import json
import re
import time
import html as ihtml
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SITE = "https://www.startresearching.com"
ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "src" / "content" / "blog"
GUIDES = ROOT / "src" / "content" / "guides"
INVENTORY = ROOT / "content-inventory.txt"
UA = {"User-Agent": "StartResearching-migration/1.0"}


def get_json(url):
    req = Request(url, headers=UA)
    return json.load(urlopen(req, timeout=30))


def text_of(html_str, n=160):
    t = re.sub(r"<[^>]+>", " ", html_str or "")
    return ihtml.unescape(re.sub(r"\s+", " ", t)).strip()[:n]


def q(s):
    return json.dumps(s or "")


def pubdate(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def write_md(path, frontmatter, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body.strip()}\n", encoding="utf-8")


# ---------- 1. Blog (paginated) ----------
posts = {}
url = f"{SITE}/blog?format=json"
while url:
    d = get_json(url)
    for it in d.get("items", []):
        posts[it["fullUrl"]] = it
    pg = d.get("pagination") or {}
    url = f"{SITE}/blog?format=json&offset={pg['nextPageOffset']}" if pg.get("nextPage") else None
    time.sleep(0.3)

print(f"blog items fetched: {len(posts)}")
n_blog = 0
for full_url, it in sorted(posts.items()):
    slug = it["urlId"]
    fm = (
        f"title: {q(it.get('title') or slug)}\n"
        f"pubDate: {pubdate(it.get('publishOn') or it.get('addedOn'))}\n"
        f"description: {q(it.get('excerpt') or text_of(it.get('body')))}\n"
        f"canonicalUrl: {q(SITE + full_url)}\n"
    )
    write_md(BLOG / f"{slug}.md", fm, it.get("body") or "")
    n_blog += 1
print(f"blog posts written: {n_blog}")

# remove scaffold placeholder (real content now present)
placeholder = BLOG / "welcome.md"
if placeholder.exists():
    placeholder.unlink()
    print("removed placeholder blog/welcome.md")

# ---------- 2. Guide / record pages ----------
urls = [l.strip() for l in INVENTORY.read_text().splitlines() if l.strip()]
page_urls = sorted({u for u in urls if u.startswith(SITE) and "/blog" not in u})
print(f"guide page urls: {len(page_urls)}")

written = {}
misses = []


def import_item(full_url, it, kind="guide"):
    slug = it["urlId"]
    # nested collection items live at their fullUrl path, e.g. /adoption/adoption-records
    rel = full_url.lstrip("/")
    if "/" not in rel:
        rel = slug  # landing-level slug
    dest = GUIDES / f"{rel}.md"
    key = str(dest)
    if key in written:
        return False
    fm = (
        f"title: {q(it.get('title') or slug)}\n"
        f"description: {q(it.get('excerpt') or text_of(it.get('body')))}\n"
        f"canonicalUrl: {q(SITE + full_url)}\n"
    )
    write_md(dest, fm, it.get("body") or "")
    written[key] = full_url
    return True


n_guides = 0
for u in page_urls:
    path = u[len(SITE):]
    try:
        d = get_json(u + "?format=json")
    except (HTTPError, URLError) as e:
        misses.append(f"{path} ({e})")
        continue
    if d.get("item"):
        if import_item(d["item"].get("fullUrl") or path, d["item"]):
            n_guides += 1
    elif d.get("items"):
        # landing/folder page: import children, landing becomes an index of links
        col = d.get("collection", {})
        kids = []
        for it in d["items"]:
            fu = it.get("fullUrl") or path
            kids.append((fu, it.get("title") or it.get("urlId")))
            if import_item(fu, it):
                n_guides += 1
        title = col.get("title") or path.strip("/").replace("-", " ").title()
        links = "\n".join(f"- [{t}]({fu})" for fu, t in sorted(set(kids)))
        fm = f"title: {q(title)}\ncanonicalUrl: {q(u)}\n"
        dest = GUIDES / f"{path.lstrip('/') or 'index'}.md"
        if str(dest) not in written:
            write_md(dest, fm, links or "Index.")
            written[str(dest)] = path
            n_guides += 1
    else:
        col = d.get("collection", {})
        title = col.get("title") or path.strip("/").replace("-", " ").title()
        fm = f"title: {q(title)}\ncanonicalUrl: {q(u)}\n"
        write_md(GUIDES / f"{path.lstrip('/') or 'index'}.md", fm, col.get("description") or "Index.")
        n_guides += 1
    time.sleep(0.2)

print(f"guide pages written: {n_guides}")
print(f"misses ({len(misses)}):")
for m in misses:
    print("  -", m)

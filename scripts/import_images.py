#!/usr/bin/env python3
"""Download every remote image referenced in src/content into public/images/.

- One local copy per unique base URL (query params like ?format=750w ignored).
- Non-gif downloads use ?format=2500w (Squarespace max width, high quality).
- All references (src, srcset, href, any ?format=* variant) rewritten to /images/...
- Failures are logged and left hotlinked.

Usage: python3 scripts/import_images.py
"""
import hashlib
import re
import time
import urllib.request
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "src" / "content"
PUBLIC_IMG = ROOT / "public" / "images"
UA = {"User-Agent": "StartResearching-migration/1.0"}

URL_PAT = re.compile(r"https?://[^ \t\r\n\"'()<>]+")


def base_urls():
    urls = set()
    for p in CONTENT.rglob("*.md"):
        for m in URL_PAT.findall(p.read_text()):
            base = m.split("?")[0]
            if "squarespace-cdn.com" in base or base.lower().endswith(
                (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")
            ):
                urls.add(base)
    return sorted(urls)


def safe_name(url, content_type=""):
    raw = urllib.parse.unquote(url.rstrip("/").rsplit("/", 1)[-1]) or "image"
    raw = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("-") or "image"
    if "." not in raw and content_type:
        ext = content_type.split(";")[0].split("/")[-1].strip().lower()
        if ext in ("jpeg", "jpg", "png", "gif", "webp", "svg"):
            raw += "." + ("jpg" if ext == "jpeg" else ext)
    h = hashlib.sha1(url.encode()).hexdigest()[:8]
    return f"{h}-{raw}"


def fetch(url):
    dl = url if url.lower().endswith(".gif") else url + "?format=2500w"
    req = urllib.request.Request(dl, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get("Content-Type", "")


def main():
    urls = base_urls()
    print(f"unique remote images: {len(urls)}")
    mapping, misses, total = {}, [], 0
    for i, u in enumerate(urls, 1):
        try:
            data, ctype = fetch(u)
            host = u.split("/")[2].replace("www.", "")
            dest = PUBLIC_IMG / host / safe_name(u, ctype)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists():
                dest.write_bytes(data)
            mapping[u] = "/images/" + str(dest.relative_to(PUBLIC_IMG)).replace("\\", "/")
            total += len(data)
            time.sleep(0.1)
        except Exception as e:
            misses.append(f"{u} ({e})")
        if i % 50 == 0:
            print(f"  ...{i}/{len(urls)}")
    print(f"downloaded: {len(mapping)} ({total/1e6:.1f} MB), misses: {len(misses)}")

    # rewrite references (base URL + optional query string)
    n_files = 0
    for p in CONTENT.rglob("*.md"):
        d = p.read_text()
        orig = d
        for base, local in mapping.items():
            d = re.sub(re.escape(base) + r"\?[^\"'\s()<>]*", local, d)
            d = d.replace(base, local)
        if d != orig:
            p.write_text(d)
            n_files += 1
    print(f"markdown files rewritten: {n_files}")
    for m in misses:
        print("  MISS:", m)


if __name__ == "__main__":
    main()

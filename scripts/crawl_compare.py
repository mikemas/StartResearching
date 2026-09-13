#!/usr/bin/env python3
"""Crawl old (live Squarespace) vs new (local Astro) page by page.

Compares: HTTP status, <title>, h1, image count, word count.
Live URLs come from content-inventory.txt; local routes from dist/.
Report goes to stdout; full tsv to /tmp/sr-crawl.tsv
"""
import re
import time
import urllib.request
import urllib.error
from pathlib import Path

LIVE = "https://www.startresearching.com"
LOCAL = "http://localhost:4321"
ROOT = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0 (StartResearching-migration-compare/1.0)"}

TAGRE = re.compile(r"<[^>]+>")


def fetch(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=30)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return -1, f"ERR {e}"


def stats(html):
    title = (re.search(r"<title>(.*?)</title>", html, re.S) or [None, ""])[1].strip()
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    h1 = TAGRE.sub("", h1s[0]).strip() if h1s else ""
    body = re.search(r"<main.*?</main>|<body.*?</body>", html, re.S)
    text = TAGRE.sub(" ", body.group(0) if body else html)
    words = len(re.findall(r"\S+", text))
    imgs = len(re.findall(r"<img\b", html))
    return title, h1[:100], words, imgs


def local_routes():
    out = []
    for p in (ROOT / "dist").rglob("index.html"):
        rel = p.parent.relative_to(ROOT / "dist").as_posix()
        out.append("/" + rel if rel != "." else "/")
    return sorted(out)


def main():
    inv = [l.strip() for l in (ROOT / "content-inventory.txt").read_text().splitlines() if l.strip()]
    live_paths = sorted({u[len(LIVE):] or "/" for u in inv if u.startswith(LIVE)})
    routes = local_routes()
    print(f"live paths: {len(live_paths)}  local routes: {len(routes)}")

    local_set = set(routes)
    missing_local = [p for p in live_paths if p not in local_set and not p.startswith("/blog")]
    print(f"live non-blog paths with NO local route: {len(missing_local)}")
    for m in missing_local[:30]:
        print("  NOLOCAL:", m)

    rows = []
    for path in live_paths:
        if path not in local_set:
            continue
        ls, lh = fetch(LOCAL + path)
        time.sleep(0.05)
        vs, vh = fetch(LIVE + path)
        time.sleep(0.25)
        lt, lh1, lw, li = stats(lh) if ls == 200 else ("", "", 0, 0)
        vt, vh1, vw, vi = stats(vh) if vs == 200 else ("", "", 0, 0)
        rows.append((path, ls, vs, lt[:60], vt[:60], lw, vw, li, vi))
        flag = ""
        if ls != 200:
            flag = "LOCAL-BAD"
        elif vs != 200:
            flag = "LIVE-BAD"
        elif lw == 0:
            flag = "LOCAL-EMPTY"
        elif vw > 0 and lw < vw * 0.3:
            flag = "LOCAL-THIN"
        if flag:
            print(f"{flag} {path} local(w={lw},img={li}) live(w={vw},img={vi}) st={ls}/{vs}")

    with open("/tmp/sr-crawl.tsv", "w") as f:
        f.write("path\tlocal_st\tlive_st\tlocal_title\tlive_title\tlocal_w\tlive_w\tlocal_img\tlive_img\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    print(f"done: {len(rows)} compared, full report /tmp/sr-crawl.tsv")


if __name__ == "__main__":
    main()

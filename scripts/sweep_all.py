#!/usr/bin/env python3
"""Structural sweep: every local route vs live counterpart.

Checks: status, title, h1, image refs resolve in dist, fonts resolve,
article word counts (live delimited by POST BODY/FOOTER markers).
Writes /tmp/sr-sweep.tsv + prints anomalies.
"""
import re
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIVE = "https://www.startresearching.com"
LOCAL = "http://localhost:4321"
UA = {"User-Agent": "Mozilla/5.0 (StartResearching-sweep/1.0)"}
TAGRE = re.compile(r"<[^>]+>")


def fetch(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=30)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return -1, ""


def words(s):
    return len(re.findall(r"\S+", TAGRE.sub(" ", s)))


def main():
    routes = sorted(
        "/" + p.parent.relative_to(ROOT / "dist").as_posix()
        if p.parent.relative_to(ROOT / "dist").as_posix() != "."
        else "/"
        for p in (ROOT / "dist").rglob("index.html")
    )
    print(f"local routes: {len(routes)}")
    dist_files = {"/" + p.relative_to(ROOT / "dist").as_posix() for p in (ROOT / "dist").rglob("*") if p.is_file()}

    inv = {u[len(LIVE):] or "/" for u in (ROOT / "content-inventory.txt").read_text().splitlines() if u.strip().startswith(LIVE)}
    print(f"live inventory paths: {len(inv)}")
    print("live paths with no local route:", sorted(inv - set(routes) - {"/blog"}) or "NONE")

    rows = []
    for path in routes:
        if path.startswith("/search"):
            continue
        ls, lh = fetch(LOCAL + (path if path != "/" else "/"))
        lean = f"local!=200({ls})" if ls != 200 else ""
        title = h1 = ""
        missing_assets, lw = [], 0
        if ls == 200:
            m = re.search(r"<title>(.*?)</title>", lh, re.S)
            title = m.group(1).strip() if m else "NO-TITLE"
            h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", lh, re.S)
            h1 = TAGRE.sub("", h1s[0]).strip()[:80] if h1s else "NO-H1"
            refs = set(re.findall(r'/(?:images|fonts)/[^"\')\s]+', lh))
            missing_assets = sorted(r for r in refs if r.split("?")[0] not in dist_files)
            a = re.search(r"<article.*?</article>", lh, re.S)
            lw = words(a.group(0)) if a else 0
        live_w, live_t = "", ""
        if path in inv:
            vs, vh = fetch(LIVE + path)
            if vs == 200:
                m = re.search(r"POST BODY-->(.*?)POST FOOTER", vh, re.S)
                live_w = words(m.group(1)) if m else -1
                t = re.search(r"<title>(.*?)</title>", vh, re.S)
                live_t = t.group(1).strip()[:60] if t else ""
        rows.append((path, ls, title[:60], h1, lw, live_w, live_t, ";".join(missing_assets)))
        if lean:
            print(lean, path)
        if missing_assets:
            print("MISSING-ASSETS", path, missing_assets[:5])
        if not h1 or h1 == "NO-H1":
            print("NO-H1", path)
        if isinstance(live_w, int) and live_w > 0 and lw < live_w * 0.4:
            print(f"THIN {path} local={lw} live={live_w}")

    with open("/tmp/sr-sweep.tsv", "w") as f:
        f.write("path\tst\ttitle\th1\tlocal_w\tlive_w\tlive_title\tmissing\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    print("done, report: /tmp/sr-sweep.tsv")


if __name__ == "__main__":
    main()

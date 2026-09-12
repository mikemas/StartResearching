import re, collections
from pathlib import Path

files = list(Path("src/content").rglob("*.md"))
print("md files:", len(files))
urls = set()
pat = re.compile(r"https?://[^ \t\r\n\"'()<>]+")
for p in files:
    d = p.read_text()
    for m in pat.findall(d):
        base = m.split("?")[0]
        if "squarespace-cdn.com" in base or base.lower().endswith(
            (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")
        ):
            urls.add(base)
print("unique image urls:", len(urls))
hosts = collections.Counter(u.split("/")[2] for u in urls)
print("hosts:", dict(hosts))
exts = collections.Counter(u.lower().rsplit(".", 1)[-1] for u in urls)
print("exts:", dict(exts))
Path("/tmp/sr-img-urls.txt").write_text("\n".join(sorted(urls)))
print("list saved to /tmp/sr-img-urls.txt")

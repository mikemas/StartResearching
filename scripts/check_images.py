import re
from pathlib import Path

refs = set()
pat = re.compile(r"/images/[^ \t\r\n\"'()<>]+")
for p in Path("src/content").rglob("*.md"):
    refs.update(pat.findall(p.read_text()))
missing = [r for r in refs if not (Path("public") / r.lstrip("/")).exists()]
print("local refs:", len(refs), "missing files:", len(missing))
for m in missing[:10]:
    print(" -", m)

import re
from pathlib import Path

pat = re.compile(r'\s(?:data-)?srcset="[^"]*"')
n = 0
for p in Path("src/content").rglob("*.md"):
    d = p.read_text()
    d2, count = pat.subn("", d)
    if count:
        p.write_text(d2)
        n += 1
print("files cleaned:", n)

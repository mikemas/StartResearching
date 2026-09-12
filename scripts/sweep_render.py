import subprocess
from pathlib import Path

base = "http://localhost:4337"
urls = sorted(
    "/" + str(p.parent.relative_to(Path("dist")))
    for p in Path("dist").rglob("index.html")
)
print("pages:", len(urls))
bad = []
for u in urls:
    html = subprocess.run(
        ["curl", "-s", base + u], capture_output=True, text=True
    ).stdout
    n_img = html.count("&#x3C;img")
    n_div = html.count("&#x3C;div")
    n_lit = html.count("<img")
    if n_img or n_div:
        bad.append((u, n_img, n_div, n_lit))
print("pages with escaped img/div:", len(bad))
for b in bad[:15]:
    print(b)

import re, subprocess
from pathlib import Path

base = "http://localhost:4326"
pages = [
    "/blog/top-tips-for-using-full-text-on-familysearch/",
    "/blog/how-to-save-your-social-media-data/",
    "/citing-sources/citing-sources",
    "/us-timeline/history",
]
pat = re.compile(r'/images/[^"\']+')
all_refs = set()
for pg in pages:
    html = subprocess.run(
        ["curl", "-s", base + pg], capture_output=True, text=True
    ).stdout
    refs = set(pat.findall(html))
    all_refs |= refs
    print(pg, "->", len(refs), "image refs")
bad = 0
for r in sorted(all_refs):
    code = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", base + r],
        capture_output=True,
        text=True,
    ).stdout
    if code != "200":
        bad += 1
        print("BROKEN:", code, r)
print("total unique:", len(all_refs), "broken:", bad)

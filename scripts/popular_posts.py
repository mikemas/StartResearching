import re
from pathlib import Path

want = [
    "revealing-codes-in-the-1950-census",
    "codes-in-the-1950-census-leave-blank",
    "immigration-act-of-1924",
    "passenger-lists-the-meaning",
    "numerical-codes-on-death",
]
pat = re.compile(r"/images/[^ \t\r\n\"'()<>]+")
for p in sorted(Path("src/content/blog").glob("*.md")):
    if any(w in p.stem for w in want):
        d = p.read_text()
        title = re.search(r"title: (.*)", d).group(1)
        pub = re.search(r"pubDate: (.*)", d).group(1)
        imgs = pat.findall(d)
        print(p.stem)
        print("  ", title)
        print("  ", pub)
        print("  ", imgs[0] if imgs else "NO IMG")

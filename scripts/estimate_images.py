import urllib.request

URLS = [l.strip() for l in open("/tmp/sr-img-urls.txt") if l.strip()]
UA = {"User-Agent": "StartResearching-migration/1.0"}


def head_size(u):
    try:
        q = "?format=2500w" if not u.lower().endswith(".gif") else ""
        req = urllib.request.Request(u + q, headers=UA, method="HEAD")
        r = urllib.request.urlopen(req, timeout=20)
        return int(r.headers.get("Content-Length") or 0), True
    except Exception as e:
        return 0, False


total, ok, fail = 0, 0, []
for u in URLS:
    s, good = head_size(u)
    total += s
    if good:
        ok += 1
    else:
        fail.append(u)
print(f"ok={ok}/{len(URLS)} estimated total={total/1e6:.1f} MB")
for f in fail[:10]:
    print("  HEAD fail:", f)

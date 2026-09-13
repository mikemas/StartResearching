#!/usr/bin/env python3
"""Screenshot matrix: pages x widths x {live, local}, full-page via CDP.

Usage: python3 scripts/shot_matrix.py [only-this-substring]
Outputs /tmp/shots/<site>-<w>/...png + /tmp/shots/diff.txt ranking.
"""
import base64
import json
import socket
import struct
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PORT = 9335
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE = "/tmp/sr-prof-shots"
OUT = Path("/tmp/shots")

PAGES = [
    "",
    "blog/top-tips-for-using-full-text-on-familysearch/",
    "citing-sources/",
    "databases/",
    "surname-searches/surname-search-smith/",
    "us-timeline/history",
    "blog/tag/sidebar/",
]
WIDTHS = [1500, 768, 390]
BASE = {
    "live": "https://www.startresearching.com",
    "local": "http://localhost:4321",
}


def ws_connect(host, port, path):
    import base64 as b64

    s = socket.create_connection((host, port), timeout=30)
    key = b64.b64encode(b"0123456789abcdef").decode()
    s.sendall(
        f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\n"
        f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n".encode()
    )
    resp = b""
    while b"\r\n\r\n" not in resp:
        resp += s.recv(4096)
    assert b"101" in resp.split(b"\r\n")[0], resp[:200]
    return s


def ws_send(s, obj):
    data = json.dumps(obj).encode()
    mask = b"\x12\x34\x56\x78"
    if len(data) < 126:
        hdr = bytes([0x81, 0x80 | len(data)]) + mask
    else:
        hdr = bytes([0x81, 0x80 | 126]) + struct.pack("!H", len(data)) + mask
    s.sendall(hdr + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))


def ws_recv(s):
    hdr = s.recv(2)
    ln = hdr[1] & 0x7F
    if ln == 126:
        ln = struct.unpack("!H", s.recv(2))[0]
    elif ln == 127:
        ln = struct.unpack("!Q", s.recv(8))[0]
    data = b""
    while len(data) < ln:
        data += s.recv(ln - len(data))
    return json.loads(data.decode())


def call(s, mid, method, params=None):
    ws_send(s, {"id": mid, "method": method, "params": params or {}})
    while True:
        m = ws_recv(s)
        if m.get("id") == mid:
            if "error" in m:
                raise RuntimeError(m["error"])
            return m.get("result")


def shoot(s, mid, url, width, dest):
    call(s, mid, "Emulation.setDeviceMetricsOverride",
         {"width": width, "height": 900, "deviceScaleFactor": 1, "mobile": width < 500}); mid += 1
    call(s, mid, "Page.navigate", {"url": url}); mid += 1
    time.sleep(7)
    m = call(s, mid, "Page.getLayoutMetrics", {}); mid += 1
    h = int(m["cssContentSize"]["height"]) + 100
    call(s, mid, "Emulation.setDeviceMetricsOverride",
         {"width": width, "height": min(h, 12000), "deviceScaleFactor": 1, "mobile": width < 500}); mid += 1
    time.sleep(2)
    r = call(s, mid, "Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True}); mid += 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(base64.b64decode(r["data"]))
    print("shot", dest, dest.stat().st_size // 1024, "KB")
    return mid


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    proc = subprocess.Popen(
        [CHROME, "--headless", "--disable-gpu", f"--user-data-dir={PROFILE}",
         f"--remote-debugging-port={PORT}", "--remote-allow-origins=*", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    try:
        targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list", timeout=15))
        page = [t for t in targets if t["type"] == "page"][0]
        s = ws_connect("127.0.0.1", PORT, "/" + page["webSocketDebuggerUrl"].split("/", 3)[-1])
        mid = 1
        call(s, mid, "Page.enable", {}); mid += 1
        for site, base in BASE.items():
            for w in WIDTHS:
                for p in PAGES:
                    if only and only not in p and only != site and str(w) != only:
                        continue
                    name = (p.strip("/") or "home").replace("/", "-")
                    try:
                        mid = shoot(s, mid, f"{base}/{p}", w, OUT / f"{site}-{w}" / f"{name}.png")
                    except Exception as e:
                        print("FAIL", site, w, p, e)
        s.close()
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()

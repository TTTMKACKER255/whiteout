"""Run after editing the standalone index.html to refresh the checked-in Arcade release."""
import base64
import gzip
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "arcade-build"
MEDIA = ROOT / "arcade-media"

def match_once(source, pattern):
    matches = list(re.finditer(pattern, source, re.DOTALL))
    if len(matches) != 1:
        raise ValueError(f"Expected one match for {pattern!r}, found {len(matches)}")
    return matches[0]

def export():
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    poster = match_once(page, r"#poster\{background-image:url\(data:image/jpeg;base64,([^)]*)\)")
    engine = match_once(page, r'<script id="embedded-engine" type="application/octet-stream">(.*?)</script>')
    engine_js = gzip.decompress(base64.b64decode(engine[1].strip(), validate=True))
    cover_jpeg = base64.b64decode(poster[1], validate=True)
    page = page.replace(engine[0], "")
    import_map = match_once(page, r'<script type="importmap">.*?</script>')
    page = page.replace(import_map[0], "")
    loader = match_once(page, r"async function runtime\(\)\{.*?\n\}")
    page = page.replace(loader[0], 'import * as arcadeEngine from "./three.js";')
    boot = match_once(page, r"T=await runtime\(\);")
    page = page.replace(boot[0], "T=arcadeEngine;")
    BUILD.mkdir(exist_ok=True)
    MEDIA.mkdir(exist_ok=True)
    (BUILD / "index.html").write_text(page, encoding="utf-8")
    (BUILD / "three.js").write_bytes(engine_js)
    (MEDIA / "cover.jpg").write_bytes(cover_jpeg)

if __name__ == "__main__":
    export()

"""Compile a Mermaid .mmd file to a 4K transparent PNG via mmdc.

`{{token}}` in the .mmd (e.g. `stroke:{{danger}}`) is replaced with colors.<token> from
config/brand_tokens.json, so diagrams stay on the token palette.

Also writes <stem>.boxes.json: {"size": [w, h], "boxes": {id: [x, y, w, h]}} in pixels of the
final PNG for every subgraph and node, so the camera can pan/zoom to one (`camera.pan_to`).
"""
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "mermaid_config.json"
COLORS = json.loads((ROOT / "config" / "brand_tokens.json").read_text(encoding="utf-8"))["colors"]
ASPECT_MIN, ASPECT_MAX = 1.2, 2.2  # w/h that sits on a 16:9 canvas without heavy letterboxing


def png_size(path: Path) -> tuple[int, int]:
    return struct.unpack(">II", path.read_bytes()[16:24])


def aspect_warning(w: int, h: int) -> str | None:
    a = w / h
    if a > ASPECT_MAX:
        return (f"{a:.2f}:1 is too wide (max {ASPECT_MAX}:1) - wrap stages in `subgraph ... direction LR` "
                f"blocks stacked under `flowchart TB`, or shorten edge labels")
    if a < ASPECT_MIN:
        return (f"{a:.2f}:1 is too tall (min {ASPECT_MIN}:1) - switch to `flowchart LR` or put "
                f"sequential stages side by side in subgraphs")
    return None


def apply_tokens(text: str) -> str:
    def sub(m: re.Match) -> str:
        if m.group(1) not in COLORS:
            raise KeyError(f"unknown brand token {{{{{m.group(1)}}}}} (have: {', '.join(COLORS)})")
        return COLORS[m.group(1)]
    return re.sub(r"\{\{(\w+)\}\}", sub, text)


def boxes(svg: str) -> dict[str, list[float]]:
    """{id: [x, y, w, h]} in percent of the viewBox (which the PNG covers exactly)."""
    vx, vy, vw, vh = map(float, re.search(r'viewBox="([^"]+)"', svg).group(1).split())
    pct = lambda x, y, w, h: [round((x - vx) / vw * 100, 2), round((y - vy) / vh * 100, 2),
                              round(w / vw * 100, 2), round(h / vh * 100, 2)]
    rid = re.escape(m.group(1)) if (m := re.search(r'<svg[^>]*id="([^"]+)"', svg)) else "my-svg"
    out = {}
    # ponytail: assumes top-level subgraphs (absolute rects); nested ones sit inside a translated <g>.
    for m in re.finditer(rf'<g class="cluster[^"]*" id="{rid}-([^"]+)"[^>]*>\s*<rect[^>]*?x="([\d.-]+)" y="([\d.-]+)" width="([\d.]+)" height="([\d.]+)"', svg):
        out[m.group(1)] = pct(*map(float, m.groups()[1:]))
    for m in re.finditer(r'<g class="node[^"]*" id="[^"]*?flowchart-(.+?)-\d+"[^>]*transform="translate\(([\d.-]+),\s*([\d.-]+)\)"[^>]*>(.*?)</g>', svg, re.S):
        size = re.search(r'width="([\d.]+)" height="([\d.]+)"', m.group(4))
        if size:
            cx, cy, w, h = float(m.group(2)), float(m.group(3)), float(size.group(1)), float(size.group(2))
            out.setdefault(m.group(1), pct(cx - w / 2, cy - h / 2, w, h))
    return out


def render(src: Path, out_dir: Path) -> Path:
    mmdc = shutil.which("mmdc")
    if not mmdc:
        raise RuntimeError("mmdc not found: npm i -g @mermaid-js/mermaid-cli")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{src.stem}.png"
    with tempfile.TemporaryDirectory() as tmp:
        mmd = Path(tmp) / src.name
        mmd.write_text(apply_tokens(src.read_text(encoding="utf-8")), encoding="utf-8")
        compile_ = lambda dst, *extra: subprocess.run(
            [mmdc, "-i", str(mmd), "-o", str(dst), "-c", str(CONFIG), "-b", "transparent", "-q", *extra], check=True)
        compile_(out, "--size", "3840")
        w, h = png_size(out)
        if warning := aspect_warning(w, h):
            print(f"  WARNING {src.name}: {warning}", flush=True)
        svg = Path(tmp) / "d.svg"
        compile_(svg)
        px = {k: [round(v[0] * w / 100), round(v[1] * h / 100), round(v[2] * w / 100), round(v[3] * h / 100)]
              for k, v in boxes(svg.read_text(encoding="utf-8")).items()}
        (out_dir / f"{src.stem}.boxes.json").write_text(json.dumps({"size": [w, h], "boxes": px}, indent=1))
    return out


if __name__ == "__main__":
    assert aspect_warning(3840, 2160) is None
    assert "too wide" in aspect_warning(3840, 979)
    assert "too tall" in aspect_warning(1821, 3840)
    demo = ('<svg viewBox="0 0 200 100"><g class="cluster" id="my-svg-S"><rect x="20" y="10" width="100" height="50"/></g>'
            '<g class="node default" id="my-svg-flowchart-N-0" transform="translate(150, 50)"><rect x="-10" y="-5" width="20" height="10"/></g></svg>')
    assert boxes(demo) == {"S": [10.0, 10.0, 50.0, 50.0], "N": [70.0, 45.0, 10.0, 10.0]}, boxes(demo)
    assert apply_tokens("stroke:{{danger}}") == f"stroke:{COLORS['danger']}"
    if len(sys.argv) > 1:
        print(render(Path(sys.argv[1]), Path(sys.argv[2] if len(sys.argv) > 2 else "build")))

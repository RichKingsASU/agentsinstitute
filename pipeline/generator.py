"""Render every asset referenced by episodes/<ep_id>/manifest.json into build/<ep_id>/.

Usage: python pipeline/generator.py <ep_id> [--only diagram,terminal,code]
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_code
import render_diagram
import render_terminal

ROOT = Path(__file__).resolve().parent.parent
RENDERERS = {"diagram": render_diagram.render, "terminal": render_terminal.render, "code": render_code.render}


def aspect(path: Path) -> float | None:
    if path.suffix == ".png":
        w, h = render_diagram.png_size(path)
        return w / h
    if path.suffix == ".mp4":
        dims = subprocess.run([shutil.which("ffprobe"), "-v", "error", "-select_streams", "v:0", "-show_entries",
                               "stream=width,height", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
        w, h = map(int, dims.strip().split(","))
        return w / h
    if path.suffix == ".svg" and (m := re.search(r'width="(\d+)" height="(\d+)"', path.read_text(encoding="utf-8"))):
        return int(m.group(1)) / int(m.group(2))
    return None


def resolve_camera(scene: dict, out_dir: Path) -> None:
    """camera.pan_to names a subgraph/node; swap in its box from <stem>.boxes.json."""
    cam = scene.get("camera")
    if not cam or "pan_to" not in cam:
        return
    boxes = json.loads((out_dir / f"{Path(scene['output']).stem}.boxes.json").read_text())
    if cam["pan_to"] not in boxes:
        raise KeyError(f"scene {scene['id']}: pan_to {cam['pan_to']!r} not in diagram (have: {', '.join(boxes)})")
    cam["focus"] = boxes[cam["pan_to"]]


def build(ep_id: str, only: set[str] | None = None) -> Path:
    ep_dir = ROOT / "episodes" / ep_id
    manifest = json.loads((ep_dir / "manifest.json").read_text(encoding="utf-8"))
    out_dir = ROOT / "build" / ep_id
    built = out_dir / "manifest.json"
    # Scenes skipped by --only keep the output from the previous build.
    previous = {s["id"]: s.get("output") for s in json.loads(built.read_text(encoding="utf-8"))["scenes"]} if built.exists() else {}
    rendered = {}  # same source used by several scenes renders once
    for scene in manifest["scenes"]:
        src = scene.get("asset")
        if not src:
            continue
        if only and scene["type"] not in only:
            if not previous.get(scene["id"]):
                continue
            scene["output"] = previous[scene["id"]]
        else:
            opts = {k: scene[k] for k in ("highlight_lines", "lines") if scene.get(k)}  # code-card options
            key = f"{src}#{json.dumps(opts, sort_keys=True)}"  # same source + options renders once
            if key not in rendered:
                print(f"[{scene['type']}] {src}", flush=True)
                rendered[key] = RENDERERS[scene["type"]](ep_dir / src, out_dir, **opts).name
            scene["output"] = rendered[key]
        if (a := aspect(out_dir / scene["output"])) is not None:
            scene["aspect"] = round(a, 4)
        resolve_camera(scene, out_dir)
    manifest["epId"] = ep_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return out_dir


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("ep_id")
    p.add_argument("--only", help="comma-separated scene types to render")
    a = p.parse_args()
    print(build(a.ep_id, set(a.only.split(",")) if a.only else None))

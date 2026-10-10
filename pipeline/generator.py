"""Render every asset referenced by episodes/<ep_id>/manifest.json into build/<ep_id>/.

Usage: python pipeline/generator.py <ep_id> [--only diagram,terminal,code]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_code
import render_diagram
import render_terminal

ROOT = Path(__file__).resolve().parent.parent
RENDERERS = {"diagram": render_diagram.render, "terminal": render_terminal.render, "code": render_code.render}


def build(ep_id: str, only: set[str] | None = None) -> Path:
    ep_dir = ROOT / "episodes" / ep_id
    manifest = json.loads((ep_dir / "manifest.json").read_text(encoding="utf-8"))
    out_dir = ROOT / "build" / ep_id
    rendered = {}  # same source used by several scenes renders once
    for scene in manifest["scenes"]:
        src = scene.get("asset")
        if not src or (only and scene["type"] not in only):
            continue
        if src not in rendered:
            print(f"[{scene['type']}] {src}", flush=True)
            rendered[src] = RENDERERS[scene["type"]](ep_dir / src, out_dir).name
        scene["output"] = rendered[src]
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

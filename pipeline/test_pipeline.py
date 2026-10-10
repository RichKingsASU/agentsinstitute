"""End-to-end check: render episodes and validate every output.

Usage: python pipeline/test_pipeline.py [ep_id ...]   (default: all episodes)
"""
import json
import shutil
import textwrap
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generator
from render_diagram import aspect_warning, png_size
from render_terminal import visible_duration

ROOT = Path(__file__).resolve().parent.parent
CAPTION_CHARS, CAPTION_LINES = 95, 3  # 56px mono in a 3200px box; 3 lines is what fits the 480px band


def clip_seconds(path: Path) -> float:
    return float(subprocess.run([shutil.which("ffprobe"), "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout)


def check(ep_id: str) -> None:
    out_dir = generator.build(ep_id)
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    for scene in manifest["scenes"]:
        lines = len(textwrap.wrap(scene["narration"], CAPTION_CHARS))
        assert lines <= CAPTION_LINES, f"{scene['id']}: narration wraps to {lines} caption lines (max {CAPTION_LINES})"
        out = out_dir / scene["output"]
        assert out.stat().st_size > 0, f"empty output {out}"
        if out.suffix == ".png":
            w, h = png_size(out)
            assert w == 3840 or h == 3840, f"{out.name}: expected a 4K long edge, got {w}x{h}"
            assert not (warn := aspect_warning(w, h)), f"{out.name}: {warn}"
        elif out.suffix == ".mp4":
            dur = clip_seconds(out)
            expected = visible_duration((ROOT / "episodes" / ep_id / scene["asset"]).read_text(encoding="utf-8"))
            if expected:
                assert abs(dur - expected) / expected < 0.10, f"{out.name}: {dur:.1f}s vs scripted {expected:.1f}s (playback rate off)"
            assert dur >= scene["duration_s"] - 1, f"{out.name}: {dur:.1f}s clip is shorter than its {scene['duration_s']}s scene"
            assert dur <= scene["duration_s"] + 0.5, f"{out.name}: {dur:.1f}s clip would be cut off by its {scene['duration_s']}s scene (final assertions lost)"
        elif out.suffix == ".svg":
            assert out.read_text(encoding="utf-8").rstrip().endswith("</svg>"), f"{out.name}: malformed svg"
        print(f"ok  {ep_id}  {scene['type']:<9} {out.name}")


def main(ep_ids: list[str]) -> None:
    ep_ids = ep_ids or sorted(p.parent.name for p in (ROOT / "episodes").glob("*/manifest.json"))
    for ep_id in ep_ids:
        check(ep_id)
    print(f"pipeline OK ({len(ep_ids)} episodes)")


if __name__ == "__main__":
    main(sys.argv[1:])

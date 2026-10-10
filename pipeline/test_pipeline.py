"""End-to-end check: every generator runs on ep01 and produces a sane file."""
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generator

EP = "ep01_mcp_servers"


def main():
    out_dir = generator.build(EP)
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    seen = set()
    for scene in manifest["scenes"]:
        out = out_dir / scene["output"]
        assert out.stat().st_size > 0, f"empty output {out}"
        seen.add(scene["type"])
        if out.suffix == ".png":
            w, _ = struct.unpack(">II", out.read_bytes()[16:24])
            assert w == 3840, f"{out.name}: expected 4K width, got {w}"
        elif out.suffix == ".mp4":
            dur = subprocess.run([shutil.which("ffprobe"), "-v", "error", "-show_entries", "format=duration",
                                  "-of", "csv=p=0", str(out)], capture_output=True, text=True, check=True).stdout
            assert float(dur) > 1, f"{out.name}: clip too short ({dur.strip()}s)"
        elif out.suffix == ".svg":
            assert out.read_text(encoding="utf-8").rstrip().endswith("</svg>"), f"{out.name}: malformed svg"
        print(f"ok  {scene['type']:<9} {out.name}")
    assert seen == {"diagram", "terminal", "code"}, f"generators not all exercised: {seen}"
    print("pipeline OK")


if __name__ == "__main__":
    main()

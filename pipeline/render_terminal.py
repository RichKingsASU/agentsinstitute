"""Run a VHS .tape file and export an MP4 clip.

VHS records PNG frames and we encode them with ffmpeg ourselves: VHS 0.12's own
encode step fails silently on Windows (no file, exit 0).
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BG = json.loads((Path(__file__).resolve().parent.parent / "config" / "brand_tokens.json").read_text())["colors"]["background"]


def _tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"{name} not found in PATH (winget install charmbracelet.vhs tsl0922.ttyd Gyan.FFmpeg)")
    return path


def _setting(tape: str, name: str, default: int) -> int:
    m = re.search(rf"^Set {name} (\d+)", tape, re.M)
    return int(m.group(1)) if m else default


def render(src: Path, out_dir: Path) -> Path:
    vhs, ffmpeg = _tool("vhs"), _tool("ffmpeg")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = (out_dir / f"{src.stem}.mp4").resolve()
    tape = src.read_text(encoding="utf-8")
    fps = _setting(tape, "Framerate", 50)
    pad = _setting(tape, "Padding", 60)  # VHS frames exclude padding; we add it back in brand background
    with tempfile.TemporaryDirectory() as tmp:
        frames = Path(tmp) / "frames"
        # Swap any Output lines for a frames dir; tape lives next to the episode so relative commands resolve.
        tmp_tape = src.parent / f".{src.stem}.render.tape"
        body = re.sub(r"^Output .*$\n?", "", tape, flags=re.M)
        tmp_tape.write_text(f'Output "{frames.as_posix()}/"\n{body}', encoding="utf-8")
        try:
            subprocess.run([vhs, tmp_tape.name], cwd=src.parent, check=True, stdout=subprocess.DEVNULL)
        finally:
            tmp_tape.unlink(missing_ok=True)
        if not any(frames.glob("frame-text-*.png")):
            raise RuntimeError(f"vhs produced no frames for {src}")
        subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error",
             "-framerate", str(fps), "-i", str(frames / "frame-text-%05d.png"),
             "-framerate", str(fps), "-i", str(frames / "frame-cursor-%05d.png"),
             "-filter_complex", f"[0][1]overlay,pad=ceil((iw+{2 * pad})/2)*2:ceil((ih+{2 * pad})/2)*2:(ow-iw)/2:(oh-ih)/2:color={BG},format=yuv420p",
             "-c:v", "libx264", "-crf", "18", "-an", str(out)],
            check=True,
        )
    return out


if __name__ == "__main__":
    print(render(Path(sys.argv[1]), Path(sys.argv[2] if len(sys.argv) > 2 else "build")))

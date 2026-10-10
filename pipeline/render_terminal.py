"""Run a VHS .tape file and export an MP4 clip that plays in real time.

VHS records PNG frames and we encode them with ffmpeg ourselves: VHS 0.12's own
encode step fails silently on Windows (no file, exit 0). VHS also drops frames
when screenshots can't keep up with `Set Framerate`, so we measure the real
capture rate (frames / scripted duration) instead of trusting the setting.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

KEYS = {"Enter", "Backspace", "Delete", "Tab", "Space", "Escape", "Up", "Down", "Left", "Right",
        "PageUp", "PageDown", "Home", "End", "Insert"}


def _tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"{name} not found in PATH (winget install charmbracelet.vhs tsl0922.ttyd Gyan.FFmpeg)")
    return path


def _setting(tape: str, name: str, default: float) -> float:
    m = re.search(rf"^Set {name} ([\d.]+)", tape, re.M)
    return float(m.group(1)) if m else default


def _seconds(text: str) -> float:
    m = re.fullmatch(r"([\d.]+)(ms|s|m)?", text)
    n, unit = float(m.group(1)), m.group(2) or "s"
    return n / 1000 if unit == "ms" else n * 60 if unit == "m" else n


def visible_duration(tape: str) -> float | None:
    """Seconds of recorded (non-Hidden) time the tape scripts, or None if a visible Wait makes it unknowable."""
    speed = 0.05
    if m := re.search(r"^Set TypingSpeed (\S+)", tape, re.M):
        speed = _seconds(m.group(1))
    total, hidden = 0.0, False
    for line in tape.splitlines():
        cmd, _, rest = line.strip().partition(" ")
        name, _, at = cmd.partition("@")
        step = _seconds(at) if at else speed
        if name == "Hide":
            hidden = True
        elif name == "Show":
            hidden = False
        elif hidden:
            continue  # hidden setup (even a Wait) isn't recorded
        elif name.startswith("Wait"):
            return None
        elif name == "Sleep":
            total += _seconds(rest)
        elif name == "Type":
            text = re.match(r'\s*(["\'`])(.*)\1', rest)
            total += step * len(text.group(2) if text else rest)
        elif name in KEYS or name.startswith(("Ctrl+", "Alt+", "Shift+")):
            total += step * (int(rest) if rest.strip().isdigit() else 1)
    return total


def render(src: Path, out_dir: Path) -> Path:
    vhs, ffmpeg = _tool("vhs"), _tool("ffmpeg")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = (out_dir / f"{src.stem}.mp4").resolve()
    tape = src.read_text(encoding="utf-8")
    fps = _setting(tape, "Framerate", 50)
    playback = _setting(tape, "PlaybackSpeed", 1.0)
    pad = int(_setting(tape, "Padding", 60))  # VHS frames exclude padding; we add it back below
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
        n = len(list(frames.glob("frame-text-*.png")))
        if not n:
            raise RuntimeError(f"vhs produced no frames for {src}")

        captured = fps
        if (expected := visible_duration(tape)) and abs(n / expected - fps) / fps > 0.03:
            captured = n / expected
            print(f"  note: VHS captured {captured:.1f} fps (asked {fps:g}); encoding at the real rate", flush=True)
        rate = f"{captured * playback:.4f}"
        # Pad with the theme's own background (bottom-left pixel is always empty terminal).
        first = Image.open(min(frames.glob("frame-text-*.png"))).convert("RGB")
        bg = "#{:02X}{:02X}{:02X}".format(*first.getpixel((0, first.height - 1)))
        filt = (f"[0][1]overlay,pad=ceil((iw+{2 * pad})/2)*2:ceil((ih+{2 * pad})/2)*2:(ow-iw)/2:(oh-ih)/2:color={bg},"
                f"fps={fps:g},format=yuv420p")
        subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error",
             "-framerate", rate, "-i", str(frames / "frame-text-%05d.png"),
             "-framerate", rate, "-i", str(frames / "frame-cursor-%05d.png"),
             "-filter_complex", filt, "-c:v", "libx264", "-crf", "18", "-an", str(out)],
            check=True,
        )
    return out


if __name__ == "__main__":
    assert visible_duration('Set TypingSpeed 40ms\nHide\nType "cls"\nShow\nType "ab"\nEnter\nSleep 1.5s\nSleep 500ms') - 2.12 < 1e-9
    assert visible_duration("Wait /done/") is None
    assert visible_duration('Hide' + chr(10) + 'Wait@60s' + chr(10) + 'Show' + chr(10) + 'Sleep 1s') == 1
    if len(sys.argv) > 1:
        print(render(Path(sys.argv[1]), Path(sys.argv[2] if len(sys.argv) > 2 else "build")))

"""Compile a Mermaid .mmd file to a 4K transparent PNG via mmdc."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "mermaid_config.json"


def render(src: Path, out_dir: Path) -> Path:
    mmdc = shutil.which("mmdc")
    if not mmdc:
        raise RuntimeError("mmdc not found: npm i -g @mermaid-js/mermaid-cli")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{src.stem}.png"
    subprocess.run(
        [mmdc, "-i", str(src), "-o", str(out), "-c", str(CONFIG),
         "-b", "transparent", "--size", "3840", "-q"],
        check=True,
    )
    return out


if __name__ == "__main__":
    print(render(Path(sys.argv[1]), Path(sys.argv[2] if len(sys.argv) > 2 else "build")))

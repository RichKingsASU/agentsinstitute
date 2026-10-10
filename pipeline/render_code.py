"""Render a source file as a branded, syntax-highlighted SVG card (Pygments)."""
import json
import sys
from pathlib import Path

from pygments import highlight
from pygments.formatters import SvgFormatter
from pygments.lexers import get_lexer_for_filename
from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, String, Text

ROOT = Path(__file__).resolve().parent.parent
BRAND = json.loads((ROOT / "config" / "brand_tokens.json").read_text())
C = BRAND["colors"]


class BrandStyle(Style):
    background_color = C["surface"]
    styles = {
        Text: C["textPrimary"],
        Comment: f"italic {C['textSecondary']}",
        Keyword: f"bold {C['secondary']}",
        Name.Function: C["primary"],
        Name.Class: f"bold {C['primary']}",
        Name.Decorator: C["primary"],
        Name.Builtin: C["primary"],
        String: "#A5F3FC",
        Number: "#C4B5FD",
        Operator: C["textSecondary"],
    }


def render(src: Path, out_dir: Path, font_size: int = 28, pad: int = 64) -> Path:
    code = src.read_text(encoding="utf-8").rstrip("\n")
    fmt = SvgFormatter(style=BrandStyle, fontfamily=f"{BRAND['fonts']['mono']}, monospace",
                       fontsize=f"{font_size}px", xoffset=pad, yoffset=pad + font_size,
                       ystep=int(font_size * 1.5))
    svg = highlight(code, get_lexer_for_filename(src.name), fmt)
    lines = code.count("\n") + 1
    w = pad * 2 + int(max(len(l) for l in code.splitlines()) * font_size * 0.6)
    h = pad * 2 + lines * int(font_size * 1.5)
    # Pygments emits a bare <svg>; give it a size and a rounded brand card behind the text.
    card = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<rect width="{w}" height="{h}" rx="24" fill="{C["surface"]}" stroke="{C["primary"]}" stroke-opacity="0.35" stroke-width="2"/>')
    svg = svg[svg.index("<g"):].replace("</svg>", "") + "</svg>"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{src.name}.svg"
    out.write_text(card + svg, encoding="utf-8")
    return out


if __name__ == "__main__":
    print(render(Path(sys.argv[1]), Path(sys.argv[2] if len(sys.argv) > 2 else "build")))

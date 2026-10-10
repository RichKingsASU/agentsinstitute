"""Render a source file (or a line range of it) as a branded, syntax-highlighted SVG card."""
import json
import sys
from pathlib import Path

from pygments import highlight
from pygments.formatters import SvgFormatter
from pygments.lexers import get_lexer_for_filename
from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, String, Token

ROOT = Path(__file__).resolve().parent.parent
BRAND = json.loads((ROOT / "config" / "brand_tokens.json").read_text())
C = BRAND["colors"]
MAX_LINES = 36  # more than this and the card's text is unreadable on a 4K frame (< ~40px per line)


class BrandStyle(Style):
    background_color = C["surface"]
    styles = {
        Token: C["textPrimary"],
        Comment: f"italic {C['textSecondary']}",
        Keyword: f"bold {C['syntaxPurple']}",
        Name.Function: C["primary"],
        Name.Class: f"bold {C['primary']}",
        Name.Decorator: C["primary"],
        Name.Builtin: C["primary"],
        String: "#A5F3FC",
        Number: "#C4B5FD",
        Operator: C["textSecondary"],
    }


def render(src: Path, out_dir: Path, highlight_lines: list[int] = (), lines: list[int] | None = None,
           font_size: int = 28, pad: int = 64) -> Path:
    """`lines` = [first, last] (1-based, inclusive) excerpts the file; highlight_lines use file line numbers."""
    all_lines = src.read_text(encoding="utf-8").rstrip().splitlines()
    first, last = lines or (1, len(all_lines))
    shown = all_lines[first - 1:last]
    if len(shown) > MAX_LINES:
        raise ValueError(f"{src.name}: {len(shown)} lines on one card (max {MAX_LINES}); add `\"lines\": [first, last]` to the scene")
    # ponytail: an excerpt is lexed on its own, so starting mid-docstring mis-colors it; start on a statement.
    code = "\n".join(shown)
    step, char_w = int(font_size * 1.5), font_size * 0.6
    gutter = int((len(str(last)) + 2) * char_w)
    fmt = SvgFormatter(style=BrandStyle, fontfamily=f"{BRAND['fonts']['mono']}, monospace",
                       fontsize=f"{font_size}px", xoffset=pad + gutter, yoffset=pad + font_size, ystep=step)
    svg = highlight(code, get_lexer_for_filename(src.name), fmt)
    w = pad * 2 + gutter + int(max(map(len, shown)) * char_w)
    h = pad * 2 + len(shown) * step
    # Pygments emits a bare <svg>; give it a size and a rounded brand card behind the text.
    card = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<rect width="{w}" height="{h}" rx="24" fill="{C["surface"]}" stroke="{C["primary"]}" stroke-opacity="0.35" stroke-width="2"/>')
    for n in highlight_lines:  # bar behind the line, plus an accent tick in the gutter
        if first <= n <= last:
            y = pad + (n - first) * step + int(font_size * 0.3)
            card += (f'<rect x="{pad // 2}" y="{y}" width="{w - pad}" height="{step}" fill="{C["primary"]}" fill-opacity="0.12"/>'
                     f'<rect x="{pad // 2}" y="{y}" width="6" height="{step}" fill="{C["primary"]}"/>')
    for i, n in enumerate(range(first, last + 1)):  # line numbers, right-aligned in the gutter
        card += (f'<text x="{pad + gutter - char_w * 2:.0f}" y="{pad + font_size + i * step}" text-anchor="end" '
                 f'font-family="{BRAND["fonts"]["mono"]}, monospace" font-size="{font_size}px" fill="{C["textSecondary"]}" '
                 f'fill-opacity="0.6">{n}</text>')
    svg = svg[svg.index("<g"):].replace("</svg>", "") + "</svg>"
    suffix = (f".L{first}-{last}" if lines else "") + (".hl" + "-".join(map(str, highlight_lines)) if highlight_lines else "")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{src.name}{suffix}.svg"
    out.write_text(card + svg, encoding="utf-8")
    return out


if __name__ == "__main__":
    print(render(Path(sys.argv[1]), Path(sys.argv[2] if len(sys.argv) > 2 else "build")))

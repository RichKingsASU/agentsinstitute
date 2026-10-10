# Engineering Rules — Agents Institute Media

## Visual
- Dark mode only. Background `#0B0F19`, cards `#151C2C`. Tokens live in `config/brand_tokens.json` — never hardcode a color that isn't there.
- High contrast: text `#F1F5F9` on dark; `#94A3B8` only for secondary labels.
- Accents: `#00F0FF` (primary, lines/highlights), `#7000FF` (secondary, grouping/emphasis). One accent per element.
- `#7000FF` is for borders, glows and fills only. It is too dark for text on `#0B0F19`/`#151C2C`. Code keywords use `colors.syntaxPurple` (`#C084FC`), a permanent token that `render_code.py` maps to Pygments `Keyword`.
- Type: `JetBrains Mono` for code, terminals, captions; `Inter` for titles.
- `colors.danger` (`#EF4444`, stroke) and `colors.dangerText` (`#F87171`, text) mark failure or anti-pattern paths only, such as a naive approach next to the right one.
- 16:9 safe zones: captions sit at least 160px above the bottom edge (`SAFE_BOTTOM`), and visuals stay above the 480px caption band (`CAPTION_BAND`), both in `remotion/src/brand.ts`. Nothing may sit under the captions.
- Zero cartoon styling: no mascots, emoji, clip-art, hand-drawn fonts, bouncy cutesy motion. Motion is spring-damped and purposeful.

## Content
- Terminal-first. Show real commands, real output, real protocol messages. If it can be demoed in a shell, demo it in a shell (`.tape`).
- Technical depth over hand-waving: name the transport, the message shape, the failure mode.
- Diagrams describe the actual mechanism (who calls whom, over what), not marketing boxes.
- Architecture diagrams use subgraphs or multi-row layouts (`flowchart TB` with `subgraph ... direction LR` rows). The rendered aspect ratio must fall between 1.2:1 and 2.2:1. `render_diagram.py` warns and `test_pipeline.py` fails outside that range.
- Every terminal demo ends in concrete, working assertions: real `assert`s on the numbers it just showed (counts, invariants, a timed benchmark against a threshold) and a printed PASS line. A demo that only prints output doesn't count.
- Tapes: `Set Framerate 30` and `Set PlaybackSpeed 1.0`. A tape's scripted duration must cover its manifest scene (`test_pipeline.py` checks).
- Every asset is generated from source in `episodes/<ep_id>/` — no hand-edited renders.

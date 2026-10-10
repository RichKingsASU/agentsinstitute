# Engineering Rules — Agents Institute Media

## Visual
- Dark mode only. Background `#0B0F19`, cards `#151C2C`. Tokens live in `config/brand_tokens.json` — never hardcode a color that isn't there.
- High contrast: text `#F1F5F9` on dark; `#94A3B8` only for secondary labels.
- Accents: `#00F0FF` (primary, lines/highlights), `#7000FF` (secondary, grouping/emphasis). One accent per element.
- Type: `JetBrains Mono` for code, terminals, captions; `Inter` for titles.
- Zero cartoon styling: no mascots, emoji, clip-art, hand-drawn fonts, bouncy cutesy motion. Motion is spring-damped and purposeful.

## Content
- Terminal-first. Show real commands, real output, real protocol messages. If it can be demoed in a shell, demo it in a shell (`.tape`).
- Technical depth over hand-waving: name the transport, the message shape, the failure mode.
- Diagrams describe the actual mechanism (who calls whom, over what), not marketing boxes.
- Every asset is generated from source in `episodes/<ep_id>/` — no hand-edited renders.

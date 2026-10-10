# Agents Institute Media Engine

Builds technical videos for agents-institute.com from source files: Mermaid → 4K PNG, VHS tapes → MP4, code → SVG cards, then Remotion makes the final 3840x2160@60 video.

## Commands (Windows PowerShell 5.1; there is no `pwsh`)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 setup            # winget tools, fonts, pip + npm deps
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 test-pipeline    # renders ep01 and checks every generator's output
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 render-assets -Episode ep01_mcp_servers
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 render-video  -Episode ep01_mcp_servers   # -> out/<ep>.mp4

python pipeline/generator.py <ep_id> [--only diagram,code,terminal]   # quick: skip the slow terminal render
python pipeline/render_diagram.py <file.mmd> [out_dir]                # each renderer also runs on its own
cd remotion; npx remotion studio; npx tsc --noEmit
```

## Layout

- `episodes/<ep_id>/manifest.json`: scenes `{id, type: diagram|terminal|code, asset, duration_s, narration}`. `asset` is a path relative to the episode folder.
- `pipeline/generator.py`: renders each scene's asset into `build/<ep_id>/` and writes `build/<ep_id>/manifest.json`, which adds `output` and `epId`. That file becomes the Remotion `--props`.
- `remotion/src/`: `Root.tsx` (composition `Episode`), `Episode.tsx` (scene `Series`), `components/` (TerminalPlayer, DiagramView, Captions). `render-video` copies `build/<ep>` to `remotion/public/<ep>`.
- `config/brand_tokens.json`: the only source of colors and fonts. Python (`render_code.py`, `render_terminal.py`) and TS (`remotion/src/brand.ts`) both read it.
- `.agents/rules/engineering.md`: visual and content rules. Follow them (dark, high contrast, terminal-first, no cartoon styling).

## Gotchas

- New shells may not see tools winget installed. `build.ps1` reloads PATH from the registry; for ad-hoc runs, open a new terminal.
- VHS 0.12's own MP4 encode fails silently on Windows. `render_terminal.py` therefore has VHS write PNG frames and encodes them with ffmpeg itself. Don't put `Output` lines in tapes; they get stripped.
- mmdc 12 has no `-w/-H` flags; use `--size`.
- JetBrains Mono and Inter are installed per-user by `setup`. Without them, mmdc and VHS silently fall back to other fonts.
- Tapes run from their episode folder (`Set Shell "powershell"`), so they can call `python client.py` and similar scripts.

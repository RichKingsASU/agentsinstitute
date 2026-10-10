# Agents Institute Media Engine

Builds technical videos for agents-institute.com from source files: Mermaid → 4K PNG, VHS tapes → MP4, code → SVG cards, then Remotion makes the final 3840x2160@60 video.

## Commands (Windows PowerShell 5.1; there is no `pwsh`)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 setup            # winget tools, fonts, pip + npm deps
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 test-pipeline    # renders + validates ALL episodes (or -Episode X)
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 render-assets [-Episode X]
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 render-video  [-Episode X]   # -> out/<ep>.mp4
make render-video EP=ep02_agent_loops                                       # same, via Makefile (needs GNU make)

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

Omitting `-Episode`/`EP` targets the episode folder with the most recently modified file, and the script prints which one. Pass it explicitly in automation.

## Standards (enforced by `pipeline/test_pipeline.py`)

- Diagrams: the aspect ratio must be 1.2–2.2:1. Use multi-row layouts (`flowchart TB` + `subgraph ... direction LR`).
- Terminal clips: real-time playback (within 10% of the tape's scripted duration) and at least as long as the scene. Tapes use `Set Framerate 30` and `Set PlaybackSpeed 1.0`, and every demo ends in real `assert`s plus a PASS line.
- Colors come only from `config/brand_tokens.json`. `colors.syntaxPurple` (`#C084FC`) is for code keywords; `#7000FF` is never used for text.
- Safe zones: captions sit 160px above the bottom edge, and visuals stay above the 480px caption band (`remotion/src/brand.ts`).

## Gotchas

- New shells may not see tools winget installed. `build.ps1` reloads PATH from the registry; for ad-hoc runs, open a new terminal.
- VHS 0.12's own MP4 encode fails silently on Windows. `render_terminal.py` therefore has VHS write PNG frames and encodes them with ffmpeg itself. Don't put `Output` lines in tapes; they get stripped.
- VHS drops frames when it can't keep up, so a 60fps tape captured about 32fps and played 2x fast. `render_terminal.py` measures the real capture rate (frames ÷ scripted duration) and encodes at that rate. Tapes containing `Wait` can't be measured, so their `Framerate` is trusted as-is.
- Terminal padding is filled with the color of the frame's bottom-left pixel, so any VHS theme (brand JSON or built-ins like `Catppuccin Mocha`) gets a matching border.
- mmdc 12 has no `-w/-H` flags; use `--size`.
- JetBrains Mono and Inter are installed per-user by `setup`. Without them, mmdc and VHS silently fall back to other fonts.
- Tapes run from their episode folder (`Set Shell "powershell"`), so they can call `python client.py` and similar scripts.

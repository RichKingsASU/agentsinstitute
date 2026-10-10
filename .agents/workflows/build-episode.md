---
description: Build, render assets, and export video for a target episode
---

# Build Episode

Target: `episodes/<ep_id>/` (e.g. `ep01_mcp_servers`).

1. Validate toolchain (mmdc, vhs, ffmpeg, Python 3.10+, Node 20+):
   `powershell -ExecutionPolicy Bypass -File scripts/build.ps1 setup`
2. Review `episodes/<ep_id>/manifest.json` — scene order, `duration_s`, `narration`, and each scene's `asset` source file.
3. Render assets (diagrams → 4K PNG, tapes → MP4, code → SVG) into `build/<ep_id>/`:
   `python pipeline/generator.py <ep_id>`
4. Check `build/<ep_id>/` contains one output per manifest scene. Fix sources and re-run step 3 on failure.
5. Render the video with Remotion (copies `build/<ep_id>` into `remotion/public/` and renders 3840x2160@60):
   `powershell -ExecutionPolicy Bypass -File scripts/build.ps1 render-video -Episode <ep_id>`
6. Output: `out/<ep_id>.mp4`. Preview interactively with `cd remotion; npx remotion studio`.

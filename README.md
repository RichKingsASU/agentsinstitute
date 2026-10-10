# agentsinstitute

Automated technical video production engine for [Agents Institute](https://agents-institute.com).

Source files go in, finished 4K video comes out. Mermaid diagrams render to 4K PNGs, VHS tapes to terminal MP4s, and code to SVG cards. Remotion then builds the final 3840x2160@60fps video.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 setup
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 test-pipeline
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 render-video -Episode ep01_mcp_servers
```

See [CLAUDE.md](CLAUDE.md) for the layout and gotchas, and [.agents/workflows/build-episode.md](.agents/workflows/build-episode.md) for the episode workflow.

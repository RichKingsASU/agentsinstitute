import { Composition } from "remotion";
import { Episode } from "./Episode";
import { Manifest, VIDEO } from "./brand";

// Real manifests come from build/<ep_id>/manifest.json via --props (scripts/build.ps1 render-video).
const placeholder: Manifest = {
  epId: "",
  title: "Agents Institute",
  scenes: [{ id: "empty", type: "diagram", duration_s: 3, narration: "Run scripts/build.ps1 render-video to load an episode." }],
};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Episode"
    component={Episode}
    width={VIDEO.width}
    height={VIDEO.height}
    fps={VIDEO.fps}
    durationInFrames={VIDEO.fps * 3}
    defaultProps={placeholder}
    calculateMetadata={({ props }) => ({
      durationInFrames: Math.max(1, Math.round(props.scenes.reduce((s, sc) => s + sc.duration_s, 0) * VIDEO.fps)),
    })}
  />
);

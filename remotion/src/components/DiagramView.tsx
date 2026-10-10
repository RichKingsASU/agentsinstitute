import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { CAPTION_BAND, Scene } from "../brand";

const PAD_X = 200;
const PAD_TOP = 120;

// Spring entry, then either a camera move onto camera.focus or a slow push-in drift.
export const DiagramView: React.FC<{ src: string; aspect?: number; camera?: Scene["camera"] }> = ({ src, aspect, camera }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width, height } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 200, mass: 0.8 } });
  const drift = interpolate(frame, [0, durationInFrames], [0, 1], { extrapolateRight: "clamp" });

  // Size the image box ourselves (object-fit: contain) so % focus coords map onto it exactly.
  const availW = width - 2 * PAD_X;
  const availH = height - PAD_TOP - CAPTION_BAND;
  const a = aspect ?? availW / availH;
  const boxW = Math.min(availW, availH * a);
  const boxH = boxW / a;

  let scale = interpolate(enter, [0, 1], [0.85, 0.92]) * (1 + 0.08 * drift); // peaks at 0.99: edges stay inside the clip
  let fx = 50;
  let fy = 50;
  if (camera?.focus) {
    const [x, y, w, h] = camera.focus;
    // Fill ~85% of the frame with the target box, never zooming out past 1x or in past 3x.
    const target = Math.min(3, Math.max(1, Math.min((0.85 * availW) / ((w / 100) * boxW), (0.85 * availH) / ((h / 100) * boxH))));
    const move = spring({ frame: frame - fps * 0.8, fps, config: { damping: 200, mass: 1.4 } });
    scale = interpolate(move, [0, 1], [camera.initial_zoom ?? 1, target]) * (1 + 0.03 * drift);
    fx = interpolate(move, [0, 1], [50, x + w / 2]);
    fy = interpolate(move, [0, 1], [50, y + h / 2]);
  } else if (camera?.initial_zoom) {
    scale *= camera.initial_zoom;
  }

  return (
    <AbsoluteFill style={{ padding: `${PAD_TOP}px ${PAD_X}px ${CAPTION_BAND}px`, alignItems: "center", justifyContent: "center", opacity: enter }}>
      {/* Clip to the safe area so a zoomed camera never runs under the captions. */}
      <div style={{ width: availW, height: availH, overflow: "hidden", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ width: boxW, height: boxH, flexShrink: 0, transform: `scale(${scale}) translate(${50 - fx}%, ${50 - fy}%)` }}>
          <Img src={src} style={{ width: "100%", height: "100%" }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

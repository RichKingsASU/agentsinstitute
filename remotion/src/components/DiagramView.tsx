import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// Spring zoom-in on entry, then a slow push-in/pan across the rest of the scene.
export const DiagramView: React.FC<{ src: string }> = ({ src }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 200, mass: 0.8 } });
  const drift = interpolate(frame, [0, durationInFrames], [0, 1], { extrapolateRight: "clamp" });
  const scale = interpolate(enter, [0, 1], [0.85, 1]) * (1 + 0.08 * drift);
  const panY = interpolate(drift, [0, 1], [2, -2]); // percent

  return (
    <AbsoluteFill style={{ padding: "120px 200px 420px", opacity: enter }}>
      <Img
        src={src}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "contain",
          transform: `translateY(${panY}%) scale(${scale})`,
        }}
      />
    </AbsoluteFill>
  );
};

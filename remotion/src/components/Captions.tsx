import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, MONO } from "../brand";

// Narration typed out word-by-word across the first ~80% of the scene, with a block cursor.
export const Captions: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();
  const words = text.split(" ");
  const shown = Math.ceil(
    interpolate(frame, [fps * 0.3, durationInFrames * 0.8], [0, words.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );
  const cursorOn = Math.floor(frame / (fps / 2)) % 2 === 0;

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 120 }}>
      <div
        style={{
          maxWidth: 3200,
          padding: "36px 56px",
          background: `${C.background}E6`,
          borderLeft: `8px solid ${C.primary}`,
          borderRadius: 12,
          fontFamily: MONO,
          fontSize: 64,
          lineHeight: 1.35,
          color: C.textPrimary,
        }}
      >
        {words.slice(0, shown).join(" ")}
        <span style={{ color: C.primary, opacity: cursorOn ? 1 : 0 }}>█</span>
      </div>
    </AbsoluteFill>
  );
};

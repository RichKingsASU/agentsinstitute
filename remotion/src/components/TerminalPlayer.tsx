import { AbsoluteFill, OffthreadVideo, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, MONO } from "../brand";

// VHS clip framed as a terminal window.
export const TerminalPlayer: React.FC<{ src: string; title: string }> = ({ src, title }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 200 } });

  return (
    <AbsoluteFill style={{ alignItems: "center", paddingTop: 100 }}>
      <div
        style={{
          width: 2800,
          borderRadius: 24,
          overflow: "hidden",
          background: C.background,
          border: `2px solid ${C.primary}55`,
          boxShadow: `0 0 120px ${C.secondary}33`,
          opacity: enter,
          transform: `translateY(${(1 - enter) * 60}px)`,
        }}
      >
        <div
          style={{
            height: 72,
            background: C.surface,
            display: "flex",
            alignItems: "center",
            padding: "0 32px",
            fontFamily: MONO,
            fontSize: 30,
            color: C.textSecondary,
          }}
        >
          <span style={{ color: C.primary }}>▍</span>&nbsp;{title}
        </div>
        <OffthreadVideo src={src} muted style={{ width: "100%", display: "block" }} />
      </div>
    </AbsoluteFill>
  );
};

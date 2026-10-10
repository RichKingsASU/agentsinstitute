import { AbsoluteFill, OffthreadVideo, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, CAPTION_BAND, MONO } from "../brand";

const TOP = 60;
const BAR = 72; // title bar height
const MAX_W = 3440;

// VHS clip framed as a terminal window sized to the clip's own aspect ratio (no letterbox bars).
export const TerminalPlayer: React.FC<{ src: string; title: string; aspect?: number }> = ({ src, title, aspect = 16 / 9 }) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 200 } });
  const videoW = Math.min(MAX_W, (height - TOP - CAPTION_BAND - BAR) * aspect);
  const videoH = videoW / aspect;

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", paddingTop: TOP, paddingBottom: CAPTION_BAND }}>
      <div
        style={{
          width: videoW,
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
            height: BAR,
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
        <OffthreadVideo src={src} muted style={{ width: videoW, height: videoH, display: "block" }} />
      </div>
    </AbsoluteFill>
  );
};

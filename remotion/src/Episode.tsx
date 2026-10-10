import { AbsoluteFill, Series, staticFile, useVideoConfig } from "remotion";
import { C, Manifest, Scene } from "./brand";
import { Captions } from "./components/Captions";
import { DiagramView } from "./components/DiagramView";
import { TerminalPlayer } from "./components/TerminalPlayer";

const Visual: React.FC<{ scene: Scene; epId: string }> = ({ scene, epId }) => {
  if (!scene.output) return null;
  const src = staticFile(`${epId}/${scene.output}`);
  return scene.type === "terminal" ? <TerminalPlayer src={src} title={scene.asset ?? ""} /> : <DiagramView src={src} />;
};

export const Episode: React.FC<Manifest> = ({ epId, scenes }) => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: C.background }}>
      <Series>
        {scenes.map((scene) => (
          <Series.Sequence key={scene.id} durationInFrames={Math.round(scene.duration_s * fps)}>
            <Visual scene={scene} epId={epId} />
            <Captions text={scene.narration} />
          </Series.Sequence>
        ))}
      </Series>
    </AbsoluteFill>
  );
};

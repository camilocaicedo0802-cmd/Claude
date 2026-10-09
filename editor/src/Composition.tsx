import { AbsoluteFill, Composition } from "remotion";
import { COLORS, FONT_FACES, FONTS, VIDEO } from "./brand";

// Plantilla vacía: la edición real se monta en el paso 3.
export const MyComponent: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.marfil, justifyContent: "center", alignItems: "center" }}>
      <style>{FONT_FACES}</style>
      <div style={{ fontFamily: FONTS.display, fontSize: 140, color: COLORS.petroleo }}>Beleza</div>
      <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 56, color: COLORS.salvia }}>Drena Oil</div>
    </AbsoluteFill>
  );
};

export const MyComposition = () => {
  return (
    <Composition
      id="Editor"
      component={MyComponent}
      durationInFrames={VIDEO.fps * 5}
      fps={VIDEO.fps}
      width={VIDEO.width}
      height={VIDEO.height}
    />
  );
};

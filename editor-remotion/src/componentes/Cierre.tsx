import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLOR } from "../estilo";

const fijar = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Cierre: logo de AgroKrack sobre el crema de su propio fondo. */
export const Cierre: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLOR.crema,
        background: `radial-gradient(ellipse 90% 60% at 50% 46%, #EFE8DC 0%, ${COLOR.crema} 60%, #CFC5B6 100%)`,
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Img
        src={staticFile("img/logo_agrokrack.png")}
        style={{
          width: 820,
          marginTop: -70,
          // El fondo blanco del logo se funde con el crema.
          mixBlendMode: "multiply",
          opacity: interpolate(t, [0.02, 0.22], [0, 1], fijar),
          scale:
            interpolate(t, [0, 0.55], [0.86, 1], { ...fijar, easing: Easing.out(Easing.cubic) }) * (1 + 0.012 * t),
        }}
      />
    </AbsoluteFill>
  );
};

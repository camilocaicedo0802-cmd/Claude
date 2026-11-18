import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { TRANSICION_LUZ } from "../estilo";

export const ANTES_DEL_CORTE = 0.32; // s que la transición empieza antes del corte
export const DESPUES_DEL_CORTE = TRANSICION_LUZ.durBajada + 0.04;

const fijar = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/**
 * Transición "anillo + fuga de luz naranja" (estilo.md §9).
 * Un anillo fino crece desde el centro; después la luz cubre el cuadro justo en el corte y
 * se disuelve sobre el plano nuevo. Se monta `ANTES_DEL_CORTE` s antes del corte.
 */
export const TransicionLuz: React.FC<{ semilla: number }> = ({ semilla }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps - ANTES_DEL_CORTE; // 0 = instante del corte

  // Anillo
  const tAnillo0 = -ANTES_DEL_CORTE;
  const avanceAnillo = interpolate(t, [tAnillo0, -0.03], [0, 1], { ...fijar, easing: Easing.out(Easing.quad) });
  const diametro = 260 + avanceAnillo * 1500;
  const opAnillo = interpolate(t, [tAnillo0, tAnillo0 + 0.05, -0.1, -0.02], [0, 0.9, 0.7, 0], fijar);

  // Fuga de luz
  const fuerza = interpolate(
    t,
    [-TRANSICION_LUZ.durSubida, 0, TRANSICION_LUZ.durBajada],
    [0, TRANSICION_LUZ.opacidadMax, 0],
    { ...fijar, easing: Easing.inOut(Easing.quad) },
  );
  // La mancha de luz cruza el cuadro; la semilla decide por qué lado entra.
  const lado = semilla % 2 === 0 ? 1 : -1;
  const cx = 50 + lado * interpolate(t, [-TRANSICION_LUZ.durSubida, TRANSICION_LUZ.durBajada], [42, -30], fijar);
  const cy = 38 + ((semilla * 13) % 24);

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {/* Tinte naranja que tapa el corte */}
      <AbsoluteFill style={{ backgroundColor: "#EE7F22", opacity: fuerza * 0.82 }} />
      {/* Núcleo de luz */}
      <AbsoluteFill
        style={{
          mixBlendMode: "screen",
          opacity: fuerza * 0.6,
          background: `radial-gradient(ellipse 80% 55% at ${cx}% ${cy}%, rgba(255,196,120,1) 0%, rgba(255,140,50,0.9) 24%, rgba(230,100,24,0.6) 54%, rgba(190,70,10,0) 86%)`,
        }}
      />
      <AbsoluteFill
        style={{
          mixBlendMode: "screen",
          opacity: fuerza * 0.45,
          background: `radial-gradient(ellipse 60% 110% at ${100 - cx}% ${92 - cy}%, rgba(255,150,60,0.9) 0%, rgba(230,100,30,0.5) 45%, rgba(160,50,0,0) 80%)`,
        }}
      />
      {/* Anillo */}
      <div
        style={{
          position: "absolute",
          left: width / 2 - diametro / 2,
          top: height * 0.47 - diametro / 2,
          width: diametro,
          height: diametro,
          borderRadius: "50%",
          border: "7px solid rgba(255,170,80,0.95)",
          boxShadow: "0 0 34px 8px rgba(255,140,50,0.75), inset 0 0 34px 8px rgba(255,140,50,0.55)",
          filter: "blur(2px)",
          mixBlendMode: "screen",
          opacity: opAnillo,
        }}
      />
    </AbsoluteFill>
  );
};

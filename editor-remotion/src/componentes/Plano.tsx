import { Video } from "@remotion/media";
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { Plano as PlanoT } from "../datos/edicion";
import { ZOOM } from "../estilo";

/**
 * Un plano de vídeo: reencuadre fijo + golpe de zoom al entrar (estilo.md §3) con
 * desenfoque de movimiento en los primeros fotogramas, deriva lenta opcional y viñeta.
 */
export const Plano: React.FC<{ plano: PlanoT }> = ({ plano }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;

  const golpe = (s: number) =>
    plano.zoom
      ? interpolate(s, [0, plano.zoom.dur], [plano.zoom.de, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        })
      : 1;

  const z = golpe(t);
  const velocidad = Math.abs(z - golpe(t + 1 / fps)) * fps; // cambio de escala por segundo
  const desenfoque = Math.min(ZOOM.desenfoqueMax, velocidad * 4);

  const { fx, fy, dx, dy } = plano.encuadre;
  const escala = Math.max(1, plano.encuadre.escala * z * (1 + (plano.deriva ?? 0) * t));
  // El punto (fx, fy) del original va a (dx, dy) de la pantalla, sin dejar bordes vacíos.
  const tx = Math.min(0, Math.max(width - escala * width, dx * width - escala * fx * width));
  const ty = Math.min(0, Math.max(height - escala * height, dy * height - escala * fy * height));

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width,
          height,
          transformOrigin: "0 0",
          transform: `translate(${tx}px, ${ty}px) scale(${escala})`,
          // Etalonado suave: algo más de contraste y saturación sobre el material de móvil.
          filter: `contrast(1.06) saturate(1.14)${desenfoque > 0.3 ? ` blur(${desenfoque.toFixed(2)}px)` : ""}`,
        }}
      >
        <Video
          src={staticFile(`clips/${plano.clip}.mp4`)}
          trimBefore={Math.round(plano.src * fps)}
          muted
          objectFit="cover"
          style={{ width: "100%", height: "100%" }}
        />
      </div>
      {/* Viñeta ligera (§10) */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 85% 75% at 50% 48%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.3) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

import { Video } from "@remotion/media";
import { AbsoluteFill, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BASE, camara, desenfoqueTH } from "../camara";

// Capa "base" = toma completa con el fondo virado a cian (§8). Capa "persona" = solo la persona (alfa),
// con piel cálida, por encima de las palabras gigantes que van "detrás".
export const ARoll: React.FC<{ capa: "base" | "persona" }> = ({ capa }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const cam = camara(t);
  const { blur, extra } = desenfoqueTH(frame);
  const filtroBase = "contrast(1.05) saturate(1.08) brightness(1.02)"; // color natural (UGC)
  const filtroPersona = filtroBase;
  return (
    <AbsoluteFill
      style={{
        // Reencuadre base: la toma UGC tiene la cara muy abajo (techo arriba). Escala 1,3 y sube 288 px
        // (el borde inferior nunca deja ver negro: 960·(s−1) + y ≥ 0).
        scale: String(BASE.s * (cam.s + extra)),
        translate: `0px ${BASE.y * (cam.s + extra) + cam.y}px`,
        filter: blur > 0.05 ? `blur(${blur}px)` : undefined,
      }}
    >
      {capa === "base" ? (
        <>
          <Video src={staticFile("edit/aroll.mp4")} muted objectFit="cover" style={{ width: "100%", height: "100%", filter: filtroBase }} />
        </>
      ) : (
        <Video src={staticFile("edit/aroll_persona.webm")} muted objectFit="cover" style={{ width: "100%", height: "100%", filter: filtroPersona }} />
      )}
    </AbsoluteFill>
  );
};

// Viñeta suave para dar profundidad y legibilidad al texto blanco
export const Vineta: React.FC = () => (
  <AbsoluteFill style={{ background: "radial-gradient(ellipse 75% 60% at 50% 42%, rgba(0,0,0,0) 55%, rgba(0,10,25,0.38) 100%)", pointerEvents: "none" }} />
);

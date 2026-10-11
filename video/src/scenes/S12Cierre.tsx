import React from "react";
import { AbsoluteFill } from "remotion";
import { easeOut, kf } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C, F } from "../theme";

export const S12 = { start: 41.3, end: 43.2 };

/**
 * Cierre elegante: fondo claro que llega con un fundido suave desde el reloj de arena; el usuario entra con
 * opacidad y un pequeño desplazamiento vertical; fundido final a negro mientras la música se apaga con su cola.
 */
export const S12Cierre: React.FC<{ start?: number; handle?: string }> = ({ start = S12.start, handle = "@tu.usuario" }) => {
  const { g } = useSceneTime(start);
  const h = kf(g, [41.9, 42.4], [0, 1], easeOut);
  const toBlack = kf(g, [42.85, 43.2], [0, 1]);
  return (
    <AbsoluteFill style={{ backgroundColor: C.paper }}>
      <div
        style={{
          position: "absolute",
          top: 1920 * 0.47 - 26,
          width: "100%",
          textAlign: "center",
          fontFamily: F.sans,
          fontWeight: 800,
          fontSize: 46,
          letterSpacing: "-0.02em",
          color: C.ink,
          opacity: h,
          translate: `0px ${(1 - h) * 22}px`,
        }}
      >
        {handle}
      </div>
      <AbsoluteFill style={{ backgroundColor: "#000", opacity: toBlack }} />
    </AbsoluteFill>
  );
};

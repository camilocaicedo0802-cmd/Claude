import React from "react";
import { AbsoluteFill } from "remotion";
import { useSceneTime } from "../lib/useSceneTime";
import { C, F } from "../theme";

export const S12 = { start: 41.3, end: 42.6 };

/** Tarjeta de cierre gris (estilo.md §3) y negro final. Cambia `handle` por tu usuario. */
export const S12Cierre: React.FC<{ start?: number; handle?: string }> = ({ start = S12.start, handle = "@tu.usuario" }) => {
  const { g } = useSceneTime(start);
  if (g >= 42.3) return <AbsoluteFill style={{ backgroundColor: "#000" }} />;
  return (
    <AbsoluteFill style={{ backgroundColor: C.endCard }}>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 80% 70% at 50% 48%, rgba(255,255,255,0.06) 0%, rgba(0,0,0,0.18) 100%)" }} />
      <div
        style={{
          position: "absolute",
          top: 1920 * 0.46 - 26,
          width: "100%",
          textAlign: "center",
          fontFamily: F.sans,
          fontWeight: 800,
          fontSize: 44,
          letterSpacing: "-0.02em",
          color: C.ink,
        }}
      >
        {handle}
      </div>
    </AbsoluteFill>
  );
};

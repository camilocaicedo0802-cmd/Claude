import React from "react";
import { AbsoluteFill } from "remotion";
import { H, W } from "../theme";

/** Cámara 2D: coloca el punto del mundo (cx, cy) en el centro de la pantalla, con zoom y giro. */
export const Camera: React.FC<{ cx: number; cy: number; scale?: number; rotate?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({
  cx,
  cy,
  scale = 1,
  rotate = 0,
  children,
  style,
}) => (
  <AbsoluteFill style={{ overflow: "hidden", ...style }}>
    <div
      style={{
        position: "absolute",
        left: 0,
        top: 0,
        width: W,
        height: H,
        transformOrigin: "0 0",
        transform: `translate(${W / 2}px, ${H / 2}px) scale(${scale}) rotate(${rotate}deg) translate(${-cx}px, ${-cy}px)`,
      }}
    >
      {children}
    </div>
  </AbsoluteFill>
);

import React from "react";
import { Img, staticFile } from "remotion";

// Registro de recortes (public/img/<nombre>.png) con su tamaño natural [ancho, alto].
// Obtén los tamaños con: python3 -c "from PIL import Image;print(Image.open('x.png').size)"
export const IMG: Record<string, readonly [number, number]> = {
  // ejemplo: hourglass: [830, 1833],
};

/** Recorte fotográfico posicionado por su centro, con sombra proyectada configurable. */
export const Cutout: React.FC<{
  name: string;
  cx: number;
  cy: number;
  width?: number;
  height?: number;
  rotate?: number;
  scale?: number;
  opacity?: number;
  brightness?: number;
  shadow?: string | false; // CSS drop-shadow, p. ej. "20px 24px 22px rgba(0,0,0,0.45)"
  style?: React.CSSProperties;
}> = ({ name, cx, cy, width, height, rotate = 0, scale = 1, opacity = 1, brightness = 1, shadow = "20px 24px 22px rgba(0,0,0,0.45)", style }) => {
  const [nw, nh] = IMG[name] ?? [1000, 1000];
  const w = width ?? (height ? (height * nw) / nh : nw);
  const h = height ?? (w * nh) / nw;
  const filters = [brightness !== 1 ? `brightness(${brightness})` : "", shadow ? `drop-shadow(${shadow})` : ""].join(" ").trim();
  return (
    <Img
      src={staticFile(`img/${name}.png`)}
      style={{ position: "absolute", left: cx - w / 2, top: cy - h / 2, width: w, height: h, rotate: `${rotate}deg`, scale: `${scale}`, opacity, filter: filters || undefined, ...style }}
    />
  );
};

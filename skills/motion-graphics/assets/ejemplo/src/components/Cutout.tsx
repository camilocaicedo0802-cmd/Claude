import React from "react";
import { Img, staticFile } from "remotion";

// Tamaños naturales de los recortes (public/img), para mantener la proporción.
export const IMG = {
  hourglass_light: [830, 1833],
  hourglass_dark: [661, 953],
  coins_stacks: [941, 727],
  coins_rising: [991, 569],
  watch_light: [843, 721],
  watch_dark: [794, 982],
  bust_marcus: [986, 1001],
  brain: [911, 919],
} as const;
export type ImgName = keyof typeof IMG;

/** Recorte fotográfico en grises con sombra proyectada abajo-derecha (estilo.md §4). */
export const Cutout: React.FC<{
  name: ImgName;
  cx: number;
  cy: number;
  width?: number;
  height?: number;
  rotate?: number;
  scale?: number;
  opacity?: number;
  brightness?: number;
  shadow?: boolean;
  shadowOpacity?: number;
  style?: React.CSSProperties;
}> = ({ name, cx, cy, width, height, rotate = 0, scale = 1, opacity = 1, brightness = 1, shadow = true, shadowOpacity = 0.45, style }) => {
  const [nw, nh] = IMG[name];
  const w = width ?? (height ? (height * nw) / nh : nw);
  const h = height ?? (w * nh) / nw;
  const filters = [
    brightness !== 1 ? `brightness(${brightness})` : "",
    shadow ? `drop-shadow(20px 24px 22px rgba(0,0,0,${shadowOpacity}))` : "",
  ].join(" ");
  return (
    <Img
      src={staticFile(`img/${name}.png`)}
      style={{
        position: "absolute",
        left: cx - w / 2,
        top: cy - h / 2,
        width: w,
        height: h,
        rotate: `${rotate}deg`,
        scale: `${scale}`,
        opacity,
        filter: filters.trim() || undefined,
        ...style,
      }}
    />
  );
};

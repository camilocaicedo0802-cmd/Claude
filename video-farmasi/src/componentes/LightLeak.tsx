import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { clamp } from "../util";

// Light leak + flash (§6): 36 f a 60 fps. Rojo-naranja → blanco → fuga arcoíris → blanco → plano nuevo.
export const LightLeak: React.FC = () => {
  const frame = useCurrentFrame();
  const naranja = interpolate(frame, [0, 8, 14, 20], [0, 1, 1, 0], clamp);
  const blanco = interpolate(frame, [8, 12, 16, 20, 28, 31, 34], [0, 1, 1, 0.25, 0.25, 0.85, 0], clamp);
  const arcoiris = interpolate(frame, [16, 20, 28, 34], [0, 1, 1, 0], clamp);
  const x = interpolate(frame, [0, 36], [70, 20]);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ mixBlendMode: "screen", opacity: naranja, background: `radial-gradient(ellipse 60% 45% at ${x + 20}% 35%, rgba(255,120,40,1), rgba(255,60,30,0.6) 45%, rgba(255,0,60,0) 75%), radial-gradient(ellipse 40% 60% at ${x}% 70%, rgba(255,200,60,0.95), rgba(255,140,0,0) 70%)` }} />
      <AbsoluteFill style={{ mixBlendMode: "screen", opacity: arcoiris, background: `radial-gradient(ellipse 50% 35% at ${100 - x}% 30%, rgba(255,80,200,0.9), rgba(255,80,200,0) 70%), radial-gradient(ellipse 55% 40% at ${x + 10}% 60%, rgba(80,200,255,0.9), rgba(80,200,255,0) 70%), radial-gradient(ellipse 45% 30% at 50% 85%, rgba(255,230,90,0.95), rgba(255,230,90,0) 70%), radial-gradient(ellipse 30% 25% at 30% 45%, rgba(170,120,255,0.85), rgba(170,120,255,0) 70%)` }} />
      <AbsoluteFill style={{ backgroundColor: "#FFFDF8", opacity: blanco }} />
    </AbsoluteFill>
  );
};

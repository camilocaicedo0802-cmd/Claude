import { evolvePath } from "@remotion/paths";
import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { C, F } from "../estilo";
import { UI } from "../plan";
import { clamp, eInOut, eOut, f, inicio } from "../util";

// Única superposición del v2: tarjeta oscura con la curva de glucosa (§4.2 "Grow").
// modo "sube": la curva sube (palabra 58 "sube"). modo "baja": sube y cae rápido (palabra 87 "baje").
const CAMINOS = {
  sube: "M 30 330 C 140 330, 200 320, 260 280 S 400 120, 470 70 S 560 40, 630 40",
  baja: "M 30 330 C 120 330, 170 150, 250 115 C 310 90, 340 215, 400 285 S 520 330, 660 330",
};
export const GraficaGlucosa: React.FC<{ modo: "sube" | "baja" }> = ({ modo }) => {
  const frame = useCurrentFrame();
  const r = modo === "sube" ? UI.graficaSube : UI.graficaBaja;
  const d = f(r.desde), h = f(r.hasta);
  if (frame < d - 1 || frame > h) return null;
  const pin = interpolate(frame, [d, d + 18], [0, 1], { ...clamp, easing: eOut });
  const pout = interpolate(frame, [h - 6, h], [1, 0], clamp);
  const v = Math.min(pin, pout);
  const palabra = modo === "sube" ? 58 : 87;
  const arriba = modo === "baja"; // en "baja" hay subtítulos en el pecho: la tarjeta va en el hueco sobre la cabeza
  const tChip = f(inicio(palabra)) - 6;
  const pd = interpolate(frame, [d + 6, modo === "sube" ? d + 56 : tChip + 18], [0, 1], { ...clamp, easing: eInOut });
  const ev = evolvePath(pd, CAMINOS[modo]);
  const pc = interpolate(frame, [tChip, tChip + 10], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ opacity: v, scale: String(0.9 + 0.1 * pin), translate: `0px ${(1 - pin) * 60}px` }}>
      <div style={{ position: "absolute", left: 215, top: arriba ? 150 : 1260, width: 650, height: 380, borderRadius: 34, background: `linear-gradient(170deg, ${C.navy1}, ${C.navy2})`, border: "1px solid rgba(120,200,255,0.3)", boxShadow: "0 24px 60px rgba(0,0,0,0.45)", overflow: "hidden" }}>
        <div style={{ position: "absolute", left: 32, top: 20, fontFamily: F.sans, fontWeight: 500, fontSize: 54, color: "#fff" }}>Glucosa</div>
        <svg width={650} height={380} viewBox="0 0 690 420" style={{ position: "absolute", inset: 0 }}>
          {[150, 240, 330].map((y) => <line key={y} x1={30} x2={660} y1={y} y2={y} stroke="rgba(120,200,255,0.25)" strokeWidth={1.5} />)}
          <path d={CAMINOS[modo]} fill="none" stroke="#2EC4F2" strokeWidth={6} strokeLinecap="round" strokeDasharray={ev.strokeDasharray} strokeDashoffset={ev.strokeDashoffset} style={{ filter: "drop-shadow(0 0 10px #2EC4F2)" }} />
        </svg>
      </div>
      <div style={{ position: "absolute", left: 640, top: arriba ? 96 : 1206, opacity: pc, scale: String(interpolate(pc, [0, 0.6, 1], [0.5, 1.12, 1])), background: modo === "sube" ? C.rojo2 : C.verde, borderRadius: 999, padding: "10px 28px 12px 18px", display: "flex", alignItems: "center", gap: 10, boxShadow: "0 10px 30px rgba(0,0,0,0.3)" }}>
        <Img src={staticFile(`iconos/flecha_${modo === "sube" ? "arriba" : "abajo"}.png`)} style={{ width: 56, height: 56 }} />
        <span style={{ fontFamily: F.sans, fontWeight: 800, fontSize: 52, color: "#fff" }}>{modo === "sube" ? "SUBE" : "BAJA"}</span>
      </div>
    </AbsoluteFill>
  );
};

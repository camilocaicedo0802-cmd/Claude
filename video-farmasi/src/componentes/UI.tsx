import { Video } from "@remotion/media";
import React from "react";
import { AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { evolvePath } from "@remotion/paths";
import { C, F } from "../estilo";
import { UI } from "../plan";
import { clamp, eInOut, eOut, f, inicio } from "../util";

// Cristal (glassmorphism) de la referencia §4.2
export const cristal: React.CSSProperties = {
  background: "linear-gradient(160deg, rgba(60,100,160,0.55), rgba(20,40,80,0.55))",
  backdropFilter: "blur(14px)",
  border: "2px solid rgba(255,255,255,0.35)",
  borderRadius: 28,
  boxShadow: "0 20px 60px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.35)",
};

// Entrada de tarjeta: opacidad, escala 0,85→1, y +80→0, desenfoque 16→0 en 22 f; salida 8 f
const usarTarjeta = (desde: number, hasta: number) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [desde, desde + 22], [0, 1], { ...clamp, easing: eOut });
  const s = interpolate(frame, [hasta - 8, hasta], [1, 0], clamp);
  const v = Math.min(p, s);
  return { frame, estilo: { opacity: v, scale: String(0.85 + 0.15 * p - (1 - s) * 0.05), translate: `0px ${(1 - p) * 80}px`, filter: v < 1 ? `blur(${(1 - v) * 16}px)` : undefined } as React.CSSProperties };
};

const Chip: React.FC<{ icono: string; texto: string; desde: number; style: React.CSSProperties }> = ({ icono, texto, desde, style }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [desde, desde + 10], [0, 1], clamp);
  const s = interpolate(p, [0, 0.6, 1], [0.6, 1.08, 1]);
  return (
    <div style={{ position: "absolute", ...cristal, borderRadius: 26, padding: "16px 26px 16px 16px", display: "flex", alignItems: "center", gap: 14, opacity: p, scale: String(s), ...style }}>
      <Img src={staticFile(`iconos/${icono}.png`)} style={{ width: 74, height: 74 }} />
      <div style={{ fontFamily: F.sans, fontWeight: 700, fontSize: 44, color: "#fff", letterSpacing: "-0.01em" }}>{texto}</div>
      <Img src={staticFile("iconos/check.png")} style={{ width: 52, height: 52, marginLeft: 4, scale: String(interpolate(frame, [desde + 6, desde + 14], [0, 1], clamp)) }} />
    </div>
  );
};

// "Almuerzo de hoy": tarjeta con vídeo del arroz + chips Arrocito / Ensalada
export const TarjetaAlmuerzo: React.FC = () => {
  const d = f(UI.almuerzo.desde), h = f(UI.almuerzo.hasta);
  const { frame, estilo } = usarTarjeta(d, h);
  if (frame < d - 1 || frame > h) return null;
  return (
    <AbsoluteFill style={{ ...estilo }}>
      <div style={{ position: "absolute", left: 170, top: 150, width: 740, height: 430, ...cristal, overflow: "hidden", rotate: "-2deg" }}>
        <div style={{ position: "absolute", inset: 0, overflow: "hidden", borderRadius: 26 }}>
          <Sequence from={d} layout="none">
            <Video src={staticFile("broll/Copia de Copia de c155.mp4")} trimBefore={Math.round(5.3 * 60)} muted objectFit="cover" style={{ width: "100%", height: "160%", marginTop: "-25%", filter: "saturate(1.15) brightness(1.1)" }} />
          </Sequence>
        </div>
        <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: 86, background: `linear-gradient(90deg, ${C.navyCab}, rgba(29,62,138,0.75))`, display: "flex", alignItems: "center", gap: 16, paddingLeft: 26 }}>
          <Img src={staticFile("iconos/plato.png")} style={{ width: 58, height: 58 }} />
          <div style={{ fontFamily: F.sans, fontWeight: 600, fontSize: 36, color: "#fff", letterSpacing: "0.05em" }}>ALMUERZO DE HOY</div>
        </div>
      </div>
      <Chip icono="arroz" texto="Arrocito" desde={f(inicio(16)) - 6} style={{ left: 50, top: 600 }} />
      <Chip icono="ensalada" texto="Ensalada" desde={f(inicio(19)) - 6} style={{ right: 50, top: 640 }} />
    </AbsoluteFill>
  );
};

// Tarjeta oscura con la curva de glucosa subiendo (§4.2 "Grow")
export const GraficaSube: React.FC = () => {
  const d = f(UI.graficaSube.desde), h = f(UI.graficaSube.hasta);
  const { frame, estilo } = usarTarjeta(d, h);
  if (frame < d - 1 || frame > h) return null;
  const camino = "M 30 330 C 140 330, 200 320, 260 280 S 400 120, 470 70 S 560 40, 630 40";
  const pd = interpolate(frame, [d + 8, d + 8 + 50], [0, 1], { ...clamp, easing: eInOut });
  const ev = evolvePath(pd, camino);
  const tChip = f(inicio(58)) - 6;
  const pc = interpolate(frame, [tChip, tChip + 10], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ ...estilo }}>
      <div style={{ position: "absolute", left: 195, top: 1250, width: 690, height: 400, borderRadius: 36, background: `linear-gradient(170deg, ${C.navy1}, ${C.navy2})`, border: "1px solid rgba(120,200,255,0.3)", boxShadow: "0 24px 60px rgba(0,0,0,0.5)", overflow: "hidden" }}>
        <div style={{ position: "absolute", left: 34, top: 22, fontFamily: F.sans, fontWeight: 500, fontSize: 60, color: "#fff" }}>Glucosa</div>
        <svg width={690} height={420} style={{ position: "absolute", inset: 0 }}>
          {[150, 240, 330].map((y) => <line key={y} x1={30} x2={660} y1={y} y2={y} stroke="rgba(120,200,255,0.25)" strokeWidth={1.5} />)}
          <path d={camino} fill="none" stroke="#2EC4F2" strokeWidth={6} strokeLinecap="round" strokeDasharray={ev.strokeDasharray} strokeDashoffset={ev.strokeDashoffset} style={{ filter: "drop-shadow(0 0 10px #2EC4F2)" }} />
        </svg>
      </div>
      <div style={{ position: "absolute", left: 650, top: 1196, opacity: pc, scale: String(interpolate(pc, [0, 0.6, 1], [0.5, 1.12, 1])), background: C.rojo2, borderRadius: 999, padding: "10px 28px 12px 18px", display: "flex", alignItems: "center", gap: 10, boxShadow: "0 10px 30px rgba(236,1,26,0.45)" }}>
        <Img src={staticFile("iconos/flecha_arriba.png")} style={{ width: 60, height: 60 }} />
        <span style={{ fontFamily: F.sans, fontWeight: 800, fontSize: 56, color: "#fff" }}>SUBE</span>
      </div>
    </AbsoluteFill>
  );
};

// Gomita dibujada (rojo-anaranjado translúcido como las Nutriplus)
export const Gomita: React.FC<{ size: number; style?: React.CSSProperties }> = ({ size, style }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" style={style}>
    <defs>
      <radialGradient id="gom" cx="35%" cy="30%" r="80%"><stop offset="0%" stopColor="#FFB08A" /><stop offset="45%" stopColor="#F2542D" /><stop offset="100%" stopColor="#9E1B1B" /></radialGradient>
    </defs>
    <path d="M50 8 C78 8 92 28 92 52 C92 78 74 92 50 92 C26 92 8 78 8 52 C8 28 22 8 50 8 Z" fill="url(#gom)" />
    <ellipse cx="36" cy="30" rx="14" ry="8" fill="rgba(255,255,255,0.55)" transform="rotate(-25 36 30)" />
    <circle cx="66" cy="70" r="5" fill="rgba(255,255,255,0.25)" />
  </svg>
);

// Widget "2 gomitas al día" con contador 0→2
export const WidgetGomitas: React.FC = () => {
  const d = f(UI.gomitas.desde), h = f(UI.gomitas.hasta);
  const { frame, estilo } = usarTarjeta(d, h);
  if (frame < d - 1 || frame > h) return null;
  const g1 = f(inicio(94)) - 4, g2 = f(inicio(95)) - 2, tDia = f(inicio(96)) - 6;
  const n = frame < g1 ? 0 : frame < g2 ? 1 : 2;
  const pop = (t: number) => interpolate(frame, [t, t + 12], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ ...estilo }}>
      <div style={{ position: "absolute", left: 160, top: 120, width: 760, height: 330, ...cristal, display: "flex", alignItems: "center", padding: "0 40px", gap: 30 }}>
        <div style={{ fontFamily: F.cond, fontSize: 300, lineHeight: 1, color: "#fff", width: 150, textAlign: "center", marginTop: 20 }}>{n}</div>
        <div style={{ display: "flex", gap: 14 }}>
          {[g1, g2].map((t, k) => (
            <Gomita key={k} size={170} style={{ scale: String(interpolate(pop(t), [0, 0.6, 1], [0, 1.2, 1])), rotate: `${(k ? 14 : -10) + Math.sin((frame - t) / 18) * 5}deg`, filter: "drop-shadow(0 14px 20px rgba(0,0,0,0.4))" }} />
          ))}
        </div>
      </div>
      <div style={{ position: "absolute", left: 560, top: 410, opacity: pop(tDia), scale: String(interpolate(pop(tDia), [0, 0.6, 1], [0.5, 1.1, 1])), background: C.pildora, borderRadius: 999, padding: "10px 34px 14px", fontFamily: F.sans, fontWeight: 800, fontSize: 56, color: "#fff", boxShadow: "0 10px 30px rgba(0,60,110,0.35)", rotate: "-3deg" }}>
        AL DÍA
      </div>
    </AbsoluteFill>
  );
};

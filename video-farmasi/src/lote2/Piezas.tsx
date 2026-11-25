import React from "react";
import { Video } from "@remotion/media";
import { AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { GP, HN } from "./fuentes";

const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const eOut = Easing.bezier(0.16, 1, 0.3, 1);
const eInOut = Easing.bezier(0.65, 0, 0.35, 1);

export type Segmento = { i: number; clip: string; enc: string; editStart: number; dur: number; a: number };
export type Golpe = { t: number; fuerza?: number; dur?: number }; // zoom de remate (chiste)

// A-roll: el vídeo ya viene reencuadrado desde el 4K. Aquí solo damos vida: empuje lento por toma
// (1,00 → 1,035) y "golpes" de zoom rápidos en los remates cómicos.
export const ARollL2: React.FC<{ src: string; segmentos: Segmento[]; golpes?: Golpe[]; luz?: number }> = ({ src, segmentos, golpes = [], luz = 1.04 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const seg = segmentos.find((s) => t >= s.editStart && t < s.editStart + s.dur) ?? segmentos[segmentos.length - 1];
  const u = Math.min(1, Math.max(0, (t - seg.editStart) / seg.dur));
  let s = 1 + 0.035 * u;
  for (const g of golpes) {
    const d = g.dur ?? 0.9;
    const k = interpolate(t, [g.t - 0.05, g.t + 0.07, g.t + d, g.t + d + 0.25], [0, 1, 1, 0], { ...cl, easing: eOut });
    s *= 1 + (g.fuerza ?? 0.1) * k;
  }
  return (
    <AbsoluteFill style={{ scale: String(s), transformOrigin: "50% 38%" }}>
      <Video
        src={staticFile(src)}
        muted
        objectFit="cover"
        style={{ width: "100%", height: "100%", filter: `brightness(${luz}) contrast(1.04) saturate(1.06)` }}
      />
    </AbsoluteFill>
  );
};

// Degradado suave abajo para que el texto blanco se lea sobre la pared blanca
export const DegradadoTexto: React.FC<{ fuerza?: number }> = ({ fuerza = 0.42 }) => (
  <AbsoluteFill
    style={{
      background: `linear-gradient(180deg, rgba(18,8,36,0) 44%, rgba(18,8,36,${fuerza * 0.55}) 62%, rgba(18,8,36,${fuerza}) 80%, rgba(18,8,36,${fuerza * 0.8}) 100%)`,
      pointerEvents: "none",
    }}
  />
);

// Emoji 3D que "salta" junto al texto o a la persona
export const EmojiPop: React.FC<{ icono: string; t: number; hasta: number; x: number; y: number; tam?: number; giro?: number }> = ({
  icono, t, hasta, x, y, tam = 150, giro = -8,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f0 = Math.round(t * fps);
  const f1 = Math.round(hasta * fps);
  if (frame < f0 || frame > f1 + 8) return null;
  const sp = spring({ frame: frame - f0, fps, config: { damping: 11, stiffness: 190, mass: 0.7 } });
  const salida = interpolate(frame, [f1, f1 + 8], [0, 1], { ...cl, easing: eInOut });
  const flota = Math.sin(((frame - f0) / fps) * 3.2) * 6;
  return (
    <div
      style={{
        position: "absolute",
        left: x - tam / 2,
        top: y - tam / 2 + flota,
        width: tam,
        height: tam,
        scale: String(sp * (1 - 0.4 * salida)),
        rotate: `${giro * (1 - sp) + Math.sin(((frame - f0) / fps) * 2.4) * 4}deg`,
        opacity: 1 - salida,
        filter: "drop-shadow(0 10px 18px rgba(30,10,60,.35))",
      }}
    >
      <Img src={staticFile(`iconos/${icono}.png`)} style={{ width: "100%", height: "100%" }} />
    </div>
  );
};

// Tarjeta de foto redondeada (como la tarjeta "Goal" de la referencia), entra desde abajo con desenfoque
export const TarjetaFoto: React.FC<{
  src: string; t: number; hasta: number; x: number; y: number; w: number; h: number; etiqueta?: string; giro?: number; foco?: string;
}> = ({ src, t, hasta, x, y, w, h, etiqueta, giro = 0, foco = "50% 50%" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f0 = Math.round(t * fps);
  const f1 = Math.round(hasta * fps);
  if (frame < f0 - 1 || frame > f1 + 9) return null;
  const e = interpolate(frame, [f0, f0 + 13], [0, 1], { ...cl, easing: eOut });
  const s = interpolate(frame, [f1, f1 + 9], [0, 1], { ...cl, easing: eInOut });
  const kb = interpolate(frame, [f0, f1 + 9], [1.08, 1.0], cl);
  return (
    <div
      style={{
        position: "absolute",
        left: x - w / 2,
        top: y - h / 2,
        width: w,
        height: h,
        borderRadius: 38,
        overflow: "hidden",
        opacity: e * (1 - s),
        translate: `0px ${(1 - e) * 60 - s * 20}px`,
        scale: String(0.9 + 0.1 * e - 0.05 * s),
        rotate: `${giro}deg`,
        filter: e < 0.99 || s > 0.01 ? `blur(${((1 - e) * 8 + s * 6).toFixed(2)}px)` : undefined,
        boxShadow: "0 24px 60px rgba(30,10,60,.38), 0 0 0 6px rgba(255,255,255,.92)",
      }}
    >
      <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: foco, scale: String(kb) }} />
      {etiqueta ? (
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            bottom: 0,
            padding: "60px 26px 22px",
            background: "linear-gradient(180deg, rgba(0,0,0,0), rgba(20,8,40,.6))",
            color: "#fff",
            fontFamily: GP,
            fontWeight: 600,
            fontSize: 46,
            letterSpacing: "-0.015em",
            textAlign: "center",
          }}
        >
          {etiqueta}
        </div>
      ) : null}
    </div>
  );
};

// Cadena de iconos que se arma palabra a palabra (p. ej. redes → link → compra → casa)
export const CadenaIconos: React.FC<{ pasos: { icono: string; t: number }[]; hasta: number; y: number; tam?: number }> = ({
  pasos, hasta, y, tam = 140,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const n = pasos.length;
  const hueco = 70;
  const anchoTotal = n * tam + (n - 1) * hueco;
  const x0 = 540 - anchoTotal / 2;
  const f1 = Math.round(hasta * fps);
  if (frame < Math.round(pasos[0].t * fps) - 2 || frame > f1 + 10) return null;
  const salida = interpolate(frame, [f1, f1 + 10], [0, 1], { ...cl, easing: eInOut });
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1920, opacity: 1 - salida, filter: salida > 0 ? `blur(${salida * 6}px)` : undefined }}>
      {pasos.map((p, i) => {
        const f0 = Math.round(p.t * fps);
        const sp = frame >= f0 ? spring({ frame: frame - f0, fps, config: { damping: 12, stiffness: 200, mass: 0.7 } }) : 0;
        const x = x0 + i * (tam + hueco);
        const flecha = i > 0 ? interpolate(frame, [f0 - 6, f0 + 4], [0, 1], { ...cl, easing: eOut }) : 0;
        return (
          <React.Fragment key={i}>
            {i > 0 ? (
              <svg width={hueco} height={40} style={{ position: "absolute", left: x - hueco, top: y + tam / 2 - 20, opacity: flecha }}>
                <path d={`M8 20 L${8 + (hueco - 26) * flecha} 20`} stroke="#fff" strokeWidth={5} strokeLinecap="round" />
                <path d={`M${hueco - 24} 10 L${hueco - 12} 20 L${hueco - 24} 30`} stroke="#fff" strokeWidth={5} fill="none" strokeLinecap="round" strokeLinejoin="round" opacity={flecha > 0.9 ? 1 : 0} />
              </svg>
            ) : null}
            <div
              style={{
                position: "absolute",
                left: x,
                top: y,
                width: tam,
                height: tam,
                borderRadius: 40,
                background: "rgba(255,255,255,.94)",
                boxShadow: "0 16px 40px rgba(30,10,60,.30)",
                scale: String(sp),
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Img src={staticFile(`iconos/${p.icono}.png`)} style={{ width: tam * 0.72, height: tam * 0.72 }} />
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
};

// Píldora de texto (chip) con icono: para datos cortos ("305 Media Club", "WhatsApp")
export const Chip: React.FC<{ texto: string; icono?: string; t: number; hasta: number; x: number; y: number; color?: string; tam?: number }> = ({
  texto, icono, t, hasta, x, y, color = "#B184F5", tam = 46,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f0 = Math.round(t * fps);
  const f1 = Math.round(hasta * fps);
  if (frame < f0 || frame > f1 + 8) return null;
  const sp = spring({ frame: frame - f0, fps, config: { damping: 13, stiffness: 210, mass: 0.6 } });
  const s = interpolate(frame, [f1, f1 + 8], [0, 1], { ...cl, easing: eInOut });
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        translate: "-50% -50%",
        scale: String(sp * (1 - 0.15 * s)),
        opacity: 1 - s,
        display: "flex",
        alignItems: "center",
        gap: 16,
        padding: `16px ${icono ? 34 : 30}px 16px ${icono ? 18 : 30}px`,
        borderRadius: 999,
        background: "rgba(255,255,255,.95)",
        boxShadow: `0 14px 34px rgba(30,10,60,.28), inset 0 0 0 3px ${color}`,
        whiteSpace: "nowrap",
      }}
    >
      {icono ? <Img src={staticFile(`iconos/${icono}.png`)} style={{ width: tam * 1.5, height: tam * 1.5 }} /> : null}
      <span style={{ fontFamily: HN, fontWeight: 700, fontSize: tam, letterSpacing: "-0.03em", color: "#24133F" }}>{texto}</span>
    </div>
  );
};

// Cierre: foto de las dos con la caja + invitación
export const CierreFoto: React.FC<{ src: string; t: number; titulo: string; sub: string; icono?: string }> = ({ src, t, titulo, sub, icono }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f0 = Math.round(t * fps);
  if (frame < f0) return null;
  const k = frame - f0;
  const e = interpolate(k, [0, 14], [0, 1], { ...cl, easing: eOut });
  const kb = interpolate(k, [0, 4 * fps], [1.12, 1.0], cl);
  const tt = interpolate(k, [10, 26], [0, 1], { ...cl, easing: eOut });
  const st = interpolate(k, [22, 38], [0, 1], { ...cl, easing: eOut });
  const luz = interpolate(k, [18, 42], [0, 1], { ...cl, easing: eInOut });
  return (
    <AbsoluteFill style={{ opacity: e, backgroundColor: "#1B0F33" }}>
      <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 30%", scale: String(kb), filter: `blur(${(1 - e) * 10}px)` }} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(27,15,51,0) 45%, rgba(27,15,51,.55) 66%, rgba(27,15,51,.85) 100%)" }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 1300, textAlign: "center" }}>
        <div
          style={{
            fontFamily: GP, fontWeight: 600, fontSize: 104, letterSpacing: "-0.015em", color: "#fff", lineHeight: 0.95,
            opacity: tt, filter: `blur(${(1 - tt) * 4}px)`, translate: `0px ${(1 - tt) * 10}px`, textShadow: "0 3px 16px rgba(0,0,0,.35)",
          }}
        >
          {titulo}
        </div>
        <svg width={620} height={30} style={{ display: "block", margin: "6px auto 0" }}>
          <defs>
            <clipPath id="cierreLuz"><rect x={0} y={0} width={620 * luz} height={30} /></clipPath>
            <filter id="cierreBlur"><feGaussianBlur stdDeviation={5} /></filter>
          </defs>
          <g clipPath="url(#cierreLuz)">
            <path d="M20 20 Q310 6 600 12" stroke="#B184F5" strokeWidth={9} fill="none" strokeLinecap="round" filter="url(#cierreBlur)" />
            <path d="M20 20 Q310 6 600 12" stroke="#EFE4FF" strokeWidth={4} fill="none" strokeLinecap="round" />
          </g>
        </svg>
        <div
          style={{
            marginTop: 26, display: "inline-flex", alignItems: "center", gap: 16, padding: "18px 36px 18px 22px", borderRadius: 999,
            background: "rgba(255,255,255,.96)", opacity: st, scale: String(0.9 + 0.1 * st), boxShadow: "0 16px 40px rgba(0,0,0,.3)",
          }}
        >
          {icono ? <Img src={staticFile(`iconos/${icono}.png`)} style={{ width: 64, height: 64 }} /> : null}
          <span style={{ fontFamily: HN, fontWeight: 700, fontSize: 48, letterSpacing: "-0.03em", color: "#24133F" }}>{sub}</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

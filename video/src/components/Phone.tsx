import React from "react";

/** Smartphone vectorial monocromo (negro brillante, isla, botones laterales, sombra). */
export const Phone: React.FC<{
  cx: number;
  cy: number;
  w: number;
  rotate?: number;
  scale?: number;
  screen?: string;
  glow?: number;
  /** borde iluminado (0–1) para separarlo de fondos oscuros */
  rim?: number;
  /** vibración: desplazamiento horizontal en px (se anima desde fuera) */
  shake?: number;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ cx, cy, w, rotate = 0, scale = 1, screen = "#1d1d1e", glow = 0, rim = 0.35, shake = 0, children, style }) => {
  const h = w * 2.05;
  const r = w * 0.15;
  const inset = w * 0.038;
  const sw = w - inset * 2;
  const sh = h - inset * 2;
  return (
    <div
      style={{
        position: "absolute",
        left: cx - w / 2 + shake,
        top: cy - h / 2,
        width: w,
        height: h,
        rotate: `${rotate}deg`,
        scale: `${scale}`,
        filter: `drop-shadow(20px 24px 26px rgba(0,0,0,0.5))${glow > 0 ? ` drop-shadow(0 0 ${60 * glow}px rgba(255,255,255,${0.32 * glow}))` : ""}`,
        ...style,
      }}
    >
      {/* botones laterales */}
      <div style={{ position: "absolute", right: -w * 0.012, top: h * 0.24, width: w * 0.02, height: h * 0.11, borderRadius: 6, background: "#2b2b2c" }} />
      <div style={{ position: "absolute", left: -w * 0.012, top: h * 0.2, width: w * 0.02, height: h * 0.06, borderRadius: 6, background: "#2b2b2c" }} />
      <div style={{ position: "absolute", left: -w * 0.012, top: h * 0.29, width: w * 0.02, height: h * 0.06, borderRadius: 6, background: "#2b2b2c" }} />
      {/* cuerpo */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: r,
          background: "linear-gradient(135deg, #3a3a3b 0%, #121213 22%, #0b0b0c 70%, #2a2a2b 100%)",
          // marco metálico con borde iluminado arriba-izquierda (misma dirección de luz que las sombras)
          boxShadow: `inset 0 0 0 3px #5a5a5b, inset 0 0 0 7px #0a0a0a, inset 3px 3px 0 1px rgba(255,255,255,${0.25 * rim}), 0 0 0 ${1.5 + rim * 1.5}px rgba(255,255,255,${0.18 + 0.4 * rim})`,
        }}
      />
      {/* pantalla */}
      <div
        style={{
          position: "absolute",
          left: inset,
          top: inset,
          width: sw,
          height: sh,
          borderRadius: r - inset,
          overflow: "hidden",
          background: screen,
        }}
      >
        {children}
        {/* reflejo */}
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(120deg, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0.0) 35%)", pointerEvents: "none" }} />
      </div>
      {/* isla */}
      <div style={{ position: "absolute", left: w / 2 - w * 0.14, top: inset + w * 0.035, width: w * 0.28, height: w * 0.075, borderRadius: w, background: "#050505" }} />
    </div>
  );
};

/** Icono monocromo simple para notificaciones. */
export const Glyph: React.FC<{ kind: "bell" | "heart" | "chat" | "play" | "user"; size: number; color?: string }> = ({ kind, size, color = "#F0F0F0" }) => {
  const s = size;
  return (
    <svg width={s} height={s} viewBox="0 0 24 24">
      {kind === "bell" && <path d="M12 3a6 6 0 0 0-6 6v4l-2 3h16l-2-3V9a6 6 0 0 0-6-6zm-2 15a2 2 0 0 0 4 0z" fill={color} />}
      {kind === "heart" && <path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" fill={color} />}
      {kind === "chat" && <path d="M4 5h16v11H9l-5 4z" fill={color} />}
      {kind === "play" && <path d="M8 5l11 7-11 7z" fill={color} />}
      {kind === "user" && (
        <g fill={color}>
          <circle cx="12" cy="8" r="4" />
          <path d="M4 20a8 8 0 0 1 16 0z" />
        </g>
      )}
    </svg>
  );
};

/** Burbuja de notificación (gris claro, icono negro, dos líneas). */
export const Notification: React.FC<{
  x: number;
  y: number;
  w: number;
  kind: "bell" | "heart" | "chat" | "play" | "user";
  title: string;
  body: string;
  when?: string;
  scale?: number;
  opacity?: number;
  rotate?: number;
  blur?: number;
  dark?: boolean;
}> = ({ x, y, w, kind, title, body, when = "ahora", scale = 1, opacity = 1, rotate = 0, blur = 0, dark = false }) => {
  const h = w * 0.24;
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: w,
        height: h,
        borderRadius: h * 0.32,
        background: dark ? "rgba(40,40,42,0.94)" : "rgba(246,246,246,0.96)",
        boxShadow: "0 18px 40px rgba(0,0,0,0.35)",
        display: "flex",
        alignItems: "center",
        gap: w * 0.04,
        padding: `0 ${w * 0.045}px`,
        boxSizing: "border-box",
        scale: `${scale}`,
        opacity,
        rotate: `${rotate}deg`,
        filter: blur ? `blur(${blur}px)` : undefined,
        fontFamily: "Archivo",
      }}
    >
      <div style={{ width: h * 0.62, height: h * 0.62, borderRadius: h * 0.18, background: dark ? "#E8E8E8" : "#141414", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
        <Glyph kind={kind} size={h * 0.36} color={dark ? "#141414" : "#F0F0F0"} />
      </div>
      <div style={{ flex: 1, minWidth: 0, color: dark ? "#F0F0F0" : "#141414" }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 800, fontSize: h * 0.22, lineHeight: 1.15 }}>
          <span>{title}</span>
          <span style={{ fontWeight: 600, opacity: 0.5, fontSize: h * 0.17 }}>{when}</span>
        </div>
        <div style={{ fontWeight: 600, fontSize: h * 0.19, opacity: 0.72, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{body}</div>
      </div>
    </div>
  );
};

/** Miniatura de vídeo genérica (gris, botón play, barra de progreso). */
export const VideoThumb: React.FC<{ x: number; y: number; w: number; h: number; tone: number; scale?: number; opacity?: number; progress?: number; radius?: number; showPlay?: boolean }> = ({
  x,
  y,
  w,
  h,
  tone,
  scale = 1,
  opacity = 1,
  progress = 0.35,
  radius = 22,
  showPlay = true,
}) => {
  const a = Math.round(40 + tone * 120);
  const b = Math.round(15 + tone * 60);
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: w,
        height: h,
        borderRadius: radius,
        overflow: "hidden",
        background: `linear-gradient(160deg, rgb(${a},${a},${a + 2}) 0%, rgb(${b},${b},${b + 1}) 100%)`,
        scale: `${scale}`,
        opacity,
        boxShadow: "0 10px 24px rgba(0,0,0,0.35)",
      }}
    >
      {/* formas abstractas de "contenido" */}
      <div style={{ position: "absolute", left: w * 0.12, top: h * 0.18, width: w * 0.42, height: w * 0.42, borderRadius: "50%", background: `rgba(255,255,255,${0.08 + tone * 0.1})` }} />
      <div style={{ position: "absolute", right: -w * 0.1, bottom: h * 0.18, width: w * 0.7, height: h * 0.32, borderRadius: w * 0.2, background: `rgba(0,0,0,${0.18 + tone * 0.1})`, rotate: "-12deg" }} />
      {showPlay && (
        <div style={{ position: "absolute", left: w / 2 - w * 0.15, top: h / 2 - w * 0.15, width: w * 0.3, height: w * 0.3, borderRadius: "50%", background: "rgba(240,240,240,0.9)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Glyph kind="play" size={w * 0.16} color="#141414" />
        </div>
      )}
      <div style={{ position: "absolute", left: w * 0.08, right: w * 0.08, bottom: h * 0.07, height: Math.max(4, h * 0.012), borderRadius: 4, background: "rgba(255,255,255,0.25)" }}>
        <div style={{ width: `${progress * 100}%`, height: "100%", borderRadius: 4, background: "#F0F0F0" }} />
      </div>
    </div>
  );
};

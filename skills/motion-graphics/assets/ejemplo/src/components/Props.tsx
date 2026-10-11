import React from "react";
import { random } from "remotion";
import { evolvePath } from "@remotion/paths";

/** Tarjeta bancaria vectorial negra (chip, contactless, número). */
export const CreditCard: React.FC<{ cx: number; cy: number; w: number; rotate?: number; scale?: number; opacity?: number }> = ({ cx, cy, w, rotate = 0, scale = 1, opacity = 1 }) => {
  const h = w * 0.63;
  return (
    <div
      style={{
        position: "absolute",
        left: cx - w / 2,
        top: cy - h / 2,
        width: w,
        height: h,
        borderRadius: w * 0.05,
        background: "linear-gradient(125deg, #4a4a4b 0%, #1c1c1d 30%, #0d0d0e 65%, #3b3b3c 100%)",
        boxShadow: "inset 0 0 0 2px rgba(255,255,255,0.12), 22px 28px 34px rgba(0,0,0,0.45)",
        rotate: `${rotate}deg`,
        scale: `${scale}`,
        opacity,
        fontFamily: "Archivo",
        color: "#E6E6E6",
        overflow: "hidden",
      }}
    >
      <div style={{ position: "absolute", left: "-20%", top: "-60%", width: "90%", height: "160%", borderRadius: "50%", background: "rgba(255,255,255,0.05)" }} />
      <div style={{ position: "absolute", left: w * 0.08, top: h * 0.12, fontWeight: 900, fontSize: w * 0.06, letterSpacing: "0.02em" }}>BANCO</div>
      {/* chip */}
      <div
        style={{
          position: "absolute",
          left: w * 0.09,
          top: h * 0.34,
          width: w * 0.14,
          height: w * 0.105,
          borderRadius: w * 0.018,
          background: "linear-gradient(135deg, #d8d8d8, #8a8a8a 45%, #cfcfcf 70%, #7a7a7a)",
          boxShadow: "inset 0 0 0 2px rgba(0,0,0,0.25)",
        }}
      >
        <div style={{ position: "absolute", left: "35%", top: 0, bottom: 0, width: 2, background: "rgba(0,0,0,0.35)" }} />
        <div style={{ position: "absolute", left: 0, right: 0, top: "50%", height: 2, background: "rgba(0,0,0,0.35)" }} />
      </div>
      {/* contactless */}
      <svg style={{ position: "absolute", left: w * 0.27, top: h * 0.35 }} width={w * 0.07} height={w * 0.09} viewBox="0 0 20 26">
        {[0, 1, 2].map((i) => (
          <path key={i} d={`M${4 + i * 5} ${4 + i * 1} q ${5} 9 0 ${18 - i * 2}`} stroke="#d0d0d0" strokeWidth={2.2} fill="none" strokeLinecap="round" />
        ))}
      </svg>
      <div style={{ position: "absolute", left: w * 0.08, top: h * 0.6, fontWeight: 600, fontSize: w * 0.058, letterSpacing: "0.12em" }}>•••• •••• •••• 2026</div>
      <div style={{ position: "absolute", left: w * 0.08, bottom: h * 0.1, fontWeight: 600, fontSize: w * 0.035, letterSpacing: "0.18em", opacity: 0.75 }}>TU NOMBRE</div>
      <div style={{ position: "absolute", right: w * 0.07, bottom: h * 0.08, display: "flex" }}>
        <div style={{ width: w * 0.09, height: w * 0.09, borderRadius: "50%", background: "#9a9a9a", opacity: 0.85 }} />
        <div style={{ width: w * 0.09, height: w * 0.09, borderRadius: "50%", background: "#d9d9d9", opacity: 0.6, marginLeft: -w * 0.035 }} />
      </div>
    </div>
  );
};

/** Señal de peligro (triángulo negro con borde blanco y "!"), en la línea de la señal STOP de la referencia. */
export const WarningSign: React.FC<{ cx: number; cy: number; w: number; rotate?: number; scale?: number; opacity?: number; post?: number }> = ({
  cx,
  cy,
  w,
  rotate = 0,
  scale = 1,
  opacity = 1,
  post = 700,
}) => {
  const h = w * 0.88;
  return (
    <div
      style={{
        position: "absolute",
        left: cx - w / 2,
        top: cy - h / 2,
        width: w,
        height: h + post,
        rotate: `${rotate}deg`,
        scale: `${scale}`,
        transformOrigin: `50% ${h + post}px`,
        opacity,
        filter: "drop-shadow(22px 26px 22px rgba(0,0,0,0.45))",
      }}
    >
      <div style={{ position: "absolute", left: w / 2 - w * 0.035, top: h * 0.6, width: w * 0.07, height: post + h * 0.4, background: "linear-gradient(90deg, #2a2a2a, #0e0e0e 60%, #333)" }} />
      <svg width={w} height={h} viewBox="0 0 100 88" style={{ position: "absolute", left: 0, top: 0 }}>
        <defs>
          <linearGradient id="warnFace" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#2c2c2d" />
            <stop offset="0.5" stopColor="#121213" />
            <stop offset="1" stopColor="#1f1f20" />
          </linearGradient>
        </defs>
        <path d="M50 3 L97 84 Q98 86 95 86 L5 86 Q2 86 3 84 Z" fill="#EDEDED" stroke="#bdbdbd" strokeWidth="1" strokeLinejoin="round" />
        <path d="M50 12 L89 80 L11 80 Z" fill="url(#warnFace)" strokeLinejoin="round" />
        <rect x="46.2" y="34" width="7.6" height="27" rx="3.5" fill="#EDEDED" />
        <circle cx="50" cy="69" r="4.4" fill="#EDEDED" />
      </svg>
    </div>
  );
};

/** Flecha circular de pincel ("volver"). */
export const LoopArrow: React.FC<{ cx: number; cy: number; r: number; progress: number; width?: number }> = ({ cx, cy, r, progress, width = 18 }) => {
  if (progress <= 0) return null;
  const a0 = -200;
  const a1 = 120;
  const pt = (a: number) => [cx + r * Math.cos((a * Math.PI) / 180), cy + r * 0.62 * Math.sin((a * Math.PI) / 180)];
  const [x0, y0] = pt(a0);
  let d = `M ${x0} ${y0}`;
  for (let a = a0 + 10; a <= a1; a += 10) {
    const [x, y] = pt(a);
    d += ` L ${x} ${y}`;
  }
  const ev = evolvePath(Math.min(progress, 1), d);
  const [xe, ye] = pt(a1);
  const [xp, yp] = pt(a1 - 8);
  const ang = Math.atan2(ye - yp, xe - xp);
  const head = progress >= 0.98;
  const hl = 46;
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
      <defs>
        <filter id="loopSoft">
          <feGaussianBlur stdDeviation="1.3" />
        </filter>
      </defs>
      <path d={d} fill="none" stroke="rgba(0,0,0,0.3)" strokeWidth={width} strokeLinecap="round" transform="translate(12 16)" style={{ filter: "blur(8px)" }} strokeDasharray={ev.strokeDasharray} strokeDashoffset={ev.strokeDashoffset} />
      <path d={d} fill="none" stroke="#151515" strokeWidth={width} strokeLinecap="round" filter="url(#loopSoft)" strokeDasharray={ev.strokeDasharray} strokeDashoffset={ev.strokeDashoffset} />
      {head && (
        <path
          d={`M ${xe - hl * Math.cos(ang - 0.5)} ${ye - hl * Math.sin(ang - 0.5)} L ${xe} ${ye} L ${xe - hl * Math.cos(ang + 0.5)} ${ye - hl * Math.sin(ang + 0.5)}`}
          fill="none"
          stroke="#151515"
          strokeWidth={width}
          strokeLinecap="round"
          strokeLinejoin="round"
          filter="url(#loopSoft)"
        />
      )}
    </svg>
  );
};

/** Partículas deterministas que se desprenden de un objeto (disolución, arena). */
export const Particles: React.FC<{
  seed: string;
  n: number;
  t: number;
  start: number;
  cx: number;
  cy: number;
  spreadX: number;
  spreadY: number;
  dx: number;
  dy: number;
  dur?: number;
  color?: string;
  size?: number;
}> = ({ seed, n, t, start, cx, cy, spreadX, spreadY, dx, dy, dur = 1.1, color = "#2a2a2a", size = 9 }) => {
  if (t < start) return null;
  return (
    <>
      {new Array(n).fill(0).map((_, i) => {
        const delay = random(`${seed}-d-${i}`) * 0.6;
        const p = (t - start - delay) / dur;
        if (p <= 0 || p >= 1) return null;
        const x0 = cx + (random(`${seed}-x-${i}`) - 0.5) * spreadX;
        const y0 = cy + (random(`${seed}-y-${i}`) - 0.5) * spreadY;
        const e = 1 - Math.pow(1 - p, 2);
        const s = size * (0.4 + random(`${seed}-s-${i}`));
        const wob = Math.sin(p * 6 + i) * 18;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x0 + dx * e * (0.6 + random(`${seed}-v-${i}`)) + wob,
              top: y0 + dy * e * (0.6 + random(`${seed}-w-${i}`)),
              width: s,
              height: s,
              borderRadius: random(`${seed}-r-${i}`) > 0.5 ? "50%" : 2,
              background: color,
              opacity: (1 - p) * 0.9,
              rotate: `${p * 180 * (random(`${seed}-o-${i}`) - 0.5)}deg`,
            }}
          />
        );
      })}
    </>
  );
};

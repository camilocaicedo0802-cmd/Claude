// Motion graphics con el lenguaje de la referencia (estilo.md §3): vidrio oscuro con degradado radial,
// borde de 1 px y esquinas redondeadas; rojo vino = problema, verde = solución/CTA; textos que se teclean.
import React from "react";
import { Easing, Img, staticFile } from "remotion";
import { keys, lerp, ramp } from "../anim";
import { C, FONT, GFX_CY, H, W } from "../theme";

const icon = (name: string) => staticFile(`media/icons/${name}.webp`);

const glass = (tone: "wine" | "gold" | "dark"): React.CSSProperties => ({
  background:
    tone === "wine"
      ? `radial-gradient(120% 160% at 50% 118%, ${C.wine} 0%, #3a0009 38%, ${C.wineDark} 78%)`
      : tone === "gold"
        ? `radial-gradient(120% 170% at 55% 120%, ${C.gold} 0%, #3a2b00 42%, #080600 82%)`
        : "linear-gradient(180deg, rgba(34,34,34,0.92), rgba(12,12,12,0.92))",
  border: "1px solid rgba(255,255,255,0.18)",
  boxShadow: "0 18px 50px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.08)",
});

/** Palabra que «cae» a su sitio: nace 20 px arriba al 30 % y se asienta en 100 ms (tecleo palabra a palabra). */
const DropWord: React.FC<{ t: number; at: number; children: React.ReactNode; gap?: string; color?: string }> = ({ t, at, children, gap = "0.28em", color }) => {
  const p = ramp(t, at, 0.1, Easing.out(Easing.quad));
  return (
    <span style={{ display: "inline-block", marginRight: gap, opacity: t < at ? 0 : 0.3 + 0.7 * p, translate: `0px ${-20 * (1 - p)}px`, color }}>{children}</span>
  );
};

// ───────────────────────── Tarjeta de alerta (problema) ─────────────────────────
export const AlertCard: React.FC<{ t: number; at: number; end: number; y: number; icon: string; words: { t: number; text: string }[]; width?: number }> = ({ t, at, end, y, icon: ic, words, width = 940 }) => {
  if (t < at || t >= end) return null;
  const p = ramp(t, at, 0.133);
  return (
    <div
      style={{
        position: "absolute",
        left: (W - width) / 2,
        top: y - 66,
        width,
        height: 132,
        borderRadius: 26,
        opacity: p,
        translate: `0px ${8 * (1 - p)}px`,
        display: "flex",
        alignItems: "center",
        gap: 26,
        padding: "0 34px",
        boxSizing: "border-box",
        ...glass("wine"),
      }}
    >
      <Img src={icon(ic)} style={{ width: 58, height: 58, flex: "0 0 auto", scale: String(lerp(0.6, 1, ramp(t, at + 0.03, 0.18, Easing.out(Easing.back(2))))) }} />
      <div style={{ fontFamily: FONT.wide, fontWeight: 300, fontSize: 41, letterSpacing: "-0.01em", color: "rgba(255,255,255,0.93)", whiteSpace: "nowrap" }}>
        {words.map((w, i) => (
          <DropWord key={i} t={t} at={w.t}>
            {w.text}
          </DropWord>
        ))}
      </div>
    </div>
  );
};

// ───────────────────────── Fichas con icono 3D (enumeraciones) ─────────────────────────
export type Tile = { at: number; icon: string; label: string };
export const Tiles: React.FC<{ t: number; tiles: Tile[]; end: number; cy?: number; tone?: "wine" | "gold" }> = ({ t, tiles, end, cy = GFX_CY, tone = "wine" }) => {
  if (t < tiles[0].at - 0.05 || t >= end) return null;
  const w = 317;
  const h = 337;
  const gap = 12;
  const total = tiles.length * w + (tiles.length - 1) * gap;
  const left0 = (W - total) / 2;
  return (
    <>
      {tiles.map((tile, i) => {
        if (t < tile.at) return null;
        // Entra sobreexpuesta (brillo ≈2,5× y escala 1,15) y se asienta en 100 ms.
        const p = ramp(t, tile.at, 0.1, Easing.out(Easing.quad));
        const fresh = 1 - ramp(t, tile.at + 0.1, 0.5);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: left0 + i * (w + gap),
              top: cy - h / 2,
              width: w,
              height: h,
              borderRadius: 28,
              scale: String(1.15 - 0.15 * p),
              filter: `brightness(${2.5 - 1.5 * p})`,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 20,
              boxSizing: "border-box",
              background:
                tone === "wine"
                  ? "radial-gradient(120% 120% at 50% 110%, rgba(138,0,21,0.85) 0%, rgba(58,0,9,0.82) 45%, rgba(14,2,4,0.86) 100%)"
                  : "radial-gradient(120% 120% at 50% 110%, rgba(184,138,0,0.8) 0%, rgba(58,43,0,0.84) 45%, rgba(8,6,0,0.9) 100%)",
              border: `1px solid rgba(255,255,255,${0.2 + 0.5 * fresh})`,
              boxShadow: `0 18px 50px rgba(0,0,0,0.55), 0 0 ${40 * fresh}px ${tone === "wine" ? "rgba(198,0,27,0.6)" : "rgba(255,222,33,0.45)"}`,
            }}
          >
            <Img src={icon(tile.icon)} style={{ width: 172, height: 172, filter: "drop-shadow(0 12px 18px rgba(0,0,0,0.5))" }} />
            <div style={{ fontFamily: FONT.wide, fontWeight: 300, fontSize: tile.label.length > 10 ? 30 : 37, letterSpacing: "0.02em", color: "rgba(255,255,255,0.88)", textTransform: "uppercase" }}>{tile.label}</div>
          </div>
        );
      })}
    </>
  );
};

// ───────────────────────── Píldora verde con avatar (solución / CTA) ─────────────────────────
export const GreenPill: React.FC<{ t: number; at: number; end: number; cy: number; typeAt: number; text: string; avatar: string; hint?: string }> = ({ t, at, end, cy, typeAt, text, avatar, hint }) => {
  if (t < at || t >= end) return null;
  const p = ramp(t, at, 0.18);
  // 1 letra cada 4 fotogramas (≈15 caracteres/s).
  const typed = Math.max(0, Math.min(text.length, Math.floor((t - typeAt) * 15) + 1));
  const shown = t < typeAt ? "" : text.slice(0, typed);
  const sent = ramp(t, typeAt + text.length / 15 + 0.25, 0.25, Easing.out(Easing.back(2.2)));
  return (
    <div style={{ position: "absolute", left: 110, top: cy - 66, width: 860, height: 132, opacity: p, translate: `0px ${14 * (1 - p)}px`, display: "flex", alignItems: "center", gap: 22 }}>
      <Img src={staticFile(avatar)} style={{ width: 112, height: 112, borderRadius: 112, objectFit: "cover", border: "2px solid rgba(255,255,255,0.22)", boxShadow: "0 10px 30px rgba(0,0,0,0.6)" }} />
      <div style={{ flex: 1, height: 132, borderRadius: 34, display: "flex", alignItems: "center", padding: "0 40px", boxSizing: "border-box", position: "relative", ...glass("gold") }}>
        {t < typeAt && hint ? <span style={{ fontFamily: FONT.wide, fontWeight: 300, fontSize: 34, color: "rgba(255,255,255,0.45)" }}>{hint}</span> : null}
        <span style={{ fontFamily: FONT.serif, fontStyle: "italic", fontSize: 92, lineHeight: 1, color: C.white, textShadow: "0 0 26px rgba(255,255,255,0.45)", letterSpacing: "0.01em" }}>{shown}</span>
        <span style={{ display: "inline-block", width: 4, height: 70, marginLeft: 8, background: C.accent, opacity: Math.floor(t * 2.5) % 2 === 0 && sent < 0.5 ? 1 : 0 }} />
        {/* Botón de enviar: aparece al terminar de teclear */}
        <div style={{ position: "absolute", right: 22, top: 26, width: 80, height: 80, borderRadius: 80, background: C.accent, display: "flex", alignItems: "center", justifyContent: "center", scale: String(sent), boxShadow: `0 0 30px ${C.accentGlow}` }}>
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#0b0b0b" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 19V5M5 12l7-7 7 7" />
          </svg>
        </div>
      </div>
    </div>
  );
};

// ───────────────────────── Tarjeta serif tecleada (frase del guion que no está grabada) ─────────────────────────
export const SerifCard: React.FC<{ t: number; at: number; end: number; cy: number; lines: { t: number; text: string }[][]; ic: string }> = ({ t, at, end, cy, lines, ic }) => {
  if (t < at || t >= end) return null;
  const p = ramp(t, at, 0.16);
  const out = 1 - ramp(t, end - 0.12, 0.12);
  return (
    <div style={{ position: "absolute", left: 70, top: cy - 140, width: 940, height: 280, borderRadius: 34, opacity: p * out, translate: `0px ${12 * (1 - p)}px`, display: "flex", alignItems: "center", gap: 30, padding: "0 44px", boxSizing: "border-box", ...glass("gold") }}>
      <Img src={icon(ic)} style={{ width: 120, height: 120, flex: "0 0 auto", filter: "drop-shadow(0 10px 16px rgba(0,0,0,0.5))", scale: String(lerp(0.5, 1, ramp(t, at + 0.05, 0.22, Easing.out(Easing.back(2))))) }} />
      <div style={{ fontFamily: FONT.serif, fontStyle: "italic", fontSize: 62, lineHeight: 1.12, color: C.white, textShadow: "0 0 22px rgba(255,255,255,0.35)" }}>
        {lines.map((line, i) => (
          <div key={i} style={{ whiteSpace: "nowrap", color: i === 0 ? C.white : "rgba(255,255,255,0.86)" }}>
            {line.map((w, j) => (
              <DropWord key={j} t={t} at={w.t} gap="0.24em">
                {w.text}
              </DropWord>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

// ───────────────────────── Notificación (llega un casting) ─────────────────────────
export const Notif: React.FC<{ t: number; at: number; end: number; y: number; title: string; words: { t: number; text: string }[] }> = ({ t, at, end, y, title, words }) => {
  if (t < at || t >= end) return null;
  const p = ramp(t, at, 0.2, Easing.out(Easing.back(1.6)));
  const out = 1 - ramp(t, end - 0.14, 0.14);
  return (
    <div style={{ position: "absolute", left: 200, top: y, width: 680, height: 118, borderRadius: 32, opacity: Math.min(1, p * 1.4) * out, translate: `0px ${-46 * (1 - p)}px`, display: "flex", alignItems: "center", gap: 22, padding: "0 26px", boxSizing: "border-box", ...glass("dark"), backdropFilter: "blur(12px)" }}>
      <Img src={icon("claqueta")} style={{ width: 70, height: 70 }} />
      <div style={{ flex: 1 }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontFamily: FONT.wide, fontSize: 25, fontWeight: 400, color: C.white }}>
          <span>{title}</span>
          <span style={{ color: "rgba(255,255,255,0.45)", fontWeight: 300 }}>ahora</span>
        </div>
        <div style={{ marginTop: 6, fontFamily: FONT.wide, fontSize: 28, fontWeight: 300, color: "rgba(255,255,255,0.82)", whiteSpace: "nowrap" }}>
          {words.map((w, i) => (
            <DropWord key={i} t={t} at={w.t} gap="0.26em">
              {w.text}
            </DropWord>
          ))}
        </div>
      </div>
    </div>
  );
};

// ───────────────────────── Globo tecleado junto al sujeto (gancho: «les cambien el nombre») ─────────────────────────
export const NamePill: React.FC<{ t: number; at: number; end: number; x: number; y: number; names: { t: number; text: string }[] }> = ({ t, at, end, x, y, names }) => {
  if (t < at || t >= end) return null;
  const p = ramp(t, at, 0.15, Easing.out(Easing.back(1.8)));
  const current = [...names].reverse().find((n) => t >= n.t);
  const typed = current ? Math.min(current.text.length, Math.floor((t - current.t) * 30) + 1) : 0;
  return (
    <div style={{ position: "absolute", left: x, top: y, translate: "-50% -50%", height: 78, padding: "0 30px", borderRadius: 40, display: "flex", alignItems: "center", gap: 16, opacity: Math.min(1, p * 1.3), scale: String(0.8 + 0.2 * p), background: "linear-gradient(180deg, rgba(214,96,96,0.86), rgba(170,52,60,0.86))", border: "1px solid rgba(255,255,255,0.3)", boxShadow: "0 12px 34px rgba(0,0,0,0.5)", fontFamily: FONT.wide, whiteSpace: "nowrap" }}>
      <span style={{ width: 12, height: 12, borderRadius: 12, background: C.redDot, boxShadow: "0 0 10px rgba(212,0,42,0.8)" }} />
      <span style={{ fontSize: 26, fontWeight: 300, letterSpacing: "0.14em", color: "rgba(255,255,255,0.75)" }}>PERSONAJE</span>
      <span style={{ fontSize: 34, fontWeight: 400, color: C.white, minWidth: 190 }}>
        {current ? current.text.slice(0, typed) : ""}
        <span style={{ display: "inline-block", width: 3, height: 30, marginLeft: 4, verticalAlign: "-4px", background: C.white, opacity: 0.9 }} />
      </span>
    </div>
  );
};

// ───────────────────────── Visor REC (pantalla completa, medidas de estilo.md §3.4) ─────────────────────────
export const Rec: React.FC<{ t: number; at: number; end: number }> = ({ t, at, end }) => {
  if (t < at || t >= end) return null;
  const p = ramp(t, at, 0.12);
  const insetX = 75;
  const top = 250; // por debajo de la cabecera de Instagram
  const bottom = H - 1560;
  const armX = 89;
  const armY = 81;
  const line = "3px solid rgba(255,255,255,0.92)";
  const corner = (sx: number, sy: number): React.CSSProperties => ({
    position: "absolute",
    left: sx < 0 ? insetX : undefined,
    right: sx > 0 ? insetX : undefined,
    top: sy < 0 ? top : undefined,
    bottom: sy > 0 ? bottom : undefined,
    width: armX,
    height: armY,
    borderLeft: sx < 0 ? line : undefined,
    borderRight: sx > 0 ? line : undefined,
    borderTop: sy < 0 ? line : undefined,
    borderBottom: sy > 0 ? line : undefined,
  });
  const blink = Math.floor((t - at) * 2) % 2 === 0;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: p, scale: String(1.04 - 0.04 * p) }}>
      <div style={corner(-1, -1)} />
      <div style={corner(1, -1)} />
      <div style={corner(-1, 1)} />
      <div style={corner(1, 1)} />
      <div style={{ position: "absolute", left: insetX + 34, top: top + 26, display: "flex", alignItems: "center", gap: 12, fontFamily: FONT.grotesk, fontWeight: 700, fontSize: 32, color: C.white, letterSpacing: "0.02em" }}>
        <span style={{ width: 16, height: 16, borderRadius: 16, background: C.redDot, opacity: blink ? 1 : 0.25, boxShadow: "0 0 12px rgba(212,0,42,0.9)" }} />
        REC
      </div>
      <div style={{ position: "absolute", right: insetX + 36, bottom: bottom + 28, width: 30, height: 30 }}>
        <div style={{ position: "absolute", left: 14, top: 0, width: 2, height: 30, background: "rgba(255,255,255,0.85)" }} />
        <div style={{ position: "absolute", left: 0, top: 14, width: 30, height: 2, background: "rgba(255,255,255,0.85)" }} />
      </div>
    </div>
  );
};

// ───────────────────────── Icono de trazo neón que entra volando ─────────────────────────
export const NeonIcon: React.FC<{ t: number; at: number; end: number; x: number; y: number; kind: "claqueta" | "flecha"; size?: number }> = ({ t, at, end, x, y, kind, size = 96 }) => {
  if (t < at || t >= end) return null;
  // Entra en curva desde abajo a la derecha, girando, en 330 ms.
  const p = ramp(t, at, 0.33, Easing.out(Easing.cubic));
  const dx = 260 * (1 - p) * (1 - p);
  const dy = 300 * (1 - p);
  const rot = kind === "flecha" ? -40 * (1 - p) : 55 * (1 - p) - 8;
  return (
    <div style={{ position: "absolute", left: x + dx, top: y + dy, width: size, height: size, translate: "-50% -50%", rotate: `${rot}deg`, opacity: Math.min(1, p * 2.5), filter: `drop-shadow(0 0 10px ${C.accentGlow}) drop-shadow(0 0 22px rgba(255,222,33,0.35))` }}>
      <svg viewBox="0 0 48 48" width={size} height={size} fill="none" stroke={C.accent} strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
        {kind === "claqueta" ? (
          <>
            <rect x="6" y="20" width="36" height="22" rx="3" />
            <path d="M6 20 L8 11 L41 6 L42 14 Z" />
            <path d="M16 9.8 L19 18.5 M26 8.3 L29 17 M35 7 L38 15.5" />
          </>
        ) : (
          <>
            <path d="M6 38 C 16 36, 26 28, 38 12" />
            <path d="M27 10 L39 10 L39 22" />
          </>
        )}
      </svg>
    </div>
  );
};

// ───────────────────────── Pentagrama: notas, ligaduras y «melodía» ─────────────────────────
export const Staff: React.FC<{ t: number; at: number; end: number; notesAt: number; slursAt: number; glowAt: number }> = ({ t, at, end, notesAt, slursAt, glowAt }) => {
  if (t < at || t >= end) return null;
  const p = ramp(t, at, 0.3);
  const out = 1 - ramp(t, end - 0.12, 0.12);
  const x0 = 150;
  const wLine = 800;
  const top = GFX_CY - 150;
  const gap = 22;
  const notes = [
    { x: 250, line: 3.5 },
    { x: 400, line: 2 },
    { x: 550, line: 3 },
    { x: 700, line: 1 },
    { x: 850, line: 2.5 },
  ];
  const ny = (l: number) => top + l * gap;
  const glow = ramp(t, glowAt, 0.3);
  const travel = ramp(t, glowAt, 0.9, Easing.inOut(Easing.cubic));
  return (
    <svg width={W} height={1920} viewBox={`0 0 ${W} 1920`} style={{ position: "absolute", left: 0, top: 0, opacity: out, overflow: "visible" }}>
      <defs>
        <filter id="staffGlow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation={6 + 6 * glow} result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      {[0, 1, 2, 3, 4].map((i) => (
        <line key={i} x1={x0} y1={top + i * gap} x2={x0 + wLine * p} y2={top + i * gap} stroke="rgba(255,255,255,0.34)" strokeWidth={2} />
      ))}
      {/* Ligaduras: la transición entre nota y nota */}
      {notes.slice(0, -1).map((n, i) => {
        const m = notes[i + 1];
        const sp = ramp(t, slursAt + i * 0.11, 0.26, Easing.out(Easing.quad));
        if (sp <= 0) return null;
        const y1 = ny(n.line) - 20;
        const y2 = ny(m.line) - 20;
        const cy = Math.min(y1, y2) - 58;
        return <path key={i} d={`M ${n.x + 8} ${y1} Q ${(n.x + m.x) / 2} ${cy} ${m.x - 8} ${y2}`} fill="none" stroke={C.accent} strokeWidth={5} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - sp} filter="url(#staffGlow)" />;
      })}
      {notes.map((n, i) => {
        const np = ramp(t, notesAt + i * 0.09, 0.14, Easing.out(Easing.back(2.4)));
        if (np <= 0) return null;
        const lit = glow > 0 ? C.accent : C.white;
        return (
          <g key={i} transform={`translate(${n.x} ${ny(n.line)}) scale(${np})`} filter={glow > 0 ? "url(#staffGlow)" : undefined}>
            <ellipse rx={17} ry={12.5} transform="rotate(-22)" fill={lit} />
            <line x1={15} y1={-4} x2={15} y2={-74} stroke={lit} strokeWidth={4} strokeLinecap="round" />
          </g>
        );
      })}
      {/* Punto de luz que recorre la melodía */}
      {travel > 0 && travel < 1 ? (
        <circle cx={lerp(notes[0].x, notes[4].x, travel)} cy={keys(lerp(notes[0].x, notes[4].x, travel), notes.map((n) => [n.x, ny(n.line) - 56] as [number, number]), (v) => v)} r={11} fill={C.white} filter="url(#staffGlow)" />
      ) : null}
    </svg>
  );
};

// ───────────────────────── Línea de BITS: nodos y tránsito entre ellos ─────────────────────────
export const BitLine: React.FC<{ t: number; at: number; end: number; nodesAt: number[]; travelAt: number }> = ({ t, at, end, nodesAt, travelAt }) => {
  if (t < at || t >= end) return null;
  const out = 1 - ramp(t, end - 0.12, 0.12);
  const cy = GFX_CY + 6;
  const xs = [170, 417, 663, 910];
  const lineP = ramp(t, at, 0.35);
  const travel = ramp(t, travelAt, 1.0, Easing.inOut(Easing.cubic));
  const arcY = (x: number) => {
    // arcos entre nodos consecutivos
    for (let i = 0; i < xs.length - 1; i++) {
      if (x >= xs[i] && x <= xs[i + 1]) {
        const u = (x - xs[i]) / (xs[i + 1] - xs[i]);
        return cy - 76 - 80 * Math.sin(Math.PI * u);
      }
    }
    return cy - 76;
  };
  const tx = lerp(xs[0], xs[3], travel);
  return (
    <svg width={W} height={1920} viewBox={`0 0 ${W} 1920`} style={{ position: "absolute", left: 0, top: 0, opacity: out, overflow: "visible" }}>
      <defs>
        <filter id="bitGlow" x="-80%" y="-80%" width="260%" height="260%">
          <feGaussianBlur stdDeviation={8} result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <radialGradient id="bitNode" cx="50%" cy="120%" r="120%">
          <stop offset="0%" stopColor={C.gold} />
          <stop offset="45%" stopColor="#3a2b00" />
          <stop offset="100%" stopColor="#080600" />
        </radialGradient>
      </defs>
      <line x1={xs[0]} y1={cy} x2={lerp(xs[0], xs[3], lineP)} y2={cy} stroke="rgba(255,255,255,0.22)" strokeWidth={2} strokeDasharray="4 10" />
      {xs.slice(0, -1).map((x, i) => {
        const segP = Math.max(0, Math.min(1, travel * 3 - i));
        if (segP <= 0) return null;
        const x2 = xs[i + 1];
        return <path key={i} d={`M ${x} ${cy - 76} Q ${(x + x2) / 2} ${cy - 76 - 160} ${x2} ${cy - 76}`} fill="none" stroke={C.accent} strokeWidth={5} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - segP} filter="url(#bitGlow)" />;
      })}
      {xs.map((x, i) => {
        const np = ramp(t, nodesAt[i], 0.14, Easing.out(Easing.back(2.2)));
        if (np <= 0) return null;
        const reached = travel > 0 && tx >= x - 6;
        return (
          <g key={i} transform={`translate(${x} ${cy}) scale(${np})`}>
            <circle r={72} fill="url(#bitNode)" stroke={reached ? C.accent : "rgba(255,255,255,0.3)"} strokeWidth={reached ? 3 : 1.5} filter={reached ? "url(#bitGlow)" : undefined} />
            <text y={-10} textAnchor="middle" fontFamily={FONT.wide} fontWeight={300} fontSize={24} fill="rgba(255,255,255,0.7)" letterSpacing="0.18em">
              BIT
            </text>
            <text y={36} textAnchor="middle" fontFamily={FONT.grotesk} fontWeight={700} fontSize={48} fill={reached ? C.accent : C.white}>
              {i + 1}
            </text>
          </g>
        );
      })}
      {travel > 0 && travel < 1 ? <circle cx={tx} cy={arcY(tx)} r={12} fill={C.white} filter="url(#bitGlow)" /> : null}
    </svg>
  );
};

// ───────────────────────── Tarjeta de la masterclass ─────────────────────────
export const MasterclassCard: React.FC<{ t: number; at: number; end: number; cy: number }> = ({ t, at, end, cy }) => {
  if (t < at || t >= end) return null;
  const p = ramp(t, at, 0.2, Easing.out(Easing.back(1.5)));
  const out = 1 - ramp(t, end - 0.12, 0.12);
  const badge = ramp(t, at + 0.35, 0.2, Easing.out(Easing.back(2.4)));
  return (
    <div style={{ position: "absolute", left: 70, top: cy - 125, width: 940, height: 250, borderRadius: 36, opacity: Math.min(1, p * 1.4) * out, scale: String(0.94 + 0.06 * p), overflow: "hidden", display: "flex", alignItems: "center", gap: 34, padding: "0 36px", boxSizing: "border-box", ...glass("gold") }}>
      <Img src={staticFile("media/img/clase_doc.jpg")} style={{ position: "absolute", right: -120, top: -20, width: 760, opacity: 0.1, rotate: "-6deg", filter: "invert(1) blur(0.6px)" }} />
      <div style={{ position: "relative", width: 178, height: 178, flex: "0 0 auto" }}>
        <Img src={staticFile("media/img/armando_serio.jpg")} style={{ width: 178, height: 178, borderRadius: 178, objectFit: "cover", border: `3px solid ${C.accent}`, boxShadow: `0 0 34px rgba(255,222,33,0.35)` }} />
        <div style={{ position: "absolute", right: -6, bottom: -2, width: 62, height: 62, borderRadius: 62, background: C.accent, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 6px 16px rgba(0,0,0,0.5)" }}>
          <svg width="26" height="26" viewBox="0 0 24 24" fill="#0b0b0b">
            <path d="M7 4.5v15l13-7.5z" />
          </svg>
        </div>
      </div>
      <div style={{ position: "relative" }}>
        <div style={{ fontFamily: FONT.wide, fontWeight: 400, fontSize: 24, letterSpacing: "0.2em", color: C.accent, textTransform: "uppercase" }}>Módulo 8 · Clase 1</div>
        <div style={{ marginTop: 8, fontFamily: FONT.grotesk, fontWeight: 700, fontSize: 84, letterSpacing: "-0.045em", lineHeight: 1, color: C.white, whiteSpace: "nowrap" }}>Qué es un BIT</div>
        <div style={{ marginTop: 12, fontFamily: FONT.wide, fontWeight: 300, fontSize: 27, color: "rgba(255,255,255,0.72)" }}>Masterclass con Armando</div>
      </div>
      <div style={{ position: "absolute", right: 28, top: 26, padding: "8px 22px", borderRadius: 30, background: C.accent, color: "#0b0b0b", fontFamily: FONT.grotesk, fontWeight: 700, fontSize: 28, letterSpacing: "0.04em", scale: String(badge), rotate: "4deg", boxShadow: `0 0 26px ${C.accentGlow}` }}>GRATIS</div>
    </div>
  );
};

// ───────────────────────── Aro de enfoque (b-roll) ─────────────────────────
export const Ring: React.FC<{ t: number; at: number; end: number; x: number; y: number; d: number }> = ({ t, at, end, x, y, d }) => {
  if (t < at || t >= end) return null;
  const p = ramp(t, at, 0.5, Easing.out(Easing.cubic));
  const out = 1 - ramp(t, end - 0.15, 0.15);
  const dd = d * (1.5 - 0.5 * p);
  return <div style={{ position: "absolute", left: x - dd / 2, top: y - dd / 2, width: dd, height: dd, borderRadius: dd, border: `4px solid ${C.cream}`, boxShadow: `0 0 18px rgba(244,230,200,0.7), inset 0 0 18px rgba(244,230,200,0.35)`, opacity: Math.min(1, p * 2) * out }} />;
};

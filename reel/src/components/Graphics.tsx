import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BARLOW, BEBAS, C, GLOW, GRADIENT, H, OUTFIT, W } from "../theme";
import { FLASHES, FLICKERS, SEATED_AT, STREAKS, VOICE_END } from "../timeline";
import { at, clamp01, easeInOut, easeOut, inOut, prog, word } from "../util";

type T = { t: number };
const W0 = (i: number) => word(i).start;

/** Texto escrito letra a letra (se acompaña de SFX de tecleo). */
const typedText = (text: string, t: number, t0: number, dur?: number) => {
  const d = dur ?? Math.min(0.6, Math.max(0.22, text.length * 0.035));
  const n = Math.floor(clamp01((t - t0) / d) * text.length + 0.001);
  return text.slice(0, n);
};
const Typed: React.FC<{ text: string; t: number; t0: number; dur?: number }> = ({ text, t, t0, dur }) => {
  const shown = typedText(text, t, t0, dur);
  return (
    <>
      {shown}
      <span style={{ opacity: 0 }}>{text.slice(shown.length)}</span>
    </>
  );
};

const glass: React.CSSProperties = {
  background: C.glass,
  border: `1.5px solid ${C.glassBorder}`,
  borderRadius: 30,
  backdropFilter: "blur(18px)",
  boxShadow: "0 20px 60px rgba(0,0,0,0.45)",
};

/** Pop estándar: escala 0,6→1,05→1 en 8 fotogramas. */
const popScale = (t: number, t0: number) => {
  const p = clamp01((t - t0) / (8 / 30));
  if (p <= 0) return 0;
  return interpolate(p, [0, 0.6, 1], [0.6, 1.06, 1], { easing: easeOut });
};

// ------------------------------------------------------------------------------------------
// Degradados de etalonaje (estilo.md §7): viñeta superior y degradado negro desde el 65 %.
// ------------------------------------------------------------------------------------------
export const GradeOverlays: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  // En el gancho la silla (producto) está en la parte baja: degradado más suave para no taparla.
  const k = interpolate(frame / fps, [SEATED_AT - 0.13, SEATED_AT], [0.45, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <AbsoluteFill
      style={{ background: "radial-gradient(ellipse 85% 70% at 50% 42%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.38) 100%)" }}
    />
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 15%)" }} />
    <AbsoluteFill
      style={{
        opacity: k,
        background:
          "linear-gradient(180deg, rgba(0,0,0,0) 62%, rgba(0,0,0,0.42) 74%, rgba(0,0,0,0.78) 86%, rgba(0,0,0,0.92) 100%)",
      }}
    />
  </AbsoluteFill>
  );
};

// ------------------------------------------------------------------------------------------
// Fotos tipo polaroid (estilo.md §3.6)
// ------------------------------------------------------------------------------------------
export const PhotoCards: React.FC<T & { cards: { src: string; t: number }[]; t1: number; dimAt: number; y: number }> = ({
  t,
  cards,
  t1,
  dimAt,
  y,
}) => {
  if (t < cards[0].t || t > t1) return null;
  const out = 1 - prog(t, t1 - 0.12, 0.12);
  const dim = prog(t, dimAt, 0.2);
  const xs = [W / 2 - 300, W / 2, W / 2 + 300];
  const rot = [-4, 1.5, 4];
  return (
    <>
      {cards.map((c, i) => {
        if (t < c.t) return null;
        const flash = 1 - clamp01((t - c.t) / (2 / 30));
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: xs[i],
              top: y * H,
              translate: "-50% -50%",
              width: 270,
              height: 350,
              background: "#fff",
              padding: 8,
              boxShadow: "0 18px 50px rgba(0,0,0,0.55)",
              rotate: `${rot[i]}deg`,
              scale: String(popScale(t, c.t)),
              opacity: out * (1 - 0.55 * dim),
              filter: dim > 0 ? `blur(${3 * dim}px)` : undefined,
            }}
          >
            <Img src={staticFile(c.src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            <div style={{ position: "absolute", inset: 8, background: "#fff", opacity: flash * 0.9 }} />
          </div>
        );
      })}
    </>
  );
};

// ------------------------------------------------------------------------------------------
// Tarjeta glass con dos iconos (madera / cuero), como "IN FITNESS / SUCCESS" (estilo.md §3.5)
// ------------------------------------------------------------------------------------------
const WoodIcon = () => (
  <svg width={60} height={60} viewBox="0 0 60 60">
    <rect x="8" y="10" width="44" height="40" rx="8" fill="#C98B4A" />
    <path d="M12 20 C24 16, 36 24, 48 19 M12 30 C22 27, 38 34, 48 29 M12 40 C26 37, 34 44, 48 39" stroke="#8A5527" strokeWidth="2.6" fill="none" strokeLinecap="round" />
    <ellipse cx="34" cy="30" rx="5" ry="3.4" stroke="#8A5527" strokeWidth="2.2" fill="none" />
  </svg>
);
const LeatherIcon = () => (
  <svg width={60} height={60} viewBox="0 0 60 60">
    <path d="M14 12 h32 c4 0 6 3 6 6 v24 c0 4 -3 7 -7 7 H15 c-4 0 -7 -3 -7 -7 V18 c0 -3 2 -6 6 -6z" fill="#8E3F1E" />
    <path d="M15 17 h30 c2 0 3 1.5 3 3 v21 c0 2 -1.5 3.5 -3.5 3.5 H15.5 C13.5 44.5 12 43 12 41 V20 c0 -1.5 1.4 -3 3 -3z" fill="none" stroke="#E7B48A" strokeWidth="2" strokeDasharray="3.5 3" />
  </svg>
);
const AppIcon: React.FC<{ children: React.ReactNode; tint: string }> = ({ children, tint }) => (
  <div
    style={{
      width: 96,
      height: 96,
      borderRadius: 24,
      background: "linear-gradient(160deg, #2A2520 0%, #141210 100%)",
      border: `1.5px solid ${C.glassBorder}`,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      boxShadow: `0 0 26px ${tint}`,
    }}
  >
    {children}
  </div>
);
export const IconCard: React.FC<T & { t0: number; t1: number; a: number; b: number; y: number }> = ({ t, t0, t1, a, b, y }) => {
  if (t < t0 || t > t1) return null;
  const v = inOut(t, t0, t1);
  const enter = prog(t, t0, 0.25);
  const col = (tc: number, icon: React.ReactNode, tint: string, small: string, big: string) => {
    const pc = prog(t, tc, 0.2);
    return (
      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 10, opacity: pc, translate: `0px ${24 * (1 - pc)}px` }}>
        <div style={{ marginTop: -66, scale: String(popScale(t, tc) || 0.001) }}>
          <AppIcon tint={tint}>{icon}</AppIcon>
        </div>
        <div style={{ fontFamily: OUTFIT, fontWeight: 400, fontSize: 36, color: "rgba(255,255,255,0.75)" }}>{small}</div>
        <div style={{ fontFamily: OUTFIT, fontWeight: 700, fontSize: 58, color: "#fff", letterSpacing: "-0.02em", textAlign: "center", lineHeight: 1.02 }}>
          <Typed text={big} t={t} t0={tc + 0.05} />
        </div>
      </div>
    );
  };
  return (
    <div style={{ position: "absolute", left: W / 2, top: y * H, translate: "-50% -50%", opacity: v, scale: String(0.9 + 0.1 * enter) }}>
      <div style={{ ...glass, width: 900, padding: "60px 30px 40px", display: "flex", gap: 20 }}>
        {col(a, <WoodIcon />, "rgba(201,139,74,0.35)", "en", "MADERA")}
        {col(b, <LeatherIcon />, "rgba(142,63,30,0.45)", "y con", "CUERO AUTÉNTICO")}
      </div>
      <GlowLine t={t} t0={t0 + 0.1} width={860} />
    </div>
  );
};
const GlowLine: React.FC<T & { t0: number; width: number }> = ({ t, t0, width }) => {
  const p = prog(t, t0, 0.5);
  return (
    <div
      style={{
        margin: "18px auto 0",
        width: width * p,
        height: 4,
        borderRadius: 4,
        background: `linear-gradient(90deg, rgba(255,194,26,0) 0%, ${C.orangeC} 30%, ${C.yellow} 60%, rgba(255,194,26,0) 100%)`,
        boxShadow: "0 0 18px rgba(255,194,26,0.8)",
      }}
    />
  );
};

// ------------------------------------------------------------------------------------------
// Etiquetas blancas apiladas (estilo.md §3.3)
// ------------------------------------------------------------------------------------------
export const TagGrid: React.FC<T & { tags: { text: string; t: number; full?: boolean }[]; t1: number; y: number; header?: { text: string; t: number } }> = ({
  t,
  tags,
  t1,
  y,
  header,
}) => {
  const t0 = header?.t ?? tags[0].t;
  if (t < t0 || t > t1) return null;
  const out = 1 - prog(t, t1 - 0.12, 0.12);
  const rows: (typeof tags)[] = [];
  tags.forEach((g) => {
    const last = rows[rows.length - 1];
    if (!g.full && last && last.length === 1 && !last[0].full) last.push(g);
    else rows.push([g]);
  });
  return (
    <div style={{ position: "absolute", left: W / 2, top: y * H, translate: "-50% -50%", display: "flex", flexDirection: "column", alignItems: "center", gap: 18, opacity: out }}>
      {header && (
        <div style={{ fontFamily: OUTFIT, fontWeight: 500, fontSize: 50, color: "#fff", textShadow: "0 2px 14px rgba(0,0,0,0.55)", opacity: prog(t, header.t, 0.17), marginBottom: 6 }}>
          {header.text}
        </div>
      )}
      {rows.map((row, r) => (
        <div key={r} style={{ display: "flex", gap: 18, width: 860, justifyContent: "center" }}>
          {row.map((g) => (
            <div
              key={g.text}
              style={{
                flex: row.length > 1 || g.full ? 1 : undefined,
                background: "rgba(255,255,255,0.96)",
                color: C.ink,
                fontFamily: OUTFIT,
                fontWeight: 600,
                fontSize: 44,
                padding: "22px 40px",
                borderRadius: 18,
                textAlign: "center",
                boxShadow: "0 8px 30px rgba(0,0,0,0.35)",
                scale: String(popScale(t, g.t)),
                opacity: t >= g.t ? 1 : 0,
                whiteSpace: "nowrap",
              }}
            >
              <Typed text={g.text} t={t} t0={g.t + 0.03} />
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

// ------------------------------------------------------------------------------------------
// Logos de clientes flotando alrededor de la persona (corrección del usuario)
// ------------------------------------------------------------------------------------------
type ClientLogo = { src: string; t: number; x: number; y: number; h: number; label?: string; phase: number };
export const FloatingLogos: React.FC<T & { logos: ClientLogo[]; t1: number }> = ({ t, logos, t1 }) => {
  if (t < logos[0].t - 0.15 || t > t1) return null;
  const out = 1 - prog(t, t1 - 0.15, 0.15);
  const head = prog(t, logos[0].t - 0.12, 0.25);
  return (
    <>
      {logos.map((l) => {
        if (t < l.t) return null;
        const pin = clamp01((t - l.t) / (9 / 30));
        const sc = interpolate(pin, [0, 0.65, 1], [0.4, 1.08, 1], { easing: easeOut });
        const fly = 1 - easeOut(pin);
        const k = t - l.t;
        const bob = Math.sin(k * 2.6 + l.phase) * 14;
        const sway = Math.cos(k * 1.9 + l.phase) * 9;
        const rot = Math.sin(k * 2.1 + l.phase) * 2.6;
        // sale desde detrás de él (centro) hacia su posición
        const dx = (0.5 - l.x) * W * 0.4 * fly;
        const dy = (0.38 - l.y) * H * 0.2 * fly;
        return (
          <div
            key={l.src}
            style={{
              position: "absolute",
              left: l.x * W,
              top: l.y * H,
              translate: `calc(-50% + ${dx + sway}px) calc(-50% + ${dy + bob}px)`,
              rotate: `${rot}deg`,
              scale: String(sc * (0.9 + 0.1 * out)),
              opacity: Math.min(1, pin * 1.6) * out,
              filter: fly > 0.04 ? `blur(${10 * fly}px)` : undefined,
            }}
          >
            <div
              style={{
                background: "rgba(255,255,255,0.97)",
                borderRadius: 30,
                padding: "24px 34px",
                boxShadow: "0 24px 60px rgba(0,0,0,0.45), 0 0 34px rgba(252,229,0,0.18)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 10,
              }}
            >
              <Img src={staticFile(l.src)} style={{ height: l.h, width: "auto", display: "block" }} />
              {l.label && (
                <div style={{ fontFamily: OUTFIT, fontWeight: 600, fontSize: 25, color: "#0B2A66", textAlign: "center", lineHeight: 1.1, whiteSpace: "pre" }}>
                  {l.label}
                </div>
              )}
            </div>
          </div>
        );
      })}
      <div style={{ position: "absolute", left: W / 2, top: 0.8 * H, translate: "-50% -50%", opacity: head * out }}>
        <div style={{ ...glass, borderRadius: 999, padding: "16px 40px", fontFamily: OUTFIT, fontWeight: 600, fontSize: 32, letterSpacing: "0.16em", color: "rgba(255,255,255,0.9)", whiteSpace: "nowrap" }}>
          <Typed text="NUESTROS CLIENTES" t={t} t0={logos[0].t - 0.1} dur={0.45} />
        </div>
      </div>
    </>
  );
};

// ------------------------------------------------------------------------------------------
// Píldora blanca conectada con puntos (estilo.md §3.2) y píldora de ubicación
// ------------------------------------------------------------------------------------------
export const PillCallout: React.FC<T & { text: string; t0: number; t1: number; y: number; x?: number }> = ({ t, text, t0, t1, y, x }) => {
  if (t < t0 || t > t1) return null;
  const v = inOut(t, t0, t1, 0.1, 0.1);
  return (
    <div style={{ position: "absolute", left: (x ?? 0.5) * W, top: y * H, translate: "-50% 0", display: "flex", flexDirection: "column", alignItems: "center", opacity: v }}>
      {[0, 1, 2].map((i) => (
        <div key={i} style={{ width: 9, height: 9, borderRadius: 9, background: "#fff", marginBottom: 7, opacity: clamp01((t - t0 - i * 0.03) / 0.05) }} />
      ))}
      <div style={{ background: "#fff", color: C.ink, fontFamily: OUTFIT, fontWeight: 600, fontSize: 42, padding: "16px 40px", borderRadius: 999, boxShadow: "0 10px 30px rgba(0,0,0,0.35)", scale: String(popScale(t, t0 + 0.08)) }}>
        <Typed text={text} t={t} t0={t0 + 0.1} />
      </div>
    </div>
  );
};

export const LocationPill: React.FC<T & { text: string; t0: number; t1: number; y: number }> = ({ t, text, t0, t1, y }) => {
  if (t < t0 || t > t1) return null;
  const v = inOut(t, t0, t1, 0.1, 0.1);
  return (
    <div style={{ position: "absolute", left: W / 2, top: y * H, translate: "-50% -50%", opacity: v, scale: String(popScale(t, t0)) }}>
      <div style={{ ...glass, borderRadius: 999, padding: "18px 40px 18px 22px", display: "flex", alignItems: "center", gap: 18 }}>
        <div style={{ width: 64, height: 64, borderRadius: 99, background: GRADIENT.yellow, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 0 22px rgba(252,229,0,0.6)" }}>
          <svg width="34" height="34" viewBox="0 0 24 24">
            <path d="M12 2.5c-3.9 0-7 3-7 6.9 0 5.2 7 12.1 7 12.1s7-6.9 7-12.1c0-3.9-3.1-6.9-7-6.9z" fill="#1A1600" />
            <circle cx="12" cy="9.4" r="2.6" fill="#FCE500" />
          </svg>
        </div>
        <div style={{ fontFamily: OUTFIT, fontWeight: 600, fontSize: 44, color: "#fff" }}>
          <Typed text={text} t={t} t0={t0 + 0.05} />
        </div>
      </div>
    </div>
  );
};

// ------------------------------------------------------------------------------------------
// Botón CTA "Contáctanos" con cursor que hace clic
// ------------------------------------------------------------------------------------------
export const CtaButton: React.FC<T & { t0: number; t1: number; clickAt: number; y: number; small?: string }> = ({ t, t0, t1, clickAt, y, small }) => {
  if (t < t0 || t > t1) return null;
  const v = inOut(t, t0, t1, 0.12, 0.12);
  const press = t >= clickAt && t < clickAt + 0.12 ? 0.93 : 1;
  const cur = prog(t, t0 + 0.1, clickAt - t0 - 0.1, easeInOut);
  const ripple = clamp01((t - clickAt) / 0.35);
  return (
    <div style={{ position: "absolute", left: W / 2, top: y * H, translate: "-50% -50%", display: "flex", flexDirection: "column", alignItems: "center", gap: 18, opacity: v }}>
      {small && <div style={{ fontFamily: OUTFIT, fontWeight: 500, fontSize: 50, color: "#fff", textShadow: "0 2px 14px rgba(0,0,0,0.55)" }}>{small}</div>}
      <div style={{ position: "relative", scale: String(popScale(t, t0) * press) }}>
        <div
          style={{
            background: GRADIENT.yellow,
            color: "#1A1600",
            fontFamily: OUTFIT,
            fontWeight: 700,
            fontSize: 72,
            letterSpacing: "-0.03em",
            padding: "30px 74px",
            borderRadius: 999,
            boxShadow: "0 0 50px rgba(252,229,0,0.55), 0 16px 40px rgba(0,0,0,0.45)",
          }}
        >
          <Typed text="Contáctanos" t={t} t0={t0 + 0.05} dur={0.35} />
        </div>
        {ripple > 0 && ripple < 1 && (
          <div style={{ position: "absolute", inset: -20 * ripple, borderRadius: 999, border: `4px solid rgba(252,229,0,${1 - ripple})` }} />
        )}
        <svg width="70" height="70" viewBox="0 0 24 24" style={{ position: "absolute", right: 30 + 260 * (1 - cur), bottom: -40 - 220 * (1 - cur), filter: "drop-shadow(0 4px 8px rgba(0,0,0,0.5))" }}>
          <path d="M5 3l14 7.5-6.2 1.6L10 18.5z" fill="#fff" stroke="#111" strokeWidth="1.2" strokeLinejoin="round" />
        </svg>
      </div>
    </div>
  );
};

// ------------------------------------------------------------------------------------------
// Estela de luz amarilla y orbe (estilo.md §3.9 y §3.11)
// ------------------------------------------------------------------------------------------
export const LightStreaks: React.FC<T> = ({ t }) => (
  <>
    {STREAKS.map((t0) => {
      if (t < t0 || t > t0 + 1.0) return null;
      const p = prog(t, t0, 0.6, easeInOut);
      const fade = 1 - prog(t, t0 + 0.6, 0.4);
      const d = "M -80 760 C 220 520, 420 900, 640 640 S 980 420, 1180 560";
      return (
        <svg key={t0} width={W} height={H} style={{ position: "absolute", inset: 0, opacity: fade }}>
          <path d={d} stroke="rgba(255,210,31,0.55)" strokeWidth={46} fill="none" strokeLinecap="round" pathLength={1} strokeDasharray="0.45 1" strokeDashoffset={0.45 - p * 1.45} style={{ filter: "blur(22px)" }} />
          <path d={d} stroke="#FFD21F" strokeWidth={16} fill="none" strokeLinecap="round" pathLength={1} strokeDasharray="0.45 1" strokeDashoffset={0.45 - p * 1.45} style={{ filter: "drop-shadow(0 0 14px rgba(255,210,31,0.9))" }} />
        </svg>
      );
    })}
  </>
);

export const Orb: React.FC<T & { t0: number; t1: number; x: number; y: number; size?: number }> = ({ t, t0, t1, x, y, size }) => {
  if (t < t0 || t > t1) return null;
  const v = inOut(t, t0, t1, 0.25, 0.15) * 0.6;
  const s = size ?? 420;
  return (
    <div style={{ position: "absolute", left: x * W, top: y * H, width: s, height: s, translate: "-50% -50%", borderRadius: s, background: "radial-gradient(circle, rgba(252,229,0,0.75) 0%, rgba(252,229,0,0.25) 45%, rgba(252,229,0,0) 70%)", opacity: v, filter: "blur(30px)" }} />
  );
};

// ------------------------------------------------------------------------------------------
// Flashes de exposición y parpadeos
// ------------------------------------------------------------------------------------------
export const FlashLayer: React.FC<T> = ({ t }) => {
  const f = FLASHES.find((x) => t >= x && t < x + 3 / 30);
  const k = FLICKERS.find((x) => t >= x && t < x + 1 / 30);
  return (
    <>
      {f !== undefined && <AbsoluteFill style={{ background: "#FFF6DA", opacity: 0.85 * (1 - (t - f) / (3 / 30)), mixBlendMode: "screen" }} />}
      {k !== undefined && <AbsoluteFill style={{ background: "#000", opacity: 0.6 }} />}
    </>
  );
};

// ------------------------------------------------------------------------------------------
// Escena a pantalla completa: barra amarilla que crece (estilo.md §3.7)
// "La empresa es una de las MAYORES EMPRESAS ... a través del TIEMPO ... en COLOMBIA"
// ------------------------------------------------------------------------------------------
export const BarScene: React.FC<T & { t0: number; t1: number }> = ({ t, t0, t1 }) => {
  if (t < t0 || t >= t1) return null;
  // La barra crece durante toda la escena (sin tramos estáticos) y acelera en "se han constituido ... tiempo".
  const fill = 0.35 * prog(t, t0 + 0.2, W0(102) - t0 - 0.2, easeInOut) + 0.65 * prog(t, W0(102), W0(108) + 0.3 - W0(102), easeInOut);
  const drift = prog(t, t0, t1 - t0, (x) => x);
  const pan = prog(t, W0(109) - 0.1, 0.45, easeInOut); // "en Colombia"
  const titleIn = prog(t, t0, 0.3);
  const barTop = 560;
  const barH = H - barTop + 40;
  const fillH = barH * (0.22 + 0.78 * fill);
  const avatarY = H - fillH + 10;
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse 80% 60% at 40% 70%, ${C.graphBg2} 0%, ${C.graphBg} 70%)`, overflow: "hidden" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1800, height: H, transformOrigin: "540px 960px", translate: `${-430 * pan}px 0px`, scale: String(1 + 0.05 * drift) }}>
        {/* Barra */}
        <div style={{ position: "absolute", left: 540 - 160, top: barTop, width: 320, height: barH, background: "#F2EEE6", borderRadius: 6, overflow: "hidden", boxShadow: "0 0 90px rgba(252,229,0,0.45)" }}>
          <div style={{ position: "absolute", left: 0, bottom: 0, width: "100%", height: fillH, background: `linear-gradient(180deg, ${C.yellow} 0%, #F6D000 100%)`, boxShadow: "0 -6px 40px rgba(252,229,0,0.9)" }} />
        </div>
              {/* Isotipo de Macizo (extraído del sello del B ROL 2) dentro del círculo, subiendo con la barra */}
        <div style={{ position: "absolute", left: 540 - 160 - 136, top: avatarY - 12, width: 118, height: 118, filter: "drop-shadow(0 0 24px rgba(252,229,0,0.7))" }}>
          <Img src={staticFile("logos/macizo_isotipo.svg")} style={{ width: "100%", height: "100%" }} />
        </div>
        {/* Título */}
        <div style={{ position: "absolute", left: 540, top: 330, translate: "-50% -50%", display: "flex", flexDirection: "column", alignItems: "center", opacity: titleIn }}>
          <div style={{ fontFamily: OUTFIT, fontWeight: 500, fontSize: 40, color: "#fff", opacity: 0.85 }}>una de las</div>
          <div style={{ fontFamily: OUTFIT, fontWeight: 600, fontSize: 112, color: "#fff", letterSpacing: "-0.04em", lineHeight: 1, whiteSpace: "nowrap" }}>
            <Typed text="Mayores empresas" t={t} t0={t0 + 0.05} dur={0.45} />
          </div>
          <div style={{ fontFamily: OUTFIT, fontWeight: 500, fontSize: 40, color: C.yellow, marginTop: 14, opacity: prog(t, W0(105), 0.2), filter: GLOW.yellow }}>
            a través del tiempo
          </div>
        </div>
        {/* Texto condensado tras el paneo */}
        <div style={{ position: "absolute", left: 1010, top: 900, opacity: pan > 0.6 ? 1 : 0 }}>
          <div style={{ fontFamily: BEBAS, fontSize: 70, color: "#fff", letterSpacing: "0.01em", lineHeight: 1 }}>
            <Typed text="EN" t={t} t0={W0(109)} dur={0.12} />
          </div>
          <div style={{ fontFamily: BEBAS, fontSize: 210, color: "#F5F5F5", lineHeight: 0.9, textShadow: "0 0 30px rgba(255,255,255,0.25)" }}>
            <Typed text="COLOMBIA" t={t} t0={W0(110) - 0.05} dur={0.4} />
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------------------------------
// "REMODELA" a pantalla completa
// ------------------------------------------------------------------------------------------
export const RemodelaScene: React.FC<T & { t0: number; t1: number }> = ({ t, t0, t1 }) => {
  if (t < t0 || t >= t1) return null;
  const p = prog(t, t0, 0.18);
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#000" }}>
      <Img src={staticFile("media/foto1.jpg")} style={{ width: W, height: H, objectFit: "cover", objectPosition: "35% 50%", scale: String(1.25 - 0.08 * p), filter: "brightness(0.42) blur(2px)" }} />
      <AbsoluteFill style={{ background: "radial-gradient(circle at 50% 50%, rgba(252,229,0,0.28) 0%, rgba(0,0,0,0) 55%)" }} />
      <div style={{ position: "absolute", left: W / 2, top: H * 0.48, translate: "-50% -50%", fontFamily: BEBAS, fontSize: 330, color: "#F5F5F5", letterSpacing: "0.01em", scale: String(1.18 - 0.18 * p), filter: `blur(${10 * (1 - p)}px) drop-shadow(0 0 40px rgba(252,229,0,0.55))`, whiteSpace: "nowrap" }}>
        <Typed text="REMODELA" t={t} t0={t0} dur={0.25} />
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------------------------------
// Tarjeta final (sin logo, por indicación del usuario)
// ------------------------------------------------------------------------------------------
export const EndCard: React.FC<T> = ({ t }) => {
  const t0 = VOICE_END;
  if (t < t0) return null;
  const p = prog(t, t0, 0.35);
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse 80% 60% at 50% 45%, #2A2312 0%, ${C.graphBg} 70%)`, opacity: p }}>
      <Orb t={t} t0={t0} t1={t0 + 30} x={0.5 + 0.06 * Math.sin((t - t0) * 1.6)} y={0.42} size={620} />
      <div style={{ position: "absolute", left: W / 2, top: H * 0.42, translate: "-50% -50%", display: "flex", flexDirection: "column", alignItems: "center", scale: String(1 + 0.025 * (t - t0)) }}>
        <div style={{ fontFamily: OUTFIT, fontWeight: 500, fontSize: 46, color: "rgba(255,255,255,0.85)", marginBottom: 26 }}>Remodela con</div>
        {/* Logotipo de Macizo vectorizado a partir del camión (foto 5); se revela de izquierda a derecha */}
        <div
          style={{
            width: 780,
            clipPath: `inset(0 ${100 * (1 - prog(t, t0 + 0.22, 0.45, easeInOut))}% 0 0)`,
            filter: "drop-shadow(0 0 30px rgba(252,229,0,0.25))",
          }}
        >
          <Img src={staticFile("logos/macizo_logotipo_blanco.svg")} style={{ width: 780, display: "block" }} />
          <div style={{ textAlign: "right", fontFamily: BARLOW, fontWeight: 400, fontSize: 58, color: "#EDEDED", marginTop: 8, paddingRight: 4 }}>
            <Typed text="Madera en el Diseño" t={t} t0={t0 + 0.7} dur={0.45} />
          </div>
        </div>
        <div style={{ display: "flex", gap: 16, marginTop: 40, opacity: prog(t, t0 + 0.8, 0.25) }}>
          {["Diseño gratuito", "Visitamos tu hogar"].map((x) => (
            <div key={x} style={{ background: "rgba(255,255,255,0.95)", color: C.ink, fontFamily: OUTFIT, fontWeight: 600, fontSize: 36, padding: "14px 30px", borderRadius: 16, whiteSpace: "nowrap" }}>
              {x}
            </div>
          ))}
        </div>
      </div>
      <CtaButton t={t} t0={t0 + 0.9} t1={t0 + 10} clickAt={t0 + 1.25} y={0.7} />
    </AbsoluteFill>
  );
};

/** Capa de todos los gráficos con un único reloj. */
export const Graphics: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <>
      <Orb t={t} t0={0} t1={SEATED_AT} x={0.5} y={0.26} size={520} />
      <Orb t={t} t0={at(11.47)} t1={at(12.53)} x={0.5} y={0.29} />
      <Orb t={t} t0={at(22.85)} t1={at(23.88)} x={0.5} y={0.29} />
      <Orb t={t} t0={at(30.52)} t1={at(33.25)} x={0.5} y={0.31} />
      <LightStreaks t={t} />
      <PhotoCards
        t={t}
        cards={[
          { src: "media/silla_completa.jpg", t: at(14.72) },
          { src: "media/silla_cuero.jpg", t: at(14.94) },
          { src: "media/silla_madera.jpg", t: at(15.16) },
        ]}
        t1={at(15.75)}
        dimAt={W0(42)}
        y={0.6}
      />
      <IconCard t={t} t0={at(18.00)} t1={at(20.82)} a={W0(50) - 0.05} b={W0(53) - 0.1} y={0.62} />
      <TagGrid
        t={t}
        header={{ text: "Tenemos", t: W0(72) }}
        tags={[
          { text: "Tapicería", t: W0(73) },
          { text: "Ebanistería", t: W0(74) },
          { text: "Metalmecánica", t: W0(75), full: true },
        ]}
        t1={at(30.52)}
        y={0.62}
      />
      <PillCallout t={t} text="Sin costo" t0={W0(130) + 0.12} t1={at(51.10)} y={0.64} />
      <LocationPill t={t} text="Visita a tu hogar" t0={W0(133)} t1={at(52.83)} y={0.6} />
      <FloatingLogos
        t={t}
        t1={at(66.63)}
        logos={[
          { src: "logos/clientes/ford.svg", t: W0(155), x: 0.2, y: 0.19, h: 96, phase: 0 },
          { src: "logos/clientes/calvin_klein.svg", t: W0(157), x: 0.8, y: 0.3, h: 50, phase: 1.7 },
          { src: "logos/clientes/unisabana_escudo.png", t: W0(160), x: 0.2, y: 0.47, h: 120, label: "Universidad\nde La Sabana", phase: 3.1 },
          { src: "logos/clientes/crepes_waffles.svg", t: W0(164), x: 0.78, y: 0.57, h: 30, phase: 4.4 },
        ]}
      />
      <TagGrid
        t={t}
        tags={[
          { text: "Diseñadores", t: W0(171) },
          { text: "Arquitectos", t: W0(173) },
        ]}
        t1={at(69.45)}
        y={0.6}
      />
      <CtaButton t={t} t0={at(80.15)} t1={at(81.37)} clickAt={at(80.95)} y={0.6} small="Solo" />
    </>
  );
};

/** Escenas que tapan el vídeo (van por debajo de los subtítulos). */
export const FullScreenScenes: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <>
      <BarScene t={t} t0={at(39.50)} t1={at(43.93)} />
      <RemodelaScene t={t} t0={at(76.37)} t1={at(77.07)} />
    </>
  );
};

export const TopLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <>
      <EndCard t={t} />
      <FlashLayer t={t} />
    </>
  );
};

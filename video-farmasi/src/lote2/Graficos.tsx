import React from "react";
import { Video } from "@remotion/media";
import { AbsoluteFill, Easing, Img, interpolate, random, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { HN } from "./fuentes";
import { LILA } from "./Subtitulos2";

// Gráficos del lote 2 (corrección de la clienta: sin emojis; iconos en línea vectorial lila; nada sobre las caras).
export const MORADO = "#2E1C52";
export const LILA_OSC = "#8B5CF6";
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const eOut = Easing.bezier(0.16, 1, 0.3, 1);
const eInOut = Easing.bezier(0.65, 0, 0.35, 1);

const useT = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return { frame, fps, t: frame / fps };
};
// entrada estilo subtítulo: opacidad, desenfoque y subida
const entra = (t: number, t0: number, dur = 0.2, dy = 14) => {
  const p = interpolate(t, [t0, t0 + dur], [0, 1], { ...cl, easing: eOut });
  return { opacity: p, filter: p < 0.99 ? `blur(${((1 - p) * 6).toFixed(2)}px)` : undefined, translate: `0px ${((1 - p) * dy).toFixed(1)}px` };
};

// ---------- iconos de línea ----------
type NombreIcono =
  | "gota" | "frasco" | "tarro" | "vaso" | "caja" | "tinte" | "plancha" | "secador" | "celular" | "enlace" | "bolsa" | "casa" | "flor";
export const Icono: React.FC<{ n: NombreIcono; tam?: number; color?: string; grosor?: number }> = ({ n, tam = 80, color = LILA_OSC, grosor = 5 }) => {
  const p = { fill: "none", stroke: color, strokeWidth: grosor, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  const d: Record<NombreIcono, React.ReactNode> = {
    gota: <path {...p} d="M50 12 C50 12 22 46 22 64 a28 28 0 0 0 56 0 C78 46 50 12 50 12 Z" />,
    frasco: <><rect {...p} x={32} y={34} width={36} height={56} rx={8} /><rect {...p} x={40} y={14} width={20} height={20} rx={3} /><path {...p} d="M40 56 h20" /></>,
    tarro: <><rect {...p} x={20} y={42} width={60} height={42} rx={10} /><rect {...p} x={24} y={28} width={52} height={14} rx={5} /><path {...p} d="M36 62 h28" /></>,
    vaso: <><path {...p} d="M28 30 h44 l-6 60 h-32 Z" /><path {...p} d="M56 30 l8 -20 h10" /><path {...p} d="M31 50 h38" /></>,
    caja: <><path {...p} d="M14 36 l36 -16 l36 16 v38 l-36 16 l-36 -16 Z" /><path {...p} d="M14 36 l36 16 l36 -16 M50 52 v38" /></>,
    tinte: <><path {...p} d="M16 50 h52 a26 22 0 0 1 -52 0 Z" /><path {...p} d="M60 44 l24 -30" /><rect {...p} x={80} y={8} width={10} height={14} rx={2} transform="rotate(38 85 15)" /></>,
    plancha: <><rect {...p} x={20} y={16} width={16} height={70} rx={6} transform="rotate(-8 28 51)" /><rect {...p} x={52} y={16} width={16} height={70} rx={6} transform="rotate(8 60 51)" /><path {...p} d="M30 86 q14 10 28 0" /></>,
    secador: <><path {...p} d="M14 30 h50 a20 20 0 0 1 0 40 h-50 Z" /><path {...p} d="M40 70 l-6 22 h14 l4 -22" /><path {...p} d="M86 40 h8 M86 50 h10 M86 60 h8" /></>,
    celular: <><rect {...p} x={28} y={10} width={44} height={80} rx={9} /><path {...p} d="M44 78 h12" /></>,
    enlace: <><path {...p} d="M44 56 l12 -12" /><path {...p} d="M38 46 l-10 10 a12 12 0 0 0 17 17 l10 -10" /><path {...p} d="M62 54 l10 -10 a12 12 0 0 0 -17 -17 l-10 10" /></>,
    bolsa: <><path {...p} d="M22 36 h56 l-5 54 h-46 Z" /><path {...p} d="M38 36 v-8 a12 12 0 0 1 24 0 v8" /></>,
    casa: <><path {...p} d="M16 48 l34 -30 l34 30" /><path {...p} d="M26 42 v44 h48 v-44" /><path {...p} d="M44 86 v-22 h12 v22" /></>,
    flor: <><circle {...p} cx={50} cy={46} r={9} />{[0, 60, 120, 180, 240, 300].map((a) => <ellipse key={a} {...p} cx={50} cy={24} rx={8} ry={13} transform={`rotate(${a} 50 46)`} />)}<path {...p} d="M50 56 v34" /></>,
  };
  return <svg width={tam} height={tam} viewBox="0 0 100 100">{d[n]}</svg>;
};

const Marca: React.FC<{ tipo: "check" | "cross"; p: number; tam?: number }> = ({ tipo, p, tam = 54 }) => (
  <svg width={tam} height={tam} viewBox="0 0 60 60" style={{ scale: String(0.4 + 0.6 * p), opacity: Math.min(1, p * 2) }}>
    <circle cx={30} cy={30} r={27} fill={tipo === "check" ? LILA_OSC : "#E2475C"} />
    {tipo === "check" ? (
      <path d="M17 31 l9 9 l17 -19" fill="none" stroke="#fff" strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={50} strokeDashoffset={50 * (1 - p)} />
    ) : (
      <path d="M20 20 L40 40 M40 20 L20 40" fill="none" stroke="#fff" strokeWidth={6} strokeLinecap="round" />
    )}
  </svg>
);

// ---------- motion graphics a pantalla completa (fondo lavanda) ----------
export const FondoLavanda: React.FC = () => {
  const { t } = useT();
  return (
    <AbsoluteFill style={{ background: "linear-gradient(165deg, #FCFAFF 0%, #F1E9FF 55%, #E2D2FF 100%)", overflow: "hidden" }}>
      <div style={{ position: "absolute", width: 900, height: 900, borderRadius: "50%", left: -300 + Math.sin(t * 0.6) * 40, top: -260, background: "radial-gradient(circle, rgba(179,139,255,.35), rgba(179,139,255,0) 65%)" }} />
      <div style={{ position: "absolute", width: 1000, height: 1000, borderRadius: "50%", left: 380, top: 1150 + Math.cos(t * 0.5) * 40, background: "radial-gradient(circle, rgba(139,92,246,.22), rgba(139,92,246,0) 65%)" }} />
    </AbsoluteFill>
  );
};

export const CorteMG: React.FC<{ desde: number; hasta: number; children: React.ReactNode }> = ({ desde, hasta, children }) => {
  const { t } = useT();
  if (t < desde - 0.01 || t > hasta + 0.2) return null;
  const e = interpolate(t, [desde, desde + 0.17], [0, 1], { ...cl, easing: eOut });
  const s = interpolate(t, [hasta, hasta + 0.15], [0, 1], { ...cl, easing: eInOut });
  return (
    <AbsoluteFill style={{ opacity: e * (1 - s), scale: String(1.05 - 0.05 * e - 0.02 * s), filter: e < 0.99 || s > 0.01 ? `blur(${((1 - e) * 12 + s * 10).toFixed(2)}px)` : undefined }}>
      <FondoLavanda />
      {children}
    </AbsoluteFill>
  );
};

export const TituloMG: React.FC<{ texto: string; t0: number; y: number; tam?: number; color?: string; sub?: string }> = ({ texto, t0, y, tam = 118, color = MORADO, sub }) => {
  const { t } = useT();
  const palabras = texto.split(" ");
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: y, textAlign: "center" }}>
      {sub ? <div style={{ fontFamily: HN, fontWeight: 500, fontSize: 46, letterSpacing: "-0.03em", color: LILA_OSC, marginBottom: 10, ...entra(t, t0, 0.2) }}>{sub}</div> : null}
      <div style={{ fontFamily: HN, fontWeight: 800, fontSize: tam, letterSpacing: "-0.035em", color, lineHeight: 0.95 }}>
        {palabras.map((w, i) => (
          <span key={i} style={{ display: "inline-block", marginRight: "0.22em", ...entra(t, t0 + 0.06 * i + (sub ? 0.08 : 0), 0.22) }}>{w}</span>
        ))}
      </div>
    </div>
  );
};

export type ItemMG = { texto: string; t: number; icono?: NombreIcono; img?: string; marca?: { tipo: "check" | "cross"; t: number }; tachar?: number };
export const ListaMG: React.FC<{ items: ItemMG[]; y: number; alto?: number; ancho?: number }> = ({ items, y, alto = 150, ancho = 880 }) => {
  const { t } = useT();
  return (
    <div style={{ position: "absolute", left: (1080 - ancho) / 2, top: y, width: ancho }}>
      {items.map((it, i) => {
        if (t < it.t - 0.05) return null;
        const p = interpolate(t, [it.t - 0.05, it.t + 0.25], [0, 1], { ...cl, easing: eOut });
        const pm = it.marca ? interpolate(t, [it.marca.t, it.marca.t + 0.25], [0, 1], { ...cl, easing: eOut }) : 0;
        const pt = it.tachar !== undefined ? interpolate(t, [it.tachar, it.tachar + 0.25], [0, 1], { ...cl, easing: eInOut }) : 0;
        return (
          <div
            key={i}
            style={{
              position: "absolute", top: i * (alto + 26), left: 0, width: ancho, height: alto, borderRadius: 40, background: "rgba(255,255,255,.96)",
              boxShadow: "0 18px 40px rgba(46,28,82,.14), inset 0 0 0 3px rgba(179,139,255,.45)", display: "flex", alignItems: "center", gap: 28, padding: "0 34px",
              opacity: p, translate: `${((1 - p) * 60).toFixed(1)}px 0px`, filter: p < 0.99 ? `blur(${((1 - p) * 6).toFixed(2)}px)` : undefined,
            }}
          >
            <div style={{ width: alto - 40, height: alto - 40, borderRadius: 30, background: it.img ? "#fff" : "#F3ECFF", boxShadow: it.img ? "inset 0 0 0 2px #EFE6FF" : undefined, display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden", flexShrink: 0 }}>
              {it.img ? <Img src={staticFile(it.img)} style={{ width: "100%", height: "100%", objectFit: "contain" }} /> : it.icono ? <Icono n={it.icono} tam={alto - 56} /> : null}
            </div>
            <div style={{ position: "relative", flex: 1, fontFamily: HN, fontWeight: 700, fontSize: 56, letterSpacing: "-0.03em", color: MORADO, lineHeight: 1 }}>
              {it.texto}
              {pt > 0 ? <div style={{ position: "absolute", left: -6, top: "52%", height: 7, borderRadius: 4, width: `${pt * 104}%`, background: "#E2475C" }} /> : null}
            </div>
            {it.marca && pm > 0 ? <Marca tipo={it.marca.tipo} p={pm} tam={70} /> : null}
          </div>
        );
      })}
    </div>
  );
};

export const BarraMG: React.FC<{ t0: number; t1: number; y: number; etiqueta: string; ancho?: number; x?: number; tam?: number }> = ({ t0, t1, y, etiqueta, ancho = 820, x, tam = 52 }) => {
  const { t } = useT();
  const p = interpolate(t, [t0, t1], [0, 1], { ...cl, easing: eInOut });
  const left = x !== undefined ? x - ancho / 2 : (1080 - ancho) / 2;
  return (
    <div style={{ position: "absolute", left, top: y, width: ancho, ...entra(t, t0 - 0.15, 0.2) }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontFamily: HN, fontWeight: 700, fontSize: tam, letterSpacing: "-0.03em", color: MORADO, marginBottom: 16 }}>
        <span>{etiqueta}</span>
        <span style={{ color: LILA_OSC, fontWeight: 800 }}>{Math.round(p * 100)}%</span>
      </div>
      <div style={{ height: tam * 0.62, borderRadius: 99, background: "rgba(255,255,255,.95)", boxShadow: "inset 0 0 0 3px rgba(179,139,255,.45)", overflow: "hidden" }}>
        <div style={{ width: `${p * 100}%`, height: "100%", borderRadius: 99, background: `linear-gradient(90deg, ${LILA}, ${LILA_OSC})` }} />
      </div>
    </div>
  );
};

// Gotas que suben (MG de hidratación)
export const Gotas: React.FC<{ t0: number }> = ({ t0 }) => {
  const { t } = useT();
  return (
    <>
      {Array.from({ length: 9 }).map((_, i) => {
        const k = t - t0 - i * 0.12;
        if (k < 0) return null;
        const x = 120 + random(`g${i}`) * 840;
        const y = 1500 - k * (260 + random(`v${i}`) * 140);
        const o = interpolate(k, [0, 0.2, 1.4, 1.8], [0, 0.85, 0.85, 0], cl);
        return <div key={i} style={{ position: "absolute", left: x, top: y, opacity: o }}><Icono n="gota" tam={70 + random(`s${i}`) * 50} color={LILA} grosor={6} /></div>;
      })}
    </>
  );
};

// Barra de color de cabello (rubio → castaño) con marcador que avanza
export const CabelloMG: React.FC<{ t0: number; tRubio: number; tPoco: number; tRecupera: number; y: number }> = ({ t0, tRubio, tPoco, tRecupera, y }) => {
  const { t } = useT();
  const m = interpolate(t, [tPoco, tRecupera + 0.4], [0.06, 0.94], { ...cl, easing: eInOut });
  const lbl = (txt: string, tt: number, lado: "izq" | "der") => (
    <div style={{ position: "absolute", top: 150, [lado === "izq" ? "left" : "right"]: 0, width: 420, textAlign: lado === "izq" ? "left" : "right", fontFamily: HN, fontWeight: 700, fontSize: 48, letterSpacing: "-0.03em", color: MORADO, lineHeight: 1.05, ...entra(t, tt, 0.22) }}>{txt}</div>
  );
  return (
    <div style={{ position: "absolute", left: 90, top: y, width: 900, height: 320, ...entra(t, t0, 0.2) }}>
      <div style={{ position: "absolute", top: 40, left: 0, width: 900, height: 70, borderRadius: 99, background: "linear-gradient(90deg, #F0D38E 0%, #D8AE67 30%, #9A6A45 65%, #4A3122 100%)", boxShadow: "0 14px 30px rgba(46,28,82,.18)" }} />
      <div style={{ position: "absolute", top: 18, left: m * 900 - 57, width: 114, height: 114, borderRadius: "50%", background: "#fff", boxShadow: `0 10px 26px rgba(46,28,82,.25), inset 0 0 0 8px ${LILA}` }} />
      {lbl("Rubio por mucho tiempo", tRubio, "izq")}
      {lbl("Recuperándolo poco a poco", tPoco, "der")}
    </div>
  );
};

// Sello grande (p. ej. "¡MENTIRA!")
export const Sello: React.FC<{ texto: string; t0: number; y: number; giro?: number }> = ({ texto, t0, y, giro = -8 }) => {
  const { t, fps } = useT();
  if (t < t0) return null;
  const sp = spring({ frame: Math.round((t - t0) * fps), fps, config: { damping: 10, stiffness: 220, mass: 0.6 } });
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: y, display: "flex", justifyContent: "center" }}>
      <div style={{ fontFamily: HN, fontWeight: 800, fontSize: 150, letterSpacing: "-0.04em", color: "#E2475C", border: "12px solid #E2475C", borderRadius: 30, padding: "4px 40px", rotate: `${giro}deg`, scale: String(1.6 - 0.6 * sp), opacity: Math.min(1, sp * 1.5), background: "rgba(255,255,255,.7)" }}>
        {texto}
      </div>
    </div>
  );
};

// ---------- piezas de humor (vídeo 1) ----------
const Tarjeta: React.FC<{ x: number; y: number; w: number; p: number; s?: number; children: React.ReactNode; giro?: number }> = ({ x, y, w, p, s = 0, children, giro = 0 }) => (
  <div
    style={{
      position: "absolute", left: x - w / 2, top: y, width: w, borderRadius: 34, background: "rgba(255,255,255,.97)", padding: "24px 28px",
      boxShadow: "0 22px 50px rgba(30,10,60,.30), inset 0 0 0 3px rgba(179,139,255,.5)", opacity: p * (1 - s), scale: String(0.85 + 0.15 * p - 0.06 * s), rotate: `${giro}deg`,
      filter: p < 0.99 || s > 0.01 ? `blur(${((1 - p) * 8 + s * 6).toFixed(2)}px)` : undefined,
    }}
  >
    {children}
  </div>
);
const usePop = (t0: number, t1: number) => {
  const { t, fps } = useT();
  const p = t >= t0 ? spring({ frame: Math.round((t - t0) * fps), fps, config: { damping: 13, stiffness: 210, mass: 0.6 } }) : 0;
  const s = interpolate(t, [t1, t1 + 0.15], [0, 1], { ...cl, easing: eInOut });
  return { t, p, s, visible: t >= t0 && t <= t1 + 0.16 };
};

// Etiqueta de personaje tipo sitcom, con línea que apunta hacia arriba (a la persona, sin taparla)
export const EtiquetaPersonaje: React.FC<{ nombre: string; rol: string; t0: number; t1: number; x: number; y: number }> = ({ nombre, rol, t0, t1, x, y }) => {
  const { p, s, visible } = usePop(t0, t1);
  if (!visible) return null;
  return (
    <div style={{ position: "absolute", left: x, top: y, translate: "-50% 0", opacity: p * (1 - s), scale: String(0.8 + 0.2 * p), filter: s > 0.01 ? `blur(${s * 6}px)` : undefined }}>
      <div style={{ width: 4, height: 70 * p, background: "#fff", margin: "0 auto", borderRadius: 2, boxShadow: "0 2px 8px rgba(0,0,0,.35)" }} />
      <div style={{ background: "rgba(255,255,255,.97)", borderRadius: 26, padding: "14px 26px 16px", boxShadow: "0 16px 36px rgba(30,10,60,.32)", textAlign: "center", whiteSpace: "nowrap" }}>
        <div style={{ fontFamily: HN, fontWeight: 800, fontSize: 58, letterSpacing: "-0.035em", color: LILA_OSC, lineHeight: 1 }}>{nombre}</div>
        <div style={{ fontFamily: HN, fontWeight: 500, fontSize: 34, letterSpacing: "-0.03em", color: MORADO, marginTop: 4 }}>{rol}</div>
      </div>
    </div>
  );
};

// "Haciendo cuentas…": 1950 → año actual = N años
export const ContadorAnios: React.FC<{ t0: number; t1: number; x: number; y: number; desde?: number; hasta?: number }> = ({ t0, t1, x, y, desde = 1950, hasta = 2026 }) => {
  const { t, p, s, visible } = usePop(t0, t1);
  if (!visible) return null;
  const k = interpolate(t, [t0 + 0.25, t0 + 1.1], [0, 1], { ...cl, easing: eInOut });
  const anio = Math.round(desde + (hasta - desde) * k);
  const fin = interpolate(t, [t0 + 1.1, t0 + 1.35], [0, 1], { ...cl, easing: eOut });
  return (
    <Tarjeta x={x} y={y} w={400} p={p} s={s} giro={3}>
      <div style={{ fontFamily: HN, fontWeight: 500, fontSize: 34, letterSpacing: "-0.03em", color: MORADO, opacity: 0.75 }}>Haciendo cuentas…</div>
      <div style={{ fontFamily: HN, fontWeight: 800, fontSize: 112, letterSpacing: "-0.04em", color: LILA_OSC, lineHeight: 1 }}>{anio}</div>
      <div style={{ fontFamily: HN, fontWeight: 800, fontSize: 60, letterSpacing: "-0.035em", color: MORADO, opacity: fin, translate: `0px ${(1 - fin) * 10}px` }}>¡{hasta - desde} años!</div>
    </Tarjeta>
  );
};

// Destellos vectoriales (estrellas de 4 puntas) alrededor de alguien, sin pisar su cara
export const Destellos: React.FC<{ t0: number; t1: number; puntos: { x: number; y: number; tam: number; d: number }[] }> = ({ t0, t1, puntos }) => {
  const { t } = useT();
  if (t < t0 || t > t1 + 0.2) return null;
  return (
    <>
      {puntos.map((q, i) => {
        const k = t - t0 - q.d;
        if (k < 0) return null;
        const a = interpolate(k, [0, 0.18, 0.5, 0.8], [0, 1, 0.75, 1], cl) * interpolate(t, [t1, t1 + 0.2], [1, 0], cl);
        return (
          <svg key={i} width={q.tam} height={q.tam} viewBox="0 0 100 100" style={{ position: "absolute", left: q.x - q.tam / 2, top: q.y - q.tam / 2, opacity: a, scale: String(0.4 + 0.6 * a), rotate: `${k * 90}deg`, filter: `drop-shadow(0 0 10px ${LILA})` }}>
            <path d="M50 0 C54 38 62 46 100 50 C62 54 54 62 50 100 C46 62 38 54 0 50 C38 46 46 38 50 0 Z" fill="#fff" />
          </svg>
        );
      })}
    </>
  );
};

// Visor de cámara "REC" (bordes de la pantalla)
export const VisorREC: React.FC<{ t0: number; t1: number }> = ({ t0, t1 }) => {
  const { t } = useT();
  if (t < t0 || t > t1 + 0.15) return null;
  const e = interpolate(t, [t0, t0 + 0.15], [0, 1], { ...cl, easing: eOut }) * interpolate(t, [t1, t1 + 0.15], [1, 0], cl);
  const parpadeo = Math.floor((t - t0) * 2) % 2 === 0 ? 1 : 0.25;
  const k = (t - t0) * 30;
  const tc = `00:00:${String(Math.floor(k / 30) % 60).padStart(2, "0")}:${String(Math.floor(k) % 30).padStart(2, "0")}`;
  const esq = (st: React.CSSProperties) => <div style={{ position: "absolute", width: 110, height: 110, borderColor: "#fff", borderStyle: "solid", borderWidth: 0, filter: "drop-shadow(0 2px 6px rgba(0,0,0,.4))", ...st }} />;
  const m = 70 + (1 - e) * 40;
  return (
    <AbsoluteFill style={{ opacity: e }}>
      {esq({ left: m, top: m + 60, borderLeftWidth: 8, borderTopWidth: 8 })}
      {esq({ right: m, top: m + 60, borderRightWidth: 8, borderTopWidth: 8 })}
      {esq({ left: m, bottom: m + 260, borderLeftWidth: 8, borderBottomWidth: 8 })}
      {esq({ right: m, bottom: m + 260, borderRightWidth: 8, borderBottomWidth: 8 })}
      <div style={{ position: "absolute", left: m + 30, top: m + 90, display: "flex", alignItems: "center", gap: 14, fontFamily: HN, fontWeight: 800, fontSize: 52, color: "#fff", letterSpacing: "-0.02em", textShadow: "0 2px 8px rgba(0,0,0,.5)" }}>
        <div style={{ width: 30, height: 30, borderRadius: "50%", background: "#FF3B4E", opacity: parpadeo }} /> REC
      </div>
      <div style={{ position: "absolute", right: m + 30, top: m + 96, fontFamily: HN, fontWeight: 500, fontSize: 38, color: "#fff", textShadow: "0 2px 8px rgba(0,0,0,.5)" }}>{tc}</div>
    </AbsoluteFill>
  );
};

// Tragamonedas "¿cuánto voy a ganar?" que se detiene en ? ? ? (sin prometer cifras)
export const Tragamonedas: React.FC<{ t0: number; t1: number; x: number; y: number }> = ({ t0, t1, x, y }) => {
  const { t, p, s, visible } = usePop(t0, t1);
  if (!visible) return null;
  const simbolos = ["$", "7", "%", "★", "$", "7"];
  return (
    <Tarjeta x={x} y={y} w={430} p={p} s={s} giro={-2}>
      <div style={{ fontFamily: HN, fontWeight: 700, fontSize: 36, letterSpacing: "-0.03em", color: MORADO, textAlign: "center", marginBottom: 12 }}>¿Cuánto voy a ganar?</div>
      <div style={{ display: "flex", gap: 14, justifyContent: "center" }}>
        {[0, 1, 2].map((i) => {
          const para = t0 + 0.7 + i * 0.28;
          const gira = t < para;
          const idx = Math.floor((t - t0) * 22 + i * 3) % simbolos.length;
          const rebote = gira ? 0 : interpolate(t, [para, para + 0.18], [1, 0], { ...cl, easing: eOut });
          return (
            <div key={i} style={{ width: 110, height: 130, borderRadius: 20, background: "#F3ECFF", boxShadow: "inset 0 0 0 3px rgba(179,139,255,.6)", display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden" }}>
              <div style={{ fontFamily: HN, fontWeight: 800, fontSize: 92, color: gira ? "#B9A2E8" : LILA_OSC, filter: gira ? "blur(3px)" : undefined, translate: `0px ${(gira ? ((t * 900) % 60) - 30 : -rebote * 18).toFixed(1)}px` }}>
                {gira ? simbolos[idx] : "?"}
              </div>
            </div>
          );
        })}
      </div>
    </Tarjeta>
  );
};

// Lista de "requisitos del equipo" con ✗ / ✓ (remate del final)
export const Requisitos: React.FC<{ t0: number; t1: number; x: number; y: number; items: { texto: string; t: number; marca: "check" | "cross"; tm: number }[] }> = ({ t0, t1, x, y, items }) => {
  const { t, p, s, visible } = usePop(t0, t1);
  if (!visible) return null;
  return (
    <Tarjeta x={x} y={y} w={410} p={p} s={s} giro={-2}>
      <div style={{ fontFamily: HN, fontWeight: 800, fontSize: 44, letterSpacing: "-0.035em", color: MORADO, lineHeight: 1, marginBottom: 14 }}>Requisitos del equipo</div>
      {items.map((it, i) => {
        if (t < it.t) return null;
        const pi = interpolate(t, [it.t, it.t + 0.22], [0, 1], { ...cl, easing: eOut });
        const pm = interpolate(t, [it.tm, it.tm + 0.25], [0, 1], { ...cl, easing: eOut });
        return (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 10, opacity: pi, translate: `${(1 - pi) * 30}px 0px` }}>
            <div style={{ width: 50, height: 50, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
              {pm > 0 ? <Marca tipo={it.marca} p={pm} tam={50} /> : <div style={{ width: 40, height: 40, borderRadius: 10, boxShadow: "inset 0 0 0 4px #CDB8F5" }} />}
            </div>
            <div style={{ position: "relative", fontFamily: HN, fontWeight: 700, fontSize: 38, letterSpacing: "-0.03em", color: MORADO, lineHeight: 1.05 }}>
              {it.texto}
              {it.marca === "cross" && pm > 0 ? <div style={{ position: "absolute", left: -4, top: "50%", height: 5, width: `${pm * 104}%`, background: "#E2475C", borderRadius: 3 }} /> : null}
            </div>
          </div>
        );
      })}
    </Tarjeta>
  );
};

// Pegatina de texto (p. ej. "% en tus compras")
export const Pegatina: React.FC<{ texto: string; sub?: string; t0: number; t1: number; x: number; y: number; giro?: number }> = ({ texto, sub, t0, t1, x, y, giro = -6 }) => {
  const { p, s, visible } = usePop(t0, t1);
  if (!visible) return null;
  return (
    <div style={{ position: "absolute", left: x, top: y, translate: "-50% -50%", rotate: `${giro}deg`, scale: String((0.6 + 0.4 * p) * (1 - 0.1 * s)), opacity: p * (1 - s), background: `linear-gradient(135deg, ${LILA}, ${LILA_OSC})`, borderRadius: 30, padding: "18px 34px", boxShadow: "0 18px 40px rgba(60,20,120,.35)", textAlign: "center", whiteSpace: "nowrap" }}>
      <div style={{ fontFamily: HN, fontWeight: 800, fontSize: 70, letterSpacing: "-0.04em", color: "#fff", lineHeight: 1 }}>{texto}</div>
      {sub ? <div style={{ fontFamily: HN, fontWeight: 500, fontSize: 32, letterSpacing: "-0.03em", color: "#fff", marginTop: 4 }}>{sub}</div> : null}
    </div>
  );
};

// Cadena de iconos vectoriales (redes → link → compra → casa)
export const FlujoIconos: React.FC<{ pasos: { icono: NombreIcono; t: number; texto: string }[]; hasta: number; y: number; tam?: number }> = ({ pasos, hasta, y, tam = 128 }) => {
  const { t, fps } = useT();
  const hueco = 46;
  const total = pasos.length * tam + (pasos.length - 1) * hueco;
  const x0 = 540 - total / 2;
  if (t < pasos[0].t - 0.05 || t > hasta + 0.2) return null;
  const sal = interpolate(t, [hasta, hasta + 0.18], [0, 1], { ...cl, easing: eInOut });
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1920, opacity: 1 - sal, filter: sal > 0 ? `blur(${sal * 6}px)` : undefined }}>
      {pasos.map((q, i) => {
        const sp = t >= q.t ? spring({ frame: Math.round((t - q.t) * fps), fps, config: { damping: 12, stiffness: 200, mass: 0.7 } }) : 0;
        const x = x0 + i * (tam + hueco);
        const fl = i > 0 ? interpolate(t, [q.t - 0.1, q.t + 0.08], [0, 1], { ...cl, easing: eOut }) : 0;
        return (
          <React.Fragment key={i}>
            {i > 0 ? (
              <svg width={hueco} height={30} style={{ position: "absolute", left: x - hueco, top: y + tam / 2 - 15, opacity: fl }}>
                <path d={`M6 15 L${6 + (hueco - 18) * fl} 15`} stroke="#fff" strokeWidth={5} strokeLinecap="round" />
                <path d={`M${hueco - 16} 7 L${hueco - 7} 15 L${hueco - 16} 23`} stroke="#fff" strokeWidth={5} fill="none" strokeLinecap="round" strokeLinejoin="round" opacity={fl > 0.9 ? 1 : 0} />
              </svg>
            ) : null}
            <div style={{ position: "absolute", left: x, top: y, width: tam, scale: String(sp), textAlign: "center" }}>
              <div style={{ width: tam, height: tam, borderRadius: 34, background: "rgba(255,255,255,.96)", boxShadow: "0 14px 34px rgba(30,10,60,.3)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Icono n={q.icono} tam={tam * 0.68} />
              </div>
              <div style={{ marginTop: 8, fontFamily: HN, fontWeight: 700, fontSize: 30, letterSpacing: "-0.03em", color: "#fff", textShadow: "0 2px 8px rgba(0,0,0,.45)" }}>{q.texto}</div>
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
};

// Panel con barra de progreso sobre el vídeo (en la zona libre, lejos de la cara)
export const PanelBarra: React.FC<{ titulo: string; etiqueta: string; t0: number; t1: number; tLlenar: [number, number]; x: number; y: number; w?: number }> = ({ titulo, etiqueta, t0, t1, tLlenar, x, y, w = 400 }) => {
  const { p, s, visible } = usePop(t0, t1);
  if (!visible) return null;
  return (
    <Tarjeta x={x} y={y} w={w} p={p} s={s} giro={2}>
      <div style={{ fontFamily: HN, fontWeight: 800, fontSize: 50, letterSpacing: "-0.035em", color: MORADO, lineHeight: 0.98, marginBottom: 18 }}>{titulo}</div>
      <div style={{ position: "relative", height: 90 }}>
        <BarraMG t0={tLlenar[0]} t1={tLlenar[1]} y={0} x={(w - 56) / 2} ancho={w - 56} etiqueta={etiqueta} tam={36} />
      </div>
    </Tarjeta>
  );
};

// Logo de marca (imagen) en placa redondeada que aparece con rebote y flota suave
export const LogoPlaca: React.FC<{ src: string; t0: number; t1: number; x: number; y: number; ancho: number; radio?: number }> = ({ src, t0, t1, x, y, ancho, radio = 34 }) => {
  const { t, p, s, visible } = usePop(t0, t1);
  if (!visible) return null;
  const flota = Math.sin((t - t0) * 2.6) * 5;
  const brillo = interpolate(t, [t0 + 0.25, t0 + 0.85], [-0.4, 1.4], cl);
  return (
    <div
      style={{
        position: "absolute", left: x - ancho / 2, top: y + flota, width: ancho, borderRadius: radio, overflow: "hidden",
        opacity: p * (1 - s), scale: String((0.7 + 0.3 * p) * (1 - 0.08 * s)), rotate: `${(1 - p) * -6}deg`,
        filter: s > 0.01 ? `blur(${s * 6}px)` : undefined, boxShadow: "0 24px 50px rgba(0,0,0,.35)",
      }}
    >
      <Img src={staticFile(src)} style={{ width: "100%", display: "block" }} />
      <div style={{ position: "absolute", inset: 0, background: `linear-gradient(115deg, rgba(255,255,255,0) ${(brillo - 0.15) * 100}%, rgba(255,255,255,.28) ${brillo * 100}%, rgba(255,255,255,0) ${(brillo + 0.15) * 100}%)` }} />
    </div>
  );
};

// Logo de WhatsApp en 3D: burbuja verde con grosor (capas apiladas), brillo y giro en Y
const WA_TEL =
  "M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347";
const WA_BURBUJA = "M12.05 0.1 A11.85 11.85 0 1 1 6.4 22.3 L0.2 23.9 L1.85 17.8 A11.85 11.85 0 0 1 12.05 0.1 Z";
export const WhatsApp3D: React.FC<{ t0: number; t1: number; x: number; y: number; tam?: number }> = ({ t0, t1, x, y, tam = 280 }) => {
  const { t, p, s, visible } = usePop(t0, t1);
  if (!visible) return null;
  const k = t - t0;
  const giro = (1 - p) * -70 + Math.sin(k * 2.2) * 16 * Math.min(1, k * 2);
  const flota = Math.sin(k * 2.6) * 8;
  const capas = 14;
  return (
    <div style={{ position: "absolute", left: x - tam / 2, top: y - tam / 2, width: tam, height: tam, perspective: 900, opacity: p * (1 - s) }}>
      <div style={{ position: "absolute", left: tam * 0.12, right: tam * 0.12, bottom: -tam * 0.1, height: tam * 0.12, borderRadius: "50%", background: "radial-gradient(closest-side, rgba(0,0,0,.35), rgba(0,0,0,0))", scale: String(1 - flota / 80) }} />
      <div style={{ width: "100%", height: "100%", transformStyle: "preserve-3d", transform: `translateY(${flota}px) rotateY(${giro}deg) rotateX(8deg) scale(${0.6 + 0.4 * p})` }}>
        <svg width={tam} height={tam} viewBox="-1 -1 26 27" style={{ overflow: "visible" }}>
          <defs>
            <radialGradient id="waCara" cx="30%" cy="25%" r="85%">
              <stop offset="0%" stopColor="#7CF5A6" />
              <stop offset="45%" stopColor="#2BD96B" />
              <stop offset="100%" stopColor="#12A548" />
            </radialGradient>
            <linearGradient id="waBrillo" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#fff" stopOpacity={0.55} />
              <stop offset="100%" stopColor="#fff" stopOpacity={0} />
            </linearGradient>
            <filter id="waSombraTel" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx={0.25} dy={0.35} stdDeviation={0.25} floodColor="#0A6E30" floodOpacity={0.6} />
            </filter>
          </defs>
          {/* grosor: capas apiladas hacia abajo-derecha */}
          {Array.from({ length: capas }).map((_, i) => (
            <path key={i} d={WA_BURBUJA} fill={i === capas - 1 ? "#0B5E2A" : "#0E7A37"} transform={`translate(${(capas - i) * 0.05} ${(capas - i) * 0.09})`} />
          ))}
          <path d={WA_BURBUJA} fill="url(#waCara)" />
          <ellipse cx={9.5} cy={6} rx={7.5} ry={4.2} fill="url(#waBrillo)" transform="rotate(-18 9.5 6)" />
          <g transform="translate(12 12) scale(1.18) translate(-12 -12)">
            <path d={WA_TEL} fill="#fff" filter="url(#waSombraTel)" />
          </g>
        </svg>
      </div>
    </div>
  );
};

// Meme recortado (vídeo con transparencia) que entra con rebote y sale encogiendo; sin taparle la cara a nadie
export const MemeRecorte: React.FC<{ src: string; t0: number; dur: number; x: number; y: number; ancho: number; alto: number; giro?: number; bucle?: boolean }> = ({ src, t0, dur, x, y, ancho, alto, giro = 0, bucle = false }) => {
  const { t, fps } = useT();
  if (t < t0 - 0.02 || t > t0 + dur + 0.02) return null;
  const k = t - t0;
  const sp = spring({ frame: Math.round(k * fps), fps, config: { damping: 11, stiffness: 200, mass: 0.6 } });
  const s = interpolate(k, [dur - 0.18, dur], [0, 1], { ...cl, easing: eInOut });
  return (
    <div
      style={{
        position: "absolute", left: x - ancho / 2, top: y, width: ancho, height: alto,
        scale: String(sp * (1 - 0.6 * s)), opacity: 1 - s, rotate: `${giro + (1 - sp) * -8}deg`, transformOrigin: "50% 100%",
        filter: "drop-shadow(0 18px 28px rgba(20,8,40,.35))",
      }}
    >
      <Sequence from={Math.round(t0 * fps)} durationInFrames={Math.round(dur * fps) + 2} layout="none">
        <Video src={staticFile(src)} muted loop={bucle} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      </Sequence>
    </div>
  );
};

// Fichas de producto en fila (foto grande + nombre), entran una a una al nombrarlas
export type FichaMG = { texto: string; t: number; img: string };
export const FichasProducto: React.FC<{ items: FichaMG[]; y: number; ancho?: number; alto?: number; hueco?: number }> = ({ items, y, ancho = 310, alto = 470, hueco = 24 }) => {
  const { t, fps } = useT();
  const total = items.length * ancho + (items.length - 1) * hueco;
  const x0 = (1080 - total) / 2;
  return (
    <>
      {items.map((it, i) => {
        if (t < it.t - 0.05) return null;
        const sp = spring({ frame: Math.round((t - it.t) * fps), fps, config: { damping: 13, stiffness: 190, mass: 0.7 } });
        const b = interpolate(t, [it.t - 0.05, it.t + 0.2], [8, 0], cl);
        return (
          <div
            key={i}
            style={{
              position: "absolute", left: x0 + i * (ancho + hueco), top: y, width: ancho, height: alto, borderRadius: 36, background: "#fff",
              boxShadow: "0 22px 46px rgba(46,28,82,.16), inset 0 0 0 3px rgba(179,139,255,.35)", overflow: "hidden",
              opacity: Math.min(1, sp * 1.4), translate: `0px ${((1 - sp) * 70).toFixed(1)}px`, scale: String(0.9 + 0.1 * sp), filter: b > 0.05 ? `blur(${b.toFixed(2)}px)` : undefined,
            }}
          >
            <div style={{ position: "absolute", left: 18, right: 18, top: 18, height: alto - 150 }}>
              <Img src={staticFile(it.img)} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
            </div>
            <div style={{ position: "absolute", left: 16, right: 16, bottom: 22, height: 104, display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", fontFamily: HN, fontWeight: 700, fontSize: 40, letterSpacing: "-0.03em", lineHeight: 1.02, color: MORADO }}>
              {it.texto}
            </div>
          </div>
        );
      })}
    </>
  );
};

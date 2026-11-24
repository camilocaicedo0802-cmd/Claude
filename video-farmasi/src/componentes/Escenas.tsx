import { Video } from "@remotion/media";
import { evolvePath } from "@remotion/paths";
import React from "react";
import { AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, F } from "../estilo";
import { ajustar, cap } from "../medida";
import { Escena } from "../plan";
import { PALABRAS, clamp, eInOut, eOut, f, inicio, limpio } from "../util";

// ---------- Envoltura: corte con desenfoque (§6): entra 20→0 px y escala 1,10→1 en 14 f; sale 0→16 px en 6 f ----------
export const EnvolturaEscena: React.FC<{ children: React.ReactNode; entrada?: boolean }> = ({ children, entrada = true }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const pi = entrada ? interpolate(frame, [0, 14], [0, 1], { ...clamp, easing: eOut }) : 1;
  const po = interpolate(frame, [durationInFrames - 6, durationInFrames], [0, 1], clamp);
  const blur = (1 - pi) * 20 + po * 16;
  return <AbsoluteFill style={{ scale: String(1.1 - 0.1 * pi + po * 0.06), filter: blur > 0.05 ? `blur(${blur}px)` : undefined, backgroundColor: "#000" }}>{children}</AbsoluteFill>;
};

// Relativo a la escena: fotograma de una palabra
const rel = (i: number, desde: number) => f(inicio(i)) - f(desde);

// ---------- B-roll a pantalla completa con Ken Burns ----------
export const BRoll: React.FC<{ e: Extract<Escena, { tipo: "broll" }> }> = ({ e }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();
  const kb = e.kb ?? [1.15, 1];
  const s = interpolate(frame, [0, durationInFrames], kb, clamp);
  return (
    <EnvolturaEscena>
      <AbsoluteFill style={{ scale: String(s) }}>
        <Video src={staticFile(e.src)} trimBefore={Math.round(e.trim * fps)} muted objectFit="cover" style={{ width: "100%", height: "100%", filter: "contrast(1.1) saturate(1.2)" }} />
      </AbsoluteFill>
    </EnvolturaEscena>
  );
};

// ---------- Montaje rápido de comidas ("cualquier cosa que coma"): cortes secos con punch ----------
export const Montaje: React.FC<{ e: Extract<Escena, { tipo: "montaje" }> }> = ({ e }) => {
  const { durationInFrames, fps } = useVideoConfig();
  const n = e.clips.length;
  const cada = Math.ceil(durationInFrames / n);
  return (
    <EnvolturaEscena>
      {e.clips.map((c, k) => (
        <Sequence key={k} from={k * cada} durationInFrames={k === n - 1 ? durationInFrames - k * cada : cada}>
          <ClipPunch src={c.src} trim={c.trim} fps={fps} />
        </Sequence>
      ))}
    </EnvolturaEscena>
  );
};
const ClipPunch: React.FC<{ src: string; trim: number; fps: number }> = ({ src, trim, fps }) => {
  const frame = useCurrentFrame();
  const s = interpolate(frame, [0, 8], [1.14, 1.02], { ...clamp, easing: eOut });
  return (
    <AbsoluteFill style={{ scale: String(s) }}>
      <Video src={staticFile(src)} trimBefore={Math.round(trim * fps)} muted objectFit="cover" style={{ width: "100%", height: "100%", filter: "contrast(1.08) saturate(1.25) brightness(1.08)" }} />
    </AbsoluteFill>
  );
};

// ---------- Fondo de los motion graphics: blanco con esquinas azul cielo (§4.1) ----------
export const FondoMG: React.FC = () => {
  const frame = useCurrentFrame();
  const d = Math.sin(frame / 50) * 4;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at ${100 + d}% ${0 - d}%, ${C.fondoSupDer} 0%, rgba(139,206,250,0) 58%), radial-gradient(circle at ${0 - d}% ${100 + d}%, ${C.fondoInfIzq} 0%, rgba(131,195,235,0) 58%), linear-gradient(135deg, ${C.fondoBlanco}, #F3F9FC)`,
      }}
    />
  );
};

const PequenaMG: React.FC<{ i: number; desde: number; size?: number }> = ({ i, desde, size = 54 }) => {
  const frame = useCurrentFrame();
  const t = rel(i, desde) - 4;
  const p = interpolate(frame, [t, t + 8], [0, 1], { ...clamp, easing: eOut });
  return <span style={{ display: "inline-block", fontFamily: F.sans, fontWeight: 400, fontSize: size, color: C.grisMG, letterSpacing: "-0.02em", marginRight: "0.24em", opacity: p, filter: `blur(${(1 - p) * 6}px)`, translate: `0px ${(1 - p) * -10}px` }}>{limpio(PALABRAS[i].text)}</span>;
};

// Titular condensado cian con degradado, letra a letra (§3.5)
export const TitularMG: React.FC<{ texto: string; desde: number; centroY: number; anchoMax?: number; maxSize?: number; salida?: number }> = ({ texto, desde, centroY, anchoMax = 900, maxSize = 270, salida }) => {
  const frame = useCurrentFrame();
  const size = ajustar(texto, "cond", anchoMax, maxSize, 0.005);
  const ps = salida !== undefined ? interpolate(frame, [salida - 6, salida], [1, 0], clamp) : 1;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: centroY - (size * cap("cond")) / 2 - size * 0.16, textAlign: "center", whiteSpace: "nowrap", opacity: ps, filter: `drop-shadow(0 8px 18px rgba(30,120,180,0.25))${ps < 1 ? ` blur(${(1 - ps) * 8}px)` : ""}` }}>
      {[...texto].map((c, k) => {
        const d = desde + k * 1.5;
        const p = interpolate(frame, [d, d + 10], [0, 1], { ...clamp, easing: eOut });
        return (
          <span key={k} style={{ display: "inline-block", fontFamily: F.cond, fontSize: size, lineHeight: 1, letterSpacing: "0.005em", backgroundImage: `linear-gradient(180deg, ${C.cianMGArriba} 10%, ${C.cianMGAbajo} 95%)`, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", opacity: p, filter: `blur(${(1 - p) * 14}px)`, translate: `0px ${(1 - p) * 30}px`, whiteSpace: "pre" }}>
            {c}
          </span>
        );
      })}
    </div>
  );
};

// ---------- MG 1: "a él le encanta INVESTIGAR TODO" (buscador tecleando + vídeo en tarjeta) ----------
export const BUSQUEDA = "sidra de manzana y glucosa";
export const tecleoBusqueda = (desdeEscena: number) => ({ desde: 14, paso: 2.3, base: f(desdeEscena) });
export const MGInvestigar: React.FC<{ desde: number }> = ({ desde }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pc = interpolate(frame, [4, 24], [0, 1], { ...clamp, easing: eOut });
  const tb = tecleoBusqueda(desde);
  const nLetras = Math.max(0, Math.min(BUSQUEDA.length, Math.floor((frame - tb.desde) / tb.paso) + 1));
  return (
    <EnvolturaEscena>
      <FondoMG />
      <div style={{ position: "absolute", top: 235, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        {[36, 37, 38, 39].map((i) => <PequenaMG key={i} i={i} desde={desde} />)}
      </div>
      <TitularMG texto="INVESTIGAR" desde={rel(40, desde) - 20} centroY={430} />
      <div style={{ position: "absolute", left: 60, top: 600, width: 960, height: 540, borderRadius: 40, overflow: "hidden", border: "6px solid rgba(255,255,255,0.85)", boxShadow: "0 30px 70px rgba(30,90,150,0.35)", opacity: pc, scale: String(0.9 + 0.1 * pc), rotate: `${(1 - pc) * -4}deg` }}>
        <Video src={staticFile("stock/mk_5518.mp4")} trimBefore={Math.round(2 * fps)} muted objectFit="cover" style={{ width: "100%", height: "100%", scale: String(1 + frame / 900) }} />
      </div>
      <div style={{ position: "absolute", left: 90, top: 1215, width: 900, height: 124, borderRadius: 62, background: "rgba(255,255,255,0.82)", border: "2px solid #fff", boxShadow: "0 18px 40px rgba(30,90,150,0.22)", display: "flex", alignItems: "center", gap: 18, paddingLeft: 26, opacity: interpolate(frame, [8, 18], [0, 1], clamp), translate: `0px ${interpolate(frame, [8, 22], [40, 0], { ...clamp, easing: eOut })}px` }}>
        <Img src={staticFile("iconos/lupa.png")} style={{ width: 74, height: 74 }} />
        <span style={{ fontFamily: F.sans, fontWeight: 500, fontSize: 46, color: C.grisMG }}>{BUSQUEDA.slice(0, nLetras)}</span>
        <span style={{ width: 4, height: 54, background: C.cian, opacity: Math.floor(frame / 15) % 2 ? 0 : 1, marginLeft: -12 }} />
      </div>
      <TitularMG texto="TODO" desde={rel(41, desde) - 14} centroY={1540} maxSize={300} />
    </EnvolturaEscena>
  );
};

// ---------- MG 2: reloj de arena (dibujado) "y demora MUCHO TIEMPO estando AHÍ" ----------
const RelojArena: React.FC<{ progreso: number }> = ({ progreso }) => {
  const arribaH = 210 * (1 - progreso * 0.55);
  const abajoH = 60 + 160 * progreso;
  return (
    <svg width={520} height={800} viewBox="0 0 520 800">
      <defs>
        <linearGradient id="madera" x1="0" x2="1"><stop offset="0" stopColor="#6B3E1F" /><stop offset="0.5" stopColor="#C98B4B" /><stop offset="1" stopColor="#5A3218" /></linearGradient>
        <linearGradient id="vidrio" x1="0" x2="1"><stop offset="0" stopColor="rgba(255,255,255,0.55)" /><stop offset="0.35" stopColor="rgba(200,235,255,0.18)" /><stop offset="1" stopColor="rgba(255,255,255,0.4)" /></linearGradient>
        <linearGradient id="arena" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#F4E2C0" /><stop offset="1" stopColor="#D9BE8C" /></linearGradient>
        <clipPath id="bulboA"><path d="M120 120 C120 260 250 330 255 400 L265 400 C270 330 400 260 400 120 Z" /></clipPath>
        <clipPath id="bulboB"><path d="M255 400 C250 470 120 540 120 680 L400 680 C400 540 270 470 265 400 Z" /></clipPath>
      </defs>
      <rect x={70} y={80} width={380} height={44} rx={16} fill="url(#madera)" />
      <rect x={70} y={676} width={380} height={44} rx={16} fill="url(#madera)" />
      {[95, 415].map((x) => <rect key={x} x={x - 9} y={110} width={18} height={580} rx={9} fill="url(#madera)" />)}
      <g clipPath="url(#bulboA)"><rect x={100} y={400 - arribaH} width={320} height={arribaH} fill="url(#arena)" /></g>
      <g clipPath="url(#bulboB)"><path d={`M120 680 L120 ${680 - abajoH * 0.6} Q260 ${680 - abajoH - 30} 400 ${680 - abajoH * 0.6} L400 680 Z`} fill="url(#arena)" /></g>
      <rect x={258} y={400} width={4} height={680 - abajoH - 400} fill="#E8D3A8" />
      <path d="M120 120 C120 260 250 330 255 400 C250 470 120 540 120 680 L400 680 C400 540 270 470 265 400 C270 330 400 260 400 120 Z" fill="url(#vidrio)" stroke="rgba(255,255,255,0.9)" strokeWidth={4} />
      <path d="M150 150 C150 240 200 290 228 330" stroke="rgba(255,255,255,0.8)" strokeWidth={8} strokeLinecap="round" fill="none" />
    </svg>
  );
};
export const MGReloj: React.FC<{ desde: number }> = ({ desde }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const pe = interpolate(frame, [0, 18], [0, 1], { ...clamp, easing: eOut });
  const giro = (1 - pe) * -24 + Math.sin(frame / 28) * 7;
  const desliza = (i: number, dir: number) => {
    const t = rel(i, desde) - 6;
    const p = interpolate(frame, [t, t + 10], [0, 1], { ...clamp, easing: eOut });
    return { opacity: p, translate: `${(1 - p) * 320 * dir}px 0px`, filter: `blur(${(1 - p) * 10}px)` };
  };
  return (
    <EnvolturaEscena>
      <FondoMG />
      <div style={{ position: "absolute", left: 280, top: 600, rotate: `${giro}deg`, scale: String((0.85 + 0.15 * pe) * 1.3), opacity: pe, filter: `drop-shadow(0 40px 40px rgba(30,80,130,0.3)) blur(${(1 - pe) * 14}px)` }}>
        <RelojArena progreso={frame / durationInFrames} />
      </div>
      <div style={{ position: "absolute", left: 80, top: 500 }}>{[59, 60].map((i) => <PequenaMG key={i} i={i} desde={desde} />)}</div>
      <div style={{ position: "absolute", left: 70, top: 560, fontFamily: F.sans, fontStyle: "italic", fontWeight: 800, fontSize: 112, color: C.cian, lineHeight: 1, letterSpacing: "-0.02em", textShadow: "0 8px 20px rgba(30,120,180,0.25)", ...desliza(61, -1) }}>mucho tiempo</div>
      <div style={{ position: "absolute", right: 80, top: 1350 }}>{[63].map((i) => <PequenaMG key={i} i={i} desde={desde} />)}</div>
      <div style={{ position: "absolute", right: 80, top: 1410, fontFamily: F.sans, fontStyle: "italic", fontWeight: 800, fontSize: 132, color: C.cian, lineHeight: 1, textShadow: "0 8px 20px rgba(30,120,180,0.25)", ...desliza(64, 1) }}>ahí</div>
    </EnvolturaEscena>
  );
};

// ---------- MG 3: gráfica "a que esa GLUCOSA no quede ARRIBA, sino que BAJE" ----------
export const MGGrafica: React.FC<{ desde: number }> = ({ desde }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const pc = interpolate(frame, [6, 24], [0, 1], { ...clamp, easing: eOut });
  const subida = interpolate(frame, [22, rel(79, desde)], [0, 1], { ...clamp, easing: eInOut });
  const meseta = interpolate(frame, [rel(79, desde), rel(84, desde) + 10], [0, 1], { ...clamp, easing: eInOut });
  const bajada = interpolate(frame, [rel(87, desde) - 16, rel(87, desde) + 26], [0, 1], { ...clamp, easing: eInOut });
  const ejes = interpolate(frame, [8, 30], [0, 1], { ...clamp, easing: eOut });
  const subeGris = "M 70 600 C 160 600, 200 420, 300 200";
  const mesetaGris = "M 300 200 C 360 150, 600 170, 720 230 S 860 380, 880 420";
  const subeCian = "M 70 600 C 160 600, 200 440, 290 260";
  const bajaCian = "M 290 260 C 340 200, 380 420, 460 540 S 640 600, 880 600";
  const ev = (p: number, d: string) => evolvePath(p, d);
  const e1 = ev(subida, subeGris), e2 = ev(meseta, mesetaGris), e3 = ev(subida, subeCian), e4 = ev(bajada, bajaCian);
  const cambio = rel(85, desde);
  const zoom = interpolate(frame, [0, durationInFrames], [1, 1.07]);
  const leyenda = interpolate(frame, [30, 44], [0, 1], clamp);
  const flecha = (t: number) => interpolate(frame, [t, t + 12], [0, 1], clamp);
  return (
    <EnvolturaEscena>
      <FondoMG />
      <AbsoluteFill style={{ scale: String(zoom) }}>
        <div style={{ position: "absolute", top: 210, left: 0, right: 0, display: "flex", justifyContent: "center" }}>{[75, 76, 77].map((i) => <PequenaMG key={i} i={i} desde={desde} />)}</div>
        <TitularMG texto="GLUCOSA" desde={rel(78, desde) - 20} centroY={400} maxSize={250} />
        <div style={{ position: "absolute", left: 70, top: 560, width: 940, height: 740, borderRadius: 40, background: "rgba(255,255,255,0.7)", border: "2px solid #fff", boxShadow: "0 30px 70px rgba(30,100,160,0.22)", opacity: pc, scale: String(0.9 + 0.1 * pc) }}>
          <svg width={940} height={740} style={{ position: "absolute", inset: 0 }}>
            <line x1={70} y1={640} x2={70 + 820 * ejes} y2={640} stroke="#9FB3C6" strokeWidth={3} />
            <line x1={70} y1={640} x2={70} y2={640 - 560 * ejes} stroke="#9FB3C6" strokeWidth={3} />
            <path d={subeGris} fill="none" stroke="#A5B2C0" strokeWidth={7} strokeDasharray={e1.strokeDasharray} strokeDashoffset={e1.strokeDashoffset} strokeLinecap="round" />
            <path d={mesetaGris} fill="none" stroke="#A5B2C0" strokeWidth={7} strokeDasharray={e2.strokeDasharray} strokeDashoffset={e2.strokeDashoffset} strokeLinecap="round" />
            <path d={subeCian} fill="none" stroke={C.cian} strokeWidth={9} strokeDasharray={e3.strokeDasharray} strokeDashoffset={e3.strokeDashoffset} strokeLinecap="round" style={{ filter: "drop-shadow(0 0 10px rgba(31,173,217,0.7))" }} />
            <path d={bajaCian} fill="none" stroke={C.cian} strokeWidth={9} strokeDasharray={e4.strokeDasharray} strokeDashoffset={e4.strokeDashoffset} strokeLinecap="round" style={{ filter: "drop-shadow(0 0 10px rgba(31,173,217,0.7))" }} />
          </svg>
          <div style={{ position: "absolute", left: 40, top: 20, fontFamily: F.sans, fontWeight: 600, fontSize: 32, color: "#5B7187" }}>Glucosa</div>
          <div style={{ position: "absolute", right: 40, top: 652, fontFamily: F.sans, fontWeight: 600, fontSize: 30, color: "#5B7187" }}>Tiempo</div>
          <div style={{ position: "absolute", left: 90, top: 680, display: "flex", gap: 34, opacity: leyenda, fontFamily: F.sans, fontWeight: 600, fontSize: 30 }}>
            <span style={{ color: "#8C9AAA" }}>— — sin</span>
            <span style={{ color: C.cian }}>━━ con sidra de manzana</span>
          </div>
          <div style={{ position: "absolute", right: 34, top: 22, fontFamily: F.sans, fontSize: 22, color: "#8FA2B4" }}>Gráfico ilustrativo</div>
          <Img src={staticFile("iconos/flecha_arriba.png")} style={{ position: "absolute", left: 560, top: 30, width: 120, height: 120, opacity: flecha(rel(84, desde) - 6), scale: String(interpolate(flecha(rel(84, desde) - 6), [0, 0.6, 1], [0, 1.2, 1])) }} />
          <Img src={staticFile("iconos/flecha_abajo.png")} style={{ position: "absolute", left: 430, top: 300, width: 120, height: 120, opacity: flecha(rel(87, desde) - 6), scale: String(interpolate(flecha(rel(87, desde) - 6), [0, 0.6, 1], [0, 1.2, 1])) }} />
        </div>
        <div style={{ position: "absolute", top: 1370, left: 60, right: 60, display: "flex", flexWrap: "wrap", justifyContent: "center", opacity: interpolate(frame, [cambio - 6, cambio], [1, 0], clamp) }}>
          {[79, 80, 81, 82, 83].map((i) => <PequenaMG key={i} i={i} desde={desde} />)}
        </div>
        <TitularMG texto="ARRIBA" desde={rel(84, desde) - 18} centroY={1560} maxSize={250} salida={cambio} />
        <div style={{ position: "absolute", top: 1370, left: 60, right: 60, display: "flex", justifyContent: "center" }}>{[85, 86].map((i) => <PequenaMG key={i} i={i} desde={desde} />)}</div>
        <TitularMG texto="BAJE" desde={rel(87, desde) - 18} centroY={1560} maxSize={280} />
      </AbsoluteFill>
    </EnvolturaEscena>
  );
};

// ---------- MG 4: cierre con el producto ----------
export const MGCierre: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pc = interpolate(frame, [6, 28], [0, 1], { ...clamp, easing: eOut });
  const pp = interpolate(frame, [26, 38], [0, 1], { ...clamp, easing: eOut });
  const pf = interpolate(frame, [4, 16], [0, 1], clamp);
  return (
    <EnvolturaEscena>
      <FondoMG />
      <div style={{ position: "absolute", top: 190, left: 0, right: 0, textAlign: "center", fontFamily: F.sans, fontWeight: 700, fontSize: 40, letterSpacing: "0.4em", color: C.grisMG, opacity: pf, paddingLeft: "0.4em" }}>FARMASI</div>
      <TitularMG texto="NUTRIPLUS GUMMIES" desde={8} centroY={360} anchoMax={940} maxSize={240} />
      <div style={{ position: "absolute", left: 270, top: 520, width: 540, height: 960, borderRadius: 44, overflow: "hidden", border: "6px solid rgba(255,255,255,0.9)", boxShadow: "0 40px 80px rgba(30,90,150,0.35)", opacity: pc, scale: String(0.88 + 0.12 * pc), rotate: `${(1 - pc) * 6 - 2}deg` }}>
        <Video src={staticFile("proxy/apoyo_3.mp4")} trimBefore={Math.round(5.6 * fps)} muted objectFit="cover" style={{ width: "100%", height: "100%", scale: String(1.05 + frame / 1200), filter: "contrast(1.06) saturate(1.15) brightness(1.06)" }} />
      </div>
      <Img src={staticFile("iconos/manzana.png")} style={{ position: "absolute", left: 120, top: 1240, width: 190, height: 190, scale: String(interpolate(pp, [0, 0.6, 1], [0, 1.2, 1])), rotate: `${Math.sin(frame / 20) * 8}deg`, filter: "drop-shadow(0 20px 24px rgba(0,0,0,0.25))" }} />
      <Img src={staticFile("iconos/brillos.png")} style={{ position: "absolute", right: 150, top: 560, width: 150, height: 150, scale: String(interpolate(pp, [0, 0.6, 1], [0, 1.2, 1])), rotate: `${Math.sin(frame / 16) * 10}deg` }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 1560, display: "flex", justifyContent: "center", opacity: pp }}>
        <div style={{ background: C.pildora, borderRadius: 999, padding: "12px 40px 16px", rotate: "-3deg", scale: String(0.7 + 0.3 * pp), fontFamily: F.sans, fontWeight: 600, fontSize: 56, color: "#fff", boxShadow: "0 12px 30px rgba(0,60,110,0.3)" }}>Gomitas de sidra de manzana</div>
      </div>
    </EnvolturaEscena>
  );
};


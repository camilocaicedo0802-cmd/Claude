import { Video } from "@remotion/media";
import { evolvePath } from "@remotion/paths";
import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, F } from "../estilo";
import { ajustar, cap } from "../medida";
import { DATOS } from "../plan";
import { PALABRAS, clamp, eInOut, eOut, f, inicio, limpio } from "../util";

// Fotograma de una palabra relativo al inicio de la escena
export const rel = (i: number, desde: number) => f(inicio(i)) - f(desde);

// Fondo de los motion graphics de la referencia: blanco con esquinas azul cielo (estilo.md 4.1)
export const FondoMG: React.FC = () => {
  const frame = useCurrentFrame();
  const d = Math.sin(frame / 50) * 4;
  return (
    <AbsoluteFill style={{ background: `radial-gradient(circle at ${100 + d}% ${0 - d}%, ${C.fondoSupDer} 0%, rgba(220,203,255,0) 58%), radial-gradient(circle at ${0 - d}% ${100 + d}%, ${C.fondoInfIzq} 0%, rgba(207,189,247,0) 58%), linear-gradient(135deg, ${C.fondoBlanco}, #F7F2FF)` }} />
  );
};

// Entrada de escena MG: desenfoque 18→0 y escala 1,08→1 en 12 f
const Entrada: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, 12], [0, 1], { ...clamp, easing: eOut });
  return <AbsoluteFill style={{ scale: String(1.08 - 0.08 * p), filter: p < 1 ? `blur(${(1 - p) * 18}px)` : undefined }}>{children}</AbsoluteFill>;
};

const PequenaMG: React.FC<{ i: number; desde: number; size?: number }> = ({ i, desde, size = 56 }) => {
  const frame = useCurrentFrame();
  const t = rel(i, desde) - 4;
  const p = interpolate(frame, [t, t + 8], [0, 1], { ...clamp, easing: eOut });
  return <span style={{ display: "inline-block", fontFamily: F.sans, fontWeight: 300, fontSize: size, color: C.grisMG, letterSpacing: "-0.02em", marginRight: "0.24em", opacity: p, filter: `blur(${(1 - p) * 6}px)`, translate: `0px ${(1 - p) * -10}px` }}>{limpio(PALABRAS[i].text)}</span>;
};

// Titular condensado lila, letra a letra (3.5)
export const TitularMG: React.FC<{ texto: string; desde: number; centroY: number; anchoMax?: number; maxSize?: number; salida?: number }> = ({ texto, desde, centroY, anchoMax = 900, maxSize = 260, salida }) => {
  const frame = useCurrentFrame();
  const size = ajustar(texto, "cond", anchoMax, maxSize, 0.005);
  const ps = salida !== undefined ? interpolate(frame, [salida - 6, salida], [1, 0], clamp) : 1;
  if (ps <= 0) return null;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: centroY - (size * cap("cond")) / 2 - size * 0.16, textAlign: "center", whiteSpace: "nowrap", opacity: ps, filter: `drop-shadow(0 8px 18px rgba(110,60,190,0.25))` }}>
      {[...texto].map((c, k) => {
        const d = desde + k * 1.5;
        const p = interpolate(frame, [d, d + 10], [0, 1], { ...clamp, easing: eOut });
        return (
          <span key={k} style={{ display: "inline-block", fontFamily: F.cond, fontWeight: 300, fontSize: size, lineHeight: 1, letterSpacing: "0.01em", backgroundImage: `linear-gradient(180deg, ${C.mgArriba} 10%, ${C.mgAbajo} 95%)`, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", opacity: p, filter: `blur(${(1 - p) * 14}px)`, translate: `0px ${(1 - p) * 30}px`, whiteSpace: "pre" }}>
            {c}
          </span>
        );
      })}
    </div>
  );
};

const Nota: React.FC<{ texto: string; top: number; desde: number }> = ({ texto, top, desde }) => {
  const frame = useCurrentFrame();
  return <div style={{ position: "absolute", left: 80, right: 80, top, textAlign: "center", fontFamily: F.sans, fontWeight: 300, fontSize: 25, lineHeight: 1.3, color: "#6E6385", opacity: interpolate(frame, [desde, desde + 10], [0, 1], clamp) }}>{texto}</div>;
};

// ---------- MG: "a que esa GLUCOSA" (molécula 3D + dato) ----------
export const MGGlucosa: React.FC<{ desde: number }> = ({ desde }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pc = interpolate(frame, [4, 22], [0, 1], { ...clamp, easing: eOut });
  const pd = interpolate(frame, [24, 36], [0, 1], { ...clamp, easing: eOut });
  return (
    <Entrada>
      <FondoMG />
      <div style={{ position: "absolute", top: 250, left: 0, right: 0, display: "flex", justifyContent: "center" }}>{[75, 76, 77].map((i) => <PequenaMG key={i} i={i} desde={desde} />)}</div>
      <TitularMG texto="GLUCOSA" desde={rel(78, desde) - 20} centroY={460} maxSize={250} />
      <div style={{ position: "absolute", left: 90, top: 640, width: 900, height: 506, borderRadius: 40, overflow: "hidden", background: "#fff", border: "6px solid rgba(255,255,255,0.95)", boxShadow: "0 30px 70px rgba(90,50,160,0.25)", opacity: pc, scale: String(0.9 + 0.1 * pc), rotate: `${(1 - pc) * -4}deg` }}>
        <Video src={staticFile("stock/mk_3768.mp4")} trimBefore={Math.round(1 * fps)} muted objectFit="cover" style={{ width: "100%", height: "100%", scale: String(1.05 + frame / 1500) }} />
      </div>
      <div style={{ position: "absolute", left: 110, right: 110, top: 1210, display: "flex", flexDirection: "column", alignItems: "center", gap: 14, opacity: pd, translate: `0px ${(1 - pd) * 30}px` }}>
        <div style={{ background: C.pildora, color: "#fff", borderRadius: 999, padding: "8px 34px 12px", fontFamily: F.sans, fontWeight: 500, fontSize: 56, boxShadow: "0 10px 30px rgba(80,40,140,0.3)" }}>C₆H₁₂O₆</div>
        <div style={{ fontFamily: F.sans, fontWeight: 400, fontSize: 46, color: C.grisMG, textAlign: "center", lineHeight: 1.2 }}>el azúcar que tu cuerpo usa como energía</div>
      </div>
    </Entrada>
  );
};

// ---------- MG: gráfica 0–3 h "no quede ARRIBA, sino que BAJE" ----------
const X = (h: number) => 80 + h * 270; // 0 h → 80 px · 3 h → 890 px
export const MGGrafica: React.FC<{ desde: number }> = ({ desde }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const pc = interpolate(frame, [2, 18], [0, 1], { ...clamp, easing: eOut });
  const ejes = interpolate(frame, [4, 22], [0, 1], { ...clamp, easing: eOut });
  const cambio = rel(85, desde);
  const subida = interpolate(frame, [8, 44], [0, 1], { ...clamp, easing: eInOut });
  const meseta = interpolate(frame, [44, rel(84, desde) + 12], [0, 1], { ...clamp, easing: eInOut });
  const bajada = interpolate(frame, [rel(87, desde) - 14, rel(87, desde) + 28], [0, 1], { ...clamp, easing: eInOut });
  // Curvas (y: 600 = nivel normal, 170 = muy alto)
  const subeSin = `M ${X(0)} 600 C ${X(0.4)} 600, ${X(0.55)} 330, ${X(1)} 190`;
  const mesetaSin = `M ${X(1)} 190 C ${X(1.4)} 150, ${X(1.9)} 200, ${X(2.3)} 330 S ${X(2.8)} 560, ${X(3)} 585`;
  const subeCon = `M ${X(0)} 600 C ${X(0.4)} 600, ${X(0.55)} 380, ${X(0.9)} 300`;
  const bajaCon = `M ${X(0.9)} 300 C ${X(1.15)} 250, ${X(1.3)} 470, ${X(1.6)} 560 S ${X(2.2)} 600, ${X(3)} 600`;
  const ev = (p: number, d: string) => evolvePath(p, d);
  const e1 = ev(subida, subeSin), e2 = ev(meseta, mesetaSin), e3 = ev(subida, subeCon), e4 = ev(bajada, bajaCon);
  const pChip = interpolate(frame, [cambio + 4, cambio + 16], [0, 1], { ...clamp, easing: eOut });
  const pop = (t: number) => interpolate(frame, [t, t + 12], [0, 1], clamp);
  const zoom = interpolate(frame, [0, durationInFrames], [1, 1.05]);
  return (
    <Entrada>
      <FondoMG />
      <AbsoluteFill style={{ scale: String(zoom) }}>
        <div style={{ position: "absolute", top: 200, left: 60, right: 60, display: "flex", flexWrap: "wrap", justifyContent: "center", opacity: interpolate(frame, [cambio - 6, cambio], [1, 0], clamp) }}>{[79, 80, 81, 82, 83].map((i) => <PequenaMG key={i} i={i} desde={desde} />)}</div>
        <TitularMG texto="ARRIBA" desde={rel(84, desde) - 18} centroY={400} maxSize={240} salida={cambio} />
        <div style={{ position: "absolute", top: 200, left: 60, right: 60, display: "flex", justifyContent: "center" }}>{[85, 86].map((i) => <PequenaMG key={i} i={i} desde={desde} />)}</div>
        <TitularMG texto="BAJE" desde={rel(87, desde) - 18} centroY={400} maxSize={260} />
        <div style={{ position: "absolute", left: 60, top: 560, width: 960, height: 760, borderRadius: 40, background: "rgba(255,255,255,0.75)", border: "2px solid #fff", boxShadow: "0 30px 70px rgba(90,50,160,0.22)", opacity: pc, scale: String(0.92 + 0.08 * pc) }}>
          <div style={{ position: "absolute", left: 40, top: 26, fontFamily: F.sans, fontWeight: 500, fontSize: 38, color: "#4A3D66" }}>Glucosa después de comer</div>
          <svg width={960} height={760} style={{ position: "absolute", inset: 0 }}>
            <line x1={X(0)} y1={640} x2={X(0) + 820 * ejes} y2={640} stroke="#B7A9D1" strokeWidth={3} />
            <line x1={X(0)} y1={640} x2={X(0)} y2={640 - 520 * ejes} stroke="#B7A9D1" strokeWidth={3} />
            <line x1={X(0)} y1={600} x2={X(3)} y2={600} stroke="rgba(155,107,242,0.25)" strokeWidth={2} strokeDasharray="8 10" />
            <path d={subeSin} fill="none" stroke="#A5B2C0" strokeWidth={7} strokeLinecap="round" strokeDasharray={e1.strokeDasharray} strokeDashoffset={e1.strokeDashoffset} />
            <path d={mesetaSin} fill="none" stroke="#A5B2C0" strokeWidth={7} strokeLinecap="round" strokeDasharray={e2.strokeDasharray} strokeDashoffset={e2.strokeDashoffset} />
            <path d={subeCon} fill="none" stroke={C.acento} strokeWidth={9} strokeLinecap="round" strokeDasharray={e3.strokeDasharray} strokeDashoffset={e3.strokeDashoffset} style={{ filter: "drop-shadow(0 0 10px rgba(155,107,242,0.7))" }} />
            <path d={bajaCon} fill="none" stroke={C.acento} strokeWidth={9} strokeLinecap="round" strokeDasharray={e4.strokeDasharray} strokeDashoffset={e4.strokeDashoffset} style={{ filter: "drop-shadow(0 0 10px rgba(155,107,242,0.7))" }} />
          </svg>
          {[0, 1, 2, 3].map((h) => (
            <div key={h} style={{ position: "absolute", left: X(h) - 30, width: 60, top: 652, textAlign: "center", fontFamily: F.sans, fontWeight: 500, fontSize: 30, color: "#6B5E86", opacity: ejes }}>{h} h</div>
          ))}
          <div style={{ position: "absolute", left: X(3) - 160, top: 560, fontFamily: F.sans, fontWeight: 500, fontSize: 24, color: "#8E6CC9", opacity: ejes }}>nivel normal</div>
          <div style={{ position: "absolute", left: 60, top: 704, display: "flex", gap: 36, fontFamily: F.sans, fontWeight: 500, fontSize: 30, opacity: interpolate(frame, [20, 32], [0, 1], clamp) }}>
            <span style={{ color: "#8C9AAA" }}>— — sin</span>
            <span style={{ color: C.acento }}>━━ con vinagre de manzana</span>
          </div>
          <Img src={staticFile("iconos/flecha_arriba.png")} style={{ filter: "hue-rotate(48deg) saturate(1.05)", position: "absolute", left: X(1.55), top: 70, width: 110, height: 110, opacity: pop(rel(84, desde) - 6), scale: String(interpolate(pop(rel(84, desde) - 6), [0, 0.6, 1], [0, 1.2, 1])) }} />
          <Img src={staticFile("iconos/flecha_abajo.png")} style={{ filter: "hue-rotate(48deg) saturate(1.05)", position: "absolute", left: X(1.25) - 20, top: 330, width: 110, height: 110, opacity: pop(rel(87, desde) - 6), scale: String(interpolate(pop(rel(87, desde) - 6), [0, 0.6, 1], [0, 1.2, 1])) }} />
        </div>
        <div style={{ position: "absolute", left: 90, right: 90, top: 1365, display: "flex", alignItems: "center", gap: 20, background: "rgba(255,255,255,0.85)", border: `3px solid ${C.acentoClaro}`, borderRadius: 30, padding: "20px 28px", boxShadow: "0 16px 40px rgba(90,50,160,0.2)", opacity: pChip, translate: `0px ${(1 - pChip) * 40}px` }}>
          <Img src={staticFile("iconos/manzana.png")} style={{ width: 90, height: 90 }} />
          <div style={{ fontFamily: F.sans, fontWeight: 500, fontSize: 40, lineHeight: 1.2, color: C.grisMG }}>{DATOS.estudio}</div>
        </div>
        <Nota texto={DATOS.notaEstudio} top={1580} desde={cambio + 10} />
      </AbsoluteFill>
    </Entrada>
  );
};

// ---------- Superposición: chip "Carbohidratos → Glucosa" (sobre el b-roll del azúcar) ----------
export const ChipCarbohidratos: React.FC<{ desde: number; hasta: number }> = ({ desde, hasta }) => {
  const frame = useCurrentFrame();
  const d = f(desde), h = f(hasta);
  if (frame < d || frame > h) return null;
  const p = interpolate(frame, [d + 6, d + 20], [0, 1], { ...clamp, easing: eOut });
  const fl = interpolate(frame, [d + 18, d + 34], [0, 1], { ...clamp, easing: eOut });
  const g = interpolate(frame, [d + 30, d + 42], [0, 1], { ...clamp, easing: eOut });
  const out = interpolate(frame, [h - 6, h], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 300, display: "flex", justifyContent: "center", opacity: Math.min(p, out) }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18, background: "rgba(30,15,50,0.55)", backdropFilter: "blur(14px)", border: "2px solid rgba(255,255,255,0.35)", borderRadius: 999, padding: "16px 34px 16px 18px", scale: String(0.85 + 0.15 * p), boxShadow: "0 18px 50px rgba(0,0,0,0.35)" }}>
        <Img src={staticFile("iconos/arroz.png")} style={{ width: 84, height: 84 }} />
        <span style={{ fontFamily: F.sans, fontWeight: 500, fontSize: 48, color: "#fff" }}>Carbohidratos</span>
        <span style={{ fontFamily: "Inter Tight", fontWeight: 600, fontSize: 52, color: C.acentoClaro, opacity: fl, translate: `${(1 - fl) * -20}px 0px` }}>→</span>
        <span style={{ fontFamily: F.sans, fontWeight: 600, fontSize: 52, color: C.acentoClaro, opacity: g, scale: String(0.8 + 0.2 * g) }}>Glucosa</span>
      </div>
    </div>
  );
};

// ---------- Superposición: tarjeta "Tiempo en volver a la normalidad: 2–3 h" ----------
export const TarjetaTiempo: React.FC<{ desde: number; hasta: number }> = ({ desde, hasta }) => {
  const frame = useCurrentFrame();
  const d = f(desde), h = f(hasta);
  if (frame < d || frame > h) return null;
  const p = interpolate(frame, [d + 2, d + 18], [0, 1], { ...clamp, easing: eOut });
  const out = interpolate(frame, [h - 6, h], [1, 0], clamp);
  const relleno = interpolate(frame, [d + 14, h - 30], [0, 1], { ...clamp, easing: eInOut });
  const pl = interpolate(frame, [h - 44, h - 32], [0, 1], clamp);
  return (
    <div style={{ position: "absolute", left: 90, right: 90, top: 150, opacity: Math.min(p, out), translate: `0px ${(1 - p) * -40}px` }}>
      <div style={{ background: "rgba(30,15,50,0.6)", backdropFilter: "blur(14px)", border: "2px solid rgba(255,255,255,0.35)", borderRadius: 32, padding: "24px 32px 22px", boxShadow: "0 20px 60px rgba(0,0,0,0.4)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <Img src={staticFile("iconos/cronometro.png")} style={{ width: 72, height: 72 }} />
          <div style={{ fontFamily: F.sans, fontWeight: 500, fontSize: 40, color: "#fff", lineHeight: 1.15 }}>Tiempo en volver a la normalidad*</div>
        </div>
        <div style={{ position: "relative", height: 26, borderRadius: 13, background: "rgba(255,255,255,0.18)", marginTop: 22, overflow: "hidden" }}>
          <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${relleno * 100}%`, borderRadius: 13, background: `linear-gradient(90deg, ${C.acentoClaro}, ${C.acento})`, boxShadow: "0 0 18px rgba(183,148,246,0.7)" }} />
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8, fontFamily: F.sans, fontWeight: 500, fontSize: 28, color: "rgba(255,255,255,0.8)" }}>
          {["0 h", "1 h", "2 h", "3 h"].map((t) => <span key={t}>{t}</span>)}
        </div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 10 }}>
          <span style={{ fontFamily: F.sans, fontWeight: 300, fontSize: 24, color: "rgba(255,255,255,0.75)" }}>{DATOS.notaNormaliza}</span>
          <span style={{ background: C.pildora, color: "#fff", borderRadius: 999, padding: "4px 22px 8px", fontFamily: F.sans, fontWeight: 600, fontSize: 46, opacity: pl, scale: String(interpolate(pl, [0, 0.6, 1], [0.5, 1.15, 1])) }}>{DATOS.normaliza}</span>
        </div>
      </div>
    </div>
  );
};

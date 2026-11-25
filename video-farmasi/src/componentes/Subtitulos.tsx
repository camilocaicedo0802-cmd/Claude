import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { C, F, T, Y } from "../estilo";
import { ajustar, cap } from "../medida";
import { BLOQUES, Bloque } from "../plan";
import { PALABRAS, clamp, eOut, entrada, f, fin, inicio, limpio } from "../util";

const SOMBRA = "0 2px 16px rgba(0,0,0,0.45), 0 0 2px rgba(0,0,0,0.35)";
const textoDe = (idx: number[]) => idx.map((i) => limpio(PALABRAS[i].text)).join(" ");

// Salida del bloque: 6 f de desvanecido + desenfoque (3.5)
const salida = (frame: number, b: Bloque) => {
  const fin_ = f(b.hasta);
  const p = interpolate(frame, [fin_ - 6, fin_], [1, 0], clamp);
  return { opacity: p, filter: p < 1 ? `blur(${(1 - p) * 6}px)` : undefined };
};

// Palabra pequeña: aparece 4 f antes de pronunciarse
const Pequena: React.FC<{ i: number; size?: number; color?: string; sombra?: boolean }> = ({ i, size = T.subtitulo, color = C.blanco, sombra = true }) => {
  const frame = useCurrentFrame();
  const a = entrada(frame, f(inicio(i)) - 4, 8);
  return (
    <span style={{ display: "inline-block", fontFamily: F.sans, fontWeight: 300, fontSize: size, color, letterSpacing: "-0.02em", textShadow: sombra ? SOMBRA : undefined, marginRight: "0.24em", ...a }}>
      {limpio(PALABRAS[i].text)}
    </span>
  );
};

// Icono 3D (pop con rotación, 4.2)
export const Icono: React.FC<{ nombre: string; desde: number; size?: number; style?: React.CSSProperties; giro?: number }> = ({ nombre, desde, size = 150, style, giro = 12 }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [desde, desde + 12], [0, 1], clamp);
  const s = interpolate(p, [0, 0.6, 1], [0, 1.2, 1]);
  const flotar = Math.sin((frame - desde) / 22) * 6;
  return (
    <Img src={staticFile(`iconos/${nombre}.png`)} style={{ width: size, height: size, position: "absolute", scale: String(s), rotate: `${(1 - p) * -giro + Math.sin((frame - desde) / 30) * 4}deg`, translate: `0px ${flotar}px`, filter: "drop-shadow(0 18px 24px rgba(0,0,0,0.35))", ...style }} />
  );
};

// ---------- Estilo 1: destacado lila en línea ----------
const BloqueLinea: React.FC<{ b: Bloque }> = ({ b }) => {
  const frame = useCurrentFrame();
  const soloDestacado = b.pequenas.length === 0;
  const tam = soloDestacado ? 118 : T.destacado;
  return (
    <AbsoluteFill style={{ ...salida(frame, b) }}>
      <div style={{ position: "absolute", top: Y.subtitulo - (soloDestacado ? 20 : 0), left: 60, right: 60, display: "flex", flexDirection: "column", alignItems: "center", lineHeight: 0.95 }}>
        {b.pequenas.length > 0 && (
          <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", maxWidth: 960 }}>
            {b.pequenas.map((i) => <Pequena key={i} i={i} />)}
          </div>
        )}
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", marginTop: 4, position: "relative" }}>
          {b.destacado.map((i) => {
            const a = entrada(frame, f(inicio(i)) - 8, 10, 0, 1.15, 8);
            return (
              <span key={i} style={{ display: "inline-block", fontFamily: F.sans, fontWeight: 600, fontSize: tam, color: C.acento, textTransform: "uppercase", letterSpacing: "0.04em", marginRight: "0.22em", textShadow: "0 3px 18px rgba(0,0,0,0.35), 0 0 22px rgba(183,148,246,0.35)", ...a }}>
                {limpio(PALABRAS[i].text)}
              </span>
            );
          })}
          {b.icono && b.destacado.length > 0 && (
            <Icono nombre={b.icono} desde={f(inicio(b.destacado[0])) + 4} size={soloDestacado ? 170 : 130} style={{ right: soloDestacado ? -190 : -150, top: soloDestacado ? -40 : -40 }} />
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- Estilo 2: gigante DETRÁS de la cabeza (se pinta entre la toma y la capa de persona) ----------
export const GiganteDetras: React.FC<{ b: Bloque }> = ({ b }) => {
  const frame = useCurrentFrame();
  const txt = textoDe(b.destacado).toUpperCase();
  const size = ajustar(txt, "cond", 990, 620, 0.005);
  const t0 = f(inicio(b.destacado[0])) - 22;
  const letras = [...txt];
  return (
    <AbsoluteFill style={{ ...salida(frame, b), filter: `${salida(frame, b).filter ?? ""} drop-shadow(0 0 24px rgba(155,107,242,0.35))` }}>
      <div style={{ position: "absolute", left: 0, right: 0, top: Y.giganteDetras - (size * cap("cond")) / 2 - size * 0.16, textAlign: "center", whiteSpace: "nowrap" }}>
        {letras.map((c, k) => {
          const d = t0 + k * 1.5;
          const p = interpolate(frame, [d, d + 10], [0, 1], { ...clamp, easing: eOut });
          return (
            <span key={k} style={{ display: "inline-block", fontFamily: F.cond, fontWeight: 400, fontSize: size, lineHeight: 1, letterSpacing: "0.01em", backgroundImage: `linear-gradient(180deg, ${C.gigArriba} 15%, ${C.gigAbajo} 95%)`, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", WebkitTextStroke: `1px rgba(228,212,255,0.45)`, opacity: p, filter: `blur(${(1 - p) * 14}px)`, translate: `0px ${(1 - p) * 30}px`, whiteSpace: "pre" }}>
              {c}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// Palabras de contexto partidas a izquierda y derecha de la cabeza (va DELANTE de la persona)
const BloqueDetrasFrente: React.FC<{ b: Bloque }> = ({ b }) => {
  const frame = useCurrentFrame();
  const mitad = Math.ceil(b.pequenas.length / 2);
  const izq = b.pequenas.slice(0, mitad);
  const der = b.pequenas.slice(mitad);
  const txt = textoDe(b.destacado).toUpperCase();
  const size = ajustar(txt, "cond", 990, 620, 0.005);
  return (
    <AbsoluteFill style={{ ...salida(frame, b) }}>
      <div style={{ position: "absolute", top: Y.contextoArriba, left: 70 }}>{izq.map((i) => <Pequena key={i} i={i} size={T.contexto} />)}</div>
      <div style={{ position: "absolute", top: Y.contextoArriba, right: 70 - 14 }}>{der.map((i) => <Pequena key={i} i={i} size={T.contexto} />)}</div>
      {b.icono && (
        <Icono nombre={b.icono} desde={f(inicio(b.destacado[0])) + 10} size={160} style={{ right: 24, top: Y.giganteDetras + (size * cap("cond")) / 2 - 110 }} />
      )}
    </AbsoluteFill>
  );
};

// ---------- Estilo 3: gigante tecleada DELANTE (blanca o alerta roja) ----------
export const Tecleada: React.FC<{ texto: string; desde: number; hasta: number; centroY: number; anchoMax?: number; maxSize?: number; alerta?: boolean; color?: string }> = ({ texto, desde, hasta, centroY, anchoMax = 880, maxSize = 250, alerta, color = C.blanco }) => {
  const frame = useCurrentFrame();
  const letras = [...texto];
  const size = ajustar(texto, "cond", anchoMax, maxSize, 0.0);
  const paso = Math.max(1.6, Math.min(3.2, (hasta - desde) / Math.max(1, letras.length)));
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: centroY - (size * cap("cond")) / 2 - size * 0.16, textAlign: "center", whiteSpace: "nowrap" }}>
      {letras.map((c, k) => {
        const d = desde + k * paso;
        const vis = frame >= d;
        const p = interpolate(frame, [d, d + 6], [0, 1], clamp);
        const rojo = alerta && frame < hasta + 18;
        const col = rojo ? C.rojo : color;
        return (
          <span key={k} style={{ display: "inline-block", fontFamily: F.cond, fontSize: size, lineHeight: 1, color: col, WebkitTextStroke: `1.5px ${col}`, opacity: vis ? 0.45 + 0.55 * p : 0, filter: `brightness(${0.75 + 0.25 * p})`, textShadow: rojo ? "0 0 28px rgba(236,1,26,0.8)" : "0 4px 24px rgba(0,0,0,0.35)", whiteSpace: "pre" }}>
            {c}
          </span>
        );
      })}
    </div>
  );
};
// Momentos de aparición de cada letra (para sincronizar el tecleo)
export const tiemposTecleo = (texto: string, desde: number, hasta: number) => {
  const n = [...texto].length;
  const paso = Math.max(1.6, Math.min(3.2, (hasta - desde) / Math.max(1, n)));
  return [...texto].map((c, k) => ({ c, t: desde + k * paso })).filter((x) => x.c !== " ");
};
export const rangoTecleada = (b: Bloque) => ({ desde: f(inicio(b.destacado[0])) - 9, hasta: f(fin(b.destacado[b.destacado.length - 1])) - 4 });

const BloqueTecleada: React.FC<{ b: Bloque }> = ({ b }) => {
  const frame = useCurrentFrame();
  const txt = textoDe(b.destacado).toUpperCase();
  const r = rangoTecleada(b);
  return (
    <AbsoluteFill style={{ ...salida(frame, b) }}>
      <div style={{ position: "absolute", top: Y.subtitulo - 40, left: 60, right: 60, display: "flex", justifyContent: "center" }}>
        {b.pequenas.map((i) => <Pequena key={i} i={i} size={T.contexto} />)}
      </div>
      <Tecleada texto={txt} desde={r.desde} hasta={r.hasta} centroY={Y.giganteDelante} alerta={b.alerta} />
      {b.icono && <Icono nombre={b.icono} desde={r.hasta} size={160} style={{ right: 60, top: Y.giganteDelante - 260 }} />}
    </AbsoluteFill>
  );
};

// ---------- Estilo 4: sobre b-roll (blanca gigante + píldora lila) ----------
const BloqueBroll: React.FC<{ b: Bloque }> = ({ b }) => {
  const frame = useCurrentFrame();
  const txt = textoDe(b.destacado).toUpperCase();
  const r = rangoTecleada(b);
  const size = ajustar(txt, "cond", 940, 330, 0);
  const centro = 520;
  const pil = b.pildora ?? [];
  const pilDesde = pil.length ? f(inicio(pil[0])) - 8 : 0;
  const pp = interpolate(frame, [pilDesde, pilDesde + 10], [0, 1], { ...clamp, easing: eOut });
  return (
    <AbsoluteFill style={{ ...salida(frame, b) }}>
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.45) 0%, rgba(0,0,0,0.05) 45%, rgba(0,0,0,0) 60%)" }} />
      <div style={{ position: "absolute", top: centro - (size * cap("cond")) / 2 - 110, left: 60, right: 60, display: "flex", flexWrap: "wrap", justifyContent: "center" }}>
        {b.pequenas.map((i) => <Pequena key={i} i={i} size={64} />)}
      </div>
      <Tecleada texto={txt} desde={r.desde} hasta={r.hasta} centroY={centro} anchoMax={940} maxSize={330} />
      {pil.length > 0 && (
        <div style={{ position: "absolute", left: 0, right: 0, top: centro + (size * cap("cond")) * 0.22, display: "flex", justifyContent: "center" }}>
          <div style={{ background: C.pildora, borderRadius: 999, padding: "8px 30px 12px", rotate: "-3deg", scale: String(0.6 + 0.4 * pp), opacity: pp, boxShadow: "0 10px 30px rgba(70,30,120,0.35)", display: "flex", alignItems: "center", position: "relative" }}>
            {pil.map((i) => {
              const a = entrada(frame, f(inicio(i)) - 4, 6, 0, 1.05, 4);
              return <span key={i} style={{ fontFamily: F.sans, fontWeight: 400, fontSize: 60, color: "#fff", marginRight: "0.22em", letterSpacing: "-0.01em", ...a }}>{limpio(PALABRAS[i].text)}</span>;
            })}
            {b.icono && <Icono nombre={b.icono} desde={f(inicio(pil[pil.length - 1])) + 2} size={120} style={{ right: -95, top: -55 }} />}
          </div>
        </div>
      )}
      {!pil.length && b.icono && <Icono nombre={b.icono} desde={r.hasta} size={150} style={{ right: 70, top: centro + 90 }} />}
    </AbsoluteFill>
  );
};

const activo = (frame: number, b: Bloque) => frame >= f(b.desde) - 10 && frame < f(b.hasta);

export const CapaDetras: React.FC = () => {
  const frame = useCurrentFrame();
  return <>{BLOQUES.filter((b) => b.estilo === "detras" && activo(frame, b)).map((b) => <GiganteDetras key={b.desde} b={b} />)}</>;
};

export const CapaFrente: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {BLOQUES.filter((b) => b.estilo !== "mg" && activo(frame, b)).map((b) => {
        if (b.estilo === "linea") return <BloqueLinea key={b.desde} b={b} />;
        if (b.estilo === "detras") return <BloqueDetrasFrente key={b.desde} b={b} />;
        if (b.estilo === "tecleada") return <BloqueTecleada key={b.desde} b={b} />;
        return <BloqueBroll key={b.desde} b={b} />;
      })}
    </>
  );
};

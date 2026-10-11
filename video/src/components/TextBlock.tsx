import React from "react";
import { random } from "remotion";
import { captions } from "../data/captions";
import { kcolor, kf } from "../lib/anim";
import { C, F } from "../theme";

/**
 * Subtítulo editorial de dos niveles (estilo.md §2):
 *  - línea guía: aparece palabra a palabra, sincronizada con la voz
 *  - palabra(s) destacada(s): entran en el frame exacto en que se pronuncian
 * Temas:
 *  - "light":   guía caligráfica negra + destacada palo seco negra (gris -> negro)
 *  - "dark":    lo mismo en blanco (la cursiva queda limitada a la guía; la palabra clave es palo seco)
 *  - "darkInv": jerarquía invertida de la referencia (§2.3): guía palo seco + destacada caligráfica grande.
 *               Reservada al clímax emocional ("tu tiempo", "jamás").
 * v2: tamaños mínimos para lectura en móvil (guía 72 px, clave ≥ 112 px).
 */
type Props = {
  /** tiempo global (s) actual */
  g: number;
  guide?: [number, number];
  keyw: [number, number];
  x: number;
  y: number;
  width?: number;
  align?: "left" | "right" | "center";
  theme?: "light" | "dark" | "darkInv";
  guideSize?: number;
  keySize?: number;
  /** segundo global en que el bloque sale (desenfoque + subida) */
  exitAt?: number;
  /** revelado de la destacada */
  reveal?: "rise" | "wipe" | "pop" | "scrollUp";
  lineGap?: number;
  /** escala del bloque (para que el texto "avance" hacia cámara) */
  scale?: number;
};

const words = (r?: [number, number]) => (r ? captions.slice(r[0], r[1] + 1).map((c, i) => ({ ...c, idx: r[0] + i })) : []);
const clean = (s: string) => s.trim().replace(/[.,]/g, "").toLowerCase();

export const TextBlock: React.FC<Props> = ({
  g,
  guide,
  keyw,
  x,
  y,
  width = 860,
  align = "left",
  theme = "light",
  guideSize,
  keySize,
  exitAt,
  reveal,
  lineGap = 0,
  scale = 1,
}) => {
  const light = theme === "light";
  const inv = theme === "darkInv";
  const ink = light ? C.ink : C.snow;
  const gSize = guideSize ?? (inv ? 60 : 72);
  const kSize = keySize ?? (inv ? 200 : 128);
  const rv = reveal ?? (inv ? "wipe" : light ? "rise" : "pop");
  const gw = words(guide);
  const kw = words(keyw);
  const first = (gw[0] ?? kw[0]).startMs / 1000;
  if (g < first - 0.05) return null;
  const exitP = exitAt !== undefined ? kf(g, [exitAt, exitAt + 0.28], [0, 1]) : 0;
  if (exitP >= 1) return null;

  const justify = align === "left" ? "flex-start" : align === "right" ? "flex-end" : "center";
  const left = align === "right" ? x - width : align === "center" ? x - width / 2 : x;

  const scriptGuide = !inv;
  const guideStyle: React.CSSProperties = scriptGuide
    ? { fontFamily: F.script, fontSize: gSize, color: ink, lineHeight: 1.22 }
    : { fontFamily: F.sans, fontWeight: 800, fontSize: gSize, letterSpacing: "-0.02em", color: ink, lineHeight: 1.05 };
  const keyBase: React.CSSProperties = inv
    ? { fontFamily: F.script, fontSize: kSize, color: ink, lineHeight: 1.12 }
    : { fontFamily: F.sans, fontWeight: 800, fontSize: kSize, letterSpacing: "-0.035em", lineHeight: 0.98 };
  // aberración cromática leve en bordes del texto (estilo.md §7)
  const aberration = light ? "-1px 0 rgba(0,170,255,0.22), 1px 0 rgba(255,110,30,0.22)" : "-1.5px 0 rgba(0,190,255,0.32), 1.5px 0 rgba(255,120,40,0.32)";

  return (
    <div
      style={{
        position: "absolute",
        left,
        top: y,
        width,
        display: "flex",
        flexDirection: "column",
        alignItems: justify,
        opacity: 1 - exitP,
        filter: exitP > 0 ? `blur(${exitP * 12}px)` : undefined,
        translate: `0px ${-exitP * 40}px`,
        scale: `${scale}`,
        transformOrigin: align === "right" ? "100% 50%" : align === "center" ? "50% 50%" : "0% 50%",
      }}
    >
      {gw.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: justify, columnGap: scriptGuide ? "0.24em" : "0.28em", ...guideStyle, textShadow: aberration }}>
          {gw.map((w) => {
            const dt = g - w.startMs / 1000;
            if (dt < 0) return <span key={w.idx} style={{ opacity: 0 }}>{clean(w.text)}</span>;
            const jitter = scriptGuide ? (random(`base-${w.idx}`) - 0.5) * 10 : 0; // línea base irregular ±5 px
            return (
              <span
                key={w.idx}
                style={{
                  display: "inline-block",
                  opacity: kf(dt, [0, 0.18], [0, 1]),
                  filter: dt < 0.2 ? `blur(${kf(dt, [0, 0.18], [8, 0])}px)` : undefined,
                  translate: `0px ${kf(dt, [0, 0.22], [12, 0]) + jitter}px`,
                  // margen interno: el desenfoque no debe recortar los rasgos de la caligráfica
                  padding: "0.2em 0.1em 0.3em",
                  margin: "-0.2em -0.1em -0.3em",
                }}
              >
                {clean(w.text)}
              </span>
            );
          })}
        </div>
      )}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: justify,
          columnGap: inv ? "0.22em" : "0.26em",
          marginTop: inv ? -gSize * 0.1 + lineGap : -gSize * 0.1 + lineGap,
          ...keyBase,
        }}
      >
        {kw.map((w) => {
          const dt = g - w.startMs / 1000;
          if (dt < 0) return <span key={w.idx} style={{ opacity: 0 }}>{clean(w.text)}</span>;
          if (rv === "wipe") {
            const p = kf(dt, [0, 0.36], [-40, 110]);
            const done = dt > 0.4;
            const mask = `linear-gradient(90deg, black ${p}%, transparent ${p + 35}%)`;
            return (
              <span
                key={w.idx}
                style={{
                  display: "inline-block",
                  color: ink,
                  textShadow: aberration,
                  filter: done ? undefined : `blur(${kf(dt, [0, 0.36], [12, 0])}px)`,
                  WebkitMaskImage: done ? undefined : mask,
                  maskImage: done ? undefined : mask,
                  padding: "0.3em 0.14em 0.42em 0.1em",
                  margin: "-0.3em -0.14em -0.42em -0.1em",
                }}
              >
                {clean(w.text)}
              </span>
            );
          }
          if (rv === "pop") {
            // entrada contundente: escala 0.55 -> 1.06 -> 1 en 0.22 s
            const s = dt < 0.12 ? kf(dt, [0, 0.12], [0.55, 1.06]) : kf(dt, [0.12, 0.24], [1.06, 1]);
            return (
              <span
                key={w.idx}
                style={{
                  display: "inline-block",
                  color: ink,
                  textShadow: aberration,
                  opacity: kf(dt, [0, 0.06], [0, 1]),
                  scale: `${s}`,
                  filter: dt < 0.12 ? `blur(${kf(dt, [0, 0.12], [6, 0])}px)` : undefined,
                }}
              >
                {clean(w.text)}
              </span>
            );
          }
          if (rv === "scrollUp") {
            // entra en la dirección del scroll (de abajo arriba)
            return (
              <span
                key={w.idx}
                style={{
                  display: "inline-block",
                  color: ink,
                  textShadow: aberration,
                  opacity: kf(dt, [0, 0.1], [0, 1]),
                  translate: `0px ${kf(dt, [0, 0.26], [110, 0])}px`,
                  filter: dt < 0.2 ? `blur(${kf(dt, [0, 0.2], [10, 0])}px)` : undefined,
                }}
              >
                {clean(w.text)}
              </span>
            );
          }
          return (
            <span
              key={w.idx}
              style={{
                display: "inline-block",
                opacity: kf(dt, [0, 0.1], [0, 1]),
                color: light ? kcolor(dt, [0, 0.3], [C.keyFrom, C.ink]) : ink,
                translate: `0px ${kf(dt, [0, 0.35], [35, 0])}px`,
                textShadow: aberration,
              }}
            >
              {clean(w.text)}
            </span>
          );
        })}
      </div>
    </div>
  );
};

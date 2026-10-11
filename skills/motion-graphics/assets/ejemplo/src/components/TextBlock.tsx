import React from "react";
import { random } from "remotion";
import { captions } from "../data/captions";
import { kcolor, kf } from "../lib/anim";
import { C, F } from "../theme";

/**
 * Subtítulo editorial de dos niveles (estilo.md §2):
 *  - línea guía: aparece palabra a palabra, sincronizada con la voz
 *  - palabra(s) destacada(s): entran en el frame exacto en que se pronuncian
 * Tema "light": guía caligráfica negra + destacada palo seco negra (gris -> negro).
 * Tema "dark": jerarquía invertida (§2.3): guía palo seco blanca + destacada caligráfica blanca grande.
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
  theme?: "light" | "dark";
  guideSize?: number;
  keySize?: number;
  /** segundo global en que el bloque sale (desenfoque + subida) */
  exitAt?: number;
  /** revelado de la destacada: subida con rampa de gris (E1) o barrido con desenfoque (E2/E3) */
  reveal?: "rise" | "wipe";
  lineGap?: number;
};

const words = (r?: [number, number]) => (r ? captions.slice(r[0], r[1] + 1).map((c, i) => ({ ...c, idx: r[0] + i })) : []);
const clean = (s: string) => s.trim().replace(/[.,]/g, "").toLowerCase();

export const TextBlock: React.FC<Props> = ({
  g,
  guide,
  keyw,
  x,
  y,
  width = 820,
  align = "left",
  theme = "light",
  guideSize,
  keySize,
  exitAt,
  reveal = "rise",
  lineGap = 0,
}) => {
  const dark = theme === "dark";
  const gSize = guideSize ?? (dark ? 52 : 58);
  const kSize = keySize ?? (dark ? 150 : 126);
  const gw = words(guide);
  const kw = words(keyw);
  const first = (gw[0] ?? kw[0]).startMs / 1000;
  if (g < first - 0.05) return null;
  const exitP = exitAt !== undefined ? kf(g, [exitAt, exitAt + 0.28], [0, 1]) : 0;
  if (exitP >= 1) return null;

  const justify = align === "left" ? "flex-start" : align === "right" ? "flex-end" : "center";
  const left = align === "right" ? x - width : align === "center" ? x - width / 2 : x;

  const guideStyle: React.CSSProperties = dark
    ? { fontFamily: F.sans, fontWeight: 800, fontSize: gSize, letterSpacing: "-0.02em", color: C.snow, lineHeight: 1.05 }
    : { fontFamily: F.script, fontSize: gSize, color: C.ink, lineHeight: 1.25 };
  const keyBase: React.CSSProperties = dark
    ? { fontFamily: F.script, fontSize: kSize, color: C.snow, lineHeight: 1.12 }
    : { fontFamily: F.sans, fontWeight: 800, fontSize: kSize, letterSpacing: "-0.035em", lineHeight: 0.98 };
  // aberración cromática leve en bordes del texto (estilo.md §7)
  const aberration = dark
    ? "-1.5px 0 rgba(0,190,255,0.35), 1.5px 0 rgba(255,120,40,0.35)"
    : "-1px 0 rgba(0,170,255,0.22), 1px 0 rgba(255,110,30,0.22)";

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
      }}
    >
      {gw.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: justify, columnGap: dark ? "0.28em" : "0.24em", ...guideStyle, textShadow: aberration }}>
          {gw.map((w) => {
            const dt = g - w.startMs / 1000;
            if (dt < 0) return <span key={w.idx} style={{ opacity: 0 }}>{clean(w.text)}</span>;
            const jitter = dark ? 0 : (random(`base-${w.idx}`) - 0.5) * 12; // línea base irregular ±6 px
            return (
              <span
                key={w.idx}
                style={{
                  display: "inline-block",
                  opacity: kf(dt, [0, 0.2], [0, 1]),
                  filter: `blur(${kf(dt, [0, 0.2], [8, 0])}px)`,
                  translate: `0px ${kf(dt, [0, 0.22], [12, 0]) + jitter}px`,
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
          columnGap: dark ? "0.22em" : "0.26em",
          marginTop: dark ? -gSize * 0.1 + lineGap : -gSize * 0.12 + lineGap,
          ...keyBase,
        }}
      >
        {kw.map((w) => {
          const dt = g - w.startMs / 1000;
          if (dt < 0) return <span key={w.idx} style={{ opacity: 0 }}>{clean(w.text)}</span>;
          if (reveal === "wipe" || dark) {
            const p = kf(dt, [0, 0.36], [-40, 110]);
            const done = dt > 0.4;
            const mask = `linear-gradient(90deg, black ${p}%, transparent ${p + 35}%)`;
            return (
              <span
                key={w.idx}
                style={{
                  display: "inline-block",
                  color: dark ? C.snow : C.ink,
                  textShadow: aberration,
                  filter: done ? undefined : `blur(${kf(dt, [0, 0.36], [12, 0])}px)`,
                  WebkitMaskImage: done ? undefined : mask,
                  maskImage: done ? undefined : mask,
                  // margen interno para que la máscara cubra rasgos que sobresalen (p, j, g, l)
                  padding: "0.3em 0.14em 0.42em 0.1em",
                  margin: "-0.3em -0.14em -0.42em -0.1em",
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
                color: kcolor(dt, [0, 0.3], [C.keyFrom, C.ink]),
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

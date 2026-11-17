import React from "react";
import { AbsoluteFill, Easing, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Card, CUTS, EDL, SubBlock } from "../edl";
import { SF } from "../fonts";

/* ------------------------------------------------------------------ Subtítulos */
// SF Pro Display Italic 57 px, blanco, centro vertical en y = 1228 (64 %), 1-3 palabras por
// bloque, corte seco entre bloques; cada palabra aparece en el fotograma exacto en que se dice.
const SubtitleBlock: React.FC<{ b: SubBlock }> = ({ b }) => {
  const frame = useCurrentFrame();
  const g = b.start + frame;
  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        right: 60,
        top: 1228 - 34,
        textAlign: "center",
        fontFamily: SF,
        fontStyle: "italic",
        fontWeight: 400,
        fontSize: 57,
        lineHeight: "68px",
        color: "#FFFFFF",
        textShadow: "0 2px 6px rgba(0,0,0,0.35), 0 0 18px rgba(0,0,0,0.18)",
        whiteSpace: "nowrap",
      }}
    >
      {b.words.map((w, i) => (
        <span key={i} style={{ opacity: g >= w.f ? 1 : 0 }}>
          {(i ? " " : "") + w.text}
        </span>
      ))}
    </div>
  );
};

export const Subtitles: React.FC = () => (
  <>
    {EDL.subtitles.map((b, i) => (
      <Sequence key={i} from={b.start} durationInFrames={b.end - b.start} name={`Sub ${b.words.map((w) => w.text).join(" ")}`}>
        <SubtitleBlock b={b} />
      </Sequence>
    ))}
  </>
);

/* ------------------------------------------------------------------ Texto tecleado */
export const Typed: React.FC<{ text: string; startAt: number; style: React.CSSProperties; every?: number }> = ({
  text,
  startAt,
  style,
  every = 1,
}) => {
  const frame = useCurrentFrame();
  const n = Math.max(0, Math.min(text.length, Math.floor((frame - startAt) / every) + 1));
  return (
    <div style={{ whiteSpace: "pre", ...style }}>
      {text.slice(0, n)}
      <span style={{ opacity: 0 }}>{text.slice(n)}</span>
    </div>
  );
};

/* ------------------------------------------------------------------ Tarjetas de b-roll */
// Como las tarjetas de foto de la referencia: esquinas de 36 px, borde de cristal, detrás de
// la persona, entrada con fundido + desenfoque 12 -> 0 en 12 fotogramas.
const CardItem: React.FC<{ c: Card }> = ({ c }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const dur = c.to - c.from_;
  const enter = spring({ frame, fps, config: { damping: 18, stiffness: 140 } });
  const blur = interpolate(frame, [0, 12], [12, 0], { extrapolateRight: "clamp" });
  const out = CUTS.has(c.to) ? 1 : interpolate(frame, [dur - 6, dur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute",
        left: c.x,
        top: c.y,
        width: c.w,
        height: c.h,
        opacity: Math.min(interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" }), out),
        translate: `0px ${interpolate(enter, [0, 1], [40, 0])}px`,
        scale: String(interpolate(enter, [0, 1], [0.9, 1])),
        rotate: `${c.rot}deg`,
        filter: blur > 0.2 ? `blur(${blur}px)` : undefined,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: 36,
          overflow: "hidden",
          boxShadow: "0 24px 60px rgba(0,0,0,0.35)",
          outline: "2px solid rgba(255,255,255,0.45)",
          outlineOffset: -2,
        }}
      >
        <OffthreadVideo src={staticFile(c.file)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(255,255,255,0.18), rgba(255,255,255,0) 35%)" }} />
      </div>
      <Typed
        text={c.label}
        startAt={6}
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: c.h + 14,
          textAlign: "center",
          fontFamily: SF,
          fontWeight: 300,
          fontStyle: "italic",
          fontSize: 46,
          color: "#FFFFFF",
          textShadow: "0 2px 8px rgba(0,0,0,0.45)",
        }}
      />
    </div>
  );
};

export const CardsLayer: React.FC = () => (
  <>
    {EDL.cards.map((c, i) => (
      <Sequence key={i} from={c.from_} durationInFrames={c.to - c.from_} name={`Tarjeta ${c.label}`}>
        <CardItem c={c} />
      </Sequence>
    ))}
  </>
);

/* ------------------------------------------------------------------ Monedas de neón */
// Mismo neón verde que la referencia (#39FF14, núcleo #9CFC8D): 4 sueldos -> 1.
const Coin: React.FC<{ draw: number; size: number }> = ({ draw, size }) => {
  const C = 2 * Math.PI * 46;
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" style={{ overflow: "visible" }}>
      <g
        fill="none"
        stroke="#9CFC8D"
        strokeWidth={7}
        strokeLinecap="round"
        style={{ filter: "drop-shadow(0 0 6px #39FF14) drop-shadow(0 0 16px #39FF14) drop-shadow(0 0 34px rgba(57,255,20,0.7))" }}
      >
        <circle cx={60} cy={60} r={46} strokeDasharray={C} strokeDashoffset={C * (1 - draw)} />
        <path
          d="M74 42 C70 35 50 33 47 44 C44 55 76 56 74 70 C72 83 50 84 44 75 M60 28 L60 92"
          strokeDasharray={160}
          strokeDashoffset={160 * (1 - Math.max(0, draw * 1.3 - 0.3))}
        />
      </g>
    </svg>
  );
};

export const NeonCoins: React.FC = () => {
  const n = EDL.neon;
  const first = n.pops[0];
  return (
    <Sequence from={first} durationInFrames={n.end - first} name="Neón 4 sueldos">
      <NeonCoinsInner />
    </Sequence>
  );
};

const NeonCoinsInner: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const n = EDL.neon;
  const g = n.pops[0] + frame;
  const size = 150;
  const xs = [540 - 285, 540 - 95, 540 + 95, 540 + 285];
  return (
    <AbsoluteFill>
      {n.pops.map((p, i) => {
        if (g < p) return null;
        const local = g - p;
        const pop = spring({ frame: local, fps, config: { damping: 12, stiffness: 180 } });
        const draw = interpolate(local, [0, 7], [0, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.quad) });
        // al decir "o solo uno": las monedas 2-4 se van hacia la primera y desaparecen; la primera crece al centro
        const c = Math.max(0, g - n.collapse);
        const t = interpolate(c, [0, 8], [0, 1], { extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });
        const keep = i === 0;
        const x = keep ? interpolate(c, [0, 10], [xs[0], 540], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }) : xs[i] + (540 - xs[i]) * t;
        const sc = keep ? interpolate(c, [0, 10], [1, 1.35], { extrapolateRight: "clamp" }) : 1 - 0.7 * t;
        const op = keep ? 1 : 1 - t;
        const y = keep ? interpolate(c, [0, 10], [n.y, n.y - 120], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }) : n.y;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x - size / 2,
              top: y - size / 2,
              width: size,
              height: size,
              scale: String(pop * sc),
              opacity: op,
            }}
          >
            <Coin draw={draw} size={size} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ Montaje de b-roll */
// Cortes al golpe de la música (2 golpes por plano), empuje suave 1,00 -> 1,08 y etiqueta tecleada.
const ShotItem: React.FC<{ file: string; dur: number; label: string }> = ({ file, dur, label }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ scale: String(interpolate(frame, [0, dur], [1.0, 1.08])) }}>
        <OffthreadVideo src={staticFile(file)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
      <div style={{ position: "absolute", left: 90, top: 300 }}>
        <Typed
          text={label}
          startAt={4}
          style={{
            fontFamily: SF,
            fontWeight: 300,
            fontStyle: "italic",
            fontSize: 92,
            lineHeight: 1,
            color: "#FFFFFF",
            textShadow: "0 3px 14px rgba(0,0,0,0.5)",
          }}
        />
        <div
          style={{
            marginTop: 18,
            height: 8,
            width: interpolate(frame, [4, 4 + label.length + 4], [0, 220], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            backgroundColor: "#E10000",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

export const MontageLayer: React.FC = () => (
  <>
    {EDL.montage.map((m, i) => (
      <Sequence key={i} from={m.from_} durationInFrames={m.dur} name={`Montaje ${m.label}`}>
        <ShotItem file={m.file} dur={m.dur} label={m.label} />
      </Sequence>
    ))}
  </>
);

/* ------------------------------------------------------------------ Destello de luz */
// Como la entrada al montaje de la referencia: destello magenta/rosa -> blanco desde abajo a la izquierda.
export const LightLeaks: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {EDL.transitions
        .filter((t) => t.kind === "leak")
        .map((t, i) => {
          const a = interpolate(frame, [t.at - 4, t.at - 1, t.at + 2, t.at + 10], [0, 1, 1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          if (a <= 0) return null;
          const drift = interpolate(frame, [t.at - 4, t.at + 10], [-120, 160]);
          return (
            <AbsoluteFill key={i} style={{ mixBlendMode: "screen", opacity: a, pointerEvents: "none" }}>
              <AbsoluteFill
                style={{
                  background: `radial-gradient(circle at ${8 + drift / 20}% ${88 - drift / 30}%, rgba(255,255,255,0.95) 0%, rgba(255,120,220,0.9) 18%, rgba(255,79,216,0.75) 34%, rgba(225,0,60,0.45) 55%, rgba(0,0,0,0) 75%)`,
                }}
              />
              <AbsoluteFill
                style={{
                  background: `radial-gradient(ellipse at ${70 + drift / 25}% ${20}%, rgba(255,150,120,0.55) 0%, rgba(255,79,216,0.25) 30%, rgba(0,0,0,0) 60%)`,
                }}
              />
            </AbsoluteFill>
          );
        })}
    </>
  );
};

/* ------------------------------------------------------------------ Transiciones de desenfoque */
// Saliente: desenfoque 0 -> 18 px y zoom 1 -> 1,04 en los últimos fotogramas; entrante: 18 -> 0.
export const useTransitionFx = () => {
  const frame = useCurrentFrame();
  let blur = 0;
  let scale = 1;
  for (const t of EDL.transitions) {
    const maxBlur = t.kind === "leak" ? 10 : 18;
    if (frame >= t.at - t.out && frame < t.at) {
      const p = (frame - (t.at - t.out) + 1) / t.out;
      blur = Math.max(blur, maxBlur * p * p);
      scale = Math.max(scale, 1 + 0.04 * p);
    } else if (frame >= t.at && frame < t.at + t.inn) {
      const p = 1 - (frame - t.at) / t.inn;
      blur = Math.max(blur, maxBlur * p);
      scale = Math.max(scale, 1 + 0.04 * p);
    }
  }
  return { blur, scale };
};

export const TransitionWrap: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { blur, scale } = useTransitionFx();
  return (
    <AbsoluteFill style={{ filter: blur > 0.3 ? `blur(${blur.toFixed(2)}px)` : undefined, scale: String(scale) }}>
      {children}
    </AbsoluteFill>
  );
};

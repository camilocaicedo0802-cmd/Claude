import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { CaptionBlock } from "./components/Captions";
import { AlertCard, BitLine, GreenPill, Headline, MasterclassCard, NamePill, NeonIcon, Notif, Rec, SerifCard, Staff, Tiles } from "./components/Graphics";
import { Stage, isTestimonio } from "./components/Stage";
import { Testimonio } from "./components/Testimonio";
import { BarsFlash, Glitch, barsBlur, blurPulse, glitchShift } from "./components/Transitions";
import { BEAT_LINES } from "./edit/beat";
import { CAPTIONS } from "./edit/captions";
import { SFX } from "./edit/sfx";
import { C, LOWER_CY, WINDOW } from "./theme";
import { BEAT_PARTITURA, END, MODE, T, TOTAL_SECONDS, seg } from "./timeline";

const BARS = [MODE.toWindow, MODE.toSolucion, MODE.toFull];
const GLITCH_AT = MODE.toTestimonio - 0.167;
const MUSIC_OFFSET = 11.5; // la batería de la pista entra justo cuando empieza la solución (28,5 s)

const Graphics: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <AbsoluteFill>
      {/* Titulares de capítulo (solo en formato ventana) */}
      <Headline t={t} start={MODE.toWindow} end={MODE.toSolucion - 0.1} eyebrow="Perfil actoral" text="El actor encasillado" />
      <Headline t={t} start={MODE.toSolucion} end={GLITCH_AT} eyebrow="La solución" text="La estructura de BITS" />
      <Headline t={t} start={MODE.morphEnd - 0.04} end={TOTAL_SECONDS + 1} eyebrow="Masterclass gratis" text="Qué es un BIT" />

      {/* Gancho */}
      <NeonIcon t={t} at={T("s01", 8) + 0.05} end={T("s01", 9)} x={842} y={1018} kind="claqueta" size={104} />
      <NamePill
        t={t}
        at={T("s01", 12)}
        end={MODE.toWindow}
        x={540}
        y={1420}
        names={[
          { t: T("s01", 13), text: "ANDRÉS" },
          { t: T("s01", 14) + 0.12, text: "MATEO" },
          { t: T("s01", 16), text: "JULIÁN" },
        ]}
      />

      {/* Problema */}
      <Notif
        t={t}
        at={T("s02", 0) - 0.03}
        end={T("s02", 6) - 0.04}
        y={WINDOW.y + 24}
        title="Casting"
        words={[
          { t: T("s02", 0) + 0.12, text: "Tienes" },
          { t: T("s02", 1) + 0.1, text: "una" },
          { t: T("s02", 2) + 0.1, text: "nueva" },
          { t: T("s02", 3) + 0.12, text: "audición" },
        ]}
      />
      <Tiles
        t={t}
        end={seg("s03").start}
        tiles={[
          { at: T("s02", 14) - 0.03, icon: "diana", label: "Intenciones" },
          { at: T("s02", 17) - 0.03, icon: "herramientas", label: "Herramientas" },
          { at: T("s02", 20) - 0.03, icon: "mascaras", label: "Reacciones" },
        ]}
      />
      <AlertCard
        t={t}
        at={T("s04", 7) - 0.08}
        end={seg("s05").start}
        y={LOWER_CY - 78}
        icon="candado"
        words={[
          { t: T("s04", 10), text: "«A" },
          { t: T("s04", 11), text: "mí" },
          { t: T("s04", 12), text: "me" },
          { t: T("s04", 13), text: "tienen" },
          { t: T("s04", 14), text: "encasillado»" },
        ]}
      />
      <AlertCard
        t={t}
        at={T("s04", 15) - 0.06}
        end={seg("s05").start}
        y={LOWER_CY + 78}
        icon="movil"
        words={[
          { t: T("s04", 17), text: "«Mi" },
          { t: T("s04", 18), text: "mánager" },
          { t: T("s04", 19), text: "no" },
          { t: T("s04", 20), text: "me" },
          { t: T("s04", 21), text: "envía" },
          { t: T("s04", 23), text: "castings»" },
        ]}
      />
      <Rec t={t} at={T("s05", 10)} end={MODE.toSolucion - 0.02} rect={WINDOW} />

      {/* Solución */}
      <BitLine t={t} at={T("s06", 17) - 0.05} end={BEAT_PARTITURA.start + 0.05} nodesAt={[17, 18, 19, 20].map((i) => T("s06", i))} travelAt={T("s06", 22)} />
      <SerifCard t={t} at={BEAT_PARTITURA.start + 0.06} end={BEAT_PARTITURA.end + 0.02} cy={LOWER_CY} lines={BEAT_LINES} ic="partitura" />
      <Staff t={t} at={T("s08", 0) - 0.02} end={seg("s09").start} notesAt={T("s08", 1)} slursAt={T("s08", 4)} glowAt={T("s08", 12)} />
      <Tiles
        t={t}
        tone="green"
        end={seg("s10").start}
        tiles={[
          { at: T("s09", 3) - 0.03, icon: "puzzle", label: "BIT" },
          { at: T("s09", 6) - 0.03, icon: "rayo", label: "Acción" },
          { at: T("s09", 11) - 0.03, icon: "repetir", label: "Cambio" },
        ]}
      />
      <NeonIcon t={t} at={T("s10", 10) + 0.04} end={seg("s11").start} x={905} y={LOWER_CY - 30} kind="flecha" size={112} />

      {/* CTA */}
      <GreenPill t={t} at={T("s14", 0) - 0.04} end={T("s14", 2) - 0.02} cy={LOWER_CY + 30} typeAt={T("s14", 1)} text="BIT" avatar="media/img/armando_avatar.jpg" hint="Escribe un comentario…" />
      <MasterclassCard t={t} at={T("s14", 7) - 0.05} end={T("s14", 17) - 0.02} cy={LOWER_CY + 40} />
      <GreenPill t={t} at={END("s14") + 0.2} end={TOTAL_SECONDS + 1} cy={LOWER_CY + 30} typeAt={END("s14") + 0.45} text="BIT" avatar="media/img/armando_avatar.jpg" hint="Escribe un comentario…" />
    </AbsoluteFill>
  );
};

const Fx: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <AbsoluteFill>
      {BARS.map((p) => (
        <BarsFlash key={p} t={t} peak={p} />
      ))}
      <Glitch t={t} at={GLITCH_AT} />
    </AbsoluteFill>
  );
};

const StageLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const blur = Math.max(blurPulse(t, T("s01", 9) - 0.06), ...BARS.map((p) => barsBlur(t, p)));
  return (
    <AbsoluteFill style={{ translate: `${glitchShift(t, GLITCH_AT)}px 0px` }}>
      <Stage blur={blur} />
    </AbsoluteFill>
  );
};

const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const testi = isTestimonio(t) ? 1 : 0;
  return (
    <AbsoluteFill
      style={{
        backgroundColor: C.bg,
        backgroundImage: `radial-gradient(70% 34% at 50% 39%, rgba(223,255,79,${0.045 + 0.02 * testi}) 0%, rgba(0,0,0,0) 100%), radial-gradient(80% 30% at 50% 70%, rgba(138,0,21,0.10) 0%, rgba(0,0,0,0) 100%)`,
      }}
    />
  );
};

const musicVolume = (t: number) => {
  // Música ≈22 dB por debajo de la voz (estilo.md §8.1); baja más bajo el testimonio y sube donde no hay voz.
  const base = 0.085;
  const beat = interpolate(t, [BEAT_PARTITURA.start - 0.2, BEAT_PARTITURA.start + 0.2, BEAT_PARTITURA.end - 0.25, BEAT_PARTITURA.end + 0.1], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const testi = interpolate(t, [MODE.toTestimonio - 0.3, MODE.toTestimonio + 0.2, MODE.toFull - 0.3, MODE.toFull + 0.2], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const outro = interpolate(t, [END("s14"), END("s14") + 0.5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fadeIn = interpolate(t, [0, 0.5], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(t, [TOTAL_SECONDS - 1.3, TOTAL_SECONDS - 0.05], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (base + 0.1 * beat - 0.035 * testi + 0.1 * outro) * fadeIn * fadeOut;
};

export const ArmandoBits: React.FC = () => {
  const { fps } = useVideoConfig();
  const s12 = seg("s12");
  return (
    <AbsoluteFill style={{ backgroundColor: C.bg }}>
      <Background />
      <StageLayer />
      <Sequence name="Testimonio · Alberto" from={Math.round(MODE.toTestimonio * fps)} durationInFrames={Math.round((MODE.toFull - MODE.toTestimonio) * fps)}>
        <Testimonio s={s12} nombre="Alberto" rol="Actor · alumno de Backstage" />
      </Sequence>
      <Graphics />
      {CAPTIONS.map((b, i) => (
        <CaptionBlock key={i} block={b} />
      ))}
      <Fx />

      {/* ── Audio ── */}
      <Audio name="Música · ANBR – Quantum" src={staticFile("media/music/quantum.m4a")} trimBefore={Math.round(MUSIC_OFFSET * fps)} volume={(f) => musicVolume(f / fps)} />
      {SFX.map((s, i) => {
        const start = s.t - (s.lead ?? 0);
        const from = Math.max(0, Math.round(start * fps));
        const trimBefore = s.trim ? Math.round(s.trim[0] * fps) : 0;
        const dur = s.trim ? Math.round((s.trim[1] - s.trim[0]) * fps) : undefined;
        return (
          <Sequence key={i} name={`SFX · ${s.name}`} from={from} durationInFrames={dur ?? Math.round(3 * fps)} layout="none">
            <Audio src={staticFile(`media/sfx/${s.name}.wav`)} volume={s.vol} trimBefore={trimBefore} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

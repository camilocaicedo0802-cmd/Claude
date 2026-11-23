import React from "react";
import { Audio, Video } from "@remotion/media";
import { AbsoluteFill, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BehindBlock, CaptionBlock } from "./components/Captions";
import { AlertCard, BitLine, GreenPill, MasterclassCard, NamePill, NeonIcon, Notif, Rec, SerifCard, Staff, Tiles } from "./components/Graphics";
import { GRADE, Scrim, Stage, shotLayout } from "./components/Stage";
import { Testimonio } from "./components/Testimonio";
import { BarsFlash, Glitch, barsBlur, blurPulse, glitchShift } from "./components/Transitions";
import fgJson from "./data/fg.json";
import { BEAT_LINES } from "./edit/beat";
import { BEHIND, CAPTIONS } from "./edit/captions";
import { SFX } from "./edit/sfx";
import { C, CHEST_CY, GFX_CY } from "./theme";
import { BEAT_PARTITURA, CUTS, END, T, TOTAL_SECONDS, seg } from "./timeline";

const BARS = [CUTS.problema, CUTS.solucion, CUTS.cta];
const GLITCH_AT = CUTS.testimonio - 0.167;
const MUSIC_OFFSET = 11.5; // la batería de la pista entra justo cuando empieza la solución (28,5 s)

type Fg = { file: string; from_: number; to: number; x: number; y: number; w: number; h: number };
const FG = fgJson as unknown as Record<string, Fg>;

/** Capa del sujeto recortado: se pinta encima del texto «detrás», alineada al píxel con el vídeo base. */
const Cutout: React.FC<{ id: string; fg: Fg }> = ({ id, fg }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = seg(id);
  const t = s.start + fg.from_ + frame / fps;
  const block = BEHIND.find((b) => b.seg === id);
  if (!block || t < block.start - 0.05 || t >= block.end) return null;
  const { left, top, sc } = shotLayout(s, t);
  return <Video src={staticFile(fg.file)} muted style={{ position: "absolute", left: left + fg.x * sc, top: top + fg.y * sc, width: fg.w * sc, height: fg.h * sc, maxWidth: "none", filter: GRADE }} />;
};

const Graphics: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <AbsoluteFill>
      {/* Gancho */}
      <NeonIcon t={t} at={T("s01", 8) + 0.05} end={T("s01", 9)} x={872} y={CHEST_CY - 132} kind="claqueta" size={110} />
      <NamePill
        t={t}
        at={T("s01", 12)}
        end={CUTS.problema}
        x={540}
        y={CHEST_CY + 262}
        names={[
          { t: T("s01", 13), text: "ANDRÉS" },
          { t: T("s01", 14) + 0.12, text: "MATEO" },
          { t: T("s01", 16), text: "JULIÁN" },
        ]}
      />

      {/* Problema */}
      <Notif
        t={t}
        at={T("s02", 0) - 0.01}
        end={T("s02", 6) - 0.04}
        y={236}
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
        y={GFX_CY - 78}
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
        y={GFX_CY + 78}
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
      <Rec t={t} at={T("s05", 10)} end={CUTS.solucion - 0.02} />

      {/* Solución */}
      <BitLine t={t} at={T("s06", 17) - 0.05} end={BEAT_PARTITURA.start + 0.05} nodesAt={[17, 18, 19, 20].map((i) => T("s06", i))} travelAt={T("s06", 22)} />
      <SerifCard t={t} at={BEAT_PARTITURA.start + 0.06} end={BEAT_PARTITURA.end + 0.02} cy={GFX_CY} lines={BEAT_LINES} ic="partitura" />
      <Staff t={t} at={T("s08", 0) - 0.02} end={seg("s09").start} notesAt={T("s08", 1)} slursAt={T("s08", 4)} glowAt={T("s08", 12)} />
      <Tiles
        t={t}
        tone="gold"
        end={seg("s10").start}
        tiles={[
          { at: T("s09", 3) - 0.03, icon: "puzzle", label: "BIT" },
          { at: T("s09", 6) - 0.03, icon: "rayo", label: "Acción" },
          { at: T("s09", 11) - 0.03, icon: "repetir", label: "Cambio" },
        ]}
      />

      {/* CTA (lo que dice Armando; sin tarjeta final) */}
      <GreenPill t={t} at={T("s14", 0) - 0.04} end={T("s14", 2) - 0.02} cy={GFX_CY + 30} typeAt={T("s14", 1)} text="BIT" avatar="media/img/armando_avatar.jpg" hint="Escribe un comentario…" />
      <MasterclassCard t={t} at={T("s14", 7) - 0.05} end={T("s14", 17) - 0.02} cy={GFX_CY + 40} />
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

/** Vídeo base + texto detrás del sujeto + sujeto recortado, todo bajo el mismo desenfoque y temblor de transición. */
const Picture: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const blur = Math.max(blurPulse(t, T("s01", 9) - 0.06), ...BARS.map((p) => barsBlur(t, p)));
  const s12 = seg("s12");
  return (
    <AbsoluteFill style={{ translate: `${glitchShift(t, GLITCH_AT)}px 0px` }}>
      <Stage blur={blur} />
      <Sequence name="Testimonio · Alberto" from={Math.round(CUTS.testimonio * fps)} durationInFrames={Math.round((CUTS.cta - CUTS.testimonio) * fps)}>
        <Testimonio s={s12} nombre="Alberto" rol="Actor · alumno de Backstage" />
      </Sequence>
      {BEHIND.map((b, i) => (
        <BehindBlock key={i} block={b} />
      ))}
      {Object.entries(FG).map(([id, fg]) => (
        <Sequence key={id} name={`Sujeto recortado · ${id}`} from={Math.round((seg(id).start + fg.from_) * fps)} durationInFrames={Math.max(1, Math.round((fg.to - fg.from_) * fps))} layout="none">
          <Cutout id={id} fg={fg} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

const musicVolume = (t: number) => {
  // Música ≈22 dB por debajo de la voz (estilo.md §8.1); baja más bajo el testimonio y sube donde no hay voz.
  const base = 0.085;
  const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
  const beat = interpolate(t, [BEAT_PARTITURA.start - 0.2, BEAT_PARTITURA.start + 0.2, BEAT_PARTITURA.end - 0.25, BEAT_PARTITURA.end + 0.1], [0, 1, 1, 0], clamp);
  const testi = interpolate(t, [CUTS.testimonio - 0.3, CUTS.testimonio + 0.2, CUTS.cta - 0.3, CUTS.cta + 0.2], [0, 1, 1, 0], clamp);
  const fadeIn = interpolate(t, [0, 0.5], [0, 1], clamp);
  const fadeOut = interpolate(t, [END("s14") - 0.1, TOTAL_SECONDS - 0.02], [1, 0], clamp);
  return (base + 0.1 * beat - 0.035 * testi) * fadeIn * fadeOut;
};

export const ArmandoBits: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: C.bg }}>
      <Picture />
      <Scrim />
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

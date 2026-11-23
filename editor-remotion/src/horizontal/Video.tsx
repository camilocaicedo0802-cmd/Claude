// OPCIÓN B · «clase horizontal»: mismo guion, mismas tomas, misma música y mismos tiempos que la opción A
// (src/Video.tsx), pero con el plano horizontal en una ventana y las tipografías y recursos arriba y abajo.
import React from "react";
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig } from "remotion";
import { CaptionBlock } from "../components/Captions";
import { AlertCard, BitLine, GreenPill, MasterclassCard, NamePill, Notif, SerifCard, Staff, Tiles } from "../components/Graphics";
import { Testimonio } from "../components/Testimonio";
import { BarsFlash, Glitch, barsBlur, blurPulse, glitchShift } from "../components/Transitions";
import { BEAT_LINES } from "../edit/beat";
import { BEHIND } from "../edit/captions";
import { BEAT_PARTITURA, CUTS, T, seg } from "../timeline";
import { SoundTrack } from "../Video";
import { CAPTIONS_H } from "./captions";
import { KEY_CY, LOWER_CY, TILES_CY } from "./layout";
import { HEADLINES, NAMES } from "./plan";
import { SFX_H } from "./sfx";
import { Backdrop, CutoutLayer, WindowStage } from "./Stage";
import { Headline, KeywordTop, RecWindow, SweepArrow } from "./TopZone";

const BARS = [CUTS.problema, CUTS.solucion, CUTS.cta];
const GLITCH_AT = CUTS.testimonio - 0.167;

/** Ventana + palabra gigante detrás + cabeza que sobresale, todo bajo el mismo desenfoque y temblor de transición. */
const Picture: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const blur = Math.max(blurPulse(t, T("s01", 9) - 0.06), ...BARS.map((p) => barsBlur(t, p)));
  return (
    <AbsoluteFill style={{ translate: `${glitchShift(t, GLITCH_AT)}px 0px` }}>
      {BEHIND.map((b, i) => (
        <KeywordTop key={i} block={b} />
      ))}
      <WindowStage blur={blur} />
      <CutoutLayer blur={blur} />
      <Sequence name="Testimonio · Alberto (pantalla completa)" from={Math.round(CUTS.testimonio * fps)} durationInFrames={Math.round((CUTS.cta - CUTS.testimonio) * fps)}>
        <Testimonio s={seg("s12")} nombre="Alberto" rol="Actor · alumno de Backstage" />
      </Sequence>
    </AbsoluteFill>
  );
};

const Graphics: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <AbsoluteFill>
      {/* ── ARRIBA ── */}
      {HEADLINES.map((h, i) => (
        <Headline key={i} h={h} />
      ))}
      <NamePill t={t} at={T("s01", 8) + 0.05} end={CUTS.problema} x={540} y={338} k={1.3} names={NAMES} />
      <Notif
        t={t}
        at={T("s02", 0) - 0.01}
        end={T("s02", 6) - 0.04}
        y={286}
        title="Casting"
        words={[
          { t: T("s02", 0) + 0.12, text: "Tienes" },
          { t: T("s02", 1) + 0.1, text: "una" },
          { t: T("s02", 2) + 0.1, text: "nueva" },
          { t: T("s02", 3) + 0.12, text: "audición" },
        ]}
      />

      {/* ── SOBRE LA VENTANA ── */}
      <RecWindow t={t} at={T("s05", 10)} end={CUTS.solucion - 0.02} />

      {/* ── ABAJO ── */}
      <Tiles
        t={t}
        cy={TILES_CY}
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
      <BitLine t={t} cy={LOWER_CY + 14} at={T("s06", 17) - 0.05} end={BEAT_PARTITURA.start + 0.05} nodesAt={[17, 18, 19, 20].map((i) => T("s06", i))} travelAt={T("s06", 22)} />
      <SerifCard t={t} at={BEAT_PARTITURA.start + 0.06} end={BEAT_PARTITURA.end + 0.02} cy={LOWER_CY} lines={BEAT_LINES} ic="partitura" />
      <Staff t={t} top={1174} at={T("s08", 0) - 0.02} end={seg("s09").start} notesAt={T("s08", 1)} slursAt={T("s08", 4)} glowAt={T("s08", 12)} />
      <Tiles
        t={t}
        cy={TILES_CY}
        tone="gold"
        end={seg("s10").start}
        tiles={[
          { at: T("s09", 3) - 0.03, icon: "puzzle", label: "BIT" },
          { at: T("s09", 6) - 0.03, icon: "rayo", label: "Acción" },
          { at: T("s09", 11) - 0.03, icon: "repetir", label: "Cambio" },
        ]}
      />
      <SweepArrow t={t} at={T("s10", 10) + 0.04} end={seg("s11").start} cy={KEY_CY} />

      {/* CTA (lo que dice Armando; sin tarjeta final) */}
      <GreenPill t={t} at={T("s14", 0) - 0.04} end={T("s14", 2) - 0.02} cy={LOWER_CY + 40} typeAt={T("s14", 1)} text="BIT" avatar="media/img/armando_avatar.jpg" hint="Escribe un comentario…" />
      <MasterclassCard t={t} at={T("s14", 7) - 0.05} end={T("s14", 17) - 0.02} cy={LOWER_CY + 52} />
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

export const ArmandoBitsHorizontal: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#060606" }}>
      <Backdrop />
      <Picture />
      <Graphics />
      {CAPTIONS_H.map((b, i) => (
        <CaptionBlock key={i} block={b} />
      ))}
      <Fx />
      <SoundTrack sfx={SFX_H} />
    </AbsoluteFill>
  );
};

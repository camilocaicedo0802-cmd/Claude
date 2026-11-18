import { Audio } from "@remotion/media";
import { interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { DURACION, EFECTOS, T_RECAP, VENTANA_CITA, VOZ } from "../datos/edicion";
import type { SegVoz } from "../datos/edicion";
import { MEZCLA } from "../estilo";

const fijar = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// La música ("ANBR – Quantum", 120 BPM) entra en el segundo 22,2 de la pista para que su
// subida de energía (56,4 s) coincida con el resumen final.
const INICIO_MUSICA = 56.38 - T_RECAP;

/** Un tramo de voz, con microfundidos para que el corte no chasquee. */
const TramoVoz: React.FC<{ v: SegVoz }> = ({ v }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f0 = Math.round(v.t0 * fps);
  const dur = Math.round((v.fin - v.ini) * fps);
  const local = frame - f0;

  return (
    <Audio
      name={`Voz · ${v.id}`}
      src={staticFile(`voz/${v.clip}.wav`)}
      from={f0}
      trimBefore={Math.round(v.ini * fps)}
      durationInFrames={dur}
      volume={
        MEZCLA.voz *
        interpolate(local, [0, 2, dur - 4, dur], [0, 1, 1, 0], fijar)
      }
    />
  );
};

/** Música de fondo ≈ 20 dB bajo la voz; sin graves durante la cita; sube en el cierre. */
const Musica: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const nivel =
    interpolate(t, [0, 0.5], [0, 1], fijar) *
    interpolate(t, [T_RECAP - 0.3, T_RECAP + 0.5], [MEZCLA.musica, MEZCLA.musicaSinVoz], fijar) *
    interpolate(t, [DURACION - 0.9, DURACION - 0.05], [1, 0], fijar);
  // 0 = pista normal, 1 = pista filtrada (paso-alto)
  const filtrada = interpolate(
    t,
    [VENTANA_CITA.ini - 0.2, VENTANA_CITA.ini + 0.15, VENTANA_CITA.fin - 0.25, VENTANA_CITA.fin + 0.1],
    [0, 1, 1, 0],
    fijar,
  );

  return (
    <>
      <Audio
        name="Música"
        src={staticFile("musica/quantum.mp3")}
        trimBefore={Math.round(INICIO_MUSICA * fps)}
        volume={nivel * (1 - filtrada)}
      />
      <Audio
        name="Música (sin graves, durante la cita)"
        src={staticFile("musica/quantum_filtrada.mp3")}
        trimBefore={Math.round(INICIO_MUSICA * fps)}
        volume={nivel * filtrada * 1.5}
      />
    </>
  );
};

export const Sonido: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <>
      {VOZ.map((v) => (
        <TramoVoz key={v.id} v={v} />
      ))}
      <Musica />
      {EFECTOS.map((e, i) => {
        const inicio = Math.max(0, e.t - (e.adelanto ?? 0));
        return (
          <Audio
            key={i}
            name={`SFX · ${e.archivo}`}
            src={staticFile(`sfx/${e.archivo}`)}
            from={Math.round(inicio * fps)}
            trimBefore={e.recorte ? Math.round(e.recorte * fps) : undefined}
            durationInFrames={e.dur ? Math.round(e.dur * fps) : undefined}
            volume={e.vol}
          />
        );
      })}
    </>
  );
};

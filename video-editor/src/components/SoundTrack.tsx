import { Audio, interpolate, Sequence, staticFile } from "remotion";
import { dbToGain, EDL } from "../edl";

// La voz va TAL CUAL sale del bruto (volumen 1, sin procesar), a petición del cliente.
// Es 4,4 dB más fuerte que la voz procesada de las versiones anteriores, así que música y
// SFX suben 4,4 dB para conservar el mismo equilibrio voz / música / efectos.
const BED_OFFSET_DB = 4.4;
// La música nunca pasa de su nivel original (0 dB) para no saturar.
const MUSIC_MAX_DB = 0;
// Volumen general: la misma bajada para todo (voz, música y SFX). Es solo volumen, no cambia
// el sonido; deja margen para que la suma no sature. Sin limitador ni compresor.
const MASTER_DB = -2;

const musicDb = (f: number) => {
  const k = EDL.music.keys;
  return interpolate(
    f,
    k.map((x) => x.f),
    k.map((x) => x.db),
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
};

export const SoundTrack: React.FC = () => (
  <>
    {/* Voz original de cada toma: sin filtros, solo cortada (fundidos de 5 ms en los bordes) */}
    {EDL.segments.map((s) => (
      <Sequence key={s.id} from={s.from_} durationInFrames={s.dur} name={`Voz ${s.id}`}>
        <Audio src={staticFile(s.wav)} trimBefore={s.clipStart} volume={dbToGain(MASTER_DB)} />
      </Sequence>
    ))}
    {/* Voz en off bajo el montaje: "trabajando para tu negocio" */}
    <Sequence from={EDL.vo.from_} name="Voz en off montaje">
      <Audio src={staticFile(EDL.vo.file)} volume={dbToGain(MASTER_DB)} />
    </Sequence>
    {/* Música: DivKid - Parisian Funk; el drop cae en el "o" de "o solo uno" */}
    <Audio
      src={staticFile(EDL.music.file)}
      volume={(f) => dbToGain(Math.min(musicDb(f) + BED_OFFSET_DB, MUSIC_MAX_DB) + MASTER_DB)}
      name="Música"
    />
    {/* SFX (solo de la carpeta del cliente) */}
    {EDL.sfx.map((s, i) => (
      <Sequence key={i} from={s.from_} name={`SFX ${s.file.replace("sfx/", "")}`}>
        <Audio src={staticFile(s.file)} volume={dbToGain(s.db + BED_OFFSET_DB + MASTER_DB)} />
      </Sequence>
    ))}
  </>
);

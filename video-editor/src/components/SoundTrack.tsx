import { Audio, interpolate, Sequence, staticFile } from "remotion";
import { dbToGain, EDL } from "../edl";

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
    {/* Voz de cada toma (procesada y a -16 LUFS en scripts/prepare_clips.py) */}
    {EDL.segments.map((s) => (
      <Sequence key={s.id} from={s.from_} durationInFrames={s.dur} name={`Voz ${s.id}`}>
        <Audio src={staticFile(`clips/${s.id}.wav`)} />
      </Sequence>
    ))}
    {/* Voz en off bajo el montaje: "trabajando para tu negocio" */}
    <Sequence from={EDL.vo.from_} name="Voz en off montaje">
      <Audio src={staticFile(EDL.vo.file)} />
    </Sequence>
    {/* Música: DivKid - Parisian Funk desde 78,83 s; el drop cae en "o solo uno" */}
    <Audio src={staticFile(EDL.music.file)} volume={(f) => dbToGain(musicDb(f))} name="Música" />
    {/* SFX (solo de la carpeta del cliente) */}
    {EDL.sfx.map((s, i) => (
      <Sequence key={i} from={s.from_} name={`SFX ${s.file.replace("sfx/", "")}`}>
        <Audio src={staticFile(s.file)} volume={dbToGain(s.db)} />
      </Sequence>
    ))}
  </>
);

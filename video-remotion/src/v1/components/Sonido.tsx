import {Audio} from '@remotion/media';
import {Sequence, interpolate, staticFile, useVideoConfig} from 'remotion';
import {MUSIC, SFX} from '../data';
import {clamp, sec} from '../helpers';

/** Música (≈9 dB bajo la voz, corte en seco tras el gancho) + efectos de sonido. */
export const Sonido: React.FC = () => {
  const {fps} = useVideoConfig();
  return (
    <>
      <Audio
        name="Música (Mixkit · OVO)"
        src={staticFile('music/ovo.wav')}
        volume={(f) => {
          const t = f / fps;
          if (t >= MUSIC.stopFrom && t < MUSIC.stopTo) return 0;
          const fadeIn = interpolate(t, [MUSIC.stopTo, MUSIC.stopTo + 0.05], [0, 1], clamp);
          const base = t < MUSIC.stopFrom ? 1 : fadeIn;
          const out = interpolate(t, [MUSIC.duckEnd, MUSIC.duckEnd + 0.9], [1, 0], clamp);
          return MUSIC.volume * base * out;
        }}
      />
      {SFX.map((s, i) => (
        <Sequence key={i} name={`SFX ${s.src}`} from={Math.max(0, sec(s.at, fps))} durationInFrames={sec(s.dur ?? 1.5, fps)}>
          <Audio src={staticFile(s.src)} volume={s.vol} trimBefore={sec(s.trim ?? 0, fps)} />
        </Sequence>
      ))}
    </>
  );
};

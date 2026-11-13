import {Audio} from '@remotion/media';
import {Sequence, interpolate, staticFile, useVideoConfig} from 'remotion';
import {useSpec} from './spec';
import {clamp, sec} from './helpers';

/** Música (≈9 dB bajo la voz, corte en seco tras el gancho) + efectos de sonido. */
export const Sonido: React.FC = () => {
  const spec = useSpec();
  const MUSIC = spec.music;
  const SFX = spec.sfx;
  const {fps} = useVideoConfig();
  return (
    <>
      <Audio
        name="Música"
        src={staticFile(MUSIC.src)}
        volume={(f) => {
          const t = f / fps;
          const stopFrom = MUSIC.stopFrom ?? -1;
          const stopTo = MUSIC.stopTo ?? -1;
          if (t >= stopFrom && t < stopTo) return 0;
          const fadeIn = interpolate(t, [stopTo, stopTo + 0.05], [0, 1], clamp);
          const base = t < stopFrom || stopTo < 0 ? 1 : fadeIn;
          const out = interpolate(t, [MUSIC.fadeOutAt, MUSIC.fadeOutAt + 0.9], [1, 0], clamp);
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

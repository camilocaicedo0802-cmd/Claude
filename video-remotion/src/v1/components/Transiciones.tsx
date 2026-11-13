import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {BLUR_PULSES, FLASHES, WHIPS} from '../data';
import {clamp} from '../helpers';

/** Flash blanco (5 fotogramas), barrido con desenfoque y pulsos de desenfoque (estilo.md §6). */
export const Transiciones: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  let flash = 0;
  for (const t of FLASHES) flash = Math.max(flash, interpolate(frame - t * fps, [-2, 0, 3], [0, 0.9, 0], clamp));
  let whip = 0;
  let whipDir = 1;
  WHIPS.forEach((t, i) => {
    const v = interpolate(frame - t * fps, [-3, 0, 3], [0, 1, 0], clamp);
    if (v > whip) {
      whip = v;
      whipDir = i % 2 ? -1 : 1;
    }
  });
  let pulse = 0;
  for (const t of BLUR_PULSES) pulse = Math.max(pulse, interpolate(frame - t * fps, [-3, 0, 4], [0, 1, 0], clamp));
  const blur = Math.max(whip * 26, pulse * 22);
  return (
    <>
      {blur > 0.5 ? <AbsoluteFill style={{backdropFilter: `blur(${blur}px)`, WebkitBackdropFilter: `blur(${blur}px)`}} /> : null}
      {whip > 0.01 ? (
        <AbsoluteFill
          style={{
            background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.35) 45%, rgba(255,255,255,0.55) 50%, rgba(255,255,255,0.35) 55%, transparent 100%)',
            translate: `${whipDir * interpolate(whip, [0, 1], [-900, 0])}px 0`,
            opacity: whip,
          }}
        />
      ) : null}
      {flash > 0.01 ? <AbsoluteFill style={{background: '#FFFFFF', opacity: flash}} /> : null}
    </>
  );
};

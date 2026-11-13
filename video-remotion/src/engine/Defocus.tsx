import {AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {useSpec} from './spec';
import {clamp, sec} from './helpers';

const DefocusLayer: React.FC<{dur: number}> = ({dur}) => {
  const frame = useCurrentFrame();
  const k = interpolate(frame, [0, 5, dur - 5, dur], [0, 1, 1, 0], clamp);
  return (
    <AbsoluteFill
      style={{
        backdropFilter: `blur(${18 * k}px) brightness(${1 - 0.55 * k}) saturate(${1 - 0.4 * k})`,
        WebkitBackdropFilter: `blur(${18 * k}px) brightness(${1 - 0.55 * k})`,
      }}
    />
  );
};

/** Desenfoca y oscurece el plano de fondo bajo tarjetas y gráficos. */
export const Defocus: React.FC = () => {
  const spec = useSpec();
  const {fps} = useVideoConfig();
  return (
    <>
      {spec.defocus.map(([s, e]) => (
        <Sequence key={s} name="Desenfoque fondo" from={sec(s, fps)} durationInFrames={sec(e - s, fps)}>
          <DefocusLayer dur={sec(e - s, fps)} />
        </Sequence>
      ))}
    </>
  );
};

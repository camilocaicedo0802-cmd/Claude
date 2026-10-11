import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame} from 'remotion';
import {loadFont} from '@remotion/fonts';
import {Background} from './components/Background';
import {E, prog} from './lib/anim';
import {S1Intro} from './scenes/S1Intro';
import {S2Monitor} from './scenes/S2Monitor';
import {S3Demo} from './scenes/S3Demo';
import {S4Atencion} from './scenes/S4Atencion';
import {S5Formatos} from './scenes/S5Formatos';
import {S6Destaca} from './scenes/S6Destaca';
import {S7CTA} from './scenes/S7CTA';

// Inter variable (100–900) empaquetada localmente.
loadFont({family: 'Inter', url: staticFile('fonts/inter-latin-wght-italic.woff2'), style: 'italic', weight: '100 900'});
loadFont({family: 'Inter', url: staticFile('fonts/inter-latin-ext-wght-italic.woff2'), style: 'italic', weight: '100 900', unicodeRange: 'U+0100-024F'});
loadFont({family: 'Inter', url: staticFile('fonts/inter-latin-wght-normal.woff2'), style: 'normal', weight: '100 900'});

// Frames de transición: los arcos punteados aceleran (≈90° en 10 frames) en cada cambio de composición.
export const TRANSITIONS = [58, 160, 252, 362, 400, 432, 462, 590, 672, 708, 766, 842];

const scenes: {from: number; to: number; C: React.FC<{f: number}>}[] = [
  {from: 0, to: 167, C: S1Intro},
  {from: 160, to: 366, C: S2Monitor},
  {from: 357, to: 466, C: S3Demo},
  {from: 464, to: 596, C: S4Atencion},
  {from: 588, to: 676, C: S5Formatos},
  {from: 670, to: 773, C: S6Destaca},
  {from: 767, to: 900, C: S7CTA},
];

export const Promo: React.FC = () => {
  const f = useCurrentFrame();
  const arcRot = f * 0.4 + TRANSITIONS.reduce((acc, t) => acc + 80 * E.cubicInOut(prog(f, t - 4, 11)), 0);
  return (
    <AbsoluteFill style={{background: '#F0F0F0'}}>
      <Background camX={-f * 0.6} camY={-f * 0.25} arcRot={arcRot} />
      {scenes.map(({from, to, C}, i) => (f >= from && f < to ? <C key={i} f={f} /> : null))}
      {/* mezcla final: voz + música + efectos (tools/audio.py) */}
      <Audio src={staticFile('audio/mezcla.wav')} />
    </AbsoluteFill>
  );
};

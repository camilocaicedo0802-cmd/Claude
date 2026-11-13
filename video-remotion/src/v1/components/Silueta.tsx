import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {SEGMENTS} from '../timeline';

// La silueta (public/silueta/f_0001..0102.png) cubre la toma 4864 desde 20,6 s.
const MATTE_START_SRC = Math.round(20.6 * 30);
const MATTE_FRAMES = 102;

/** Devuelve el índice de fotograma de silueta para el fotograma actual (o null si no hay). */
export const matteIndex = (frame: number, hold = false): number | null => {
  const seg = SEGMENTS.find((s) => s.take === '4864' && frame >= s.start && frame < s.start + (s.srcOut - s.srcIn));
  if (!seg) {
    if (!hold) return null;
    return MATTE_FRAMES; // después del último segmento: se congela el último fotograma
  }
  const src = seg.srcIn + (frame - seg.start);
  const idx = src - MATTE_START_SRC + 1;
  if (idx < 1) return null;
  return Math.min(idx, MATTE_FRAMES);
};

export const matteSrc = (idx: number) => staticFile(`silueta/f_${String(idx).padStart(4, '0')}.png`);

/** Silueta recortada encima de los títulos "detrás" (texto detrás de la persona). */
export const Silueta: React.FC<{from: number; to: number}> = ({from, to}) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  const idx = matteIndex(frame);
  if (!idx) return null;
  return (
    <AbsoluteFill>
      <Img src={matteSrc(idx)} style={{width: '100%', height: '100%'}} />
    </AbsoluteFill>
  );
};

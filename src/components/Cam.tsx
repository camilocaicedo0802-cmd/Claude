import React from 'react';
import {DirBlur} from './base';

/** Cámara virtual de una escena: traslación, escala, rotación 3D y motion blur direccional. */
export const Cam: React.FC<{
  s?: number;
  x?: number;
  y?: number;
  rx?: number;
  ry?: number;
  rz?: number;
  blurX?: number;
  blurY?: number;
  opacity?: number;
  origin?: string;
  children?: React.ReactNode;
}> = ({s = 1, x = 0, y = 0, rx = 0, ry = 0, rz = 0, blurX = 0, blurY = 0, opacity = 1, origin = '50% 50%', children}) => (
  <div style={{position: 'absolute', inset: 0, perspective: 1400, opacity}}>
    <div
      style={{
        position: 'absolute',
        inset: 0,
        transform: `translate(${x}px, ${y}px) scale(${s}) rotateX(${rx}deg) rotateY(${ry}deg) rotate(${rz}deg)`,
        transformOrigin: origin,
      }}
    >
      <DirBlur x={blurX} y={blurY}>
        {children}
      </DirBlur>
    </div>
  </div>
);

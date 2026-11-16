import {Video} from '@remotion/media';
import React from 'react';
import {AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS, P, SANS, clamp, easeInOut, easeOut, fr} from './base';
import {T} from './data';
import {Persona} from './Persona';

const useTiempo = () => useCurrentFrame() / FPS;

/** Degradado oscuro abajo para que el texto se lea sobre el B-roll. */
const Base: React.FC<{from?: number}> = ({from = 55}) => (
  <AbsoluteFill style={{background: `linear-gradient(180deg, transparent ${from}%, rgba(0,0,0,0.55) 100%)`}} />
);

// ------------------------------------------------------------------ B-roll del cliente: persona mirando el móvil
export const Cliente: React.FC = () => {
  const t = useTiempo();
  const {from, to} = T.cliente;
  if (t < from || t >= to) return null;
  const z = interpolate(t, [from, to], [1.0, 1.07], clamp);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{transform: `scale(${z})`}}>
        <Sequence from={fr(from)} durationInFrames={fr(to - from)} layout="none">
          <Video src={staticFile('broll/g4_cliente_celular.mp4')} trimBefore={fr(4.8)} muted objectFit="cover" style={{width: '100%', height: '100%'}} />
        </Sequence>
      </AbsoluteFill>
      <Base />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ maqueta: perfil de comercio desordenado
const POSTS: {img?: string; txt?: string; bg?: string; fg?: string; font?: string; f?: string}[] = [
  {img: 'img/post_02.jpg', f: 'saturate(2) contrast(1.3)'},
  {txt: '¡¡OFERTA!! 🔥🔥', bg: '#FFE600', fg: '#E10600', font: 'Impact, sans-serif'},
  {img: 'img/post_07.jpg', f: 'sepia(0.8)'},
  {txt: 'Feliz lunes ☀️☀️', bg: '#FF8FC7', fg: '#1A1AFF', font: 'Georgia, serif'},
  {img: 'img/post_04.jpg', f: 'hue-rotate(90deg) saturate(1.6)'},
  {img: 'img/post_10.jpg', f: 'grayscale(1) contrast(1.4)'},
  {txt: '2x1 SOLO HOY!!!', bg: '#18C964', fg: '#FFFFFF', font: 'Arial Black, sans-serif'},
  {img: 'img/post_06.jpg', f: 'blur(2px) brightness(1.2)'},
  {txt: 'ESCRÍBENOS AL DM 📲', bg: '#1A1AFF', fg: '#FFE600', font: 'Courier New, monospace'},
  {img: 'img/post_01.jpg', f: 'saturate(0.3)'},
  {txt: 'gracias x su compra ❤️', bg: '#FFFFFF', fg: '#FF2D55', font: 'Comic Sans MS, cursive'},
  {img: 'img/post_11.jpg', f: 'hue-rotate(-60deg)'},
  {txt: 'ABIERTO', bg: '#000000', fg: '#FF8C00', font: 'Impact, sans-serif'},
  {img: 'img/post_03.jpg', f: 'contrast(1.6) saturate(1.5)'},
  {txt: 'nuevos productos!!', bg: '#7CFFB2', fg: '#6A00FF', font: 'Times New Roman, serif'},
];

const PerfilDesordenado: React.FC<{scroll: number}> = ({scroll}) => (
  <div style={{position: 'absolute', inset: 0, background: '#FFFFFF', fontFamily: SANS, color: '#111', overflow: 'hidden'}}>
    <div style={{transform: `translateY(${-scroll}px)`}}>
      <div style={{height: 110, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 36}}>tunegocio_oficial2023 ⌄</div>
      <div style={{display: 'flex', alignItems: 'center', padding: '10px 40px', gap: 46}}>
        <div style={{width: 170, height: 170, borderRadius: 85, background: 'linear-gradient(135deg,#FFB300,#FF2D55,#1A1AFF)', padding: 6}}>
          <div style={{width: '100%', height: '100%', borderRadius: '50%', background: '#DDD', overflow: 'hidden'}}>
            <Img src={staticFile('img/post_09.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'blur(1.5px)'}} />
          </div>
        </div>
        {[
          ['38', 'publicaciones'],
          ['112', 'seguidores'],
          ['980', 'seguidos'],
        ].map(([n, l]) => (
          <div key={l} style={{textAlign: 'center'}}>
            <div style={{fontWeight: 700, fontSize: 38}}>{n}</div>
            <div style={{fontSize: 24}}>{l}</div>
          </div>
        ))}
      </div>
      <div style={{padding: '14px 40px', fontSize: 27, lineHeight: 1.35}}>
        <div style={{fontWeight: 700}}>Tu Negocio Oficial 🔥🔥</div>
        <div>VENTAS!!! 📲 escribenos al dm ✨ envios a todo el pais!!! 🚚💯 #ofertas #barato #moda #2x1 #emprendimiento</div>
      </div>
      <div style={{display: 'flex', gap: 30, padding: '20px 40px'}}>
        {['😎', 'promo', 'random', 'fotos', '♥'].map((h) => (
          <div key={h} style={{textAlign: 'center', fontSize: 20}}>
            <div style={{width: 110, height: 110, borderRadius: 55, border: '3px solid #DDD', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 34, background: '#F4F4F4'}}>{h.length < 3 ? h : ''}</div>
            {h.length < 3 ? '' : h}
          </div>
        ))}
      </div>
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 4, marginTop: 10}}>
        {POSTS.map((p, i) => (
          <div key={i} style={{aspectRatio: '1 / 1', overflow: 'hidden', background: p.bg ?? '#EEE'}}>
            {p.img ? (
              <Img src={staticFile(p.img)} style={{width: '100%', height: '100%', objectFit: 'cover', filter: p.f}} />
            ) : (
              <div style={{width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', color: p.fg, fontFamily: p.font, fontWeight: 900, fontSize: 40, padding: 14, lineHeight: 1.05}}>
                {p.txt}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  </div>
);

/** Fondo: la persona desenfocada y oscurecida (para tarjetas y maquetas). */
const PersonaDesenfocada: React.FC = () => (
  <AbsoluteFill>
    <AbsoluteFill style={{filter: 'blur(26px) brightness(0.45) saturate(1.2)', transform: 'scale(1.08)'}}>
      <Persona />
    </AbsoluteFill>
  </AbsoluteFill>
);

export const Maqueta: React.FC = () => {
  const t = useTiempo();
  const {from, to} = T.maqueta;
  if (t < from || t >= to) return null;
  const p = interpolate(t, [from, from + 0.35], [0, 1], {...clamp, easing: easeOut});
  const scroll = interpolate(t, [from + 0.2, to], [0, 430], {...clamp, easing: easeInOut});
  return (
    <AbsoluteFill>
      <PersonaDesenfocada />
      <div
        style={{
          position: 'absolute',
          left: 170,
          top: 96 + (1 - p) * 900,
          width: 740,
          height: 1390,
          borderRadius: 74,
          background: '#0B0B0B',
          padding: 18,
          boxShadow: '0 40px 80px rgba(0,0,0,0.6), 0 0 0 3px #3A3A3A, 0 0 60px rgba(183,1,252,0.35)',
          transform: `rotate(${(1 - p) * 8 - 1.5}deg)`,
        }}
      >
        <div style={{position: 'relative', width: '100%', height: '100%', borderRadius: 58, overflow: 'hidden'}}>
          <PerfilDesordenado scroll={scroll} />
        </div>
      </div>
      <Base from={60} />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ B-roll de su carpeta: persona sola en el escritorio
export const Escritorio: React.FC = () => {
  const t = useTiempo();
  const {from, to} = T.escritorio;
  if (t < from || t >= to) return null;
  const p = interpolate(t, [from, from + 0.35], [0, 1], {...clamp, easing: easeOut});
  const w = 820;
  const h = (w * 1605) / 970;
  return (
    <AbsoluteFill>
      <PersonaDesenfocada />
      <div
        style={{
          position: 'absolute',
          left: 540 - w / 2,
          top: 120 + (1 - p) * 120,
          width: w,
          height: h,
          borderRadius: 36,
          overflow: 'hidden',
          opacity: p,
          transform: `scale(${0.94 + 0.06 * p})`,
          boxShadow: '0 0 0 6px #E2C7FF, 0 0 50px 10px rgba(183,1,252,0.45), 0 30px 60px rgba(0,0,0,0.5)',
        }}
      >
        <Sequence from={fr(from)} durationInFrames={fr(to - from)} layout="none">
          <Video src={staticFile('broll/g4_c226_escritorio.mp4')} trimBefore={fr(1.0)} muted objectFit="cover" style={{width: '100%', height: '100%'}} />
        </Sequence>
      </div>
      <Base from={62} />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ marco «caja central» (estilo.md §4.4) + grabación de Grow
const CAJA = {x0: 40, x1: 1040, y0: 290, y1: 1600};

export const Marco: React.FC = () => {
  const t = useTiempo();
  const {from} = T.marco;
  const fin = T.cierre.from;
  if (t < from || t > T.cierre.to) return null;
  // parpadeo de entrada: encendido 2 f, apagado 2 f, encendido
  const k = Math.floor((t - from) * FPS);
  if (k >= 2 && k < 4) return null;
  // tono: oscuro al 78 % → pleno al final
  const pleno = interpolate(t, [fin - 0.5, fin], [0, 1], clamp);
  const op = 0.78 + 0.22 * pleno;
  const color = pleno > 0.5 ? P.purple : P.deep;
  // cierre: el hueco se cierra hasta tapar todo
  const c = interpolate(t, [fin - 0.05, fin + 0.35], [0, 1], {...clamp, easing: easeInOut});
  const x0 = CAJA.x0 + (540 - CAJA.x0) * c;
  const x1 = CAJA.x1 - (CAJA.x1 - 540) * c;
  const y0 = CAJA.y0 + (945 - CAJA.y0) * c;
  const y1 = CAJA.y1 - (CAJA.y1 - 945) * c;
  // escalones que se desplazan (como en la referencia)
  const e = interpolate(t, [from + 0.08, from + 0.5], [0, 1], {...clamp, easing: easeOut});
  const deriva = Math.sin((t - from) * 1.6) * 14;
  const panel = (style: React.CSSProperties, key: string) => (
    <div key={key} style={{position: 'absolute', background: `linear-gradient(160deg, ${color} 0%, ${P.mid} 55%, ${P.deep} 100%)`, opacity: c > 0.98 ? 1 : op, ...style}} />
  );
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {panel({left: 0, top: 0, width: 1080, height: y0}, 'arriba')}
      {panel({left: 0, top: y1, width: 1080, height: 1920 - y1}, 'abajo')}
      {panel({left: 0, top: y0, width: x0, height: y1 - y0}, 'izq')}
      {panel({left: x1, top: y0, width: 1080 - x1, height: y1 - y0}, 'der')}
      {c < 0.5
        ? [
            panel({left: x1 - 130 * e, top: y1 - 150 + deriva, width: 130 * e, height: 150 - deriva}, 'esc1'),
            panel({left: x1 - 60 * e, top: y1 - 300 + deriva, width: 60 * e, height: 150}, 'esc2'),
            panel({left: x0, top: y1 - 70 - deriva * 0.5, width: 180 * e, height: 70 + deriva * 0.5}, 'esc3'),
          ]
        : null}
    </AbsoluteFill>
  );
};

/** Grabación del perfil de @growmarketingpro_ dentro de la caja: el perfil que sí responde las tres preguntas. */
export const Grow: React.FC = () => {
  const t = useTiempo();
  const {from, to} = T.grow;
  if (t < from || t >= to) return null;
  const mitad = 31.9;
  const p = interpolate(t, [from, from + 0.3], [0, 1], {...clamp, easing: easeOut});
  // 1) cabecera con bio y seguidores · 2) cuadrícula coherente con la marca
  // (−90 px: fuera la barra de estado del móvil de la grabación)
  const tramo = t < mitad ? {clip: 0.2, y: -90, z: 1.0} : {clip: 2.2, y: -300, z: 1.08};
  const z = tramo.z + interpolate(t, [t < mitad ? from : mitad, t < mitad ? mitad : to], [0, 0.04], clamp);
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: CAJA.x0, top: CAJA.y0, width: CAJA.x1 - CAJA.x0, height: CAJA.y1 - CAJA.y0, overflow: 'hidden', background: '#000', opacity: p}}>
        <div style={{position: 'absolute', left: 0, top: tramo.y, width: '100%', transform: `scale(${z})`, transformOrigin: '50% 0%'}}>
          <Sequence from={fr(t < mitad ? from : mitad)} durationInFrames={fr(t < mitad ? mitad - from : to - mitad)} layout="none">
            <Video key={tramo.clip} src={staticFile('broll/g4_ig_grow.mp4')} trimBefore={fr(tramo.clip)} muted style={{width: '100%'}} />
          </Sequence>
        </div>
        <AbsoluteFill style={{background: 'linear-gradient(180deg, transparent 55%, rgba(8,0,20,0.82) 78%, rgba(8,0,20,0.9) 100%)'}} />
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ cierre
export const Cierre: React.FC = () => {
  const t = useTiempo();
  const {from} = T.cierre;
  if (t < from + 0.2) return null;
  const p = interpolate(t, [from + 0.25, from + 0.7], [0, 1], {...clamp, easing: easeOut});
  const vida = t - from;
  const fondo = interpolate(t, [from + 0.2, from + 0.42], [0, 1], clamp);
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <AbsoluteFill style={{opacity: fondo, background: 'radial-gradient(ellipse 75% 45% at 50% 48%, #3A0080 0%, #18003A 45%, #07000F 100%)'}} />
      <Img
        src={staticFile('img/logo_grow.png')}
        style={{
          width: 700,
          opacity: p,
          filter: `blur(${(1 - p) * 12}px) drop-shadow(0 0 30px rgba(255,255,255,0.35))`,
          transform: `scale(${(1.08 - 0.08 * p) * (1 + vida * 0.012)})`,
        }}
      />
      <div
        style={{
          marginTop: 40,
          fontFamily: SANS,
          fontWeight: 500,
          fontSize: 44,
          letterSpacing: '0.04em',
          color: P.white,
          opacity: interpolate(t, [from + 0.5, from + 0.85], [0, 1], clamp),
        }}
      >
        @growmarketingpro_
      </div>
    </AbsoluteFill>
  );
};

import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {clamp, rand} from '../engine/helpers';
import {Sonido} from '../engine/Sonido';
import {SpecContext} from '../engine/spec';
import {Comentario, CierreC, Monitor, Nivel, Nota, Perdida, Perfil, Publicar, Stats} from './Apps';
import {Title} from '../engine/Title';
import {PersonCut, SmallSubs} from './Subs';
import {SHAKES, SPEC_C, T, TITLES} from './data';
import {Cursor, Escritorio, MenuBar, Pantalla, PuntoApagado, screenAt} from './Desktop';

const F = 30;

/** Destellos: encendido inicial y desfibrilador. */
const Flash: React.FC = () => {
  const frame = useCurrentFrame();
  const v = interpolate(frame - T.on * F, [-1, 0, 6], [0, 1, 0], clamp);
  return v > 0.01 ? <AbsoluteFill style={{background: '#fff', opacity: v}} /> : null;
};

/** Encendido de pantalla al empezar: la imagen se abre desde una línea brillante en el centro (TV vieja). */
const PowerOn: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame > 8) return null;
  const p = interpolate(frame, [0, 7], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const bar = 960 * (1 - p);
  const line = interpolate(frame, [0, 2, 7], [1, 1, 0], clamp);
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: bar, background: '#000'}} />
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: bar, background: '#000'}} />
      <div style={{position: 'absolute', left: 0, right: 0, top: bar - 3, height: 6, background: '#fff', boxShadow: '0 0 30px #fff, 0 0 60px #B701FC', opacity: line}} />
      <div style={{position: 'absolute', left: 0, right: 0, bottom: bar - 3, height: 6, background: '#fff', boxShadow: '0 0 30px #fff, 0 0 60px #B701FC', opacity: line}} />
    </AbsoluteFill>
  );
};

export const Video3: React.FC = () => {
  const frame = useCurrentFrame();
  let sx = 0;
  let sy = 0;
  for (const t of SHAKES) {
    const l = frame - t * F;
    if (l >= 0 && l < 9) {
      const a = 16 * (1 - l / 9);
      sx = (rand(frame * 1.7) - 0.5) * 2 * a;
      sy = (rand(frame * 2.3 + 5) - 0.5) * 2 * a;
    }
  }
  const s = screenAt(frame);
  const desk = interpolate(s.k, [0.6, 1], [1, 0], clamp);
  return (
    <SpecContext.Provider value={SPEC_C}>
      <AbsoluteFill style={{background: '#000'}}>
        <AbsoluteFill style={{translate: `${sx}px ${sy}px`}}>
          <Escritorio />
          <MenuBar opacity={desk} />
          <Pantalla />
          {TITLES.filter((t) => t.scene).map((t) => (
            <Title key={t.id} t={t} />
          ))}
          <PersonCut />
          <PuntoApagado />
          <Publicar />
          <Nota />
          <Perdida />
          <Stats />
          <Perfil />
          <Nivel />
          <Monitor />
          <Comentario />
          <CierreC />
          {TITLES.filter((t) => !t.scene).map((t) => (
            <Title key={t.id} t={t} />
          ))}
          <SmallSubs />
          <Cursor />
        </AbsoluteFill>
        <PowerOn />
        <Flash />
        <Sonido />
      </AbsoluteFill>
    </SpecContext.Provider>
  );
};

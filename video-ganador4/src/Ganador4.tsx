import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {FPS} from './base';
import {T} from './data';
import {Cierre, Cliente, Escritorio, Grow, Maqueta, Marco} from './Escenas';
import {Gancho} from './Gancho';
import {LienzoFondo, LienzoFrente, Rayas, Tarjeta} from './Lienzo';
import {Persona, blurAt} from './Persona';
import {Sonido} from './Sonido';
import {Lista, Textos} from './Textos';

/** Ganador 4 · «Los 3 problemas de las redes» — edición según estilo.md (referente: vídeo derecho «Our edit»). */
export const Ganador4: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const b = blurAt(t);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {/* imagen (las transiciones de desenfoque afectan a todo menos al texto) */}
      <AbsoluteFill style={{filter: b > 0.05 ? `blur(${b}px)` : undefined, transform: b > 0.05 ? `scale(${1 + b * 0.003})` : undefined}}>
        <LienzoFondo />
        <Tarjeta>
          <Persona />
        </Tarjeta>
        <LienzoFrente />
        <Gancho />
        <Cliente />
        <Maqueta />
        <Escritorio />
        <Grow />
        <Marco />
        <Rayas at={T.rayas} />
      </AbsoluteFill>
      <Textos />
      <Lista />
      <Cierre />
      <Sonido />
    </AbsoluteFill>
  );
};

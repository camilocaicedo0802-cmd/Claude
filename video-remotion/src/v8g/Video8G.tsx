import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Sonido} from '../engine/Sonido';
import {SpecContext} from '../engine/spec';
import {SCENES, SPEC_G, sceneAt} from './data';
import {
  Broll,
  Cierre,
  Destello,
  DosLineas,
  Fondo3D,
  FondoBlanco,
  FondoEscenario,
  FondoEstudio,
  Ganchos,
  Gigantes,
  Laminas,
  Palabras3D,
  Recorte,
  Sala,
  Silueta,
  UnaPalabra,
  Voz,
} from './Escenas';
import './fonts';
import {DM, Google, IGDemo, Perfil} from './UI';

const F = 30;

/** Escena actual: fondo, textos detrás, persona, textos delante. */
const Escena: React.FC = () => {
  const frame = useCurrentFrame();
  const sc = sceneAt(frame / F);
  switch (sc.kind) {
    case 'estudio':
      return (
        <>
          <FondoEstudio />
          <Ganchos layer="behind" />
          {frame < 2 || (frame >= 6 && frame < 8) ? null : frame < 6 ? <Silueta /> : <Recorte scene={sc} />}
          <Ganchos layer="front" />
        </>
      );
    case 'blanco':
      return (
        <>
          <FondoBlanco />
          <Gigantes />
          <Recorte scene={sc} />
        </>
      );
    case 'escenario':
      return (
        <>
          <FondoEscenario />
          <Gigantes />
          <Recorte scene={sc} />
        </>
      );
    case 'palabras3d':
      return (
        <>
          <Fondo3D />
          <Palabras3D scene={sc} layer="behind" />
          <Recorte scene={sc} />
          <Palabras3D scene={sc} layer="front" />
        </>
      );
    case 'sala':
      return <Sala scene={sc} />;
    case 'lamina':
      return <Laminas />;
    case 'perfil':
      return <Perfil scene={sc} />;
    case 'google':
      return <Google scene={sc} />;
    case 'dm':
      return <DM scene={sc} />;
    case 'ig':
      return <IGDemo />;
    case 'broll':
      return <Broll scene={sc} />;
    case 'cierre':
      return <Cierre />;
  }
};

export const Video8G: React.FC = () => (
  <SpecContext.Provider value={SPEC_G}>
    <AbsoluteFill style={{background: '#000'}}>
      <Escena />
      <DosLineas />
      <UnaPalabra />
      <Destello />
      <Voz />
      <Sonido />
    </AbsoluteFill>
  </SpecContext.Provider>
);

void SCENES;

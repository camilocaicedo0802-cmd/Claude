import {EditVideo} from '../engine/EditVideo';
import {SPEC} from './data';
import {Checklist, Encuesta, PerfilVacio, Versus} from './Escenas';

export const Video9: React.FC = () => (
  <EditVideo
    spec={SPEC}
    underCards={<PerfilVacio />}
    scenes={
      <>
        <Versus />
        <Checklist />
        <Encuesta />
      </>
    }
  />
);

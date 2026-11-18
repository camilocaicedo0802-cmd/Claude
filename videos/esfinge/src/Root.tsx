import React from 'react';
import {Composition, Still} from 'remotion';
import {Completo} from './Completo';
import {PortadaCulpable, PortadaDibujo, PortadaMito} from './Portadas';
import {FIN_VIDEO} from './escenas/Historia';

export const Root: React.FC = () => (
	<>
		<Composition id="Completo" component={Completo} durationInFrames={FIN_VIDEO} fps={30} width={1080} height={1920} />
		<Still id="Portada1-Mito" component={PortadaMito} width={1080} height={1920} />
		<Still id="Portada2-Dibujo" component={PortadaDibujo} width={1080} height={1920} />
		<Still id="Portada3-Culpable" component={PortadaCulpable} width={1080} height={1920} />
	</>
);

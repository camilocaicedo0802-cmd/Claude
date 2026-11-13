import React from 'react';
import {Composition} from 'remotion';
import {Completo} from './Completo';
import {FIN_VIDEO} from './escenas/Historia';
import {Galeria} from './Prueba';

export const Root: React.FC = () => (
	<>
		<Composition id="Completo" component={Completo} durationInFrames={FIN_VIDEO} fps={30} width={1080} height={1920} />
		<Composition id="Galeria" component={Galeria} durationInFrames={150} fps={30} width={1080} height={1920} />
	</>
);

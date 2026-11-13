import React from 'react';
import {Composition, Still} from 'remotion';
import {Completo} from './Completo';
import {FIN_VIDEO} from './escenas/Historia';
import {PortadaNoche, PortadaQuiz, PortadaYoVivi} from './Portadas';
import {Galeria} from './Prueba';

export const Root: React.FC = () => (
	<>
		<Composition id="Completo" component={Completo} durationInFrames={FIN_VIDEO} fps={30} width={1080} height={1920} />
		<Still id="Portada1-YoVivi" component={PortadaYoVivi} width={1080} height={1920} />
		<Still id="Portada2-Noche" component={PortadaNoche} width={1080} height={1920} />
		<Still id="Portada3-Quiz" component={PortadaQuiz} width={1080} height={1920} />
		<Composition id="Galeria" component={Galeria} durationInFrames={150} fps={30} width={1080} height={1920} />
	</>
);

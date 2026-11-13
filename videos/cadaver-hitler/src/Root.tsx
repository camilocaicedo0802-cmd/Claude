import React from 'react';
import {Composition} from 'remotion';
import {Completo} from './Completo';
import {FIN_VIDEO} from './escenas/Desarrollo';
import {CORTES} from './escenas/Gancho';
import {Muestra} from './Muestra';
import {Prueba} from './Prueba';

export const Root: React.FC = () => (
	<>
		<Composition id="Completo" component={Completo} durationInFrames={FIN_VIDEO} fps={30} width={1080} height={1920} />
		<Composition id="Muestra" component={Muestra} durationInFrames={CORTES.fin} fps={30} width={1080} height={1920} />
		<Composition id="Prueba" component={Prueba} durationInFrames={30} fps={30} width={1080} height={1920} />
	</>
);

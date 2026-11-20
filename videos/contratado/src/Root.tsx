import React from 'react';
import {Composition, Still} from 'remotion';
import {Completo} from './Completo';
import {FIN_VIDEO} from './escenas/Short';
import {Portada52, PortadaContrato, PortadaRodeado} from './Portadas';

export const Root: React.FC = () => (
	<>
		<Composition id="Completo" component={Completo} durationInFrames={FIN_VIDEO} fps={30} width={1080} height={1920} />
		<Still id="PortadaContrato" component={PortadaContrato} width={1080} height={1920} />
		<Still id="PortadaRodeado" component={PortadaRodeado} width={1080} height={1920} />
		<Still id="Portada52" component={Portada52} width={1080} height={1920} />
	</>
);

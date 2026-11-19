import React from 'react';
import {Composition, Still} from 'remotion';
import {Completo} from './Completo';
import {PortadaAparatito, PortadaHotel, PortadaPuerta} from './Portadas';
import {FIN_VIDEO} from './escenas/Historia';

export const Root: React.FC = () => (
	<>
		<Composition id="Completo" component={Completo} durationInFrames={FIN_VIDEO} fps={30} width={1080} height={1920} />
		<Still id="Portada1-Hotel" component={PortadaHotel} width={1080} height={1920} />
		<Still id="Portada2-Aparatito" component={PortadaAparatito} width={1080} height={1920} />
		<Still id="Portada3-Puerta" component={PortadaPuerta} width={1080} height={1920} />
	</>
);

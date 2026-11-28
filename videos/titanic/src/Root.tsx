import React from 'react';
import {Composition, Still} from 'remotion';
import {Completo} from './Completo';
import {FIN_VIDEO} from './escenas/Short';
import {Portada37, PortadaArmario, PortadaLlave} from './Portadas';

export const Root: React.FC = () => (
	<>
		<Composition id="Completo" component={Completo} durationInFrames={FIN_VIDEO} fps={30} width={1080} height={1920} />
		<Still id="PortadaLlave" component={PortadaLlave} width={1080} height={1920} />
		<Still id="Portada37" component={Portada37} width={1080} height={1920} />
		<Still id="PortadaArmario" component={PortadaArmario} width={1080} height={1920} />
	</>
);

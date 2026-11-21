import React from 'react';
import {Composition, Still} from 'remotion';
import {Completo} from './Completo';
import {FIN_VIDEO} from './escenas/Short';
import {PortadaGlobo, PortadaPeriodico, PortadaSecreto} from './Portadas';

export const Root: React.FC = () => (
	<>
		<Composition id="Completo" component={Completo} durationInFrames={FIN_VIDEO} fps={30} width={1080} height={1920} />
		<Still id="PortadaGlobo" component={PortadaGlobo} width={1080} height={1920} />
		<Still id="PortadaPeriodico" component={PortadaPeriodico} width={1080} height={1920} />
		<Still id="PortadaSecreto" component={PortadaSecreto} width={1080} height={1920} />
	</>
);

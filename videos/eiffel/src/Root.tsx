import React from 'react';
import {Composition, Still} from 'remotion';
import {Completo} from './Completo';
import {FIN_VIDEO} from './escenas/Short';
import {PortadaAprendiz, PortadaSoborno, PortadaVendida} from './Portadas';

export const Root: React.FC = () => (
	<>
		<Composition id="Completo" component={Completo} durationInFrames={FIN_VIDEO} fps={30} width={1080} height={1920} />
		<Still id="PortadaVendida" component={PortadaVendida} width={1080} height={1920} />
		<Still id="PortadaSoborno" component={PortadaSoborno} width={1080} height={1920} />
		<Still id="PortadaAprendiz" component={PortadaAprendiz} width={1080} height={1920} />
	</>
);

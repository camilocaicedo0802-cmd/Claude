import React from 'react';
import {Composition, Still} from 'remotion';
import {Completo} from './Completo';
import {PortadaBug, PortadaPolemica, PortadaPolicia} from './Portadas';
import {FIN_VIDEO} from './escenas/Historia';

export const Root: React.FC = () => (
	<>
		<Composition id="Completo" component={Completo} durationInFrames={FIN_VIDEO} fps={30} width={1080} height={1920} />
		<Still id="Portada1-Bug" component={PortadaBug} width={1080} height={1920} />
		<Still id="Portada2-Policia" component={PortadaPolicia} width={1080} height={1920} />
		<Still id="Portada3-Polemica" component={PortadaPolemica} width={1080} height={1920} />
	</>
);

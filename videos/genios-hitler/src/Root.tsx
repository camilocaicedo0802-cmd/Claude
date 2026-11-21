import React from 'react';
import {Composition, Still} from 'remotion';
import {Completo} from './Completo';
import {FIN_VIDEO} from './escenas/Historia';
import {Miniatura, MiniaturaA, MiniaturaA2, MiniaturaA3, MiniaturaA4, MiniaturaB, MiniaturaC, PortadaContrato, PortadaInofensivo, PortadaMayoria} from './Portadas';

export const Root: React.FC = () => (
	<>
		<Composition id="Completo" component={Completo} durationInFrames={FIN_VIDEO} fps={24} width={1920} height={1080} />
		<Still id="PortadaContrato" component={PortadaContrato} width={1920} height={1080} />
		<Still id="PortadaMayoria" component={PortadaMayoria} width={1920} height={1080} />
		<Still id="PortadaInofensivo" component={PortadaInofensivo} width={1920} height={1080} />
		<Still id="Miniatura" component={Miniatura} width={1920} height={1080} />
		<Still id="MiniaturaA" component={MiniaturaA} width={1920} height={1080} />
		<Still id="MiniaturaA2" component={MiniaturaA2} width={1920} height={1080} />
		<Still id="MiniaturaA3" component={MiniaturaA3} width={1920} height={1080} />
		<Still id="MiniaturaA4" component={MiniaturaA4} width={1920} height={1080} />
		<Still id="MiniaturaB" component={MiniaturaB} width={1920} height={1080} />
		<Still id="MiniaturaC" component={MiniaturaC} width={1920} height={1080} />
	</>
);

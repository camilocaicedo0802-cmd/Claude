import React from 'react';
import {Composition, Still} from 'remotion';
import {Completo} from './Completo';
import {FIN_VIDEO} from './escenas/Historia';
import {Miniatura, PortadaContrato, PortadaInofensivo, PortadaMayoria} from './Portadas';

export const Root: React.FC = () => (
	<>
		<Composition id="Completo" component={Completo} durationInFrames={FIN_VIDEO} fps={24} width={1920} height={1080} />
		<Still id="PortadaContrato" component={PortadaContrato} width={1920} height={1080} />
		<Still id="PortadaMayoria" component={PortadaMayoria} width={1920} height={1080} />
		<Still id="PortadaInofensivo" component={PortadaInofensivo} width={1920} height={1080} />
		<Still id="Miniatura" component={Miniatura} width={1920} height={1080} />
	</>
);

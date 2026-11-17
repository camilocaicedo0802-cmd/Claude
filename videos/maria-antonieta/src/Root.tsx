import React from 'react';
import {Composition, Still} from 'remotion';
import {Completo} from './Completo';
import {FIN_VIDEO} from './escenas/Historia';
import {PortadaFakeNews, PortadaNuncaLoDijo, PortadaVersus} from './Portadas';

export const Root: React.FC = () => (
	<>
		<Composition id="Completo" component={Completo} durationInFrames={FIN_VIDEO} fps={30} width={1080} height={1920} />
		<Still id="Portada1-NuncaLoDijo" component={PortadaNuncaLoDijo} width={1080} height={1920} />
		<Still id="Portada2-FakeNews" component={PortadaFakeNews} width={1080} height={1920} />
		<Still id="Portada3-Versus" component={PortadaVersus} width={1080} height={1920} />
	</>
);

import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {ATLANTE, CIUDADANA, Personaje, PLATON, POSEIDON, REY} from './componentes/Personaje';
import {EnMundo} from './componentes/Toma';
import {EscAtenas, EscCanales, EscCielo, EscCiudadAerea, EscLibro, EscNoche, EscPalacio, EscPlaza, EscProfundo, EscSubmarino, EscTerraza, EscTesoro, EscTsunami} from './escenarios/Escenarios';

const ESCENAS = [
	<EscCanales key="a" />,
	<EscCanales key="b" variante="temblor" />,
	<EscCanales key="c" variante="inundada" nivelAgua={200} />,
	<EscCiudadAerea key="d" />,
	<EscTerraza key="e" />,
	<EscPalacio key="f" />,
	<EscTesoro key="g" />,
	<EscPlaza key="h" />,
	<EscCielo key="i" tormenta rayos={[73, 74]} />,
	<EscTsunami key="j" subida={0.8} />,
	<EscNoche key="k" hundir={0.5} />,
	<EscSubmarino key="l" />,
	<EscAtenas key="m" />,
	<EscProfundo key="n" />,
	<EscLibro key="o" />,
];

export const Galeria: React.FC = () => {
	const f = useCurrentFrame();
	const i = Math.min(ESCENAS.length - 1, Math.floor(f / 10));
	return (
		<AbsoluteFill style={{background: '#000'}}>
			{ESCENAS[i]}
			{i === 0 && (
				<>
					<EnMundo x={200} y={1800} alto={700}><Personaje diseno={ATLANTE} boca="sonrisa" /></EnMundo>
					<EnMundo x={540} y={1800} alto={700}><Personaje diseno={REY} boca="sonrisa" ojos="feliz" /></EnMundo>
					<EnMundo x={880} y={1800} alto={700}><Personaje diseno={CIUDADANA} boca="sonrisa" /></EnMundo>
				</>
			)}
			{i === 12 && <EnMundo x={540} y={1800} alto={800}><Personaje diseno={PLATON} boca="seria" /></EnMundo>}
			{i === 8 && <EnMundo x={540} y={1500} alto={1400}><Personaje diseno={POSEIDON} cejas="enojado" boca="dientes" sombra={false} /></EnMundo>}
		</AbsoluteFill>
	);
};

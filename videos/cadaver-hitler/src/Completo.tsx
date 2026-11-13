import React from 'react';
import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useVideoConfig} from 'remotion';
import {Subtitulos} from './componentes/Subtitulos';
import {Desarrollo, ENTRADA_DESARROLLO, INICIO_DESARROLLO, SONIDOS_DESARROLLO} from './escenas/Desarrollo';
import {Gancho, SONIDOS_GANCHO} from './escenas/Gancho';

export const Sonidos: React.FC<{lista: [string, number, number][]}> = ({lista}) => (
	<>
		{lista.map(([archivo, desde, volumen], i) => (
			<Sequence key={i} from={Math.max(0, desde)} durationInFrames={90} layout="none">
				<Audio src={staticFile(`sfx/${archivo}.wav`)} volume={volumen} />
			</Sequence>
		))}
	</>
);

/** Video completo: "El cadáver que engañó a Hitler" (~62 s). */
export const Completo: React.FC = () => {
	const {durationInFrames} = useVideoConfig();
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<Gancho finMapa={INICIO_DESARROLLO} salidaMapa={ENTRADA_DESARROLLO} />
			<Desarrollo />
			<Subtitulos />
			<Audio src={staticFile('voz.wav')} />
			<Audio
				src={staticFile('musica.wav')}
				volume={(f) => interpolate(f, [0, 6, durationInFrames - 30, durationInFrames], [0, 0.15, 0.15, 0], {extrapolateRight: 'clamp'})}
			/>
			<Sonidos lista={[...SONIDOS_GANCHO, ...SONIDOS_DESARROLLO]} />
		</AbsoluteFill>
	);
};

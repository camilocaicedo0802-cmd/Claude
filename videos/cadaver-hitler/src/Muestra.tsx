import React from 'react';
import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useVideoConfig} from 'remotion';
import {Subtitulos} from './componentes/Subtitulos';
import {Gancho, SONIDOS_GANCHO} from './escenas/Gancho';

const Sonidos: React.FC<{lista: [string, number, number][]}> = ({lista}) => (
	<>
		{lista.map(([archivo, desde, volumen], i) => (
			<Sequence key={i} from={Math.max(0, desde)} durationInFrames={90} layout="none">
				<Audio src={staticFile(`sfx/${archivo}.wav`)} volume={volumen} />
			</Sequence>
		))}
	</>
);

/** Muestra: el gancho + "Era 1943, y los aliados querían invadir Sicilia." (~11,5 s) */
export const Muestra: React.FC = () => {
	const {durationInFrames} = useVideoConfig();
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<Gancho />
			<Subtitulos />
			<Audio src={staticFile('voz.wav')} volume={1} />
			<Audio
				src={staticFile('musica.wav')}
				volume={(f) => interpolate(f, [0, 6, durationInFrames - 12, durationInFrames], [0, 0.16, 0.16, 0], {extrapolateRight: 'clamp'})}
			/>
			<Sonidos lista={SONIDOS_GANCHO} />
		</AbsoluteFill>
	);
};

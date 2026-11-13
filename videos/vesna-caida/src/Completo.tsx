import React from 'react';
import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useVideoConfig} from 'remotion';
import {Subtitulos} from './componentes/Subtitulos';
import {Historia, SONIDOS} from './escenas/Historia';

const Sonidos: React.FC<{lista: [string, number, number][]}> = ({lista}) => (
	<>
		{lista.map(([archivo, desde, volumen], i) => (
			<Sequence key={i} from={Math.max(0, desde)} durationInFrames={110} layout="none">
				<Audio src={staticFile(`sfx/${archivo}.wav`)} volume={volumen} />
			</Sequence>
		))}
	</>
);

/** Video completo: la azafata que cayó 10.000 metros sin paracaídas. */
export const Completo: React.FC = () => {
	const {durationInFrames} = useVideoConfig();
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<Historia />
			<Subtitulos />
			<Audio src={staticFile('voz.wav')} />
			<Audio
				src={staticFile('musica.wav')}
				volume={(f) => interpolate(f, [0, 6, durationInFrames - 30, durationInFrames], [0, 0.14, 0.14, 0], {extrapolateRight: 'clamp'})}
			/>
			<Sonidos lista={SONIDOS} />
		</AbsoluteFill>
	);
};

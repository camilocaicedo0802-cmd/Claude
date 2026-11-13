import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig} from 'remotion';
import {Subtitulos} from './componentes/Subtitulos';
import {volumenFx, volumenMusica} from './mezcla';
import {Historia, SONIDOS} from './escenas/Historia';

const Sonidos: React.FC<{lista: [string, number, number][]}> = ({lista}) => (
	<>
		{lista.map(([archivo, desde, volumen], i) => (
			<Sequence key={i} from={Math.max(0, desde)} durationInFrames={110} layout="none">
				<Audio src={staticFile(`sfx/${archivo}.wav`)} volume={(f) => volumenFx(archivo, volumen, Math.max(0, desde) + f)} />
			</Sequence>
		))}
	</>
);

/** Video completo: la azafata que cayó 10.000 metros sin paracaídas. */
export const Completo: React.FC<{pistas?: 'todo' | 'sinVoz'}> = ({pistas = 'todo'}) => {
	const {durationInFrames} = useVideoConfig();
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<Historia />
			<Subtitulos />
			{pistas === 'todo' && <Audio src={staticFile('voz.wav')} />}
			<Audio src={staticFile('musica.wav')} volume={(f) => volumenMusica(f, durationInFrames)} />
			<Sonidos lista={SONIDOS} />
		</AbsoluteFill>
	);
};

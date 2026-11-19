import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig} from 'remotion';
import {Historia, SONIDOS} from './escenas/Historia';
import {volumenFx, volumenMusica} from './mezcla';

const Sonidos: React.FC<{lista: [string, number, number][]}> = ({lista}) => (
	<>
		{lista.map(([archivo, desde, volumen], i) => (
			<Sequence key={i} from={Math.max(0, desde)} durationInFrames={96} layout="none">
				<Audio src={staticFile(`sfx/${archivo}.wav`)} volume={(f) => volumenFx(archivo, volumen, Math.max(0, desde) + f)} />
			</Sequence>
		))}
	</>
);

/** Video largo: «Los genios que contrataron a Hitler» (16:9, 24 fps). Sin subtítulos quemados: van en el SRT. */
export const Completo: React.FC<{pistas?: 'todo' | 'sinVoz' | 'musica'}> = ({pistas = 'todo'}) => {
	const {durationInFrames} = useVideoConfig();
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<Historia />
			{pistas === 'todo' && <Audio src={staticFile('voz.wav')} />}
			<Audio src={staticFile('musica.wav')} volume={(f) => volumenMusica(f, durationInFrames)} />
			{pistas !== 'musica' && <Sonidos lista={SONIDOS} />}
		</AbsoluteFill>
	);
};

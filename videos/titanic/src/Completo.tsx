import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig} from 'remotion';
import {Subtitulos} from './componentes/Subtitulos';
import {Historia, SONIDOS} from './escenas/Short';
import {volumenFx, volumenMusica} from './mezcla';

const Sonidos: React.FC<{lista: [string, number, number][]}> = ({lista}) => (
	<>
		{lista.map(([archivo, desde, volumen], i) => (
			<Sequence key={i} from={Math.max(0, desde)} durationInFrames={110} layout="none">
				<Audio src={staticFile(`sfx/${archivo}.wav`)} volume={(f) => volumenFx(archivo, volumen, Math.max(0, desde) + f)} />
			</Sequence>
		))}
	</>
);

/** Short vertical: «La llave del Titanic» (1080x1920, 30 fps), con subtítulos de 1–2 palabras. */
export const Completo: React.FC<{pistas?: 'todo' | 'sinVoz' | 'musica'}> = ({pistas = 'todo'}) => {
	const {durationInFrames} = useVideoConfig();
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<Historia />
			<Subtitulos />
			{pistas === 'todo' && <Audio src={staticFile('voz.wav')} />}
			<Audio src={staticFile('musica.wav')} volume={(f) => volumenMusica(f, durationInFrames)} />
			{pistas !== 'musica' && <Sonidos lista={SONIDOS} />}
		</AbsoluteFill>
	);
};

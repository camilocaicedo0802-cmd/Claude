import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig} from 'remotion';
import {Subtitulos} from './componentes/Subtitulos';
import {volumenFx, volumenMusica} from './mezcla';
import {Desarrollo, ENTRADA_DESARROLLO, INICIO_DESARROLLO, SONIDOS_DESARROLLO} from './escenas/Desarrollo';
import {Gancho, SONIDOS_GANCHO} from './escenas/Gancho';

export const Sonidos: React.FC<{lista: [string, number, number][]}> = ({lista}) => (
	<>
		{lista.map(([archivo, desde, volumen], i) => (
			<Sequence key={i} from={Math.max(0, desde)} durationInFrames={90} layout="none">
				<Audio src={staticFile(`sfx/${archivo}.wav`)} volume={(f) => volumenFx(archivo, volumen, Math.max(0, desde) + f)} />
			</Sequence>
		))}
	</>
);

/** Video completo: "El cadáver que engañó a Hitler" (~62 s). */
export const Completo: React.FC<{pistas?: 'todo' | 'sinVoz'}> = ({pistas = 'todo'}) => {
	const {durationInFrames} = useVideoConfig();
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<Gancho finMapa={INICIO_DESARROLLO} salidaMapa={ENTRADA_DESARROLLO} />
			<Desarrollo />
			<Subtitulos />
			{pistas === 'todo' && <Audio src={staticFile('voz.wav')} />}
			<Audio src={staticFile('musica.wav')} volume={(f) => volumenMusica(f, durationInFrames)} />
			<Sonidos lista={[...SONIDOS_GANCHO, ...SONIDOS_DESARROLLO]} />
		</AbsoluteFill>
	);
};

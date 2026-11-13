import React from 'react';
import {AbsoluteFill, Audio, interpolate, staticFile, useVideoConfig} from 'remotion';
import {Subtitulos} from './componentes/Subtitulos';
import {Sonidos} from './Completo';
import {Gancho, SONIDOS_GANCHO} from './escenas/Gancho';

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

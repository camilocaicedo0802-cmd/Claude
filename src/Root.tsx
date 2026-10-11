import React from 'react';
import {Composition} from 'remotion';
import {CamisetaBombastik} from './Video';
import {DURATION, FPS} from './edl';

export const RemotionRoot: React.FC = () => (
	<Composition
		id="CamisetaBombastik"
		component={CamisetaBombastik}
		durationInFrames={DURATION}
		fps={FPS}
		width={1080}
		height={1920}
	/>
);

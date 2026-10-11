import React from 'react';
import {AbsoluteFill, Audio, OffthreadVideo, Sequence, staticFile} from 'remotion';
import {FPS, SHOTS} from './edl';
import {LUTS} from './grades';

// Etalonaje por plano: tabla por canal aplicada en sRGB (ver analisis/etalonaje.py)
const GradeFilters: React.FC = () => (
	<svg width={0} height={0} style={{position: 'absolute'}}>
		<defs>
			{LUTS.map(([r, g, b], i) => (
				<filter key={i} id={`grade-${i}`} colorInterpolationFilters="sRGB" x="0" y="0" width="100%" height="100%">
					<feComponentTransfer>
						<feFuncR type="table" tableValues={r.join(' ')} />
						<feFuncG type="table" tableValues={g.join(' ')} />
						<feFuncB type="table" tableValues={b.join(' ')} />
					</feComponentTransfer>
				</filter>
			))}
		</defs>
	</svg>
);

export const CamisetaBombastik: React.FC = () => {
	return (
		<AbsoluteFill style={{backgroundColor: '#060508'}}>
			<GradeFilters />
			{SHOTS.map((s, i) => (
				// Cortes secos: cada plano es una Sequence sin transición
				<Sequence key={i} from={s.start} durationInFrames={s.end - s.start} name={`${i + 1} ${s.diseno} ${s.take}`}>
					<AbsoluteFill style={{filter: `url(#grade-${i})`}}>
						<OffthreadVideo
							src={staticFile(`tomas/${s.take}.mp4`)}
							trimBefore={Math.round(s.from * FPS)}
							playbackRate={s.velocidad ?? 1}
							muted
							style={{width: '100%', height: '100%', objectFit: 'cover'}}
						/>
					</AbsoluteFill>
				</Sequence>
			))}
			<Audio src={staticFile('audio/bombastik_estribillo.wav')} />
		</AbsoluteFill>
	);
};

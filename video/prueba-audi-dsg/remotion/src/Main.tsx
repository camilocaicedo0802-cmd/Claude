import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import edl from './edl.json';
import {Grain, Vignette, f} from './fx';
import {Overlay, Subtitle} from './Overlays';
import {Visual} from './Scenes';
import {Watermark} from './Watermark';

export const Main: React.FC = () => {
	const e: any = edl;
	return (
		<AbsoluteFill style={{background: '#000', fontFamily: 'Poppins'}}>
			{e.visuals.map((v: any, i: number) => (
				<Sequence key={`v${i}`} from={f(v.from)} durationInFrames={Math.max(1, f(v.to) - f(v.from))} name={`${v.kind} ${i}`}>
					<Visual v={v} />
				</Sequence>
			))}
			<Vignette />
			{e.subs.map((s: any, i: number) => (
				<Sequence key={`s${i}`} from={f(s.from)} durationInFrames={Math.max(1, f(s.to) - f(s.from))} name={`sub ${i}`}>
					<Subtitle s={s} />
				</Sequence>
			))}
			{e.overlays.map((o: any, i: number) => (
				<Sequence key={`o${i}`} from={f(o.from)} durationInFrames={Math.max(1, f(o.to) - f(o.from))} name={`${o.kind} ${i}`}>
					<Overlay o={o} total={e.total} />
				</Sequence>
			))}
			<Watermark />
			<Grain />
		</AbsoluteFill>
	);
};

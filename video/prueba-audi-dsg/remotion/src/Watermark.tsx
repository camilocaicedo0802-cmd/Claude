import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

const NAME = 'JUAN CAICEDO';

// Anti-theft watermark: a faint diagonal pattern over the whole frame (hard to crop or
// mask) + a semi-transparent signature that changes position every few seconds.
const tileStyle: React.CSSProperties = {
	fontFamily: 'Poppins',
	fontWeight: 800,
	fontStyle: 'italic',
	fontSize: 44,
	letterSpacing: 6,
	textTransform: 'uppercase',
	color: '#ffffff',
	WebkitTextStroke: '1.4px rgba(0,0,0,0.85)',
	whiteSpace: 'nowrap',
};

const SPOTS: {x: number; y: number; align: 'left' | 'right' | 'center'}[] = [
	{x: 56, y: 345, align: 'left'},
	{x: 56, y: 1640, align: 'right'},
	{x: 56, y: 400, align: 'right'},
	{x: 56, y: 1610, align: 'left'},
	{x: 0, y: 1700, align: 'center'},
	{x: 56, y: 360, align: 'left'},
];
const HOLD = 150; // frames per position (5 s)

export const Watermark: React.FC = () => {
	const frame = useCurrentFrame();
	const gap = 230;
	const step = 600; // approx tile width + gap, for a seamless drift
	const drift = (frame * 0.8) % step;
	const rows = new Array(10).fill(0);
	const cols = new Array(5).fill(0);

	const idx = Math.floor(frame / HOLD) % SPOTS.length;
	const local = frame % HOLD;
	const fade = Math.min(interpolate(local, [0, 10], [0, 1], {extrapolateRight: 'clamp'}), interpolate(local, [HOLD - 10, HOLD], [1, 0], {extrapolateLeft: 'clamp'}));
	const spot = SPOTS[idx];
	const pos: React.CSSProperties =
		spot.align === 'center'
			? {left: 0, width: '100%', textAlign: 'center'}
			: spot.align === 'left'
				? {left: spot.x}
				: {right: spot.x};

	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			<AbsoluteFill style={{opacity: 0.1, overflow: 'hidden'}}>
				<div
					style={{
						position: 'absolute',
						left: -760,
						top: -720,
						width: 2600,
						height: 3360,
						transform: 'rotate(-28deg)',
						display: 'flex',
						flexDirection: 'column',
						justifyContent: 'space-between',
					}}
				>
					{rows.map((_, r) => (
						<div key={r} style={{display: 'flex', gap, transform: `translateX(${(r % 2 ? -step / 2 : 0) + drift - step}px)`}}>
							{cols.map((__, c) => (
								<div key={c} style={tileStyle}>
									{NAME}
								</div>
							))}
						</div>
					))}
				</div>
			</AbsoluteFill>
			<div
				style={{
					position: 'absolute',
					top: spot.y,
					...pos,
					opacity: 0.46 * fade,
					fontFamily: 'Poppins',
					fontWeight: 700,
					fontSize: 34,
					letterSpacing: 3,
					color: '#ffffff',
					textTransform: 'uppercase',
					textShadow: '0 2px 6px rgba(0,0,0,0.75), 0 0 1px rgba(0,0,0,0.9)',
					whiteSpace: 'nowrap',
				}}
			>
				© {NAME}
			</div>
		</AbsoluteFill>
	);
};

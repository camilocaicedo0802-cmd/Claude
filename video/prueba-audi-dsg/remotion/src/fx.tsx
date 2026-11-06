import React from 'react';
import {AbsoluteFill, Easing, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

// ------------------------------------------------------------------ palette
export const RED = '#ff1f12';
export const RED_DEEP = '#c40000';
export const BLACK = '#070707';
export const WHITE = '#ffffff';
export const FPS = 30;
export const f = (s: number) => Math.round(s * FPS);
const NOISE = `url(${staticFile('noise.png')})`;

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Approximate fit of Poppins Black uppercase italic into a width.
export const fit = (text: string, base: number, maxW = 960, k = 0.7) => Math.min(base, maxW / Math.max(1, text.length * k));

// ------------------------------------------------------------------ entrances
export const useZoomBlurIn = (len = 7, from = 1.35) => {
	const frame = useCurrentFrame();
	const s = interpolate(frame, [0, len], [from, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const b = interpolate(frame, [0, len - 1], [26, 0], clamp);
	const br = interpolate(frame, [0, len - 2], [1.7, 1], clamp);
	return {transform: `scale(${s})`, filter: `blur(${b}px) brightness(${br})`};
};

export const pop = (frame: number, at: number, fps = FPS, damping = 11) =>
	spring({frame: frame - at, fps, config: {damping, stiffness: 220, mass: 0.6}});

// ------------------------------------------------------------------ text styles
// White texture: gradient white -> soft red + grain, red glow + hard extrude.
export const texWhite = (size: number): React.CSSProperties => ({
	fontFamily: 'Poppins',
	fontWeight: 900,
	fontStyle: 'italic',
	fontSize: size,
	lineHeight: 0.95,
	letterSpacing: -size * 0.02,
	textTransform: 'uppercase',
	backgroundImage: `${NOISE}, linear-gradient(180deg, #ffffff 0%, #ffffff 48%, #ffe1de 72%, #ff9d93 100%)`,
	backgroundSize: '160px 160px, 100% 100%',
	WebkitBackgroundClip: 'text',
	backgroundClip: 'text',
	color: 'transparent',
	filter: `drop-shadow(0 ${size * 0.035}px 0 #5a0000) drop-shadow(0 0 ${size * 0.16}px rgba(255,35,15,0.55)) drop-shadow(0 ${size * 0.08}px ${size * 0.12}px rgba(0,0,0,0.55))`,
	whiteSpace: 'nowrap',
});

// Red bevel / chrome texture used for the punch words (CAKED UP equivalent).
export const RedBevel: React.FC<{text: string; size: number; style?: React.CSSProperties}> = ({text, size, style}) => {
	const base: React.CSSProperties = {
		fontFamily: 'Poppins',
		fontWeight: 900,
		fontStyle: 'italic',
		fontSize: size,
		lineHeight: 0.92,
		letterSpacing: -size * 0.025,
		textTransform: 'uppercase',
		whiteSpace: 'nowrap',
	};
	return (
		<div style={{position: 'relative', display: 'inline-block', ...style}}>
			{/* extrude */}
			<div style={{...base, position: 'absolute', left: 0, top: 0, color: '#2a0000', transform: `translate(${size * 0.012}px, ${size * 0.06}px)`, filter: `drop-shadow(0 ${size * 0.06}px ${size * 0.1}px rgba(0,0,0,0.7))`}}>{text}</div>
			<div style={{...base, position: 'absolute', left: 0, top: 0, color: '#6d0000', transform: `translate(${size * 0.006}px, ${size * 0.03}px)`}}>{text}</div>
			{/* face */}
			<div
				style={{
					...base,
					position: 'relative',
					backgroundImage: `${NOISE}, linear-gradient(180deg, #ff8f84 0%, #ff3a2a 34%, #e00a00 58%, #8f0000 100%)`,
					backgroundSize: '140px 140px, 100% 100%',
					WebkitBackgroundClip: 'text',
					backgroundClip: 'text',
					color: 'transparent',
					WebkitTextStroke: `${Math.max(1.5, size * 0.012)}px rgba(255,190,180,0.55)`,
					filter: `drop-shadow(0 0 ${size * 0.18}px rgba(255,20,0,0.75))`,
				}}
			>
				{text}
			</div>
		</div>
	);
};

export const subStyle = (size = 62): React.CSSProperties => ({
	fontFamily: 'Poppins',
	fontWeight: 800,
	fontSize: size,
	lineHeight: 1.04,
	letterSpacing: -0.5,
	textTransform: 'uppercase',
	color: WHITE,
	textShadow: '0 3px 0 rgba(0,0,0,0.35), 0 4px 18px rgba(0,0,0,0.65), 0 0 2px rgba(0,0,0,0.6)',
	whiteSpace: 'nowrap',
});

// ------------------------------------------------------------------ boxes & pills
export const LabelBox: React.FC<{children: React.ReactNode; style?: React.CSSProperties; light?: boolean}> = ({children, style, light}) => (
	<div
		style={{
			display: 'inline-flex',
			flexDirection: 'column',
			alignItems: 'center',
			padding: '14px 30px 16px',
			borderRadius: 16,
			background: light ? 'linear-gradient(180deg,#ffffff,#f1f1f1)' : 'linear-gradient(180deg,#ff4a3a 0%,#ef1407 45%,#b80000 100%)',
			boxShadow: light
				? '0 0 0 3px rgba(255,31,18,0.95), 0 0 38px rgba(255,31,18,0.6), 0 16px 34px rgba(0,0,0,0.5)'
				: 'inset 0 2px 0 rgba(255,255,255,0.45), inset 0 -3px 0 rgba(80,0,0,0.5), 0 0 0 2px rgba(255,255,255,0.55), 0 0 44px rgba(255,25,10,0.8), 0 18px 36px rgba(0,0,0,0.55)',
			...style,
		}}
	>
		{children}
	</div>
);

export const labelText = (size: number, color = WHITE): React.CSSProperties => ({
	fontFamily: 'Poppins',
	fontWeight: 900,
	fontStyle: 'italic',
	fontSize: size,
	lineHeight: 1,
	letterSpacing: -size * 0.015,
	textTransform: 'uppercase',
	color,
	textShadow: color === WHITE ? '0 3px 0 rgba(90,0,0,0.55), 0 0 14px rgba(0,0,0,0.25)' : 'none',
	whiteSpace: 'nowrap',
});

export const Pill: React.FC<{children: React.ReactNode; style?: React.CSSProperties; red?: boolean}> = ({children, style, red}) => (
	<div
		style={{
			display: 'inline-flex',
			alignItems: 'center',
			gap: 14,
			padding: '12px 30px',
			borderRadius: 999,
			background: red ? 'linear-gradient(180deg,#ff4334,#d40800)' : 'linear-gradient(180deg,#1b1b1b,#050505)',
			border: red ? '2px solid rgba(255,255,255,0.6)' : `3px solid ${RED}`,
			boxShadow: red ? '0 0 34px rgba(255,30,10,0.75), 0 12px 26px rgba(0,0,0,0.5)' : '0 0 26px rgba(255,31,18,0.65), 0 12px 26px rgba(0,0,0,0.55)',
			fontFamily: 'Poppins',
			fontWeight: 800,
			color: WHITE,
			textTransform: 'uppercase',
			whiteSpace: 'nowrap',
			...style,
		}}
	>
		{children}
	</div>
);

// ------------------------------------------------------------------ icons
export const PinIcon: React.FC<{size?: number}> = ({size = 44}) => (
	<svg width={size} height={size} viewBox="0 0 24 24">
		<path d="M12 2c-3.9 0-7 3.1-7 7 0 5.2 7 13 7 13s7-7.8 7-13c0-3.9-3.1-7-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z" fill="#fff" />
	</svg>
);
export const ChatIcon: React.FC<{size?: number; color?: string}> = ({size = 54, color = '#fff'}) => (
	<svg width={size} height={size} viewBox="0 0 24 24">
		<path d="M4 3h16a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H9l-5 4v-4H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z" fill={color} />
		<circle cx="8" cy="10.5" r="1.4" fill={RED} />
		<circle cx="12" cy="10.5" r="1.4" fill={RED} />
		<circle cx="16" cy="10.5" r="1.4" fill={RED} />
	</svg>
);
export const CheckIcon: React.FC<{size?: number; color?: string}> = ({size = 40, color = RED}) => (
	<svg width={size} height={size} viewBox="0 0 24 24">
		<circle cx="12" cy="12" r="11" fill={color} />
		<path d="M6.5 12.5l3.5 3.5 7.5-8" stroke="#fff" strokeWidth="2.8" fill="none" strokeLinecap="round" strokeLinejoin="round" />
	</svg>
);

export const BigX: React.FC<{size: number; style?: React.CSSProperties}> = ({size, style}) => {
	const bar: React.CSSProperties = {
		position: 'absolute',
		left: '50%',
		top: '50%',
		width: size,
		height: size * 0.2,
		marginLeft: -size / 2,
		marginTop: -size * 0.1,
		borderRadius: size * 0.04,
		background: 'linear-gradient(180deg,#ff6b5e,#e00a00 55%,#8f0000)',
		boxShadow: `0 0 ${size * 0.25}px rgba(255,20,0,0.85)`,
	};
	return (
		<div style={{position: 'absolute', width: size, height: size, ...style}}>
			<div style={{...bar, transform: 'rotate(45deg)'}} />
			<div style={{...bar, transform: 'rotate(-45deg)'}} />
		</div>
	);
};

// ------------------------------------------------------------------ media
export const Clip: React.FC<{src: string; start: number; rate?: number; style?: React.CSSProperties; grade?: string}> = ({src, start, rate, style, grade}) => (
	<OffthreadVideo
		src={staticFile(src)}
		trimBefore={Math.max(0, Math.round(start * FPS))}
		playbackRate={rate ?? 1}
		muted
		style={{width: '100%', height: '100%', objectFit: 'cover', filter: grade === 'dark' ? 'contrast(1.12) saturate(1.15) brightness(0.86)' : 'contrast(1.07) saturate(1.1)', ...style}}
	/>
);

export const Card: React.FC<{src: string; start: number; w: number; h: number; style?: React.CSSProperties; radius?: number; light?: boolean}> = ({src, start, w, h, style, radius = 34, light}) => (
	<div
		style={{
			position: 'absolute',
			width: w,
			height: h,
			borderRadius: radius,
			overflow: 'hidden',
			boxShadow: light
				? '0 0 0 4px rgba(255,255,255,0.95), 0 26px 60px rgba(120,0,0,0.35), 0 0 60px rgba(255,31,18,0.35)'
				: '0 0 0 3px rgba(255,255,255,0.92), 0 0 46px 6px rgba(255,30,10,0.7), 0 34px 70px rgba(0,0,0,0.6)',
			background: '#111',
			...style,
		}}
	>
		<Clip src={src} start={start} />
	</div>
);

// ------------------------------------------------------------------ backgrounds
export const DarkBG: React.FC = () => {
	const frame = useCurrentFrame();
	const dx = Math.sin(frame / 22) * 6;
	const dy = Math.cos(frame / 27) * 5;
	return (
		<AbsoluteFill>
			<AbsoluteFill style={{background: `radial-gradient(130% 85% at ${78 + dx}% ${102 + dy}%, #ff2a12 0%, #c10000 20%, #4a0000 44%, #0b0000 66%, #000 100%)`}} />
			<AbsoluteFill style={{background: `radial-gradient(60% 40% at ${12 - dx}% ${8 - dy}%, rgba(255,40,20,0.28) 0%, rgba(0,0,0,0) 70%)`}} />
		</AbsoluteFill>
	);
};

export const LightBG: React.FC = () => {
	const frame = useCurrentFrame();
	const d = Math.sin(frame / 25) * 4;
	return <AbsoluteFill style={{background: `radial-gradient(95% 72% at 50% ${44 + d}%, #ffffff 0%, #ffffff 38%, #ffe7e4 60%, #ff7a6c 86%, #e30c00 100%)`}} />;
};

export const Brackets: React.FC<{x: number; y: number; w: number; h: number; color?: string; len?: number}> = ({x, y, w, h, color = RED, len = 46}) => {
	const t = 7;
	const c = (st: React.CSSProperties) => <div style={{position: 'absolute', width: len, height: len, ...st}} />;
	const glow = `drop-shadow(0 0 10px ${color})`;
	return (
		<div style={{position: 'absolute', left: x, top: y, width: w, height: h, filter: glow}}>
			{c({left: 0, top: 0, borderLeft: `${t}px solid ${color}`, borderTop: `${t}px solid ${color}`, borderTopLeftRadius: 12})}
			{c({right: 0, top: 0, borderRight: `${t}px solid ${color}`, borderTop: `${t}px solid ${color}`, borderTopRightRadius: 12})}
			{c({left: 0, bottom: 0, borderLeft: `${t}px solid ${color}`, borderBottom: `${t}px solid ${color}`, borderBottomLeftRadius: 12})}
			{c({right: 0, bottom: 0, borderRight: `${t}px solid ${color}`, borderBottom: `${t}px solid ${color}`, borderBottomRightRadius: 12})}
		</div>
	);
};

export const Grain: React.FC = () => {
	const frame = useCurrentFrame();
	const x = (frame * 137) % 512;
	const y = (frame * 241) % 512;
	return (
		<AbsoluteFill
			style={{
				backgroundImage: `url(${staticFile('grain.png')})`,
				backgroundPosition: `${x}px ${y}px`,
				opacity: 0.07,
				mixBlendMode: 'overlay',
				pointerEvents: 'none',
			}}
		/>
	);
};

export const Vignette: React.FC = () => <AbsoluteFill style={{background: 'radial-gradient(120% 90% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.38) 100%)', pointerEvents: 'none'}} />;

export const useLocal = () => {
	const frame = useCurrentFrame();
	const {durationInFrames} = useVideoConfig();
	return {frame, dur: durationInFrames};
};

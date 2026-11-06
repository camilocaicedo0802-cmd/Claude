import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {BLACK, Brackets, Card, CheckIcon, Clip, DarkBG, LabelBox, LightBG, Pill, RED, WHITE, clamp, f, fit, labelText, pop, texWhite, useZoomBlurIn} from './fx';

type V = any;

const Enter: React.FC<{v: V; children: React.ReactNode}> = ({v, children}) => {
	const zb = useZoomBlurIn(7, 1.38);
	const frame = useCurrentFrame();
	if (v.enter === 'zoomblur') return <AbsoluteFill style={zb}>{children}</AbsoluteFill>;
	if (v.enter === 'cut') {
		// punch-in cut: 2-frame scale overshoot
		const s = interpolate(frame, [0, 3], [1.08, 1], clamp);
		return <AbsoluteFill style={{transform: `scale(${s})`}}>{children}</AbsoluteFill>;
	}
	return <AbsoluteFill>{children}</AbsoluteFill>;
};

// ---------------------------------------------------------------- footage
const Footage: React.FC<{v: V; dur: number}> = ({v, dur}) => {
	const frame = useCurrentFrame();
	const z = interpolate(frame, [0, dur], v.zoom ?? [1.05, 1.1], {...clamp, easing: Easing.inOut(Easing.sin)});
	let sx = 0;
	let sy = 0;
	if (v.shake) {
		const k = interpolate(frame, [0, 10], [1, 0], clamp) * v.shake * 40;
		sx = Math.sin(frame * 2.7) * k;
		sy = Math.cos(frame * 3.3) * k;
	}
	const o = v.origin ?? [50, 50];
	return (
		<AbsoluteFill style={{transform: `translate(${sx}px, ${sy}px) scale(${z})`, transformOrigin: `${o[0]}% ${o[1]}%`}}>
			<Clip src={v.src} start={v.srcStart} rate={v.rate} grade={v.grade} />
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- dark cards (ref: INTERIOR and EXTERIOR)
const DarkCards: React.FC<{v: V; dur: number}> = ({v}) => {
	const frame = useCurrentFrame();
	const [c1, c2] = v.cards;
	const t2 = f(c2.at);
	const c1x = interpolate(frame, [t2 - 2, t2 + 7], [540, c1.x], {...clamp, easing: Easing.out(Easing.cubic)});
	const c1in = interpolate(frame, [0, 8], [1.5, 1], {...clamp, easing: Easing.out(Easing.back(1.4))});
	const c1b = interpolate(frame, [0, 6], [20, 0], clamp);
	const c2x = interpolate(frame, [t2, t2 + 8], [1500, c2.x], {...clamp, easing: Easing.out(Easing.back(1.2))});
	const c2b = interpolate(frame, [t2, t2 + 6], [24, 0], clamp);
	const drift = Math.sin(frame / 18) * 6;
	return (
		<AbsoluteFill>
			<DarkBG />
			<div style={{position: 'absolute', left: c1x - c1.w / 2, top: c1.y - c1.h / 2 + drift, transform: `scale(${c1in}) rotate(-2deg)`, filter: `blur(${c1b}px)`}}>
				<Card src={c1.src} start={c1.srcStart} w={c1.w} h={c1.h} style={{position: 'relative'}} />
			</div>
			{frame >= t2 && (
				<div style={{position: 'absolute', left: c2x - c2.w / 2, top: c2.y - c2.h / 2 - drift, transform: 'rotate(2deg)', filter: `blur(${c2b}px)`}}>
					<Card src={c2.src} start={c2.srcStart} w={c2.w} h={c2.h} style={{position: 'relative'}} />
				</div>
			)}
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- collage (ref: smear marks grid)
const Collage: React.FC<{v: V; dur: number}> = ({v, dur}) => {
	const frame = useCurrentFrame();
	const tiles: [string, number][] = v.tiles;
	const colA = tiles.filter((_, i) => i % 2 === 0);
	const colB = tiles.filter((_, i) => i % 2 === 1);
	const yA = interpolate(frame, [0, dur], [-120, -420], clamp);
	const yB = interpolate(frame, [0, dur], [-460, -160], clamp);
	const tileW = 430;
	const tileH = 560;
	const col = (list: [string, number][], x: number, y: number) => (
		<div style={{position: 'absolute', left: x, top: y, display: 'flex', flexDirection: 'column', gap: 28}}>
			{list.map(([src, st], i) => (
				<div key={i} style={{position: 'relative', width: tileW, height: tileH}}>
					<Card src={src} start={st} w={tileW} h={tileH} radius={38} light style={{left: 0, top: 0}} />
				</div>
			))}
		</div>
	);
	return (
		<AbsoluteFill>
			<LightBG />
			<AbsoluteFill style={{transform: 'rotate(-7deg) scale(1.12)', transformOrigin: '50% 50%'}}>
				{col(colA, 70, yA)}
				{col(colB, 580, yB)}
			</AbsoluteFill>
			{/* soft wash so the red tags read */}
			<AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(255,255,255,0.0) 0%, rgba(255,255,255,0.0) 60%, rgba(255,60,40,0.35) 100%)'}} />
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- floating 3D cards (ref: DEEP VACUUM)
const Float3D: React.FC<{v: V; dur: number}> = ({v}) => {
	const frame = useCurrentFrame();
	const [a, b] = v.cards;
	const tb = f(b.at);
	const ain = interpolate(frame, [0, 9], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.3))});
	const bin = interpolate(frame, [tb, tb + 9], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.3))});
	const rot = Math.sin(frame / 14) * 4;
	const lab = (text: string, p: number) => (
		<div style={{position: 'absolute', left: '50%', bottom: -96, transform: `translateX(-50%) scale(${p})`}}>
			<LabelBox style={{padding: '10px 26px 12px'}}>
				<div style={labelText(text.length > 12 ? 46 : 58)}>{text}</div>
			</LabelBox>
		</div>
	);
	return (
		<AbsoluteFill>
			<DarkBG />
			<AbsoluteFill style={{perspective: 1500}}>
				<div
					style={{
						position: 'absolute',
						left: 200,
						top: 230,
						width: 480,
						height: 660,
						transform: `translate(${(1 - ain) * -500}px, ${(1 - ain) * 300}px) rotateY(${18 + rot}deg) rotateX(${8 - rot / 2}deg) rotateZ(-6deg)`,
						transformStyle: 'preserve-3d',
						opacity: ain > 0 ? 1 : 0,
					}}
				>
					<Card src={a.src} start={a.srcStart} w={480} h={660} style={{left: 0, top: 0}} />
					{lab(a.label, Math.min(1, ain * 1.1))}
				</div>
				{frame >= tb && (
					<div
						style={{
							position: 'absolute',
							left: 420,
							top: 960,
							width: 480,
							height: 660,
							transform: `translate(${(1 - bin) * 600}px, ${(1 - bin) * 200}px) rotateY(${-18 - rot}deg) rotateX(${-6 + rot / 2}deg) rotateZ(4deg)`,
							transformStyle: 'preserve-3d',
						}}
					>
						<Card src={b.src} start={b.srcStart} w={480} h={660} style={{left: 0, top: 0}} />
						{lab(b.label, Math.min(1, bin * 1.1))}
					</div>
				)}
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- light card (ref: crumbs on the floor)
const LightCardScene: React.FC<{v: V; dur: number}> = ({v, dur}) => {
	const frame = useCurrentFrame();
	const W = 880;
	const H = 1240;
	const x = (1080 - W) / 2;
	const y = 400;
	const z = interpolate(frame, [0, dur], [1.0, 1.06], clamp);
	return (
		<AbsoluteFill>
			<LightBG />
			<div style={{position: 'absolute', left: x, top: y, width: W, height: H, borderRadius: 44, overflow: 'hidden', boxShadow: '0 0 0 5px #fff, 0 30px 70px rgba(120,0,0,0.35), 0 0 70px rgba(255,31,18,0.35)'}}>
				<div style={{width: '100%', height: '100%', transform: `scale(${z})`}}>
					<Clip src={v.src} start={v.srcStart} style={{objectPosition: '42% 50%'}} />
				</div>
				<AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,0) 45%, rgba(0,0,0,0.35) 100%)'}} />
			</div>
			<Brackets x={x - 34} y={y - 34} w={W + 68} h={H + 68} />
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- clone scene (interactive progress)
const CloneScene: React.FC<{v: V; dur: number}> = ({v}) => {
	const frame = useCurrentFrame();
	const tV = f(v.tVieja);
	const tN = f(v.tNueva);
	const tOk = f(v.tValores);
	const p0 = 12;
	const prog = interpolate(frame, [p0, tOk - 2], [0, 100], {...clamp, easing: Easing.inOut(Easing.quad)});
	const lIn = interpolate(frame, [0, 8], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.3))});
	const rIn = interpolate(frame, [4, 12], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.3))});
	const titleP = pop(frame, 0);
	const tagV = pop(frame, tV);
	const tagN = pop(frame, tN);
	const ok = pop(frame, tOk);
	const cw = 430;
	const ch = 590;
	const cy = 560;
	return (
		<AbsoluteFill>
			<DarkBG />
			{/* title */}
			<div style={{position: 'absolute', top: 330, width: '100%', display: 'flex', justifyContent: 'center', transform: `scale(${interpolate(titleP, [0, 1], [1.6, 1])})`, opacity: Math.min(1, titleP * 2)}}>
				<div style={texWhite(150)}>CLONAR</div>
			</div>
			{/* cards */}
			<div style={{position: 'absolute', left: 60, top: cy, transform: `translateX(${(1 - lIn) * -600}px) rotate(-3deg)`}}>
				<Card src={v.left.src} start={v.left.srcStart} w={cw} h={ch} style={{position: 'relative', filter: 'grayscale(0.6) brightness(0.85)'}} />
				<div style={{position: 'absolute', left: '50%', bottom: -40, transform: `translateX(-50%) scale(${tagV})`}}>
					<Pill red style={{fontSize: 46, padding: '8px 30px'}}>VIEJA</Pill>
				</div>
			</div>
			<div style={{position: 'absolute', left: 590, top: cy, transform: `translateX(${(1 - rIn) * 600}px) rotate(3deg)`}}>
				<Card src={v.right.src} start={v.right.srcStart} w={cw} h={ch} style={{position: 'relative'}} />
				<div style={{position: 'absolute', left: '50%', bottom: -40, transform: `translateX(-50%) scale(${tagN})`}}>
					<Pill style={{fontSize: 46, padding: '8px 30px', background: '#fff', color: BLACK}}>NUEVA</Pill>
				</div>
			</div>
			{/* data stream */}
			{prog > 0 && prog < 100 &&
				new Array(5).fill(0).map((_, i) => {
					const t = ((frame * 0.07 + i / 5) % 1);
					return (
						<div
							key={i}
							style={{
								position: 'absolute',
								left: 440 + t * 200,
								top: cy + ch / 2 - 14,
								width: 28,
								height: 28,
								borderRadius: 6,
								background: RED,
								boxShadow: `0 0 18px ${RED}`,
								opacity: Math.sin(t * Math.PI),
								transform: 'rotate(45deg)',
							}}
						/>
					);
				})}
			{/* progress */}
			<div style={{position: 'absolute', left: 120, top: 1330, width: 840}}>
				<div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, fontFamily: 'Poppins', fontWeight: 800, fontSize: 40, color: WHITE, textTransform: 'uppercase'}}>
					{frame < tOk ? <span>CLONANDO INFORMACIÓN</span> : (
						<span style={{display: 'flex', alignItems: 'center', gap: 14, transform: `scale(${ok})`, transformOrigin: 'left center'}}>
							<CheckIcon size={48} /> MISMOS VALORES
						</span>
					)}
					<span style={{color: RED, fontStyle: 'italic', fontWeight: 900, textShadow: `0 0 16px ${RED}`}}>{Math.round(prog)}%</span>
				</div>
				<div style={{height: 30, borderRadius: 99, background: 'rgba(255,255,255,0.14)', boxShadow: 'inset 0 0 0 2px rgba(255,255,255,0.25)', overflow: 'hidden'}}>
					<div style={{width: `${prog}%`, height: '100%', borderRadius: 99, background: 'linear-gradient(90deg,#9a0000,#ff2a1a 80%,#ff9a90)', boxShadow: `0 0 24px ${RED}`}} />
				</div>
			</div>
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- landscape clip on dark (installation)
const DarkWide: React.FC<{v: V; dur: number}> = ({v, dur}) => {
	const frame = useCurrentFrame();
	const W = 980;
	const H = 760;
	const tilt = interpolate(frame, [0, dur], [10, 4], clamp);
	return (
		<AbsoluteFill>
			<DarkBG />
			<AbsoluteFill style={{perspective: 1600}}>
				<div style={{position: 'absolute', left: (1080 - W) / 2, top: 520, width: W, height: H, transform: `rotateX(${tilt}deg) rotateY(${-tilt / 2}deg)`}}>
					<Card src={v.src} start={v.srcStart} w={W} h={H} style={{left: 0, top: 0}} />
				</div>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- end card
const EndCard: React.FC<{v: V; dur: number}> = ({v, dur}) => {
	const frame = useCurrentFrame();
	const z = interpolate(frame, [0, dur], [1.12, 1.22], clamp);
	return (
		<AbsoluteFill>
			<AbsoluteFill style={{transform: `scale(${z})`, transformOrigin: '50% 60%'}}>
				<Clip src={v.src} start={v.srcStart} rate={v.rate} style={{filter: 'contrast(1.1) saturate(1.15) brightness(0.62) blur(2px)'}} />
			</AbsoluteFill>
			<AbsoluteFill style={{background: 'radial-gradient(110% 70% at 50% 100%, rgba(255,20,0,0.55) 0%, rgba(80,0,0,0.35) 40%, rgba(0,0,0,0.55) 100%)'}} />
		</AbsoluteFill>
	);
};

export const Visual: React.FC<{v: V}> = ({v}) => {
	const dur = f(v.to) - f(v.from);
	let inner: React.ReactNode = null;
	switch (v.kind) {
		case 'speaker':
		case 'broll':
			inner = <Footage v={v} dur={dur} />;
			break;
		case 'darkcards':
			inner = <DarkCards v={v} dur={dur} />;
			break;
		case 'collage':
			inner = <Collage v={v} dur={dur} />;
			break;
		case 'float3d':
			inner = <Float3D v={v} dur={dur} />;
			break;
		case 'lightcard':
			inner = <LightCardScene v={v} dur={dur} />;
			break;
		case 'clone':
			inner = <CloneScene v={v} dur={dur} />;
			break;
		case 'darkwide':
			inner = <DarkWide v={v} dur={dur} />;
			break;
		case 'endcard':
			inner = <EndCard v={v} dur={dur} />;
			break;
	}
	return (
		<AbsoluteFill style={{overflow: 'hidden', background: '#000'}}>
			<Enter v={v}>{inner}</Enter>
		</AbsoluteFill>
	);
};

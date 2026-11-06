import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {BLACK, BigX, ChatIcon, CheckIcon, LabelBox, Pill, PinIcon, RED, RedBevel, WHITE, clamp, f, fit, labelText, pop, subStyle, texWhite} from './fx';

type O = any;

const Center: React.FC<{y: number; children: React.ReactNode; style?: React.CSSProperties}> = ({y, children, style}) => (
	<div style={{position: 'absolute', left: 0, top: y, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', ...style}}>{children}</div>
);

// exit: quick scale-up + blur on the last 4 frames
const useExit = (dur: number) => {
	const frame = useCurrentFrame();
	const e = interpolate(frame, [dur - 4, dur], [0, 1], clamp);
	return {transform: `scale(${1 + e * 0.25})`, opacity: 1 - e, filter: `blur(${e * 14}px)`};
};

// glitch: RGB split jitter for a few frames after `at`
const glitch = (frame: number, at: number, len = 7) => {
	const k = interpolate(frame, [at, at + len], [1, 0], clamp) * (frame >= at ? 1 : 0);
	const j = Math.sin(frame * 12.9898) * 43758.5453;
	const r = j - Math.floor(j);
	return {k, dx: (r - 0.5) * 40 * k, dy: (Math.cos(frame * 7.1) * 10) * k};
};

// ---------------------------------------------------------------- HOOK (ref: WHAT DOES THIS CAR NEED? typed)
const Hook: React.FC<{o: O; dur: number}> = ({o, dur}) => {
	const frame = useCurrentFrame();
	const ex = useExit(dur);
	const t2 = f(o.tLine2 - o.from);
	const chars = o.line1.split('');
	const per = Math.max(1, (t2 - 2) / chars.length);
	const g = glitch(frame, t2);
	const p2 = pop(frame, t2, 30, 9);
	const sz2 = fit('FALLANDO?', 168, 980, 0.72);
	return (
		<Center y={1020} style={ex}>
			<div style={{...texWhite(fit(o.line1, 60, 960, 0.64)), display: 'flex'}}>
				{chars.map((c: string, i: number) => {
					const t = frame + 4 - i * per;
					const a = interpolate(t, [0, 3], [0, 1], clamp);
					return (
						<span key={i} style={{opacity: a, display: 'inline-block', transform: `scale(${interpolate(t, [0, 3], [1.6, 1], clamp)})`, filter: `blur(${(1 - a) * 8}px)`, whiteSpace: 'pre'}}>
							{c}
						</span>
					);
				})}
			</div>
			{frame >= t2 && (
				<div style={{position: 'relative', marginTop: 16, transform: `scale(${interpolate(p2, [0, 1], [2.2, 1])}) translate(${g.dx}px, ${g.dy}px)`, opacity: Math.min(1, p2 * 3)}}>
					<div style={{...texWhite(78), textAlign: 'center', marginBottom: -6}}>ESTÁ</div>
					{g.k > 0.05 && (
						<>
							<div style={{position: 'absolute', left: -14 * g.k, bottom: 0, opacity: 0.7 * g.k, mixBlendMode: 'screen'}}>
								<div style={{fontFamily: 'Poppins', fontWeight: 900, fontStyle: 'italic', fontSize: sz2, color: '#00e5ff', lineHeight: 0.92, letterSpacing: -sz2 * 0.025}}>FALLANDO?</div>
							</div>
						</>
					)}
					<RedBevel text="FALLANDO?" size={sz2} />
				</div>
			)}
		</Center>
	);
};

// ---------------------------------------------------------------- BIG WORD (ref: This BEAUTIFUL [G80])
const BigWord: React.FC<{o: O; dur: number}> = ({o, dur}) => {
	const frame = useCurrentFrame();
	const ex = useExit(dur);
	const s = interpolate(frame, [0, 6], [1.9, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const b = interpolate(frame, [0, 5], [16, 0], clamp);
	const ghosts = [0.35, 0.18];
	const sz = fit(o.big, 190, 1000, 0.7);
	const pillX = interpolate(frame, [9, 16], [600, 0], {...clamp, easing: Easing.out(Easing.back(1.6))});
	const small = pop(frame, 2);
	return (
		<Center y={o.y - 120} style={ex}>
			<div style={{...texWhite(70), alignSelf: 'flex-start', marginLeft: 120, transform: `translateY(${(1 - small) * 30}px)`, opacity: small}}>{o.small}</div>
			<div style={{position: 'relative'}}>
				{frame < 8 &&
					ghosts.map((op, i) => (
						<div key={i} style={{position: 'absolute', left: 0, top: 0, opacity: op, transform: `scale(${s + 0.25 * (i + 1)})`, filter: `blur(${b + 6}px)`}}>
							<div style={texWhite(sz)}>{o.big}</div>
						</div>
					))}
				<div style={{transform: `scale(${s})`, filter: `blur(${b}px)`}}>
					<div style={texWhite(sz)}>{o.big}</div>
				</div>
			</div>
			{frame >= 9 && (
				<div style={{alignSelf: 'flex-end', marginRight: 130, marginTop: 4, transform: `translateX(${pillX}px)`}}>
					<Pill style={{fontSize: 44, padding: '6px 30px'}}>{o.pill}</Pill>
				</div>
			)}
		</Center>
	);
};

// ---------------------------------------------------------------- LOCATION TAG
const Location: React.FC<{o: O; dur: number}> = ({o, dur}) => {
	const frame = useCurrentFrame();
	const ex = useExit(dur);
	const a = pop(frame, 0);
	const tb = f(o.tB);
	const b = pop(frame, tb);
	return (
		<Center y={1240} style={ex}>
			<div style={{transform: `scale(${a})`}}>
				<Pill red style={{fontSize: 64, padding: '12px 40px 12px 28px', fontStyle: 'italic', fontWeight: 900}}>
					<PinIcon size={60} /> {o.a}
				</Pill>
			</div>
			{frame >= tb && (
				<div style={{marginTop: 18, transform: `translateY(${(1 - b) * 40}px) scale(${0.6 + 0.4 * b})`, opacity: b}}>
					<Pill style={{fontSize: 48, padding: '8px 32px'}}>{o.b}</Pill>
				</div>
			)}
		</Center>
	);
};

// ---------------------------------------------------------------- LABEL (ref: INTERIOR and EXTERIOR / DEEP CLEANING)
const Label: React.FC<{o: O; dur: number}> = ({o, dur}) => {
	const frame = useCurrentFrame();
	const ex = useExit(dur);
	const p = interpolate(frame, [0, 7], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.7))});
	const t2 = f(o.tLine2);
	const q = interpolate(frame, [t2, t2 + 6], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.5))});
	const [w1, w2] = o.line1.split(' ');
	return (
		<Center y={o.y} style={ex}>
			<div style={{transform: `translateY(${(1 - p) * 120}px) scale(${0.7 + 0.3 * p})`, opacity: Math.min(1, p * 2)}}>
				<LabelBox>
					<div style={{display: 'flex', alignItems: 'baseline', gap: 14}}>
						<span style={labelText(64)}>{w1}</span>
						<span style={{...labelText(64), color: BLACK, background: WHITE, padding: '2px 14px', borderRadius: 8, textShadow: 'none'}}>{w2}</span>
					</div>
					{frame >= t2 && (
						<div style={{...labelText(fit(o.line2, 112, 880, 0.72)), marginTop: 4, transform: `translateX(${(1 - q) * 260}px)`, opacity: q}}>{o.line2}</div>
					)}
				</LabelBox>
			</div>
		</Center>
	);
};

// ---------------------------------------------------------------- CODES (ref: Smear marks + X)
const Codes: React.FC<{o: O; dur: number}> = ({o, dur}) => {
	const frame = useCurrentFrame();
	const ex = useExit(dur);
	const tp = pop(frame, 2);
	return (
		<AbsoluteFill style={ex}>
			<Center y={250}>
				<div style={{transform: `scale(${tp})`}}>
					<Pill style={{fontSize: 52, padding: '12px 36px', fontWeight: 900, fontStyle: 'italic'}}>
						<span style={{color: RED, textShadow: `0 0 14px ${RED}`}}>2</span> {o.title}
					</Pill>
				</div>
			</Center>
			{o.codes.map(([code, at]: [string, number], i: number) => {
				const t = f(at);
				if (frame < t) return null;
				const p = pop(frame, t, 30, 8);
				const xs = interpolate(frame, [t, t + 6], [2.4, 1], {...clamp, easing: Easing.out(Easing.cubic)});
				const g = glitch(frame, t, 6);
				const y = i === 0 ? 760 : 1150;
				return (
					<div key={code} style={{position: 'absolute', left: 0, top: y, width: '100%', height: 300}}>
						<div style={{position: 'absolute', left: '50%', top: '50%', width: 900, height: 600, marginLeft: -450, marginTop: -300, background: 'radial-gradient(closest-side, rgba(255,25,10,0.55), rgba(255,25,10,0))'}} />
						<BigX size={470} style={{left: 540 - 235, top: 150 - 235, transform: `scale(${xs})`, opacity: Math.min(1, (frame - t) / 3)}} />
						<div style={{position: 'absolute', left: '50%', top: '50%', transform: `translate(-50%,-50%) translate(${g.dx}px, ${g.dy}px) scale(${p})`}}>
							<LabelBox style={{padding: '10px 40px 14px', flexDirection: 'row', gap: 18}}>
								<span style={{...labelText(32), opacity: 0.85}}>CÓDIGO</span>
								<span style={labelText(74)}>{code}</span>
							</LabelBox>
						</div>
					</div>
				);
			})}
		</AbsoluteFill>
	);
};

// ---------------------------------------------------------------- IMPACT (ref: CAKED UP)
const Impact: React.FC<{o: O; dur: number}> = ({o, dur}) => {
	const frame = useCurrentFrame();
	const ex = useExit(dur);
	const a = interpolate(frame, [0, 4], [2.3, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const ab = interpolate(frame, [0, 4], [18, 0], clamp);
	const b = interpolate(frame, [3, 7], [2.6, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const bb = interpolate(frame, [3, 7], [20, 0], clamp);
	const shake = interpolate(frame, [7, 16], [1, 0], clamp) * (frame >= 7 ? 1 : 0);
	const sx = Math.sin(frame * 3.1) * 16 * shake;
	const sy = Math.cos(frame * 2.3) * 12 * shake;
	const u = pop(frame, 10);
	const bigSz = fit(o.big, 230, 1000, 0.72);
	return (
		<Center y={o.y - 200} style={{...ex, transform: `${ex.transform} translate(${sx}px, ${sy}px)`}}>
			<div style={{transform: `scale(${a})`, filter: `blur(${ab}px)`, marginBottom: -18}}>
				<RedBevel text={o.small} size={150} />
			</div>
			{frame >= 3 && (
				<div style={{transform: `scale(${b})`, filter: `blur(${bb}px)`}}>
					<RedBevel text={o.big} size={bigSz} />
				</div>
			)}
			{frame >= 10 && (
				<div style={{...texWhite(84), marginTop: 10, transform: `translateY(${(1 - u) * 40}px)`, opacity: u}}>{o.under}</div>
			)}
		</Center>
	);
};

// ---------------------------------------------------------------- STEP CHIP
export const StepChip: React.FC<{text: string; sub?: string; dur: number}> = ({text, sub, dur}) => {
	const frame = useCurrentFrame();
	const ex = useExit(dur);
	const p = interpolate(frame, [0, 8], [-260, 0], {...clamp, easing: Easing.out(Easing.back(1.4))});
	return (
		<Center y={190} style={ex}>
			<div style={{transform: `translateY(${p}px)`, display: 'flex', borderRadius: 999, overflow: 'hidden', boxShadow: `0 0 0 3px ${RED}, 0 0 30px rgba(255,31,18,0.7), 0 14px 30px rgba(0,0,0,0.5)`}}>
				<div style={{background: 'linear-gradient(180deg,#ff4334,#c90000)', padding: '10px 26px', fontFamily: 'Poppins', fontWeight: 900, fontStyle: 'italic', fontSize: 40, color: WHITE}}>{text}</div>
				{sub && <div style={{background: BLACK, padding: '10px 30px', fontFamily: 'Poppins', fontWeight: 800, fontSize: 40, color: WHITE, letterSpacing: 1}}>{sub}</div>}
			</div>
		</Center>
	);
};

// ---------------------------------------------------------------- STEP WORD (ref: CONTACT WASH / AND DRY)
const StepWord: React.FC<{o: O; dur: number}> = ({o, dur}) => {
	const frame = useCurrentFrame();
	const ex = useExit(dur);
	const s = interpolate(frame, [0, 6], [1.7, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const b = interpolate(frame, [0, 5], [18, 0], clamp);
	const sm = pop(frame, 4);
	const y = o.y ?? 1060;
	const sz = fit(o.big, 190, 980, 0.74);
	return (
		<>
			<StepChip text={o.step} dur={dur} />
			<Center y={y - 110} style={ex}>
				{o.small && <div style={{...texWhite(64), transform: `translateY(${(1 - sm) * -30}px)`, opacity: sm, marginBottom: 2}}>{o.small}</div>}
				<div style={{transform: `scale(${s})`, filter: `blur(${b}px)`}}>
					<div style={texWhite(sz)}>{o.big}</div>
				</div>
			</Center>
		</>
	);
};

// ---------------------------------------------------------------- CTA + closing
const Cta: React.FC<{o: O; dur: number; endAt: number}> = ({o, dur, endAt}) => {
	const frame = useCurrentFrame();
	const a = pop(frame, 0, 30, 9);
	const b = pop(frame, 4, 30, 9);
	const g = glitch(frame, 4, 6);
	const move = interpolate(frame, [endAt, endAt + 10], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
	const y = interpolate(move, [0, 1], [1010, 560]);
	const btn = pop(frame, endAt + 10);
	const pulse = 1 + Math.sin((frame - endAt) / 3.2) * 0.035 * (frame > endAt + 18 ? 1 : 0);
	const chip = pop(frame, endAt + 4);
	const line = interpolate(frame, [endAt + 16, endAt + 26], [0, 1], clamp);
	const sz = fit('UN MENSAJE', 150, 980, 0.72);
	const fadeOut = interpolate(frame, [dur - 6, dur], [1, 0], clamp);
	return (
		<AbsoluteFill style={{opacity: fadeOut}}>
			{frame >= endAt && (
				<Center y={250}>
					<div style={{transform: `scale(${chip})`}}>
						<Pill style={{fontSize: 40, padding: '10px 30px'}}>
							<CheckIcon size={44} /> AUDI A3 · DSG REPARADA
						</Pill>
					</div>
				</Center>
			)}
			<Center y={y}>
				<div style={{...texWhite(120), transform: `scale(${interpolate(a, [0, 1], [1.8, 1])})`, opacity: Math.min(1, a * 3)}}>{o.small}</div>
				{frame >= 4 && (
					<div style={{transform: `scale(${interpolate(b, [0, 1], [2.2, 1])}) translate(${g.dx}px, ${g.dy}px)`, opacity: Math.min(1, b * 3), marginTop: 6}}>
						<RedBevel text={o.big} size={sz} />
					</div>
				)}
			</Center>
			{frame >= endAt + 10 && (
				<Center y={1060}>
					<div style={{transform: `scale(${btn * pulse})`}}>
						<div style={{display: 'flex', alignItems: 'center', gap: 20, padding: '24px 54px', borderRadius: 999, background: WHITE, boxShadow: `0 0 0 5px ${RED}, 0 0 50px rgba(255,31,18,0.85), 0 20px 40px rgba(0,0,0,0.5)`}}>
							<ChatIcon size={66} color={RED} />
							<span style={{fontFamily: 'Poppins', fontWeight: 900, fontStyle: 'italic', fontSize: 62, color: BLACK, textTransform: 'uppercase'}}>ESCRÍBENOS</span>
						</div>
					</div>
					<div style={{marginTop: 46, opacity: line, transform: `translateY(${(1 - line) * 20}px)`, fontFamily: 'Poppins', fontWeight: 700, fontSize: 31, color: WHITE, letterSpacing: 1, textShadow: '0 3px 12px rgba(0,0,0,0.7)', display: 'flex', gap: 12, alignItems: 'center'}}>
						DIAGNÓSTICO <span style={{color: RED}}>●</span> MECATRÓNICA <span style={{color: RED}}>●</span> PROGRAMACIÓN
					</div>
				</Center>
			)}
		</AbsoluteFill>
	);
};

export const Overlay: React.FC<{o: O; total: number}> = ({o, total}) => {
	const dur = f(o.to) - f(o.from);
	switch (o.kind) {
		case 'hook':
			return <Hook o={o} dur={dur} />;
		case 'bigword':
			return <BigWord o={o} dur={dur} />;
		case 'location':
			return <Location o={o} dur={dur} />;
		case 'label':
			return <Label o={o} dur={dur} />;
		case 'codes':
			return <Codes o={o} dur={dur} />;
		case 'impact':
			return <Impact o={o} dur={dur} />;
		case 'stepchip':
			return <StepChip text={o.text} sub={o.sub} dur={dur} />;
		case 'stepword':
			return <StepWord o={o} dur={dur} />;
		case 'cta':
			return <Cta o={o} dur={dur} endAt={f(o.endAt - o.from)} />;
	}
	return null;
};

// ---------------------------------------------------------------- SUBTITLES (minimal, word by word)
export const Subtitle: React.FC<{s: any}> = ({s}) => {
	const frame = useCurrentFrame();
	let idx = 0;
	const dur = f(s.to) - f(s.from);
	const out = interpolate(frame, [dur - 3, dur], [1, 0], clamp);
	return (
		<Center y={1210} style={{opacity: out}}>
			{s.lines.map((ln: any[], li: number) => (
				<div key={li} style={{display: 'flex', gap: 16, justifyContent: 'center'}}>
					{ln.map((w: any) => {
						const at = f(s.at[idx] - s.from);
						idx++;
						const t = frame - at;
						const a = interpolate(t, [0, 4], [0, 1], clamp);
						const c = interpolate(t, [2, 6], [0, 1], clamp);
						const col = w.red ? RED : WHITE;
						return (
							<span
								key={idx}
								style={{
									...subStyle(w.red ? 66 : 62),
									display: 'inline-block',
									opacity: t < 0 ? 0 : 0.35 + 0.65 * a,
									transform: `translateX(${(1 - a) * 18}px) scale(${0.92 + 0.08 * a})`,
									filter: `blur(${(1 - a) * 5}px)`,
									color: c < 1 ? (w.red ? '#ff8a80' : '#bdbdbd') : col,
									fontStyle: w.red ? 'italic' : 'normal',
									fontWeight: w.red ? 900 : 800,
									textShadow: w.red ? `0 3px 0 rgba(0,0,0,0.55), 0 0 3px rgba(0,0,0,0.9), 0 0 18px rgba(255,31,18,0.6), 0 4px 14px rgba(0,0,0,0.75)` : subStyle().textShadow,
								}}
							>
								{w.t}
							</span>
						);
					})}
				</div>
			))}
		</Center>
	);
};

import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';
import {SERIF, TITULAR} from '../fuentes';
import {usePop} from './Utileria';

/* Utilería propia del short de Vesna (coordenadas del mundo 1080x1920). */

const TINTA = '#1b1b1f';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** El carrito de los refrigerios, con cara: el "empleado del mes". */
export const Carrito: React.FC<{
	x: number;
	y: number;
	ancho?: number;
	ojos?: 'normal' | 'guino' | 'feliz' | 'grandes';
	boca?: 'sonrisa' | 'o' | 'grande';
	medalla?: boolean;
	rot?: number;
	escala?: number;
}> = ({x, y, ancho = 360, ojos = 'normal', boca = 'sonrisa', medalla, rot = 0, escala = 1}) => {
	const f = useCurrentFrame();
	const alto = ancho * 1.25;
	const parpadeo = ojos === 'normal' && f % 83 > 79;
	const ojo = (cx: number, guino: boolean) =>
		guino || parpadeo ? (
			<path d={`M ${cx - 16} 176 Q ${cx} 190 ${cx + 16} 176`} stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" />
		) : ojos === 'feliz' ? (
			<path d={`M ${cx - 16} 182 Q ${cx} 164 ${cx + 16} 182`} stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" />
		) : ojos === 'grandes' ? (
			<g>
				<circle cx={cx} cy={176} r={22} fill="#fff" stroke={TINTA} strokeWidth={6} />
				<circle cx={cx} cy={178} r={9} fill={TINTA} />
			</g>
		) : (
			<g>
				<ellipse cx={cx} cy={176} rx={10} ry={14} fill={TINTA} />
				<circle cx={cx + 4} cy={171} r={3.5} fill="#fff" />
			</g>
		);
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto, width: ancho, height: alto, transform: `rotate(${rot}deg) scale(${escala})`, transformOrigin: '50% 100%'}}>
			<svg viewBox="0 0 300 375" width="100%" height="100%" style={{overflow: 'visible'}}>
				<ellipse cx={150} cy={368} rx={130} ry={14} fill="rgba(0,0,0,0.25)" />
				{/* cosas encima */}
				<rect x={58} y={40} width={34} height={46} rx={6} fill="#ffffff" stroke={TINTA} strokeWidth={6} />
				<rect x={98} y={28} width={30} height={58} rx={6} fill="#e3262e" stroke={TINTA} strokeWidth={6} />
				<path d="M 140 86 L 146 44 L 176 44 L 182 86 Z" fill="#7ec8ff" stroke={TINTA} strokeWidth={6} />
				<rect x={192} y={50} width={52} height={36} rx={8} fill="#ffd84a" stroke={TINTA} strokeWidth={6} />
				{/* asa */}
				<path d="M 20 110 L 20 70 L 52 70" stroke={TINTA} strokeWidth={12} fill="none" strokeLinecap="round" />
				{/* cuerpo */}
				<rect x={24} y={86} width={252} height={250} rx={22} fill="#c9d1da" stroke={TINTA} strokeWidth={9} />
				<rect x={24} y={86} width={252} height={30} rx={14} fill="#aeb8c4" stroke={TINTA} strokeWidth={7} />
				<rect x={46} y={130} width={208} height={150} rx={16} fill="#e2e8ee" stroke={TINTA} strokeWidth={6} />
				<line x1={46} y1={296} x2={254} y2={296} stroke={TINTA} strokeWidth={6} />
				<rect x={128} y={304} width={44} height={14} rx={6} fill="#8d97a3" stroke={TINTA} strokeWidth={4} />
				{/* cara */}
				{ojo(116, false)}
				{ojo(184, ojos === 'guino')}
				<g fill="#ff8fa3" opacity={0.5}>
					<ellipse cx={86} cy={214} rx={18} ry={10} />
					<ellipse cx={214} cy={214} rx={18} ry={10} />
				</g>
				{boca === 'o' ? (
					<ellipse cx={150} cy={232} rx={14} ry={18} fill="#5a1414" stroke={TINTA} strokeWidth={6} />
				) : boca === 'grande' ? (
					<path d="M 112 214 L 188 214 Q 184 258 150 258 Q 116 258 112 214 Z" fill="#5a1414" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
				) : (
					<path d="M 120 218 Q 150 246 180 218" stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" />
				)}
				{/* ruedas */}
				{[64, 236].map((cx) => (
					<g key={cx}>
						<rect x={cx - 6} y={334} width={12} height={14} fill={TINTA} />
						<circle cx={cx} cy={354} r={16} fill="#3a3a44" stroke={TINTA} strokeWidth={5} />
					</g>
				))}
				{medalla && (
					<g transform={`rotate(${Math.sin(f / 6) * 6} 230 120)`}>
						<path d="M 216 100 L 230 152 L 244 100 Z" fill="#c3342b" stroke={TINTA} strokeWidth={4} />
						<circle cx={230} cy={166} r={24} fill="#f2c53d" stroke={TINTA} strokeWidth={5} />
						<path d="M 230 150 L 235 161 L 247 162 L 238 169 L 241 181 L 230 175 L 219 181 L 222 169 L 213 162 L 225 161 Z" fill="#fff3b0" />
					</g>
				)}
			</svg>
		</div>
	);
};

/** Avión de perfil (estilo DC-9) que se parte en tres pedazos a partir de `parte`. */
export const AvionPartido: React.FC<{x: number; y: number; ancho?: number; parte?: number; cortes?: number}> = ({x, y, ancho = 900, parte = 99999, cortes}) => {
	const f = useCurrentFrame();
	const id = React.useId().replace(/:/g, '');
	const l = Math.max(0, f - parte);
	const sep = interpolate(l, [0, 18], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const caer = l * l * 0.25;
	const piezas = [
		{x0: 0, x1: 340, dx: -110 * sep, dy: caer * 0.7 + 40 * sep, r: -14 * sep - l * 0.5},
		{x0: 340, x1: 640, dx: 0, dy: caer * 0.9 + 60 * sep, r: 6 * sep + l * 0.3},
		{x0: 640, x1: 1000, dx: 120 * sep, dy: caer * 0.6 + 20 * sep, r: 18 * sep + l * 0.6},
	];
	const lineasCorte = cortes !== undefined && f >= cortes && f < parte;
	const alto = ancho * 0.36;
	const cuerpo = (
		<g>
			{/* ala trasera visible */}
			<path d="M 430 196 L 560 196 L 640 300 L 600 300 Z" fill="#b9c4d0" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
			{/* fuselaje */}
			<path d="M 40 170 Q 40 120 110 112 L 840 104 Q 900 104 930 70 L 960 70 Q 950 150 930 196 L 100 222 Q 40 222 40 170 Z" fill="#f4f6f8" stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
			<path d="M 60 186 L 930 168" stroke="#1f5fa8" strokeWidth={14} />
			<path d="M 60 204 L 920 186" stroke="#e3262e" strokeWidth={8} />
			{/* cabina */}
			<path d="M 64 150 Q 74 128 108 124 L 112 150 Z" fill="#7ec8ff" stroke={TINTA} strokeWidth={6} />
			{/* ventanillas */}
			{Array.from({length: 18}).map((_, i) => (
				<circle key={i} cx={150 + i * 38} cy={146} r={9} fill="#7ec8ff" stroke={TINTA} strokeWidth={4} />
			))}
			{/* puerta */}
			<rect x={128} y={124} width={28} height={58} rx={8} fill="none" stroke={TINTA} strokeWidth={4} />
			{/* motores traseros */}
			<rect x={700} y={86} width={150} height={46} rx={23} fill="#d6dde5" stroke={TINTA} strokeWidth={8} />
			<ellipse cx={850} cy={109} rx={10} ry={20} fill={TINTA} />
			{/* cola en T */}
			<path d="M 840 104 L 900 -60 L 950 -60 L 960 70" fill="#f4f6f8" stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
			<path d="M 860 -60 L 990 -60 L 980 -42 L 870 -42 Z" fill="#1f5fa8" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
			{/* ala delantera */}
			<path d="M 400 196 L 540 196 L 470 330 L 420 330 Z" fill="#dde4ec" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
		</g>
	);
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto}}>
			<svg viewBox="0 -80 1000 440" width="100%" height="100%" style={{overflow: 'visible'}}>
				<defs>
					{piezas.map((p, i) => (
						<clipPath key={i} id={`${id}-p${i}`}>
							<rect x={p.x0} y={-200} width={p.x1 - p.x0} height={700} />
						</clipPath>
					))}
				</defs>
				{piezas.map((p, i) => (
					<g key={i} transform={`translate(${p.dx} ${p.dy}) rotate(${p.r} ${(p.x0 + p.x1) / 2} 160)`}>
						<g clipPath={`url(#${id}-p${i})`}>{cuerpo}</g>
						{l > 0 && (
							<g>
								{[0, 1].map((k) => (
									<circle key={k} cx={k === 0 ? p.x0 + 6 : p.x1 - 6} cy={165} r={18 + Math.sin(l + k) * 4} fill="#ff9a2e" opacity={0.85} />
								))}
							</g>
						)}
					</g>
				))}
				{lineasCorte &&
					[340, 640].map((cx) => (
						<line key={cx} x1={cx} y1={40} x2={cx} y2={260} stroke="#e3262e" strokeWidth={10} strokeDasharray="22 14" />
					))}
			</svg>
		</div>
	);
};

/** Pedazo de cola del avión (fuselaje trasero con la aleta en T y borde roto). */
export const ColaAvion: React.FC<{x: number; y: number; ancho?: number; rot?: number}> = ({x, y, ancho = 620, rot = 0}) => (
	<div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.35, width: ancho, height: ancho * 0.7, transform: `rotate(${rot}deg)`}}>
		<svg viewBox="0 0 600 420" width="100%" height="100%" style={{overflow: 'visible'}}>
			<path d="M 40 160 L 70 120 L 52 96 L 90 70 L 70 40 L 460 60 Q 520 60 540 20 L 570 20 Q 562 140 540 220 L 70 250 L 92 222 L 50 200 Z" fill="#f4f6f8" stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
			<path d="M 90 190 L 540 172" stroke="#1f5fa8" strokeWidth={16} />
			<path d="M 90 212 L 530 196" stroke="#e3262e" strokeWidth={9} />
			{Array.from({length: 7}).map((_, i) => (
				<circle key={i} cx={130 + i * 46} cy={118} r={11} fill="#7ec8ff" stroke={TINTA} strokeWidth={5} />
			))}
			<rect x={300} y={40} width={170} height={52} rx={26} fill="#d6dde5" stroke={TINTA} strokeWidth={9} />
			<path d="M 460 60 L 520 -110 L 570 -110 L 570 20" fill="#f4f6f8" stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
			<path d="M 480 -110 L 610 -110 L 600 -90 L 490 -90 Z" fill="#1f5fa8" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
			{/* borde roto chamuscado */}
			<path d="M 40 160 L 70 120 L 52 96 L 90 70 L 70 40" stroke="#4a3a2a" strokeWidth={18} fill="none" opacity={0.6} />
		</svg>
	</div>
);

/** Escombros que caen girando, con estela de humo. */
export const Escombros: React.FC<{desde: number; n?: number; subiendo?: boolean}> = ({desde, n = 12, subiendo}) => {
	const f = useCurrentFrame();
	const l = f - desde;
	if (l < 0) return null;
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			{Array.from({length: n}).map((_, i) => {
				const x = random(`ex${i}`) * 1080;
				const v = 8 + random(`ev${i}`) * 14;
				const y0 = -200 - random(`ey${i}`) * 1400;
				const y = subiendo ? 2100 - ((l * v * 2 + random(`ez${i}`) * 2000) % 2400) : y0 + l * v;
				const t = 60 + random(`et${i}`) * 110;
				const r = l * (random(`er${i}`) - 0.5) * 18;
				const forma = ['0,0 100,10 80,70 10,90', '0,20 70,0 100,60 40,100', '10,0 100,30 60,100 0,60'][i % 3];
				return (
					<div key={i} style={{position: 'absolute', left: x - t / 2, top: y - t / 2, width: t, height: t, transform: `rotate(${r}deg)`}}>
						<svg viewBox="-10 -10 120 120" width="100%" height="100%" style={{overflow: 'visible'}}>
							{!subiendo && <path d="M 50 50 L 50 -180" stroke="rgba(60,60,60,0.35)" strokeWidth={50} strokeLinecap="round" />}
							<polygon points={forma} fill={i % 4 === 0 ? '#1f5fa8' : '#c9d1da'} stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
						</svg>
					</div>
				);
			})}
		</AbsoluteFill>
	);
};

/** Líneas de velocidad verticales: sensación de caída libre. */
export const LineasViento: React.FC<{intensidad?: number}> = ({intensidad = 1}) => {
	const f = useCurrentFrame();
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			{Array.from({length: 22}).map((_, i) => {
				const x = random(`lx${i}`) * 1080;
				const largo = 200 + random(`ll${i}`) * 400;
				const v = 70 + random(`lv${i}`) * 60;
				const y = 2200 - ((f * v * intensidad + random(`ly${i}`) * 2600) % 2800);
				return <div key={i} style={{position: 'absolute', left: x, top: y, width: 6 + random(`lw${i}`) * 6, height: largo, borderRadius: 6, background: 'rgba(255,255,255,0.55)'}} />;
			})}
		</AbsoluteFill>
	);
};

/** Copos de nieve cayendo. */
export const Nieve: React.FC<{n?: number}> = ({n = 60}) => {
	const f = useCurrentFrame();
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			{Array.from({length: n}).map((_, i) => {
				const v = 3 + random(`nv${i}`) * 4;
				const y = ((f * v + random(`ny${i}`) * 2000) % 2000) - 40;
				const x = random(`nx${i}`) * 1080 + Math.sin(f / 20 + i) * 30;
				const t = 8 + random(`nt${i}`) * 14;
				return <div key={i} style={{position: 'absolute', left: x, top: y, width: t, height: t, borderRadius: '50%', background: '#fff', opacity: 0.85}} />;
			})}
		</AbsoluteFill>
	);
};

/** Cronómetro que cuenta hasta `valor` minutos. */
export const Cronometro: React.FC<{x: number; y: number; tam?: number; desde: number; hasta: number; valor: number}> = ({x, y, tam = 420, desde, hasta, valor}) => {
	const f = useCurrentFrame();
	const p = usePop(desde - 4, 200);
	if (f < desde - 4) return null;
	const n = Math.round(interpolate(f, [desde, hasta], [0, valor], {...clamp, easing: Easing.out(Easing.quad)}));
	const ang = (n / 60) * 360;
	const fin = f >= hasta;
	return (
		<div style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, width: tam, height: tam * 1.15, transform: `scale(${p * (fin ? 1 + Math.max(0, 0.08 - (f - hasta) * 0.01) : 1)})`}}>
			<svg viewBox="0 0 200 230" width="100%" height="100%" style={{overflow: 'visible'}}>
				<rect x={86} y={4} width={28} height={22} rx={6} fill="#c9d1da" stroke={TINTA} strokeWidth={6} />
				<circle cx={100} cy={128} r={92} fill="#fff" stroke={TINTA} strokeWidth={12} />
				<circle cx={100} cy={128} r={78} fill="none" stroke={fin ? '#e3262e' : '#ffd84a'} strokeWidth={14} strokeDasharray={`${(ang / 360) * 490} 490`} transform="rotate(-90 100 128)" />
				<line x1={100} y1={128} x2={100 + Math.sin((ang * Math.PI) / 180) * 64} y2={128 - Math.cos((ang * Math.PI) / 180) * 64} stroke={TINTA} strokeWidth={7} strokeLinecap="round" />
				<circle cx={100} cy={128} r={8} fill={TINTA} />
			</svg>
			<div style={{position: 'absolute', left: 0, right: 0, top: tam * 0.62, textAlign: 'center', fontFamily: TITULAR, fontWeight: 900, fontSize: tam * 0.2, color: fin ? '#e3262e' : TINTA}}>
				{n} MIN
			</div>
		</div>
	);
};

/** Monitor de signos vitales. */
export const Monitor: React.FC<{x: number; y: number; ancho?: number}> = ({x, y, ancho = 360}) => {
	const f = useCurrentFrame();
	const puntos = Array.from({length: 60}).map((_, i) => {
		const fase = (i * 4 + f * 6) % 120;
		const yy = fase > 50 && fase < 56 ? -60 : fase >= 56 && fase < 60 ? 40 : 0;
		return `${i * 5},${70 + yy}`;
	});
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: ancho * 0.75, background: '#0b1f17', border: `10px solid ${TINTA}`, borderRadius: 22, boxShadow: '0 12px 0 rgba(0,0,0,0.35)', overflow: 'hidden'}}>
			<svg viewBox="0 0 300 140" width="100%" height="70%">
				<polyline points={puntos.join(' ')} fill="none" stroke="#46ff8a" strokeWidth={5} strokeLinejoin="round" />
			</svg>
			<div style={{fontFamily: TITULAR, fontWeight: 900, color: '#46ff8a', fontSize: ancho * 0.12, textAlign: 'center'}}>♥ {68 + Math.round(Math.sin(f / 9) * 3)}</div>
		</div>
	);
};

/** Tarjeta de puntaje de juez. */
export const Tarjeta: React.FC<{x: number; y: number; texto: string; desde: number; rot?: number}> = ({x, y, texto, desde, rot = 0}) => {
	const f = useCurrentFrame();
	const sube = interpolate(f, [desde, desde + 6], [120, 0], {...clamp, easing: Easing.out(Easing.back(2))});
	if (f < desde) return null;
	return (
		<div style={{position: 'absolute', left: x - 95, top: y - 140 + sube, width: 190, height: 280, transform: `rotate(${rot}deg)`}}>
			<div style={{position: 'absolute', left: 82, top: 200, width: 26, height: 120, background: '#a77b4b', border: `6px solid ${TINTA}`, borderRadius: 6}} />
			<div style={{position: 'absolute', inset: '0 0 80px 0', background: '#fff', border: `10px solid ${TINTA}`, borderRadius: 18, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: TITULAR, fontWeight: 900, fontSize: 130, color: '#1f5fa8', boxShadow: '0 10px 0 rgba(0,0,0,0.3)'}}>
				{texto}
			</div>
		</div>
	);
};

/** Tarjeta de reseña: una estrellita. */
export const Resena: React.FC<{x: number; y: number; desde: number}> = ({x, y, desde}) => {
	const p = usePop(desde, 200);
	const f = useCurrentFrame();
	if (f < desde) return null;
	return (
		<div style={{position: 'absolute', left: x - 380, top: y, width: 760, transform: `scale(${p}) rotate(-3deg)`, background: '#fff', border: `10px solid ${TINTA}`, borderRadius: 30, padding: '22px 30px', boxShadow: '0 14px 0 rgba(0,0,0,0.4)', boxSizing: 'border-box'}}>
			<div style={{fontFamily: TITULAR, fontWeight: 900, fontSize: 44, color: TINTA}}>Califica tu vuelo:</div>
			<div style={{display: 'flex', gap: 10, marginTop: 10}}>
				{[0, 1, 2, 3, 4].map((i) => (
					<svg key={i} viewBox="0 0 100 100" width={110} height={110}>
						<path d="M 50 6 L 62 38 L 96 38 L 68 58 L 79 92 L 50 72 L 21 92 L 32 58 L 4 38 L 38 38 Z" fill={i === 0 ? '#ffd84a' : '#e3e3e3'} stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
					</svg>
				))}
			</div>
		</div>
	);
};

/** Ficha de videojuego: ¡objeto legendario obtenido! */
export const FichaObjeto: React.FC<{desde: number}> = ({desde}) => {
	const f = useCurrentFrame();
	const p = usePop(desde, 170, 12);
	if (f < desde) return null;
	const brillo = 0.6 + 0.4 * Math.sin((f - desde) / 4);
	const stats: [string, string][] = [
		['DEFENSA', '+999'],
		['AMORTIGUACIÓN', '+500'],
		['REFRIGERIOS', '∞'],
	];
	return (
		<div style={{position: 'absolute', left: 90, top: 330, width: 900, transform: `scale(${p})`, transformOrigin: '50% 30%'}}>
			<div style={{background: 'linear-gradient(180deg,#2b1d4f,#16102e)', border: `10px solid ${TINTA}`, borderRadius: 34, padding: 34, boxShadow: `0 0 ${60 * brillo}px rgba(255,190,40,0.8), 0 16px 0 rgba(0,0,0,0.5)`}}>
				<div style={{fontFamily: TITULAR, fontWeight: 900, fontSize: 54, color: '#ffd84a', textAlign: 'center', letterSpacing: 2}}>¡OBJETO LEGENDARIO!</div>
				<div style={{fontFamily: TITULAR, fontWeight: 900, fontSize: 40, color: '#fff', textAlign: 'center', marginTop: 6}}>Carrito de refrigerios</div>
				<div style={{height: 460}} />
				{stats.map(([k, v]) => (
					<div key={k} style={{display: 'flex', justifyContent: 'space-between', fontFamily: TITULAR, fontWeight: 900, fontSize: 46, color: '#fff', borderTop: '4px solid rgba(255,255,255,0.15)', padding: '10px 6px'}}>
						<span>{k}</span>
						<span style={{color: '#5dff8f'}}>{v}</span>
					</div>
				))}
			</div>
		</div>
	);
};

/** Certificado de récord mundial (genérico, sin marcas). */
export const Certificado: React.FC<{x: number; y: number; ancho?: number; desde: number}> = ({x, y, ancho = 820, desde}) => {
	const p = usePop(desde, 150, 12);
	const f = useCurrentFrame();
	if (f < desde) return null;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, transform: `scale(${p}) rotate(${Math.sin(f / 15) * 1.5 - 2}deg)`}}>
			<div style={{background: '#fbf3dc', border: `12px solid ${TINTA}`, outline: '10px solid #d9a441', outlineOffset: -34, borderRadius: 20, padding: '50px 50px 60px', textAlign: 'center', boxShadow: '0 18px 0 rgba(0,0,0,0.4)'}}>
				<div style={{fontFamily: TITULAR, fontWeight: 900, fontSize: 64, color: '#b8862a', letterSpacing: 4}}>RÉCORD MUNDIAL</div>
				<div style={{fontFamily: SERIF, fontWeight: 900, fontSize: 46, color: TINTA, marginTop: 14, lineHeight: 1.2}}>Caída más alta sobrevivida sin paracaídas</div>
				<div style={{fontFamily: TITULAR, fontWeight: 900, fontSize: 110, color: '#e3262e', marginTop: 10}}>10.160 m</div>
				<div style={{fontFamily: SERIF, fontWeight: 900, fontSize: 52, color: TINTA, marginTop: 6}}>Vesna</div>
			</div>
			<svg viewBox="0 0 100 100" width={190} height={190} style={{position: 'absolute', right: -40, bottom: -60}}>
				<path d="M 30 60 L 20 98 L 38 88 L 46 100 L 50 66 Z M 70 60 L 80 98 L 62 88 L 54 100 L 50 66 Z" fill="#e3262e" stroke={TINTA} strokeWidth={4} />
				<circle cx={50} cy={46} r={34} fill="#f2c53d" stroke={TINTA} strokeWidth={6} />
				<circle cx={50} cy={46} r={22} fill="none" stroke="#b8862a" strokeWidth={4} />
			</svg>
		</div>
	);
};

/** "¡BOOM!" de cómic. */
export const Boom: React.FC<{x: number; y: number; desde: number; tam?: number}> = ({x, y, desde, tam = 700}) => {
	const f = useCurrentFrame();
	const l = f - desde;
	if (l < 0 || l > 40) return null;
	const s = interpolate(l, [0, 5, 9, 40], [0.2, 1.15, 1, 1.05], clamp);
	const pts = Array.from({length: 32})
		.map((_, i) => {
			const a = (i / 32) * Math.PI * 2;
			const r = i % 2 === 0 ? 100 : 62 + random(`bm${i}`) * 12;
			return `${Math.cos(a) * r},${Math.sin(a) * r * 0.8}`;
		})
		.join(' ');
	return (
		<div style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, width: tam, height: tam, transform: `scale(${s}) rotate(${-8 + Math.sin(l) * 2}deg)`}}>
			<svg viewBox="-110 -110 220 220" width="100%" height="100%" style={{overflow: 'visible'}}>
				<polygon points={pts} fill="#ffd84a" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
				<polygon points={pts} fill="#ff7a1a" transform="scale(0.72)" />
			</svg>
			<div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: TITULAR, fontWeight: 900, fontSize: tam * 0.26, color: '#fff', WebkitTextStroke: `${tam * 0.02}px ${TINTA}`, letterSpacing: -4}}>
				BOOM!
			</div>
		</div>
	);
};

/** Regla de altura (10.000 m → 0 m) con un punto que cae. */
export const Regla: React.FC<{desde: number; hasta: number}> = ({desde, hasta}) => {
	const f = useCurrentFrame();
	const p = usePop(desde, 200);
	if (f < desde) return null;
	const caida = interpolate(f, [desde, hasta], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
	const top = 300;
	const bottom = 1700;
	const marcas = [10000, 7500, 5000, 2500, 0];
	return (
		<div style={{position: 'absolute', left: 60, top, width: 360, height: bottom - top, transform: `scaleY(${p})`, transformOrigin: '50% 0%'}}>
			<div style={{position: 'absolute', left: 120, top: 0, width: 28, height: '100%', background: '#fff', border: `8px solid ${TINTA}`, borderRadius: 14}} />
			{marcas.map((m, i) => (
				<div key={m} style={{position: 'absolute', left: 0, top: (i / (marcas.length - 1)) * (bottom - top) - 30, width: 360, display: 'flex', alignItems: 'center'}}>
					<div style={{width: 110, textAlign: 'right', fontFamily: TITULAR, fontWeight: 900, fontSize: 34, color: '#fff', WebkitTextStroke: `7px ${TINTA}`, paintOrder: 'stroke'}}>{m === 0 ? '0 m' : `${m.toLocaleString('es-ES')}`}</div>
					<div style={{marginLeft: 14, width: 44, height: 10, background: TINTA, borderRadius: 4}} />
				</div>
			))}
			<div style={{position: 'absolute', left: 104, top: caida * (bottom - top) - 30, width: 60, height: 60, borderRadius: '50%', background: '#e3262e', border: `8px solid ${TINTA}`}} />
		</div>
	);
};

/** "Zzz" flotando. */
export const Zzz: React.FC<{x: number; y: number}> = ({x, y}) => {
	const f = useCurrentFrame();
	return (
		<>
			{[0, 1, 2].map((i) => {
				const l = (f + i * 14) % 42;
				return (
					<div key={i} style={{position: 'absolute', left: x + l * 2.2 + i * 10, top: y - l * 4, fontFamily: TITULAR, fontWeight: 900, fontSize: 60 + i * 18, color: '#9fd3ff', WebkitTextStroke: `6px ${TINTA}`, paintOrder: 'stroke', opacity: interpolate(l, [0, 8, 34, 42], [0, 1, 1, 0])}}>
						Z
					</div>
				);
			})}
		</>
	);
};

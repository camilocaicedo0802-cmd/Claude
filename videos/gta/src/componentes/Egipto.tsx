import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {CONDENSADA, SERIF} from '../fuentes';
import {Canasta} from './Objetos';

/*
 * Utilería del short «La nariz de la Esfinge».
 * Mundo: coordenadas 1080 x 1920. "En la mano": origen en la muñeca, +y hacia los dedos, puño en (0, 36).
 */

const TINTA = '#1b1b1f';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const PUNO = 36;
const ARENISCA = '#dcb46c';
const ARENISCA_S = '#b88a48';
const ARENISCA_C = '#e8c98a';

const Giro: React.FC<{rot?: number; children: React.ReactNode}> = ({rot = 0, children}) => <g transform={`rotate(${rot} 0 ${PUNO})`}>{children}</g>;

/* =============================== LA ESFINGE =============================== */

export type CaraEsfinge = 'normal' | 'triste' | 'sorpresa' | 'enojo' | 'cerrados';

/** Lienzo de la Esfinge: 1000 x 800, de frente, con las patas hacia la cámara. La nariz está en (500, 330). */
const ESF = {w: 1000, h: 800, narizX: 500, narizY: 330};

/** Punto del mundo donde está la nariz de una Esfinge colocada en (x, y) con ese ancho */
export const narizEn = (x: number, y: number, ancho: number): [number, number] => [x + ((ESF.narizX - ESF.w / 2) / ESF.w) * ancho, y - ((ESF.h - ESF.narizY) / ESF.w) * ancho];

export const Esfinge: React.FC<{
	x: number;
	/** suelo bajo las patas */
	y: number;
	ancho: number;
	/** 1 = nariz completa; 0 = rota (chata) */
	nariz?: number;
	/** cuánto se ha desprendido la nariz a cincel (0..1): se va quedando sin la punta */
	cincel?: number;
	diana?: boolean;
	cara?: CaraEsfinge;
	/** hacia dónde miran las pupilas (-1..1) */
	mira?: number;
	opacidad?: number;
}> = ({x, y, ancho, nariz = 0, cincel = 0, diana = false, cara = 'normal', mira = 0, opacidad = 1}) => {
	const f = useCurrentFrame();
	const k = ancho / ESF.w;
	const px = mira * 12;
	const parpadeo = cara !== 'cerrados' && f % 150 > 144;
	const ojoSup = cara === 'triste' ? 10 : cara === 'enojo' ? 8 : cara === 'sorpresa' ? -8 : 0;
	const ceja = (lado: -1 | 1) => {
		const cx = 500 + lado * 62;
		switch (cara) {
			case 'triste':
				return `M ${cx - lado * 40} 210 Q ${cx} 214 ${cx + lado * 40} 232`;
			case 'enojo':
				return `M ${cx - lado * 40} 238 Q ${cx} 222 ${cx + lado * 40} 210`;
			case 'sorpresa':
				return `M ${cx - 42} 206 Q ${cx} 184 ${cx + 42} 206`;
			default:
				return `M ${cx - 42} 222 Q ${cx} 206 ${cx + 42} 220`;
		}
	};
	const boca = cara === 'sorpresa' ? null : cara === 'triste' || cara === 'enojo' ? 'M 456 414 Q 500 398 544 414' : 'M 456 404 Q 500 420 544 404';
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - ESF.h * k, width: ancho, height: ESF.h * k, opacity: opacidad}}>
			<svg viewBox={`0 0 ${ESF.w} ${ESF.h}`} width="100%" height="100%" style={{overflow: 'visible'}}>
				<ellipse cx={500} cy={792} rx={480} ry={34} fill="rgba(80,50,20,0.28)" />
				{/* lomo de león detrás */}
				<path d="M 40 560 Q 60 380 250 356 L 750 356 Q 940 380 960 560 L 960 720 L 40 720 Z" fill={ARENISCA_S} stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
				{[420, 470, 520, 580, 640].map((yy, i) => (
					<path key={yy} d={`M ${70 + i * 6} ${yy} Q 140 ${yy - 10} 230 ${yy + 4} M ${770} ${yy + 4} Q 860 ${yy - 10} ${930 - i * 6} ${yy}`} stroke={TINTA} strokeWidth={4} opacity={0.25} fill="none" />
				))}
				{/* pecho */}
				<path d="M 320 540 L 680 540 L 660 790 L 340 790 Z" fill={ARENISCA_S} stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
				<path d="M 380 600 Q 500 640 620 600 M 390 680 Q 500 712 610 680" stroke={TINTA} strokeWidth={5} opacity={0.25} fill="none" />
				{/* patas hacia la cámara */}
				{[-1, 1].map((lado) => {
					const c = 500 + lado * 280;
					return (
						<g key={lado}>
							<path d={`M ${c - 95} 590 L ${c + 95} 590 L ${c + 118} 780 Q ${c} 806 ${c - 118} 780 Z`} fill={ARENISCA} stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
							{[-1, 0, 1].map((d) => (
								<path key={d} d={`M ${c + d * 44 - 16} 786 Q ${c + d * 44} 760 ${c + d * 44 + 16} 786`} stroke={TINTA} strokeWidth={6} fill="none" />
							))}
							<path d={`M ${c - 70} 640 L ${c - 40} 660 M ${c + 50} 700 L ${c + 80} 690`} stroke={TINTA} strokeWidth={4} opacity={0.3} />
						</g>
					);
				})}
				{/* nemes (el tocado a rayas) */}
				<path d="M 296 150 Q 500 20 704 150 L 770 480 Q 720 512 642 504 L 634 330 L 366 330 L 358 504 Q 280 512 230 480 Z" fill={ARENISCA} stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
				{Array.from({length: 9}).map((_, i) => {
					const yy = 190 + i * 34;
					const t = (yy - 150) / 330;
					return (
						<g key={i} opacity={0.5}>
							<path d={`M ${296 - t * 66} ${yy} L ${364 - t * 4} ${yy}`} stroke={ARENISCA_S} strokeWidth={14} />
							<path d={`M ${636 + t * 4} ${yy} L ${704 + t * 66} ${yy}`} stroke={ARENISCA_S} strokeWidth={14} />
						</g>
					);
				})}
				{/* cara */}
				<path d="M 364 168 Q 500 118 636 168 L 640 372 Q 606 470 500 482 Q 394 470 360 372 Z" fill={ARENISCA_C} stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
				<path d="M 352 172 Q 500 120 648 172" stroke={TINTA} strokeWidth={8} fill="none" />
				{/* desgaste */}
				<path d="M 390 330 L 410 350 L 404 372 M 612 300 L 598 322 M 430 440 L 452 452" stroke={TINTA} strokeWidth={4} opacity={0.3} fill="none" />
				{/* ojos */}
				{[-1, 1].map((lado) => {
					const cx = 500 + lado * 62;
					return (
						<g key={lado}>
							<path d={`M ${cx - 40} 270 Q ${cx} 240 ${cx + 40} 270 Q ${cx} 294 ${cx - 40} 270 Z`} fill="#f6e6c0" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
							{!parpadeo && cara !== 'cerrados' && <circle cx={cx + px} cy={270} r={cara === 'sorpresa' ? 10 : 13} fill={TINTA} />}
							{(parpadeo || cara === 'cerrados') && <path d={`M ${cx - 40} 270 Q ${cx} 286 ${cx + 40} 270`} stroke={TINTA} strokeWidth={7} fill="none" />}
							{ojoSup > 0 && !parpadeo && <path d={`M ${cx - 42} 270 Q ${cx} ${240} ${cx + 42} 270 L ${cx + 42} ${262 - (10 - ojoSup)} Q ${cx} ${248 + ojoSup} ${cx - 42} ${262 - (10 - ojoSup)} Z`} fill={ARENISCA_C} stroke={TINTA} strokeWidth={6} strokeLinejoin="round" transform={cara === 'enojo' ? `rotate(${lado * -8} ${cx} 262)` : cara === 'triste' ? `rotate(${lado * 8} ${cx} 262)` : undefined} />}
							<path d={ceja(lado as -1 | 1)} stroke={TINTA} strokeWidth={9} fill="none" strokeLinecap="round" />
						</g>
					);
				})}
				{/* nariz rota (siempre debajo) */}
				<path d="M 470 318 L 486 304 L 506 310 L 524 306 L 534 330 L 526 350 L 504 356 L 480 352 L 466 338 Z" fill="#cfa462" stroke={ARENISCA_S} strokeWidth={4} strokeLinejoin="round" />
				<path d="M 482 322 L 494 334 L 488 344 M 512 318 L 506 332 L 516 342" stroke={TINTA} strokeWidth={3} opacity={0.35} fill="none" />
				<path d="M 482 352 Q 492 360 500 356 M 508 356 Q 516 360 524 350" stroke={TINTA} strokeWidth={4} opacity={0.5} fill="none" strokeLinecap="round" />
				{/* nariz completa */}
				{nariz > 0 && (
					<g opacity={nariz}>
						<path d={`M 500 282 L ${470 + cincel * 12} ${364 - cincel * 34} Q 500 ${378 - cincel * 40} ${530 - cincel * 12} ${364 - cincel * 34} Z`} fill={ARENISCA_C} stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
						<path d="M 488 300 L 482 340" stroke={ARENISCA_S} strokeWidth={6} opacity={0.6} />
					</g>
				)}
				{/* boca */}
				{boca ? <path d={boca} stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" /> : <ellipse cx={500} cy={412} rx={20} ry={24} fill="#5a3418" stroke={TINTA} strokeWidth={6} />}
				{/* diana pintada en la nariz */}
				{diana && (
					<g>
						{[64, 46, 28, 12].map((r, i) => (
							<circle key={r} cx={500} cy={330} r={r} fill={i % 2 ? '#ffffff' : '#e3262e'} stroke={TINTA} strokeWidth={5} opacity={0.92} />
						))}
					</g>
				)}
			</svg>
		</div>
	);
};

/* =============================== CAÑÓN =============================== */

/** Boca del cañón en el mundo (para lanzar la bala desde ahí) */
export const bocaCanon = (x: number, y: number, tam: number, elev: number, voltear = false): [number, number] => {
	const a = (-elev * Math.PI) / 180;
	const bx = -30 + Math.cos(a) * 250;
	const by = -100 + Math.sin(a) * 250;
	return [x + (voltear ? -bx : bx) * tam, y + by * tam];
};

/** Cañón de bronce sobre cureña, visto de lado. (x, y) = suelo bajo las ruedas. */
export const Canon: React.FC<{x: number; y: number; tam?: number; voltear?: boolean; elev?: number; dispara?: number; opacidad?: number}> = ({x, y, tam = 1, voltear, elev = 8, dispara = 1e9, opacidad = 1}) => {
	const f = useCurrentFrame();
	const l = f - dispara;
	const retroceso = l >= 0 ? interpolate(l, [0, 3, 14], [0, -26, 0], {...clamp, easing: Easing.out(Easing.quad)}) : 0;
	const humo = l >= 0 && l < 40;
	const fogonazo = l >= 0 && l < 5;
	const [bx, by] = [-30 + Math.cos((-elev * Math.PI) / 180) * 250, -100 + Math.sin((-elev * Math.PI) / 180) * 250];
	return (
		<div style={{position: 'absolute', left: x - 300 * tam, top: y - 300 * tam, width: 600 * tam, height: 340 * tam, opacity: opacidad, transform: voltear ? 'scaleX(-1)' : undefined}}>
			<svg viewBox="-300 -300 600 340" width="100%" height="100%" style={{overflow: 'visible'}}>
				<g transform={`translate(${retroceso} 0)`}>
					{/* cureña */}
					<path d="M -190 -10 L -150 -96 L 40 -112 L 70 -60 L -20 -40 Z" fill="#8a5a32" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
					{/* tubo */}
					<g transform={`rotate(${-elev} -30 -100)`}>
						<path d="M -110 -146 L 220 -126 L 220 -74 L -110 -54 Q -150 -100 -110 -146 Z" fill="#b5833a" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
						<rect x={208} y={-136} width={34} height={72} rx={8} fill="#c9963f" stroke={TINTA} strokeWidth={7} />
						{[-40, 60, 150].map((rx) => (
							<rect key={rx} x={rx} y={-140 + (rx + 110) * 0.06} width={16} height={84 - (rx + 110) * 0.12} rx={4} fill="#9a6c2a" stroke={TINTA} strokeWidth={5} />
						))}
						<path d="M -90 -126 L 200 -114" stroke="#f0cf86" strokeWidth={7} strokeLinecap="round" opacity={0.7} />
					</g>
					{/* rueda */}
					<circle cx={-40} cy={-58} r={58} fill="#6b4424" stroke={TINTA} strokeWidth={8} />
					{Array.from({length: 6}).map((_, i) => {
						const a = (i / 6) * Math.PI * 2;
						return <line key={i} x1={-40} y1={-58} x2={-40 + Math.cos(a) * 50} y2={-58 + Math.sin(a) * 50} stroke={TINTA} strokeWidth={6} />;
					})}
					<circle cx={-40} cy={-58} r={12} fill="#e0b23a" stroke={TINTA} strokeWidth={5} />
				</g>
				{fogonazo && <circle cx={bx + 30} cy={by} r={interpolate(l, [0, 4], [30, 70], clamp)} fill="#ffd23f" stroke="#ff7a1a" strokeWidth={10} />}
				{humo &&
					[0, 1, 2, 3].map((i) => {
						const t = (l - i * 2) / 38;
						if (t < 0) return null;
						return <circle key={i} cx={bx + 40 + t * (120 + i * 30)} cy={by - t * (60 + i * 25)} r={30 + t * 90} fill="#e9e4da" stroke="#bdb4a4" strokeWidth={5} opacity={Math.max(0, 0.9 - t)} />;
					})}
			</svg>
		</div>
	);
};

/** Bala de cañón que vuela en arco de (x1, y1) a (x2, y2). */
export const BalaCanon: React.FC<{x1: number; y1: number; x2: number; y2: number; desde: number; llega: number; arco?: number; tam?: number}> = ({x1, y1, x2, y2, desde, llega, arco = 160, tam = 46}) => {
	const f = useCurrentFrame();
	if (f < desde || f > llega) return null;
	const t = interpolate(f, [desde, llega], [0, 1], clamp);
	const pos = (u: number): [number, number] => [x1 + (x2 - x1) * u, y1 + (y2 - y1) * u - Math.sin(u * Math.PI) * arco];
	const [bx, by] = pos(t);
	const [ax, ay] = pos(Math.max(0, t - 0.12));
	return (
		<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
			<line x1={ax} y1={ay} x2={bx} y2={by} stroke="#ffffff" strokeWidth={tam * 0.7} strokeLinecap="round" opacity={0.45} />
			<circle cx={bx} cy={by} r={tam / 2} fill="#26262c" stroke={TINTA} strokeWidth={5} />
			<circle cx={bx - tam * 0.14} cy={by - tam * 0.14} r={tam * 0.12} fill="#6a6a74" />
		</svg>
	);
};

/** Trozos de piedra que saltan de un punto. */
export const Esquirlas: React.FC<{x: number; y: number; desde: number; n?: number; tam?: number; color?: string}> = ({x, y, desde, n = 7, tam = 1, color = ARENISCA_S}) => {
	const f = useCurrentFrame();
	const l = f - desde;
	if (l < 0 || l > 28) return null;
	return (
		<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
			{Array.from({length: n}).map((_, i) => {
				const a = -Math.PI * 0.9 + (i / (n - 1)) * Math.PI * 0.8;
				const v = (9 + (i % 3) * 4) * tam;
				const px = x + Math.cos(a) * v * l;
				const py = y + Math.sin(a) * v * l + 0.9 * tam * l * l;
				const s = (12 + (i % 3) * 6) * tam;
				return <path key={i} d={`M ${px - s} ${py} L ${px} ${py - s} L ${px + s} ${py - s * 0.2} L ${px + s * 0.4} ${py + s} Z`} fill={color} stroke={TINTA} strokeWidth={4} opacity={interpolate(l, [20, 28], [1, 0], clamp)} transform={`rotate(${l * 20 * (i % 2 ? 1 : -1)} ${px} ${py})`} />;
			})}
		</svg>
	);
};

/* =============================== PIEDRA DE ROSETTA =============================== */

export const PiedraRosetta: React.FC<{x: number; y: number; ancho: number; rot?: number; brillo?: number; enterrada?: number}> = ({x, y, ancho, rot = 0, brillo = 0, enterrada = 0}) => {
	const alto = ancho * 1.35;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, transform: `rotate(${rot}deg)`}}>
			<svg viewBox="0 0 400 540" width="100%" height="100%" style={{overflow: 'visible'}}>
				{brillo > 0 && <ellipse cx={200} cy={270} rx={300} ry={360} fill="#fff3a0" opacity={0.35 * brillo} />}
				<path d="M 30 120 L 80 60 L 140 74 L 190 30 L 290 50 L 340 26 L 376 90 L 384 520 L 22 520 Z" fill="#3c414b" stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
				<path d="M 60 110 L 120 92 M 250 64 L 320 50" stroke="#5a606c" strokeWidth={6} opacity={0.7} />
				{/* jeroglíficos */}
				{Array.from({length: 4}).map((_, fila) =>
					Array.from({length: 7}).map((__, col) => {
						const gx = 66 + col * 42;
						const gy = 136 + fila * 30;
						const t = (fila * 7 + col) % 4;
						return t === 0 ? (
							<circle key={`${fila}-${col}`} cx={gx} cy={gy} r={8} fill="none" stroke="#a9afba" strokeWidth={4} />
						) : t === 1 ? (
							<path key={`${fila}-${col}`} d={`M ${gx - 10} ${gy + 8} L ${gx} ${gy - 10} L ${gx + 10} ${gy + 8}`} fill="none" stroke="#a9afba" strokeWidth={4} />
						) : t === 2 ? (
							<path key={`${fila}-${col}`} d={`M ${gx - 10} ${gy} q 5 -12 10 0 q 5 12 10 0`} fill="none" stroke="#a9afba" strokeWidth={4} />
						) : (
							<rect key={`${fila}-${col}`} x={gx - 8} y={gy - 8} width={16} height={16} fill="none" stroke="#a9afba" strokeWidth={4} />
						);
					}),
				)}
				<line x1={46} y1={262} x2={360} y2={262} stroke="#7a808c" strokeWidth={4} />
				{/* demótico */}
				{Array.from({length: 5}).map((_, i) => (
					<path key={i} d={`M 50 ${284 + i * 22} ${Array.from({length: 14}).map((__, j) => `q 5 ${j % 2 ? 8 : -8} 11 0`).join(' ')}`} fill="none" stroke="#a9afba" strokeWidth={3.5} />
				))}
				<line x1={40} y1={398} x2={366} y2={398} stroke="#7a808c" strokeWidth={4} />
				{/* griego */}
				{Array.from({length: 5}).map((_, i) => (
					<line key={i} x1={48} y1={420 + i * 20} x2={350 - (i % 2) * 30} y2={420 + i * 20} stroke="#a9afba" strokeWidth={5} strokeDasharray="10 6 4 6" />
				))}
				{enterrada > 0 && <rect x={-20} y={540 - 540 * enterrada} width={440} height={560 * enterrada} fill="#e3c27e" />}
			</svg>
		</div>
	);
};

/** Vitrina de museo (vidrio con reflejos) sobre su pedestal. (x, y) = suelo. */
export const Vitrina: React.FC<{x: number; y: number; ancho: number; alto: number; children?: React.ReactNode}> = ({x, y, ancho, alto, children}) => {
	const pie = alto * 0.32;
	return (
		<>
			<div style={{position: 'absolute', left: x - ancho * 0.46, top: y - pie, width: ancho * 0.92, height: pie, background: '#3a2a22', border: `9px solid ${TINTA}`, boxSizing: 'border-box'}} />
			{children}
			<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto, width: ancho, height: alto - pie + 10, border: `9px solid ${TINTA}`, background: 'linear-gradient(120deg, rgba(200,230,255,0.28), rgba(200,230,255,0.08) 40%, rgba(255,255,255,0.3) 46%, rgba(200,230,255,0.06) 52%)', boxSizing: 'border-box'}}>
				<div style={{position: 'absolute', left: '12%', top: '8%', width: 18, height: '50%', background: 'rgba(255,255,255,0.55)', transform: 'rotate(18deg)'}} />
				<div style={{position: 'absolute', left: '22%', top: '6%', width: 8, height: '36%', background: 'rgba(255,255,255,0.45)', transform: 'rotate(18deg)'}} />
			</div>
		</>
	);
};

/** Placa del museo */
export const Placa: React.FC<{x: number; y: number; texto: string; ancho?: number}> = ({x, y, texto, ancho = 420}) => (
	<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, padding: '10px 14px', background: '#f4efe2', border: `7px solid ${TINTA}`, borderRadius: 8, fontFamily: SERIF, fontWeight: 700, fontSize: ancho * 0.07, color: TINTA, textAlign: 'center', whiteSpace: 'pre', lineHeight: 1.1}}>{texto}</div>
);

/* =============================== EN LA MANO =============================== */

/** Cuaderno de dibujo abierto, con la Esfinge ya chata dibujada. */
export const Cuaderno: React.FC<{rot?: number; dibujo?: number}> = ({rot = 0, dibujo = 1}) => (
	<Giro rot={rot}>
		<g transform="translate(0 60)">
			<rect x={-150} y={-10} width={300} height={190} rx={10} fill="#7a4a24" stroke={TINTA} strokeWidth={7} />
			<rect x={-140} y={-2} width={138} height={174} fill="#f7eed6" stroke={TINTA} strokeWidth={4} />
			<rect x={2} y={-2} width={138} height={174} fill="#f7eed6" stroke={TINTA} strokeWidth={4} />
			<g opacity={dibujo} stroke="#5a3a1e" strokeWidth={4} fill="none" strokeLinecap="round">
				<path d="M -120 140 L -110 90 Q -80 70 -50 90 L -40 140" />
				<path d="M -100 100 L -100 80 Q -80 60 -60 80 L -60 100" />
				<path d="M -136 150 L -20 150" />
				<path d="M 20 40 L 120 40 M 20 70 L 110 70 M 20 100 L 120 100" opacity={0.5} />
			</g>
		</g>
	</Giro>
);

export const Martillo: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<line x1={0} y1={-10} x2={0} y2={140} stroke={TINTA} strokeWidth={22} strokeLinecap="round" />
		<line x1={0} y1={-10} x2={0} y2={140} stroke="#9a6a3a" strokeWidth={12} strokeLinecap="round" />
		<rect x={-44} y={128} width={88} height={46} rx={8} fill="#7d838c" stroke={TINTA} strokeWidth={7} />
		<rect x={-36} y={134} width={30} height={10} rx={4} fill="#b9c0c8" />
	</Giro>
);

export const Cincel: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<path d="M -9 -20 L 9 -20 L 9 110 L 0 140 L -9 110 Z" fill="#9aa1aa" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
		<rect x={-13} y={-30} width={26} height={22} rx={5} fill="#6f757e" stroke={TINTA} strokeWidth={5} />
	</Giro>
);

export const Pala: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<line x1={0} y1={-170} x2={0} y2={250} stroke={TINTA} strokeWidth={22} strokeLinecap="round" />
		<line x1={0} y1={-170} x2={0} y2={250} stroke="#9a6a3a" strokeWidth={12} strokeLinecap="round" />
		<path d="M -48 240 L 48 240 L 44 330 Q 0 374 -44 330 Z" fill="#8d949c" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
	</Giro>
);

/** Canasta con frutas y pan (ofrendas). */
export const Ofrenda: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<g>
			<circle cx={-40} cy={106} r={26} fill="#ff9a1f" stroke={TINTA} strokeWidth={6} />
			<circle cx={8} cy={96} r={28} fill="#e3262e" stroke={TINTA} strokeWidth={6} />
			<ellipse cx={46} cy={104} rx={34} ry={22} fill="#e0a85a" stroke={TINTA} strokeWidth={6} />
			{[0, 1, 2].map((i) => (
				<circle key={i} cx={-14 + i * 14} cy={74 + (i % 2) * 6} r={11} fill="#7b3fa0" stroke={TINTA} strokeWidth={4} />
			))}
		</g>
		<Canasta />
	</Giro>
);

/* =============================== LÍNEA DE TIEMPO =============================== */

export type Hito = {anio: number; texto: string; desde: number; color?: string; arriba?: boolean};

/** Línea de tiempo vertical (de arriba a abajo), con hitos que aparecen al decirlos. */
export const LineaTiempo: React.FC<{x: number; y1: number; y2: number; desde: number; rango: [number, number]; hitos: Hito[]; marcador?: {anio: number; desde: number; hasta: number}}> = ({x, y1, y2, desde, rango, hitos, marcador}) => {
	const f = useCurrentFrame();
	const yDe = (a: number) => y1 + ((a - rango[0]) / (rango[1] - rango[0])) * (y2 - y1);
	const crece = interpolate(f, [desde, desde + 12], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	return (
		<>
			<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
				<line x1={x} y1={y1} x2={x} y2={y1 + (y2 - y1) * crece} stroke={TINTA} strokeWidth={22} strokeLinecap="round" />
				<line x1={x} y1={y1} x2={x} y2={y1 + (y2 - y1) * crece} stroke="#f4efe2" strokeWidth={10} strokeLinecap="round" />
				{marcador && f >= marcador.desde && (
					<line x1={x} y1={yDe(marcador.anio)} x2={x} y2={yDe(Math.round(interpolate(f, [marcador.desde, marcador.hasta], [marcador.anio, rango[1]], clamp)))} stroke="#e3262e" strokeWidth={12} strokeLinecap="round" />
				)}
			</svg>
			{hitos.map((h) => {
				const p = interpolate(f, [h.desde, h.desde + 7], [0, 1], {...clamp, easing: Easing.out(Easing.back(2))});
				if (p <= 0) return null;
				const yy = yDe(h.anio);
				const color = h.color ?? '#1f6fd1';
				return (
					<React.Fragment key={h.anio}>
						<div style={{position: 'absolute', left: x - 30, top: yy - 30, width: 60, height: 60, borderRadius: '50%', background: color, border: `8px solid ${TINTA}`, boxSizing: 'border-box', transform: `scale(${p})`}} />
						<div style={{position: 'absolute', left: x + 56, top: yy - 52, transform: `scale(${p})`, transformOrigin: '0% 50%', whiteSpace: 'nowrap'}}>
							<div style={{fontFamily: CONDENSADA, fontSize: 84, lineHeight: 1, color, WebkitTextStroke: `3px ${TINTA}`}}>{h.anio}</div>
							<div style={{fontFamily: CONDENSADA, fontSize: 44, lineHeight: 1.05, color: TINTA}}>{h.texto}</div>
						</div>
					</React.Fragment>
				);
			})}
		</>
	);
};

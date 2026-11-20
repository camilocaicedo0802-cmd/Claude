import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {CONDENSADA, MONO, ROTULADO} from '../fuentes';

/*
 * Utilería del short «GTA existe por un bug».
 * Mundo: 1080 x 1920. "En la mano": origen en la muñeca, +y hacia los dedos, puño en (0, 36).
 * Todo es dibujo propio: el nombre del juego se escribe con letra libre (Bowlby One, OFL), sin el logo oficial.
 */

const TINTA = '#1b1b1f';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const PUNO = 36;
const Giro: React.FC<{rot?: number; children: React.ReactNode}> = ({rot = 0, children}) => <g transform={`rotate(${rot} 0 ${PUNO})`}>{children}</g>;

/** Interpola una ruta de claves [cuadro, x, y, giro] con suavizado. */
export const ruta = (f: number, claves: [number, number, number, number][], curva: 'suave' | 'lineal' = 'suave'): {x: number; y: number; rot: number} => {
	if (f <= claves[0][0]) return {x: claves[0][1], y: claves[0][2], rot: claves[0][3]};
	for (let i = 0; i < claves.length - 1; i++) {
		const [c1, x1, y1, r1] = claves[i];
		const [c2, x2, y2, r2] = claves[i + 1];
		if (f <= c2) {
			const t = interpolate(f, [c1, c2], [0, 1], {...clamp, easing: curva === 'suave' ? Easing.inOut(Easing.quad) : (u) => u});
			return {x: x1 + (x2 - x1) * t, y: y1 + (y2 - y1) * t, rot: r1 + (r2 - r1) * t};
		}
	}
	const u = claves[claves.length - 1];
	return {x: u[1], y: u[2], rot: u[3]};
};

/* =============================== EL JUEGO VISTO DESDE ARRIBA =============================== */

export type AutoA = {x: number; y: number; rot: number; color?: string; policia?: boolean; jugador?: boolean};

const AutoArribaSVG: React.FC<{a: AutoA; f: number}> = ({a, f}) => {
	const c = a.policia ? '#f4f4f4' : a.color ?? '#e3262e';
	const sir = Math.floor(f / 4) % 2 === 0;
	return (
		<g transform={`translate(${a.x} ${a.y}) rotate(${a.rot})`}>
			<rect x={-30} y={-56} width={72} height={128} rx={18} fill="rgba(0,0,0,0.3)" />
			<rect x={-36} y={-64} width={72} height={128} rx={18} fill={c} stroke={TINTA} strokeWidth={6} />
			{a.policia && (
				<>
					<path d="M -30 -58 Q 0 -66 30 -58 L 30 -30 L -30 -30 Z" fill="#1b1b22" />
					<path d="M -30 40 L 30 40 L 30 56 Q 0 64 -30 56 Z" fill="#1b1b22" />
				</>
			)}
			<path d="M -27 -32 L 27 -32 L 22 -12 L -22 -12 Z" fill="#9fd2f0" stroke={TINTA} strokeWidth={4} />
			<rect x={-24} y={-12} width={48} height={42} rx={6} fill={a.policia ? '#e4e4e4' : 'rgba(0,0,0,0.18)'} stroke={TINTA} strokeWidth={3} />
			<path d="M -22 30 L 22 30 L 26 44 L -26 44 Z" fill="#9fd2f0" stroke={TINTA} strokeWidth={4} />
			<circle cx={-22} cy={-58} r={6} fill="#fff6b0" />
			<circle cx={22} cy={-58} r={6} fill="#fff6b0" />
			{a.policia && (
				<>
					<rect x={-26} y={2} width={26} height={14} rx={3} fill={sir ? '#ff2a2a' : '#6a1414'} stroke={TINTA} strokeWidth={3} />
					<rect x={0} y={2} width={26} height={14} rx={3} fill={sir ? '#24306a' : '#2a6bff'} stroke={TINTA} strokeWidth={3} />
					<circle cx={sir ? -13 : 13} cy={9} r={46} fill={sir ? '#ff2a2a' : '#2a6bff'} opacity={0.18} />
				</>
			)}
			{a.jugador && <path d="M -10 -96 L 0 -80 L 10 -96 Z" fill="#ffd84a" stroke={TINTA} strokeWidth={4} />}
		</g>
	);
};

const TECHOS = ['#c4553a', '#5f7a9a', '#d9a95a', '#7a5f9a', '#4f8a6a', '#a8a08c', '#b86a8a', '#5a6a7a'];
const CELDA = 640;
const CALLE = 200;

/** Ciudad vista desde arriba, como los primeros juegos de mundo abierto. (cx, cy) = centro de la cámara en el mapa. */
export const MapaJuego: React.FC<{cx: number; cy: number; zoom: number; ancho: number; alto: number; autos: AutoA[]; children?: React.ReactNode; noche?: boolean}> = ({cx, cy, zoom, ancho, alto, autos, children, noche}) => {
	const f = useCurrentFrame();
	const w = ancho / zoom;
	const h = alto / zoom;
	const x0 = cx - w / 2;
	const y0 = cy - h / 2;
	const i0 = Math.floor(x0 / CELDA) - 1;
	const i1 = Math.ceil((x0 + w) / CELDA) + 1;
	const j0 = Math.floor(y0 / CELDA) - 1;
	const j1 = Math.ceil((y0 + h) / CELDA) + 1;
	const celdas: [number, number][] = [];
	for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) celdas.push([i, j]);
	const hash = (i: number, j: number) => Math.abs((i * 73856093) ^ (j * 19349663)) % 997;
	return (
		<svg width={ancho} height={alto} viewBox={`${x0} ${y0} ${w} ${h}`} style={{position: 'absolute', left: 0, top: 0, display: 'block'}}>
			<rect x={x0} y={y0} width={w} height={h} fill="#5d6470" />
			{celdas.map(([i, j]) => {
				const bx = i * CELDA + CALLE / 2;
				const by = j * CELDA + CALLE / 2;
				const lado = CELDA - CALLE;
				const k = hash(i, j);
				const parque = k % 7 === 0;
				return (
					<g key={`${i}-${j}`}>
						<rect x={bx} y={by} width={lado} height={lado} fill="#c9c3b5" stroke="#8d877a" strokeWidth={6} />
						{parque ? (
							<g>
								<rect x={bx + 24} y={by + 24} width={lado - 48} height={lado - 48} rx={20} fill="#5aa85a" />
								{[0, 1, 2, 3, 4].map((t) => (
									<circle key={t} cx={bx + 90 + ((t * 97) % 260)} cy={by + 90 + ((t * 151) % 260)} r={44} fill="#3f8a46" stroke={TINTA} strokeWidth={4} />
								))}
							</g>
						) : (
							<g>
								<rect x={bx + 26} y={by + 26} width={lado - 52} height={lado - 52} fill={TECHOS[k % TECHOS.length]} stroke={TINTA} strokeWidth={6} />
								<rect x={bx + 46} y={by + 46} width={lado - 92} height={lado - 92} fill="none" stroke="rgba(0,0,0,0.25)" strokeWidth={8} />
								<rect x={bx + 90 + (k % 80)} y={by + 100} width={70} height={56} fill="#d8d8d0" stroke={TINTA} strokeWidth={4} />
								<rect x={bx + 220} y={by + 220 + (k % 60)} width={90} height={50} fill="#b8b8b0" stroke={TINTA} strokeWidth={4} />
								<circle cx={bx + 120} cy={by + 300} r={22} fill="#8a8a84" stroke={TINTA} strokeWidth={4} />
							</g>
						)}
					</g>
				);
			})}
			{/* líneas de carril */}
			{Array.from({length: i1 - i0 + 1}).map((_, n) => {
				const x = (i0 + n) * CELDA;
				return <line key={`v${n}`} x1={x} y1={y0} x2={x} y2={y0 + h} stroke="#ffd84a" strokeWidth={6} strokeDasharray="40 36" />;
			})}
			{Array.from({length: j1 - j0 + 1}).map((_, n) => {
				const y = (j0 + n) * CELDA;
				return <line key={`h${n}`} x1={x0} y1={y} x2={x0 + w} y2={y} stroke="#ffd84a" strokeWidth={6} strokeDasharray="40 36" />;
			})}
			{/* cruces */}
			{celdas.map(([i, j]) => (
				<rect key={`c${i}-${j}`} x={i * CELDA - CALLE / 2 + 4} y={j * CELDA - CALLE / 2 + 4} width={CALLE - 8} height={CALLE - 8} fill="#5d6470" />
			))}
			{children}
			{autos.map((a, i) => (
				<AutoArribaSVG key={i} a={a} f={f} />
			))}
			{noche && <rect x={x0} y={y0} width={w} height={h} fill="#0a1030" opacity={0.35} />}
		</svg>
	);
};

/** Estallido de choque dentro del mapa (coordenadas del mapa). */
export const ChoqueSVG: React.FC<{x: number; y: number; desde: number; tam?: number}> = ({x, y, desde, tam = 1}) => {
	const f = useCurrentFrame();
	const l = f - desde;
	if (l < 0 || l > 16) return null;
	const s = interpolate(l, [0, 4, 16], [0.3, 1.1, 1.3], clamp) * tam;
	const o = interpolate(l, [0, 2, 10, 16], [0, 1, 1, 0], clamp);
	const puntas = Array.from({length: 12}).map((_, i) => {
		const a = (i / 12) * Math.PI * 2;
		const r = i % 2 ? 46 : 100;
		return `${Math.cos(a) * r},${Math.sin(a) * r}`;
	});
	return (
		<g transform={`translate(${x} ${y}) scale(${s})`} opacity={o}>
			<polygon points={puntas.join(' ')} fill="#ffd23f" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
			<polygon points={puntas.map((p) => p.split(',').map((v) => Number(v) * 0.55).join(',')).join(' ')} fill="#ff7a1a" />
		</g>
	);
};

/** Marcador del juego: dinero arriba a la izquierda, nivel de búsqueda (estrellas) a la derecha. */
export const Hud: React.FC<{estrellas: number; dinero: number; ancho?: number; arriba?: number}> = ({estrellas, dinero, ancho = 1080, arriba = 150}) => {
	const f = useCurrentFrame();
	return (
		<>
			<div style={{position: 'absolute', left: 40, top: arriba, fontFamily: CONDENSADA, fontSize: 64, color: '#7dff8a', WebkitTextStroke: `10px ${TINTA}`, paintOrder: 'stroke', letterSpacing: 2}}>$ {String(Math.round(dinero)).padStart(6, '0')}</div>
			<div style={{position: 'absolute', right: 1080 - ancho + 40, top: arriba, display: 'flex', gap: 6}}>
				{Array.from({length: 5}).map((_, i) => {
					const llena = i < estrellas;
					const parpadea = llena && i >= estrellas - 1 && Math.floor(f / 5) % 2 === 0;
					return (
						<svg key={i} width={66} height={66} viewBox="-50 -50 100 100">
							<polygon points="0,-44 12,-14 44,-14 18,6 28,40 0,20 -28,40 -18,6 -44,-14 -12,-14" fill={llena ? (parpadea ? '#ffffff' : '#ffd23f') : 'rgba(255,255,255,0.15)'} stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
						</svg>
					);
				})}
			</div>
		</>
	);
};

/** Líneas de barrido y viñeta de monitor de tubo. */
export const Barrido: React.FC<{fuerza?: number}> = ({fuerza = 1}) => (
	<>
		<div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.16) 0px, rgba(0,0,0,0.16) 2px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 6px)', opacity: fuerza, pointerEvents: 'none'}} />
		<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.5) 100%)', opacity: fuerza, pointerEvents: 'none'}} />
	</>
);

/* =============================== MONITOR DE TUBO =============================== */

export const pantallaDe = (ancho: number) => ({w: ancho * 0.8, h: ancho * 0.6});

/** Monitor CRT beige de los 90. (x, y) = centro de la caja. Los hijos van dentro de la pantalla (w x h de pantallaDe). */
export const Monitor: React.FC<{x: number; y: number; ancho: number; children?: React.ReactNode; rot?: number; pie?: boolean}> = ({x, y, ancho, children, rot = 0, pie = true}) => {
	const alto = ancho * 0.84;
	const {w, h} = pantallaDe(ancho);
	const f = useCurrentFrame();
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, transform: `rotate(${rot}deg)`}}>
			{pie && <div style={{position: 'absolute', left: ancho * 0.3, top: alto * 0.92, width: ancho * 0.4, height: alto * 0.16, background: '#cfc6ae', border: `${ancho * 0.01}px solid ${TINTA}`, borderRadius: `0 0 ${ancho * 0.03}px ${ancho * 0.03}px`, boxSizing: 'border-box'}} />}
			<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(170deg,#efe7d2,#d9cfb4)', border: `${ancho * 0.012}px solid ${TINTA}`, borderRadius: ancho * 0.05, boxShadow: `0 ${ancho * 0.03}px 0 rgba(0,0,0,0.3)`, boxSizing: 'border-box'}} />
			<div style={{position: 'absolute', left: (ancho - w) / 2, top: ancho * 0.07, width: w, height: h, borderRadius: ancho * 0.04, overflow: 'hidden', background: '#07120c', border: `${ancho * 0.012}px solid ${TINTA}`, boxSizing: 'border-box'}}>
				<div style={{position: 'absolute', inset: 0}}>{children}</div>
				<Barrido />
				<div style={{position: 'absolute', left: '6%', top: '5%', width: '30%', height: '18%', borderRadius: '50%', background: 'rgba(255,255,255,0.12)', transform: 'rotate(-12deg)'}} />
			</div>
			<div style={{position: 'absolute', right: ancho * 0.1, bottom: ancho * 0.06, width: ancho * 0.03, height: ancho * 0.03, borderRadius: '50%', background: Math.floor(f / 20) % 6 ? '#3fe07a' : '#1f8a46', border: `${ancho * 0.005}px solid ${TINTA}`}} />
			{[0.12, 0.2].map((k) => (
				<div key={k} style={{position: 'absolute', left: ancho * k, bottom: ancho * 0.055, width: ancho * 0.05, height: ancho * 0.02, borderRadius: ancho * 0.01, background: '#a89f88', border: `${ancho * 0.004}px solid ${TINTA}`}} />
			))}
		</div>
	);
};

/** Pantalla de código (verde sobre negro) con una línea de error que se pone roja. */
export const PantallaCodigo: React.FC<{w: number; h: number; desde: number; error: number; glitch?: number}> = ({w, h, desde, error, glitch = 1e9}) => {
	const f = useCurrentFrame();
	const lineas = [
		'IF policia.cerca(jugador)',
		'   policia.seguir(jugador)',
		'   policia.velocidad = 40',
		'IF policia.choca(jugador)',
		'   policia.frenar()',
		'ELSE',
		'   policia.embestir()  <<',
		'END IF',
		'GOTO bucle_principal',
	];
	const tam = h / 13;
	const visibles = Math.floor(interpolate(f, [desde, desde + 18], [2, lineas.length], clamp));
	const g = f >= glitch ? Math.sin(f * 7.1) * tam * 0.4 : 0;
	return (
		<div style={{position: 'absolute', inset: 0, padding: `${tam * 0.8}px ${tam}px`, fontFamily: MONO, fontWeight: 700, fontSize: tam, lineHeight: 1.25, color: '#5dff8a', transform: `translateX(${g}px)`}}>
			{lineas.slice(0, visibles).map((l, i) => {
				const mala = i === 6 && f >= error;
				return (
					<div key={i} style={{whiteSpace: 'pre', background: mala ? 'rgba(255,40,40,0.85)' : 'transparent', color: mala ? '#fff' : '#5dff8a'}}>
						{l}
					</div>
				);
			})}
			{f >= error && Math.floor((f - error) / 6) % 2 === 0 && <div style={{position: 'absolute', right: tam, bottom: tam * 0.8, fontFamily: CONDENSADA, fontSize: tam * 1.6, color: '#ff4040'}}>ERROR</div>}
		</div>
	);
};

/* =============================== EL BICHO (el "bug") =============================== */

export const Bicho: React.FC<{x: number; y: number; tam?: number; rot?: number; corona?: boolean; trebol?: boolean; camina?: boolean; cara?: 'feliz' | 'susto' | 'picaro'; opacidad?: number}> = ({x, y, tam = 200, rot = 0, corona, trebol, camina = true, cara = 'picaro', opacidad = 1}) => {
	const f = useCurrentFrame();
	const paso = camina ? Math.sin(f / 2.2) : 0;
	return (
		<div style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, width: tam, height: tam, transform: `rotate(${rot}deg)`, opacity: opacidad}}>
			<svg viewBox="-100 -100 200 200" width="100%" height="100%" style={{overflow: 'visible'}}>
				{/* patas */}
				{[-1, 1].map((l) =>
					[-26, 4, 34].map((yy, i) => {
						const a = (i % 2 ? 1 : -1) * paso * 10 * l;
						return <path key={`${l}${i}`} d={`M ${l * 40} ${yy} L ${l * 76} ${yy + a - 10} L ${l * 92} ${yy + a + 14}`} stroke={TINTA} strokeWidth={9} fill="none" strokeLinecap="round" strokeLinejoin="round" />;
					}),
				)}
				{/* cuerpo */}
				<ellipse cx={0} cy={18} rx={52} ry={62} fill="#46b04a" stroke={TINTA} strokeWidth={8} />
				<path d="M 0 -40 L 0 78" stroke={TINTA} strokeWidth={6} />
				<circle cx={-24} cy={20} r={10} fill="#2f7a33" />
				<circle cx={24} cy={44} r={8} fill="#2f7a33" />
				<circle cx={20} cy={4} r={7} fill="#2f7a33" />
				{/* cabeza */}
				<circle cx={0} cy={-48} r={36} fill="#2c3a2c" stroke={TINTA} strokeWidth={7} />
				<path d={`M -14 -78 Q -30 -${110 + paso * 4} -46 -104`} stroke={TINTA} strokeWidth={6} fill="none" strokeLinecap="round" />
				<path d={`M 14 -78 Q 30 -${110 - paso * 4} 46 -104`} stroke={TINTA} strokeWidth={6} fill="none" strokeLinecap="round" />
				<circle cx={-46} cy={-104} r={7} fill="#ff4f6a" stroke={TINTA} strokeWidth={4} />
				<circle cx={46} cy={-104} r={7} fill="#ff4f6a" stroke={TINTA} strokeWidth={4} />
				{[-1, 1].map((l) => (
					<g key={l}>
						<circle cx={l * 15} cy={-54} r={cara === 'susto' ? 15 : 13} fill="#ffffff" stroke={TINTA} strokeWidth={4} />
						<circle cx={l * 15 + (cara === 'picaro' ? 4 : 0)} cy={-52} r={6} fill={TINTA} />
					</g>
				))}
				{cara === 'picaro' && <path d="M -30 -70 L -4 -64 M 30 -70 L 4 -64" stroke={TINTA} strokeWidth={5} strokeLinecap="round" />}
				{cara === 'susto' ? <ellipse cx={0} cy={-30} rx={9} ry={11} fill="#5a1414" /> : <path d="M -14 -34 Q 0 -22 14 -34" stroke="#fff" strokeWidth={5} fill="none" strokeLinecap="round" />}
				{corona && (
					<g transform="translate(0 -92) scale(0.9)">
						<path d="M -40 10 L -46 -36 L -20 -12 L 0 -44 L 20 -12 L 46 -36 L 40 10 Z" fill="#ffd23f" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
						<circle cx={0} cy={-4} r={7} fill="#e3262e" stroke={TINTA} strokeWidth={3} />
					</g>
				)}
				{trebol && (
					<g transform="translate(70 30) rotate(20)">
						<line x1={0} y1={0} x2={0} y2={60} stroke="#2f7a33" strokeWidth={7} strokeLinecap="round" />
						{[0, 90, 180, 270].map((a) => (
							<ellipse key={a} cx={0} cy={-18} rx={14} ry={20} fill="#3fbf4a" stroke={TINTA} strokeWidth={4} transform={`rotate(${a})`} />
						))}
					</g>
				)}
			</svg>
		</div>
	);
};

/* =============================== EN LA MANO =============================== */

/** Lata de insecticida; `rocia` = 0..1 nube */
export const Insecticida: React.FC<{rot?: number; rocia?: number}> = ({rot = 0, rocia = 0}) => (
	<Giro rot={rot}>
		<rect x={-26} y={10} width={52} height={110} rx={10} fill="#e3262e" stroke={TINTA} strokeWidth={6} />
		<rect x={-26} y={46} width={52} height={36} fill="#ffd23f" stroke={TINTA} strokeWidth={4} />
		<path d="M -14 58 L 14 72 M 14 58 L -14 72" stroke={TINTA} strokeWidth={5} strokeLinecap="round" />
		<rect x={-16} y={120} width={32} height={18} fill="#9aa1aa" stroke={TINTA} strokeWidth={4} />
		<rect x={-8} y={136} width={16} height={14} fill="#1b1b22" />
		{rocia > 0 &&
			[0, 1, 2, 3, 4].map((i) => (
				<circle key={i} cx={(i - 2) * 14 * rocia} cy={170 + i * 30 * rocia} r={18 + i * 12 * rocia} fill="#e6f6ff" stroke="#b8d8e8" strokeWidth={3} opacity={0.85 - i * 0.12} />
			))}
	</Giro>
);

/** Celular "ladrillo" de los 90 con antena. */
export const Ladrillo: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<rect x={-22} y={-10} width={44} height={150} rx={8} fill="#2a2a32" stroke={TINTA} strokeWidth={6} />
		<rect x={-14} y={6} width={28} height={30} fill="#7dff8a" stroke={TINTA} strokeWidth={3} />
		{Array.from({length: 9}).map((_, i) => (
			<rect key={i} x={-14 + (i % 3) * 10} y={48 + Math.floor(i / 3) * 14} width={8} height={9} rx={2} fill="#9aa1aa" />
		))}
		<line x1={14} y1={-10} x2={14} y2={-62} stroke={TINTA} strokeWidth={8} strokeLinecap="round" />
	</Giro>
);

/** Control de consola gris (para sostener frente al pecho, en coordenadas del lienzo). */
export const Control: React.FC<{x?: number; y?: number; ancho?: number}> = ({x = 200, y = 470, ancho = 190}) => {
	const k = ancho / 190;
	return (
		<g transform={`translate(${x} ${y}) scale(${k})`}>
			<path d="M -95 -10 Q -95 -40 -60 -40 L 60 -40 Q 95 -40 95 -10 L 100 40 Q 100 70 70 64 L 40 30 L -40 30 L -70 64 Q -100 70 -100 40 Z" fill="#b9b9c0" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
			<path d="M -62 -14 h 12 v -12 h 12 v 12 h 12 v 12 h -12 v 12 h -12 v -12 h -12 Z" fill="#3a3a44" />
			{[[52, -18, '#e3262e'], [72, -2, '#1f6fd1'], [32, -2, '#22a84f'], [52, 14, '#ffd23f']].map(([cx, cy, c], i) => (
				<circle key={i} cx={cx as number} cy={cy as number} r={9} fill={c as string} stroke={TINTA} strokeWidth={3} />
			))}
		</g>
	);
};

/* =============================== OBJETOS DEL MUNDO =============================== */

/** Gran botón rojo de "CANCELAR" sobre su pedestal. (x, y) = suelo. */
export const BotonRojo: React.FC<{x: number; y: number; tam?: number; presion?: number; texto?: string}> = ({x, y, tam = 1, presion = 0, texto = 'CANCELAR'}) => (
	<div style={{position: 'absolute', left: x - 170 * tam, top: y - 420 * tam, width: 340 * tam, height: 420 * tam}}>
		<svg viewBox="-170 -420 340 420" width="100%" height="100%" style={{overflow: 'visible'}}>
			<rect x={-110} y={-250} width={220} height={250} fill="#5a5f66" stroke={TINTA} strokeWidth={9} />
			<rect x={-150} y={-290} width={300} height={50} rx={10} fill="#3c4048" stroke={TINTA} strokeWidth={9} />
			<path d={`M -100 -290 Q -100 ${-380 + presion * 50} 0 ${-384 + presion * 50} Q 100 ${-380 + presion * 50} 100 -290 Z`} fill="#e3262e" stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
			<path d={`M -60 ${-330 + presion * 30} Q -40 ${-360 + presion * 40} 0 ${-364 + presion * 44}`} stroke="#ff9a9a" strokeWidth={12} fill="none" strokeLinecap="round" />
			<rect x={-96} y={-200} width={192} height={64} rx={8} fill="#ffd23f" stroke={TINTA} strokeWidth={6} />
			<text x={0} y={-155} textAnchor="middle" fontFamily={CONDENSADA} fontSize={46} fill={TINTA}>
				{texto}
			</text>
		</svg>
	</div>
);

/** Máquina de escribir con la hoja que sale mientras se escribe. (x, y) = base. */
export const MaquinaEscribir: React.FC<{x: number; y: number; ancho: number; hoja: number; titular: string; desde: number}> = ({x, y, ancho, hoja, titular, desde}) => {
	const f = useCurrentFrame();
	const letras = Math.floor(interpolate(f, [desde, desde + titular.length * 2.2], [0, titular.length], clamp));
	const k = ancho / 600;
	const altoHoja = 360 * hoja;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - 400 * k, width: ancho, height: 400 * k}}>
			<div style={{position: 'absolute', left: 130 * k, top: (130 - 300 * hoja) * k, width: 340 * k, height: (altoHoja + 60) * k, background: '#fbfbf5', border: `${7 * k}px solid ${TINTA}`, boxSizing: 'border-box', padding: `${20 * k}px ${22 * k}px`}}>
				<div style={{fontFamily: CONDENSADA, fontSize: 64 * k, lineHeight: 1, color: '#d6262e', textAlign: 'center'}}>{titular.slice(0, letras)}</div>
				{hoja > 0.6 &&
					[0, 1, 2].map((i) => (
						<div key={i} style={{height: 10 * k, marginTop: 16 * k, background: 'rgba(27,27,31,0.45)', width: `${[90, 76, 84][i]}%`}} />
					))}
			</div>
			<svg viewBox="0 0 600 400" width="100%" height="100%" style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
				<rect x={90} y={130} width={420} height={40} rx={20} fill="#2a2a32" stroke={TINTA} strokeWidth={8} />
				<path d="M 40 380 L 70 180 L 530 180 L 560 380 Z" fill="#2f5a46" stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
				{Array.from({length: 3}).map((_, r) =>
					Array.from({length: 9 - r}).map((__, c) => {
						const cx = 120 + r * 18 + c * 46;
						const cy = 250 + r * 42;
						const pulsada = Math.floor((f + c * 3 + r * 5) / 3) % 7 === 0 && f >= desde && f < desde + titular.length * 2.2;
						return <circle key={`${r}-${c}`} cx={cx} cy={cy + (pulsada ? 4 : 0)} r={16} fill="#f4f1e8" stroke={TINTA} strokeWidth={5} />;
					}),
				)}
			</svg>
		</div>
	);
};

/** Pizarra blanca con marco. */
export const Pizarra: React.FC<{x: number; y: number; ancho: number; alto: number; children?: React.ReactNode}> = ({x, y, ancho, alto, children}) => (
	<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, background: '#fbfbf7', border: `14px solid #9aa1aa`, outline: `8px solid ${TINTA}`, borderRadius: 10, boxShadow: '0 18px 0 rgba(0,0,0,0.3)'}}>
		{children}
	</div>
);

/** Texto escrito a mano en la pizarra, que se va dibujando. */
export const Marcador: React.FC<{texto: string; desde: number; color?: string; tam?: number; tachado?: number}> = ({texto, desde, color = '#1f3a7a', tam = 70, tachado = 1e9}) => {
	const f = useCurrentFrame();
	const n = Math.floor(interpolate(f, [desde, desde + texto.length * 0.9], [0, texto.length], clamp));
	const t = interpolate(f, [tachado, tachado + 8], [0, 100], clamp);
	if (f < desde) return null;
	return (
		<div style={{position: 'relative', display: 'inline-block', fontFamily: CONDENSADA, fontSize: tam, color, lineHeight: 1.1, transform: 'rotate(-2deg)'}}>
			{texto.slice(0, n)}
			{t > 0 && <div style={{position: 'absolute', left: 0, top: '52%', height: tam * 0.12, width: `${t}%`, background: '#e3262e', borderRadius: 8, transform: 'rotate(-4deg)'}} />}
		</div>
	);
};

/* =============================== CARRO DE LADO =============================== */

/** Carro visto de lado. (x, y) = suelo bajo las ruedas, centro. */
export const AutoLado: React.FC<{x: number; y: number; ancho: number; color?: string; policia?: boolean; voltear?: boolean; rueda?: number; puerta?: number; rot?: number; salta?: number; texto?: string; ritmoSirena?: number}> = ({x, y, ancho, color = '#e3262e', policia, voltear, rueda = 0, puerta = 0, rot = 0, salta = 0, texto = 'POLICE', ritmoSirena = 4}) => {
	const f = useCurrentFrame();
	const k = ancho / 600;
	const sir = Math.floor(f / ritmoSirena) % 2 === 0;
	const cuerpo = policia ? '#f4f4f4' : color;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - 300 * k - salta, width: ancho, height: 300 * k, transform: `${voltear ? 'scaleX(-1) ' : ''}rotate(${rot}deg)`, transformOrigin: '50% 100%'}}>
			<svg viewBox="0 0 600 300" width="100%" height="100%" style={{overflow: 'visible'}}>
				<ellipse cx={300} cy={292} rx={280} ry={14} fill="rgba(0,0,0,0.3)" />
				{policia && (
					<g>
						<rect x={250} y={34} width={50} height={22} rx={5} fill={sir ? '#ff2a2a' : '#6a1414'} stroke={TINTA} strokeWidth={6} />
						<rect x={300} y={34} width={50} height={22} rx={5} fill={sir ? '#24306a' : '#2a6bff'} stroke={TINTA} strokeWidth={6} />
						<circle cx={sir ? 270 : 330} cy={44} r={70} fill={sir ? '#ff2a2a' : '#2a6bff'} opacity={0.22} />
					</g>
				)}
				<path d="M 30 230 L 40 160 Q 60 140 130 136 L 190 70 Q 210 56 250 56 L 390 56 Q 430 56 450 80 L 500 136 Q 560 142 572 170 L 578 230 Z" fill={cuerpo} stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
				{policia && <path d="M 30 230 L 40 160 Q 60 140 130 136 L 160 136 L 160 230 Z M 470 136 L 500 136 Q 560 142 572 170 L 578 230 L 470 230 Z" fill="#1b1b22" />}
				<path d="M 206 80 Q 218 70 250 70 L 300 70 L 300 136 L 152 136 Z" fill="#9fd2f0" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
				<path d="M 316 70 L 386 70 Q 420 70 436 90 L 470 136 L 316 136 Z" fill="#9fd2f0" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
				{/* puerta delantera (se abre) */}
				<g transform={`translate(160 0) scale(${1 - puerta * 0.55} 1) translate(-160 0)`}>
					<path d="M 160 136 L 300 136 L 300 230 L 160 230 Z" fill={cuerpo} stroke={TINTA} strokeWidth={6} />
					<rect x={262} y={156} width={26} height={8} rx={4} fill={TINTA} />
				</g>
				{policia && (
					<text x={385} y={200} textAnchor="middle" fontFamily={CONDENSADA} fontSize={44} fill="#1f3a7a" stroke="#ffffff" strokeWidth={2}>
						{texto}
					</text>
				)}
				<circle cx={562} cy={176} r={12} fill="#fff6b0" stroke={TINTA} strokeWidth={4} />
				<rect x={30} y={168} width={18} height={16} fill="#e3262e" stroke={TINTA} strokeWidth={4} />
				{[150, 460].map((cx) => (
					<g key={cx} transform={`rotate(${rueda} ${cx} 236)`}>
						<circle cx={cx} cy={236} r={54} fill="#1b1b22" stroke={TINTA} strokeWidth={6} />
						<circle cx={cx} cy={236} r={26} fill="#c9c9d0" stroke={TINTA} strokeWidth={5} />
						<line x1={cx - 22} y1={236} x2={cx + 22} y2={236} stroke={TINTA} strokeWidth={5} />
					</g>
				))}
			</svg>
		</div>
	);
};

/* =============================== TÍTULO HOMENAJE =============================== */

const letrero = (tam: number, color: string, borde = 0.16): React.CSSProperties => ({
	fontFamily: ROTULADO,
	fontSize: tam,
	lineHeight: 0.95,
	color,
	WebkitTextStroke: `${tam * borde}px ${TINTA}`,
	paintOrder: 'stroke',
	letterSpacing: tam * 0.01,
	textShadow: `0 ${tam * 0.08}px 0 rgba(0,0,0,0.55)`,
	whiteSpace: 'nowrap',
});

/** El nombre del juego en rotulación propia (no es el logo oficial): cada palabra entra al decirla. */
export const NombreJuego: React.FC<{y: number; desdes: [number, number, number]; tam?: number}> = ({y, desdes, tam = 150}) => {
	const f = useCurrentFrame();
	const palabras = ['GRAND', 'THEFT', 'AUTO'];
	return (
		<div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', flexDirection: 'column', alignItems: 'center', transform: 'rotate(-4deg)'}}>
			{palabras.map((p, i) => {
				const l = f - desdes[i];
				const s = interpolate(l, [0, 5, 9], [2.2, 0.94, 1], {...clamp, easing: Easing.out(Easing.quad)});
				const o = interpolate(l, [0, 2], [0, 1], clamp);
				const ultima = i === 2;
				return (
					<div key={p} style={{...letrero(ultima ? tam * 1.45 : tam, ultima ? '#ffd23f' : '#ffffff'), transform: `scale(${s})`, opacity: o, marginTop: ultima ? tam * 0.04 : 0}}>
						{p}
					</div>
				);
			})}
		</div>
	);
};

/** Caja del juego (diseño propio, sin el arte oficial): nombre en rotulación libre y un carro. `prohibido` dibuja la señal roja. */
export const CajaJuego: React.FC<{x: number; y: number; ancho: number; rot?: number; prohibido?: number}> = ({x, y, ancho, rot = 0, prohibido = 0}) => {
	const alto = ancho * 1.25;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, transform: `rotate(${rot}deg)`}}>
			<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(160deg,#2a2a36,#141418)', border: `${ancho * 0.03}px solid ${TINTA}`, borderRadius: ancho * 0.03, boxShadow: '0 16px 0 rgba(0,0,0,0.4)', overflow: 'hidden'}}>
				<div style={{position: 'absolute', left: 0, right: 0, top: ancho * 0.08, height: ancho * 0.36, background: '#ffd23f', transform: 'skewY(-6deg)'}} />
				<div style={{position: 'absolute', left: 0, right: 0, top: ancho * 0.1, textAlign: 'center', ...letrero(ancho * 0.3, '#ffffff', 0.12)}}>GTA</div>
				<div style={{position: 'absolute', left: ancho * 0.08, right: ancho * 0.08, bottom: ancho * 0.16}}>
					<svg viewBox="0 0 600 300" width="100%" style={{overflow: 'visible'}}>
						<path d="M 30 230 L 40 160 Q 60 140 130 136 L 190 70 Q 210 56 250 56 L 390 56 Q 430 56 450 80 L 500 136 Q 560 142 572 170 L 578 230 Z" fill="#e3262e" stroke={TINTA} strokeWidth={12} />
						<circle cx={150} cy={236} r={52} fill={TINTA} />
						<circle cx={460} cy={236} r={52} fill={TINTA} />
					</svg>
				</div>
				<div style={{position: 'absolute', left: 0, right: 0, bottom: ancho * 0.04, textAlign: 'center', fontFamily: CONDENSADA, fontSize: ancho * 0.09, color: '#ffffff', letterSpacing: 2}}>PC CD-ROM · 1997</div>
			</div>
			{prohibido > 0 && (
				<svg viewBox="-100 -100 200 200" style={{position: 'absolute', left: -ancho * 0.15, top: alto / 2 - ancho * 0.65, width: ancho * 1.3, height: ancho * 1.3, overflow: 'visible', transform: `scale(${0.6 + 0.4 * prohibido})`, opacity: prohibido}}>
					<circle cx={0} cy={0} r={86} fill="none" stroke={TINTA} strokeWidth={30} />
					<circle cx={0} cy={0} r={86} fill="none" stroke="#e3262e" strokeWidth={20} />
					<line x1={-60} y1={-60} x2={60} y2={60} stroke={TINTA} strokeWidth={30} />
					<line x1={-60} y1={-60} x2={60} y2={60} stroke="#e3262e" strokeWidth={20} />
				</svg>
			)}
		</div>
	);
};

/** Atril de discurso (por delante del orador). (x, y) = suelo. */
export const Atril: React.FC<{x: number; y: number; ancho?: number; alto?: number}> = ({x, y, ancho = 380, alto = 470}) => (
	<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto, width: ancho, height: alto}}>
		<svg viewBox="0 0 380 470" width="100%" height="100%" style={{overflow: 'visible'}}>
			<path d="M 10 40 L 370 40 L 320 470 L 60 470 Z" fill="#7a4a24" stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
			<rect x={-10} y={0} width={400} height={50} rx={10} fill="#8a5a32" stroke={TINTA} strokeWidth={10} />
			<circle cx={190} cy={190} r={56} fill="#e0b23a" stroke={TINTA} strokeWidth={8} />
			<path d="M 190 150 L 202 182 L 236 182 L 208 202 L 218 234 L 190 214 L 162 234 L 172 202 L 144 182 L 178 182 Z" fill="#fff4c2" />
			<line x1={210} y1={0} x2={260} y2={-120} stroke={TINTA} strokeWidth={10} strokeLinecap="round" />
			<ellipse cx={266} cy={-132} rx={20} ry={26} fill="#2a2a32" stroke={TINTA} strokeWidth={6} />
		</svg>
	</div>
);

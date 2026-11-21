import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Actor, Muneco, Ropa} from '../componentes/Muneco';
import {CONDENSADA, SERIF, TITULAR} from '../fuentes';
import {Humo} from '../escenarios/Epoca';
import {TINTA, clamp} from './base';

/* Utilería y escenarios de los capítulos 8 (Los dos meses) y 9 (La cuenta). */

/* ---------------- el cronómetro de Papen ---------------- */

/** cronómetro de bolsillo: la aguja corre desde `desde` y se detiene en `para` */
export const Cronometro: React.FC<{x: number; y: number; tam: number; desde?: number; para?: number; brillo?: number}> = ({x, y, tam, desde = 0, para = 1e9, brillo = 0}) => {
	const f = useCurrentFrame();
	const t = Math.min(f, para) - desde;
	const ang = t * 15;
	const parado = f >= para;
	return (
		<svg width={tam} height={tam * 1.18} viewBox="0 0 200 236" style={{position: 'absolute', left: x - tam / 2, top: y - tam * 0.68, overflow: 'visible', filter: brillo ? `drop-shadow(0 0 ${20 * brillo}px rgba(255,220,140,0.8))` : undefined}}>
			<rect x={88} y={0} width={24} height={30} rx={5} fill="#c9a43a" stroke={TINTA} strokeWidth={6} />
			<circle cx={100} cy={20} r={14} fill="none" stroke={TINTA} strokeWidth={6} />
			<circle cx={100} cy={136} r={96} fill="#c9a43a" stroke={TINTA} strokeWidth={8} />
			<circle cx={100} cy={136} r={80} fill={parado ? '#fde9e0' : '#f6efdc'} stroke={TINTA} strokeWidth={5} />
			{Array.from({length: 12}, (_, i) => {
				const a = (i / 12) * Math.PI * 2;
				return <line key={i} x1={100 + Math.sin(a) * 66} y1={136 - Math.cos(a) * 66} x2={100 + Math.sin(a) * 76} y2={136 - Math.cos(a) * 76} stroke={TINTA} strokeWidth={i % 3 === 0 ? 6 : 3} />;
			})}
			<line x1={100} y1={136} x2={100 + Math.sin((ang * Math.PI) / 180) * 64} y2={136 - Math.cos((ang * Math.PI) / 180) * 64} stroke="#c8202a" strokeWidth={6} strokeLinecap="round" />
			<circle cx={100} cy={136} r={8} fill={TINTA} />
		</svg>
	);
};

/* ---------------- el calendario de los 60 días ---------------- */

/** calendario de pared con 60 casillas; se tachan `tachados` (puede ser fraccionario); `marca` resalta un número */
export const Calendario60: React.FC<{x: number; y: number; ancho: number; tachados: number; marca?: number; titulo?: string}> = ({x, y, ancho, tachados, marca, titulo = '60 DÍAS'}) => {
	const k = ancho / 900;
	const celda = 840 / 10;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, background: '#f6efdc', border: `${8 * k}px solid ${TINTA}`, borderRadius: 8 * k, boxShadow: `${16 * k}px ${20 * k}px 0 rgba(0,0,0,0.3)`}}>
			<div style={{background: '#a8262e', color: '#f6efdc', fontFamily: CONDENSADA, fontSize: 110 * k, textAlign: 'center', letterSpacing: 8 * k, borderBottom: `${7 * k}px solid ${TINTA}`, lineHeight: 1.25}}>{titulo}</div>
			<div style={{position: 'relative', margin: 30 * k, height: celda * 6 * k}}>
				{Array.from({length: 60}, (_, i) => {
					const cx = (i % 10) * celda * k;
					const cy = Math.floor(i / 10) * celda * k;
					const t = Math.max(0, Math.min(1, tachados - i));
					const esMarca = marca === i + 1;
					return (
						<div key={i} style={{position: 'absolute', left: cx, top: cy, width: celda * k, height: celda * k, border: `${3 * k}px solid rgba(20,20,26,0.5)`, boxSizing: 'border-box', fontFamily: TITULAR, fontWeight: 700, fontSize: 30 * k, color: '#2a2218', padding: 6 * k, background: esMarca ? '#ffd84a' : undefined}}>
							{i + 1}
							{t > 0 && (
								<svg viewBox="0 0 100 100" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
									<line x1={14} y1={14} x2={14 + 72 * Math.min(1, t * 2)} y2={14 + 72 * Math.min(1, t * 2)} stroke="#c8202a" strokeWidth={10} strokeLinecap="round" />
									{t > 0.5 && <line x1={86} y1={14} x2={86 - 72 * (t * 2 - 1)} y2={14 + 72 * (t * 2 - 1)} stroke="#c8202a" strokeWidth={10} strokeLinecap="round" />}
								</svg>
							)}
						</div>
					);
				})}
			</div>
		</div>
	);
};

/* ---------------- el Parlamento en llamas (de noche) ---------------- */

const Llama: React.FC<{x: number; y: number; alto: number; fase: number}> = ({x, y, alto, fase}) => {
	const f = useCurrentFrame();
	const a = alto * (0.8 + 0.25 * Math.sin(f / 3 + fase) + 0.1 * Math.sin(f / 1.7 + fase * 2));
	const w = alto * 0.45;
	const bx = Math.sin(f / 4 + fase) * w * 0.25;
	return (
		<svg width={w * 2} height={a * 1.2} viewBox={`${-w} ${-a} ${w * 2} ${a * 1.2}`} style={{position: 'absolute', left: x - w, top: y - a, overflow: 'visible'}}>
			<path d={`M ${-w * 0.9} 0 Q ${-w} ${-a * 0.5} ${bx} ${-a} Q ${w} ${-a * 0.45} ${w * 0.9} 0 Z`} fill="#ff6a1a" opacity={0.9} />
			<path d={`M ${-w * 0.5} 0 Q ${-w * 0.5} ${-a * 0.4} ${bx * 0.6} ${-a * 0.7} Q ${w * 0.5} ${-a * 0.35} ${w * 0.5} 0 Z`} fill="#ffc23a" />
		</svg>
	);
};

/** silueta del edificio del Parlamento (fachada con columnas, cúpula y cuatro torres) */
export const SiluetaParlamento: React.FC<{x: number; y: number; ancho: number; color?: string; ventanas?: string}> = ({x, y, ancho, color = '#120a0a', ventanas}) => {
	const k = ancho / 1400;
	return (
		<svg width={ancho} height={ancho * 0.5} viewBox="0 0 1400 700" style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.5, overflow: 'visible'}}>
			<rect x={0} y={300} width={1400} height={400} fill={color} />
			{[0, 1180].map((tx) => (
				<rect key={tx} x={tx} y={180} width={220} height={520} fill={color} />
			))}
			<rect x={420} y={230} width={560} height={470} fill={color} />
			<polygon points="400,240 700,120 1000,240" fill={color} />
			<path d="M 520 120 Q 520 -20 700 -30 Q 880 -20 880 120 Z" fill={color} />
			<rect x={540} y={100} width={320} height={40} fill={color} />
			{ventanas &&
				Array.from({length: 16}, (_, i) => (
					<rect key={i} x={60 + i * 82} y={380 + (i % 2) * 140} width={40} height={90} fill={ventanas} opacity={0.85} />
				))}
			{ventanas && Array.from({length: 6}, (_, i) => <rect key={`c${i}`} x={460 + i * 90} y={300} width={36} height={360} fill={ventanas} opacity={0.6} />)}
			<rect x={0} y={690} width={1400} height={10} fill={color} />
			{k < 0 && null}
		</svg>
	);
};

export const EscIncendio: React.FC = () => {
	const f = useCurrentFrame();
	const pulso = 0.85 + 0.15 * Math.sin(f / 3);
	return (
		<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #0a0610 0%, #2a0c10 45%, #7a2210 75%, #1a0806 100%)'}}>
			<div style={{position: 'absolute', left: 260, top: 120, width: 1400, height: 900, borderRadius: '50%', background: `radial-gradient(ellipse at 50% 60%, rgba(255,120,40,${0.55 * pulso}) 0%, rgba(255,80,20,0) 65%)`}} />
			<Humo color="60,30,30" densidad={0.5} y={-120} alto={700} />
			<SiluetaParlamento x={960} y={900} ancho={1400} ventanas="#ff9a3a" />
			{[
				[700, 690, 260], [960, 580, 320], [1220, 690, 260], [380, 640, 180], [1540, 640, 180], [520, 760, 140], [1400, 760, 140], [960, 420, 200],
			].map(([x, y, a], i) => (
				<Llama key={i} x={x} y={y} alto={a} fase={i * 1.7} />
			))}
			{Array.from({length: 24}, (_, i) => {
				const t = (f * (1.5 + (i % 4) * 0.4) + i * 41) % 600;
				return <div key={i} style={{position: 'absolute', left: 500 + ((i * 137) % 900) + Math.sin(t / 30 + i) * 40, top: 700 - t, width: 6, height: 6, borderRadius: 3, background: '#ffcf6a', opacity: Math.max(0, 1 - t / 600)}} />;
			})}
			<div style={{position: 'absolute', left: 0, right: 0, top: 900, bottom: 0, background: 'linear-gradient(180deg, #2a0c08, #0a0404)'}} />
		</div>
	);
};

/* ---------------- silueta (persona en negro, para escenas serias) ---------------- */

export const Silueta: React.FC<{x: number; y: number; alto: number; ropa: Ropa; camina?: number; voltear?: boolean; tono?: number; pose?: React.ComponentProps<typeof Muneco>['pose']}> = ({x, y, alto, ropa, camina = 0, voltear, tono = 0.08, pose}) => (
	<Actor x={x} y={y} alto={alto} voltear={voltear}>
		<div style={{width: '100%', height: '100%', filter: `brightness(${tono})`}}>
			<Muneco ropa={ropa} camina={camina} pose={pose} sombra={false} ojos="cerrados" boca="seria" parpadea={false} />
		</div>
	</Actor>
);

/* ---------------- Dachau (casi blanco y negro, sin caricatura) ---------------- */

export const EscDachau: React.FC<{abre?: number}> = ({abre = 0}) => (
	<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #8a8a8a 0%, #a8a8a6 45%, #6a6a68 62%, #4a4a48 100%)', filter: 'grayscale(1)'}}>
		{/* alambrada en perspectiva */}
		{Array.from({length: 9}, (_, i) => {
			const x = 120 + i * 90;
			const alto = 260 - i * 18;
			return <div key={i} style={{position: 'absolute', left: x, top: 640 - alto, width: 10, height: alto, background: '#2a2a2a'}} />;
		})}
		{[0, 1, 2, 3].map((k) => (
			<svg key={k} width={900} height={300} style={{position: 'absolute', left: 120, top: 380 + k * 52 - 30, overflow: 'visible'}}>
				<line x1={0} y1={0} x2={760} y2={140 - k * 10} stroke="#2a2a2a" strokeWidth={3} />
			</svg>
		))}
		{[0, 1, 2, 3].map((k) => (
			<svg key={`d${k}`} width={900} height={300} style={{position: 'absolute', left: 1080, top: 520 + k * 40 - 120, overflow: 'visible'}}>
				<line x1={0} y1={0} x2={760} y2={-120 + k * 10} stroke="#2a2a2a" strokeWidth={3} />
			</svg>
		))}
		{Array.from({length: 7}, (_, i) => (
			<div key={`p${i}`} style={{position: 'absolute', left: 1120 + i * 110, top: 640 - (120 + i * 22), width: 10, height: 120 + i * 22, background: '#2a2a2a'}} />
		))}
		{/* torre de vigilancia */}
		<div style={{position: 'absolute', left: 1500, top: 250, width: 160, height: 110, background: '#3a3a3a'}} />
		<div style={{position: 'absolute', left: 1480, top: 220, width: 200, height: 36, background: '#2a2a2a', clipPath: 'polygon(10% 0, 90% 0, 100% 100%, 0 100%)'}} />
		<div style={{position: 'absolute', left: 1515, top: 360, width: 10, height: 280, background: '#2a2a2a', transform: 'rotate(4deg)'}} />
		<div style={{position: 'absolute', left: 1635, top: 360, width: 10, height: 280, background: '#2a2a2a', transform: 'rotate(-4deg)'}} />
		{/* la verja */}
		<div style={{position: 'absolute', left: 820, top: 360, width: 60, height: 320, background: '#3a3a3a'}} />
		<div style={{position: 'absolute', left: 1060, top: 360, width: 60, height: 320, background: '#3a3a3a'}} />
		{[0, 1].map((lado) => (
			<div key={lado} style={{position: 'absolute', left: lado ? 970 : 880, top: 400, width: 90, height: 260, transformOrigin: lado ? '100% 50%' : '0 50%', transform: `perspective(800px) rotateY(${(lado ? 1 : -1) * abre * 70}deg)`}}>
				{Array.from({length: 7}, (_, i) => (
					<div key={i} style={{position: 'absolute', left: i * 14, top: 0, width: 5, height: 260, background: '#2a2a2a'}} />
				))}
				<div style={{position: 'absolute', left: 0, top: 20, width: 90, height: 6, background: '#2a2a2a'}} />
				<div style={{position: 'absolute', left: 0, top: 230, width: 90, height: 6, background: '#2a2a2a'}} />
			</div>
		))}
		{/* camino */}
		<div style={{position: 'absolute', left: 0, right: 0, top: 680, bottom: 0, background: 'linear-gradient(180deg, #5a5a58, #3a3a38)', clipPath: 'polygon(46% 0, 54% 0, 100% 100%, 0 100%)'}} />
		{/* el rótulo, en una tabla sobre dos postes */}
		<div style={{position: 'absolute', left: 250, top: 700, width: 12, height: 200, background: '#2a2a2a'}} />
		<div style={{position: 'absolute', left: 560, top: 700, width: 12, height: 200, background: '#2a2a2a'}} />
		<div style={{position: 'absolute', left: 190, top: 640, width: 440, padding: '16px 0', background: '#d8d6d0', border: '6px solid #2a2a2a', textAlign: 'center', fontFamily: CONDENSADA, color: '#1a1a1a'}}>
			<div style={{fontSize: 70, letterSpacing: 10, lineHeight: 1}}>DACHAU</div>
			<div style={{fontSize: 30, letterSpacing: 4, marginTop: 6}}>22 DE MARZO DE 1933</div>
		</div>
	</div>
);

/* ---------------- bancadas del Parlamento (diputados que levantan la mano) ---------------- */

export type Bancada = {color: string; n: number; levanta?: number; entusiasmo?: boolean};

/** filas de diputados vistos de frente; cada grupo levanta la mano en su cuadro (o no) */
export const Bancadas: React.FC<{grupos: Bancada[]; filas?: number; y0?: number}> = ({grupos, filas = 4, y0 = 470}) => {
	const f = useCurrentFrame();
	const todos: {color: string; levanta?: number; entusiasmo?: boolean}[] = [];
	for (const g of grupos) for (let i = 0; i < g.n; i++) todos.push(g);
	const porFila = Math.ceil(todos.length / filas);
	return (
		<>
			{Array.from({length: filas}, (_, fi) => (
				<div key={`b${fi}`} style={{position: 'absolute', left: -40, right: -40, top: y0 + fi * 150 + 70, height: 90, background: '#4a3220', borderTop: `7px solid ${TINTA}`}} />
			))}
			{todos.map((g, i) => {
				const fi = Math.floor(i / porFila);
				const col = i % porFila;
				const esc = 1.05 + fi * 0.16;
				const x = 60 + col * (1800 / porFila) + (fi % 2) * 30;
				const y = y0 + fi * 150;
				const t = g.levanta !== undefined ? interpolate(f, [g.levanta + (col % 5), g.levanta + (col % 5) + 6], [0, 1], clamp) : 0;
				const sube = g.entusiasmo ? t * (1 + 0.12 * Math.sin(f / 2 + i)) : t;
				// brazo: del hombro (28, -4) al codo y a la mano, que sube por encima de la cabeza
				const codo = [40 + 4 * (1 - sube), -4 - 34 * sube + 30 * (1 - sube)];
				const mano = [44 - 6 * sube, codo[1] - 40 * sube + 20 * (1 - sube)];
				const d = `M 28 -4 L ${codo[0]} ${codo[1]} L ${mano[0]} ${mano[1]}`;
				return (
					<svg key={i} width={100 * esc} height={160 * esc} viewBox="-50 -120 100 160" style={{position: 'absolute', left: x - 50 * esc, top: y - 120 * esc, overflow: 'visible'}}>
						<path d="M -32 40 L -30 -10 Q 0 -24 30 -10 L 32 40 Z" fill={g.color} stroke={TINTA} strokeWidth={5} />
						<circle cx={0} cy={-44} r={26} fill="#f4f1ea" stroke={TINTA} strokeWidth={5} />
						<path d={d} stroke={TINTA} strokeWidth={17} fill="none" strokeLinecap="round" strokeLinejoin="round" />
						<path d={d} stroke={g.color} strokeWidth={9} fill="none" strokeLinecap="round" strokeLinejoin="round" />
						{sube > 0.3 && <circle cx={mano[0]} cy={mano[1] - 4} r={9} fill="#f4f1ea" stroke={TINTA} strokeWidth={4} />}
					</svg>
				);
			})}
		</>
	);
};

/* ---------------- candados, megáfono, periódico y puerta ---------------- */

export const Candado: React.FC<{x: number; y: number; tam: number; cierra: number}> = ({x, y, tam, cierra}) => {
	const f = useCurrentFrame();
	const t = interpolate(f, [cierra - 8, cierra], [0, 1], clamp);
	if (f < cierra - 8) return null;
	const caida = interpolate(t, [0, 0.6], [-200, 0], clamp);
	const arco = interpolate(t, [0.6, 1], [-30, 0], clamp);
	return (
		<svg width={tam} height={tam * 1.3} viewBox="0 0 100 130" style={{position: 'absolute', left: x - tam / 2, top: y - tam * 0.65 + caida, overflow: 'visible'}}>
			<path d={`M 26 ${60 + arco} L 26 ${34 + arco} Q 26 ${8 + arco} 50 ${8 + arco} Q 74 ${8 + arco} 74 ${34 + arco} L 74 60`} stroke={TINTA} strokeWidth={18} fill="none" />
			<path d={`M 26 ${60 + arco} L 26 ${34 + arco} Q 26 ${8 + arco} 50 ${8 + arco} Q 74 ${8 + arco} 74 ${34 + arco} L 74 60`} stroke="#9a9aa4" strokeWidth={9} fill="none" />
			<rect x={10} y={56} width={80} height={66} rx={8} fill="#c9a43a" stroke={TINTA} strokeWidth={6} />
			<circle cx={50} cy={84} r={8} fill={TINTA} />
			<rect x={47} y={86} width={6} height={18} fill={TINTA} />
		</svg>
	);
};

export const Periodico: React.FC<{x: number; y: number; ancho: number; titular: string; fecha?: string; rot?: number; nombre?: string}> = ({x, y, ancho, titular, fecha = '', rot = 0, nombre = 'DIE ZEITUNG'}) => {
	const k = ancho / 600;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, background: '#ece6d6', border: `${6 * k}px solid ${TINTA}`, padding: 22 * k, boxSizing: 'border-box', transform: `rotate(${rot}deg)`, boxShadow: `${12 * k}px ${14 * k}px 0 rgba(0,0,0,0.3)`, color: '#1a1a1a'}}>
			<div style={{fontFamily: SERIF, fontWeight: 900, fontSize: 52 * k, textAlign: 'center', borderBottom: `${4 * k}px double #1a1a1a`, lineHeight: 1.1}}>{nombre}</div>
			<div style={{fontFamily: TITULAR, fontSize: 18 * k, textAlign: 'center', margin: `${6 * k}px 0`}}>{fecha}</div>
			<div style={{fontFamily: CONDENSADA, fontSize: 70 * k, lineHeight: 1.02, textAlign: 'center', margin: `${10 * k}px 0`}}>{titular}</div>
			{[0, 1, 2].map((c) => (
				<div key={c} style={{display: 'inline-block', width: '31%', marginRight: c < 2 ? '3%' : 0, verticalAlign: 'top'}}>
					{Array.from({length: 6}, (_, i) => (
						<div key={i} style={{height: 7 * k, background: '#9a9488', margin: `${8 * k}px 0`, width: `${70 + ((i * 17 + c * 7) % 30)}%`}} />
					))}
				</div>
			))}
		</div>
	);
};

export const Megafono: React.FC<{x: number; y: number; tam: number}> = ({x, y, tam}) => (
	<svg width={tam} height={tam * 0.7} viewBox="0 0 200 140" style={{position: 'absolute', left: x - tam / 2, top: y - tam * 0.35, overflow: 'visible'}}>
		<path d="M 30 50 L 150 8 L 150 132 L 30 90 Z" fill="#e3e0d6" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
		<rect x={6} y={44} width={30} height={52} rx={6} fill="#c8202a" stroke={TINTA} strokeWidth={7} />
		<rect x={60} y={86} width={22} height={50} rx={6} fill="#5a5a62" stroke={TINTA} strokeWidth={7} />
	</svg>
);

export const PuertaSalon: React.FC<{x: number; y: number; alto: number; letrero?: string}> = ({x, y, alto, letrero = 'SALÓN'}) => {
	const k = alto / 500;
	return (
		<div style={{position: 'absolute', left: x - 170 * k, top: y - alto, width: 340 * k, height: alto, background: '#6a3e26', border: `${8 * k}px solid ${TINTA}`, borderRadius: `${150 * k}px ${150 * k}px 0 0`}}>
			<div style={{position: 'absolute', left: '50%', top: 0, bottom: 0, width: 6 * k, background: TINTA}} />
			<div style={{position: 'absolute', left: 60 * k, top: 120 * k, padding: `${6 * k}px ${16 * k}px`, background: '#c9a43a', border: `${4 * k}px solid ${TINTA}`, fontFamily: CONDENSADA, fontSize: 30 * k, color: TINTA}}>{letrero}</div>
		</div>
	);
};

/* ---------------- camión de noche ---------------- */

export const Camion: React.FC<{x: number; y: number; ancho: number; color?: string}> = ({x, y, ancho, color = '#1a1a20'}) => (
	<svg width={ancho} height={ancho * 0.48} viewBox="0 0 500 240" style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.48, overflow: 'visible'}}>
		<rect x={0} y={20} width={330} height={170} rx={8} fill={color} />
		<path d="M 330 80 L 420 80 L 470 140 L 470 190 L 330 190 Z" fill={color} />
		<rect x={350} y={96} width={60} height={44} fill="#ffd27a" opacity={0.5} />
		<circle cx={80} cy={200} r={36} fill="#0a0a0c" />
		<circle cx={400} cy={200} r={36} fill="#0a0a0c" />
		<rect x={470} y={150} width={16} height={20} fill="#ffe2a0" />
	</svg>
);

/* ---------------- papeleta con una sola casilla ---------------- */

export const Papeleta: React.FC<{x: number; y: number; ancho: number; tachados: number; partidos: string[]; unico?: string}> = ({x, y, ancho, tachados, partidos, unico}) => {
	const k = ancho / 600;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, background: '#f6f2e6', border: `${6 * k}px solid ${TINTA}`, padding: `${24 * k}px ${30 * k}px`, boxSizing: 'border-box', boxShadow: `${12 * k}px ${14 * k}px 0 rgba(0,0,0,0.3)`, fontFamily: TITULAR, color: '#1a1a1a'}}>
			<div style={{fontFamily: CONDENSADA, fontSize: 52 * k, textAlign: 'center', letterSpacing: 4 * k, marginBottom: 16 * k}}>PAPELETA</div>
			{partidos.map((p, i) => {
				const t = Math.max(0, Math.min(1, tachados - i));
				return (
					<div key={i} style={{position: 'relative', display: 'flex', alignItems: 'center', gap: 16 * k, margin: `${12 * k}px 0`, fontSize: 30 * k, fontWeight: 700, opacity: 1 - 0.55 * t}}>
						<div style={{width: 40 * k, height: 40 * k, border: `${5 * k}px solid ${TINTA}`, boxSizing: 'border-box'}} />
						<span>{p}</span>
						{t > 0 && <div style={{position: 'absolute', left: -6 * k, top: '50%', height: 8 * k, width: `${t * 104}%`, background: '#c8202a', borderRadius: 4 * k}} />}
					</div>
				);
			})}
			{unico && (
				<div style={{display: 'flex', alignItems: 'center', gap: 16 * k, marginTop: 18 * k, fontSize: 34 * k, fontWeight: 800}}>
					<div style={{width: 48 * k, height: 48 * k, border: `${6 * k}px solid ${TINTA}`, boxSizing: 'border-box'}} />
					<span>{unico}</span>
				</div>
			)}
		</div>
	);
};

/* ---------------- el Parlamento diminuto y asustado (en el rincón) ---------------- */

export const ParlamentoMini: React.FC<{x: number; y: number; ancho: number; susto?: boolean}> = ({x, y, ancho, susto = true}) => {
	const f = useCurrentFrame();
	const tiembla = susto ? Math.sin(f * 2.1) * 2 : 0;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2 + tiembla, top: y - ancho * 0.62, width: ancho, height: ancho * 0.62}}>
			<svg width={ancho} height={ancho * 0.62} viewBox="0 0 400 248" style={{overflow: 'visible'}}>
				<rect x={20} y={110} width={360} height={130} fill="#cfc6b0" stroke={TINTA} strokeWidth={7} />
				<rect x={0} y={80} width={70} height={160} fill="#c4bba4" stroke={TINTA} strokeWidth={7} />
				<rect x={330} y={80} width={70} height={160} fill="#c4bba4" stroke={TINTA} strokeWidth={7} />
				<polygon points="120,110 200,70 280,110" fill="#c4bba4" stroke={TINTA} strokeWidth={7} />
				<path d="M 150 72 Q 150 20 200 16 Q 250 20 250 72 Z" fill="#9fb4c0" stroke={TINTA} strokeWidth={7} />
				{[0, 1, 2, 3, 4].map((i) => (
					<rect key={i} x={140 + i * 26} y={120} width={12} height={110} fill="#b0a68e" stroke={TINTA} strokeWidth={3} />
				))}
				{/* cara asustada */}
				<circle cx={90} cy={160} r={22} fill="#fff" stroke={TINTA} strokeWidth={5} />
				<circle cx={310} cy={160} r={22} fill="#fff" stroke={TINTA} strokeWidth={5} />
				<circle cx={92} cy={164} r={8} fill={TINTA} />
				<circle cx={308} cy={164} r={8} fill={TINTA} />
				<path d="M 70 128 L 110 136 M 330 128 L 290 136" stroke={TINTA} strokeWidth={6} strokeLinecap="round" />
				<ellipse cx={200} cy={218} rx={30} ry={14} fill="#3a1a1a" stroke={TINTA} strokeWidth={4} />
			</svg>
			{susto &&
				[0, 1, 2].map((i) => (
					<div key={i} style={{position: 'absolute', left: -50 - i * 26, top: 60 + i * 30, width: 40, height: 6, background: TINTA, transform: `rotate(${-20 + i * 20}deg)`, opacity: 0.5 + 0.5 * Math.abs(Math.sin(f / 3 + i))}} />
				))}
		</div>
	);
};

/* ---------------- la caja de regalo ---------------- */

export const Regalo: React.FC<{x: number; y: number; tam: number; rot?: number}> = ({x, y, tam, rot = 0}) => (
	<svg width={tam} height={tam} viewBox="0 0 200 200" style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, transform: `rotate(${rot}deg)`, overflow: 'visible'}}>
		<rect x={20} y={70} width={160} height={120} fill="#c8202a" stroke={TINTA} strokeWidth={8} />
		<rect x={10} y={50} width={180} height={34} fill="#d8343c" stroke={TINTA} strokeWidth={8} />
		<rect x={88} y={50} width={24} height={140} fill="#ffd84a" stroke={TINTA} strokeWidth={6} />
		<path d="M 100 50 Q 60 0 40 30 Q 30 52 100 50 Q 140 0 160 30 Q 170 52 100 50 Z" fill="#ffd84a" stroke={TINTA} strokeWidth={6} />
	</svg>
);

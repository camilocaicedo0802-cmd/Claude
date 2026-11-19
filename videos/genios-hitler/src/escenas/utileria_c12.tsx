import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Ropa} from '../componentes/Muneco';
import {EDITOR, FUNCIONARIO, HITLER_1919, HITLER_CELDA, SENOR_1, SENOR_2, SENOR_3} from '../componentes/Vestuario';
import {CONDENSADA, SERIF, TITULAR} from '../fuentes';
import {TINTA, clamp} from './base';

/* Utilería y escenarios propios de los capítulos 1 (El espía) y 2 (El golpe de la cervecería). */

/** punto del lienzo de un muñeco (cx, cy) llevado al mundo: Actor en (x, y) con alto A */
export const enActor = (x: number, y: number, A: number, cx: number, cy: number, voltear = false): [number, number] => [x + (voltear ? -1 : 1) * (cx - 200) * (A / 900), y + (cy - 880) * (A / 900)];

/* ---------------- vestuario extra ---------------- */

/** los tipos de la cervecería de 1919 */
export const PARROQUIANOS: Ropa[] = [SENOR_1, SENOR_2, SENOR_3, FUNCIONARIO, {...SENOR_2, casaca: '#5a4a3a', casacaSombra: '#42362a', cabeza: {...SENOR_2.cabeza, pelo: 'calvo', bigote: 'morsa', colorBigote: '#8a7a68'}}];
/** el secretario que pasa a máquina en la celda */
export const SECRETARIO: Ropa = {...FUNCIONARIO, cabeza: {...FUNCIONARIO.cabeza, pelo: 'raya', colorPelo: '#3a2a1e', lentes: false}, casaca: '#5a5048', casacaSombra: '#42382f'};
/** Hitler de traje claro en la celda, con barriga (ver `barriga`) */
export const HITLER_PRESO = HITLER_CELDA;
export const HITLER_UNIFORME = HITLER_1919;
export const EDITOR_C2 = EDITOR;

/* ---------------- cosas que Hitler no tiene ---------------- */

export const CartelAlquila: React.FC<{x: number; y: number; ancho: number}> = ({x, y, ancho}) => {
	const k = ancho / 600;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho}}>
			<div style={{width: ancho, height: 700 * k, background: '#3a2a1e', border: `${10 * k}px solid ${TINTA}`, borderRadius: `${300 * k}px ${300 * k}px 0 0`, position: 'relative'}}>
				<div style={{position: 'absolute', left: 60 * k, right: 60 * k, top: 80 * k, bottom: 0, background: 'linear-gradient(180deg, #2a3a4a, #1a2430)', border: `${8 * k}px solid ${TINTA}`, borderRadius: `${240 * k}px ${240 * k}px 0 0`}} />
				<div style={{position: 'absolute', left: 90 * k, right: 90 * k, top: 300 * k, padding: `${18 * k}px 0`, background: '#f6efdc', border: `${8 * k}px solid ${TINTA}`, transform: 'rotate(-6deg)', textAlign: 'center', fontFamily: CONDENSADA, fontSize: 96 * k, color: '#a8262e', letterSpacing: 4 * k, boxShadow: `${10 * k}px ${12 * k}px 0 rgba(0,0,0,0.35)`}}>
					SE ALQUILA
				</div>
			</div>
		</div>
	);
};

export const MarcoVacio: React.FC<{x: number; y: number; ancho: number}> = ({x, y, ancho}) => {
	const k = ancho / 500;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: 620 * k, background: '#c9a43a', border: `${10 * k}px solid ${TINTA}`, borderRadius: 16 * k, padding: 50 * k, boxSizing: 'border-box', boxShadow: `${14 * k}px ${18 * k}px 0 rgba(0,0,0,0.35)`}}>
			<div style={{width: '100%', height: '100%', background: '#ece4cf', border: `${8 * k}px solid ${TINTA}`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
				<svg width={200 * k} height={180 * k} viewBox="0 0 200 180" style={{opacity: 0.35}}>
					<path d="M 100 170 C 20 110 0 60 40 30 C 70 8 100 40 100 56 C 100 40 130 8 160 30 C 200 60 180 110 100 170 Z" fill="none" stroke="#8a7a5a" strokeWidth={10} strokeDasharray="18 14" />
				</svg>
			</div>
		</div>
	);
};

export const LibretaPlan: React.FC<{x: number; y: number; ancho: number; rot?: number}> = ({x, y, ancho, rot = -3}) => {
	const k = ancho / 600;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: 760 * k, transform: `rotate(${rot}deg)`, background: '#fbf8ef', border: `${10 * k}px solid ${TINTA}`, borderRadius: 14 * k, boxShadow: `${14 * k}px ${18 * k}px 0 rgba(0,0,0,0.35)`}}>
			{Array.from({length: 9}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: -26 * k, top: (60 + i * 76) * k, width: 52 * k, height: 26 * k, borderRadius: 13 * k, border: `${7 * k}px solid ${TINTA}`, background: '#c9c9d0'}} />
			))}
			<div style={{position: 'absolute', left: 70 * k, right: 40 * k, top: 50 * k, fontFamily: CONDENSADA, fontSize: 130 * k, color: '#2a2218', letterSpacing: 8 * k, borderBottom: `${8 * k}px solid #2a2218`, lineHeight: 1.1}}>PLAN</div>
			{Array.from({length: 7}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: 70 * k, right: 40 * k, top: (260 + i * 66) * k, height: 4 * k, background: '#b9cbe0'}} />
			))}
		</div>
	);
};

export const PlatoVacio: React.FC<{x: number; y: number; ancho: number}> = ({x, y, ancho}) => (
	<svg width={ancho} height={ancho * 0.5} viewBox="0 0 400 200" style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.25, overflow: 'visible'}}>
		<ellipse cx={200} cy={110} rx={190} ry={78} fill="#f4f1e8" stroke={TINTA} strokeWidth={9} />
		<ellipse cx={200} cy={110} rx={120} ry={46} fill="#e6e0d0" stroke="#c9c1ae" strokeWidth={5} />
		<g transform="translate(-30 0)">
			<line x1={0} y1={60} x2={0} y2={170} stroke={TINTA} strokeWidth={10} strokeLinecap="round" />
			{[-12, 0, 12].map((d) => (
				<line key={d} x1={d} y1={40} x2={d} y2={80} stroke={TINTA} strokeWidth={6} strokeLinecap="round" />
			))}
		</g>
		<line x1={440} y1={60} x2={440} y2={170} stroke={TINTA} strokeWidth={12} strokeLinecap="round" />
	</svg>
);

/* ---------------- relojes ---------------- */

export const RelojPared: React.FC<{x: number; y: number; tam: number; vel?: number; desde?: number}> = ({x, y, tam, vel = 1, desde = 0}) => {
	const f = useCurrentFrame();
	const t = Math.max(0, f - desde);
	const min = t * 6 * vel;
	const hora = min / 12;
	return (
		<svg width={tam} height={tam} viewBox="-110 -110 220 220" style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, overflow: 'visible'}}>
			<circle r={100} fill="#f6efdc" stroke="#6a4a2a" strokeWidth={14} />
			<circle r={100} fill="none" stroke={TINTA} strokeWidth={5} />
			{Array.from({length: 12}, (_, i) => (
				<line key={i} x1={0} y1={-84} x2={0} y2={-70} stroke={TINTA} strokeWidth={6} transform={`rotate(${i * 30})`} />
			))}
			<line x1={0} y1={0} x2={0} y2={-48} stroke={TINTA} strokeWidth={10} strokeLinecap="round" transform={`rotate(${hora})`} />
			<line x1={0} y1={0} x2={0} y2={-74} stroke={TINTA} strokeWidth={6} strokeLinecap="round" transform={`rotate(${min})`} />
			<circle r={8} fill={TINTA} />
		</svg>
	);
};

export const RelojBolsillo: React.FC<{x: number; y: number; tam: number; vel?: number}> = ({x, y, tam, vel = 1}) => {
	const f = useCurrentFrame();
	const tiembla = vel > 3 ? Math.sin(f * 2.1) * 4 : 0;
	return (
		<svg width={tam} height={tam * 1.3} viewBox="-120 -170 240 300" style={{position: 'absolute', left: x - tam / 2 + tiembla, top: y - tam * 0.75, overflow: 'visible'}}>
			<path d="M 0 -130 Q 60 -200 140 -210 Q 220 -220 300 -170" stroke="#c9a43a" strokeWidth={8} fill="none" strokeDasharray="14 6" />
			<rect x={-18} y={-150} width={36} height={34} rx={8} fill="#c9a43a" stroke={TINTA} strokeWidth={6} />
			<circle cx={0} cy={-150} r={14} fill="none" stroke="#c9a43a" strokeWidth={8} />
			<circle r={112} fill="#d9b24a" stroke={TINTA} strokeWidth={8} />
			<circle r={94} fill="#fbf6e6" stroke={TINTA} strokeWidth={5} />
			{Array.from({length: 12}, (_, i) => (
				<text key={i} x={Math.sin((i * Math.PI) / 6) * 74} y={-Math.cos((i * Math.PI) / 6) * 74 + 9} textAnchor="middle" fontFamily={SERIF} fontSize={24} fill={TINTA}>
					{i === 0 ? 12 : i}
				</text>
			))}
			<line x1={0} y1={0} x2={0} y2={-46} stroke={TINTA} strokeWidth={9} strokeLinecap="round" transform={`rotate(${f * 6 * vel})`} />
			<line x1={0} y1={0} x2={0} y2={-70} stroke="#a8262e" strokeWidth={5} strokeLinecap="round" transform={`rotate(${f * 72 * vel})`} />
			<circle r={7} fill={TINTA} />
		</svg>
	);
};

/* ---------------- gritos, barbas y vapor ---------------- */

/** barba que crece (largo 0..1) colgando de la barbilla (x, y) */
export const Barba: React.FC<{x: number; y: number; ancho: number; largo: number; color?: string}> = ({x, y, ancho, largo, color = '#9a8a74'}) => {
	if (largo <= 0.02) return null;
	const L = ancho * 0.2 + ancho * 1.8 * largo;
	return (
		<svg width={ancho} height={L} viewBox={`0 0 100 ${(L / ancho) * 100}`} style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.12, overflow: 'visible'}}>
			<path d={`M 0 0 Q 50 14 100 0 Q 104 ${(L / ancho) * 60} 50 ${(L / ancho) * 100} Q -4 ${(L / ancho) * 60} 0 0 Z`} fill={color} stroke={TINTA} strokeWidth={4} strokeLinejoin="round" />
			{[25, 50, 75].map((cx) => (
				<path key={cx} d={`M ${cx} 12 Q ${cx + 6} ${(L / ancho) * 40} ${cx - 4} ${(L / ancho) * 70}`} stroke="rgba(0,0,0,0.25)" strokeWidth={3} fill="none" />
			))}
		</svg>
	);
};

/** vapor que sale de las orejas (dos chorros, a izquierda y derecha de (x, y)) */
export const Vapor: React.FC<{x: number; y: number; separacion: number; desde: number; tam?: number}> = ({x, y, separacion, desde, tam = 1}) => {
	const f = useCurrentFrame();
	const t = f - desde;
	if (t < 0) return null;
	return (
		<>
			{[-1, 1].map((lado) =>
				Array.from({length: 5}, (_, i) => {
					const u = ((t * 1.4 + i * 9) % 45) / 45;
					const r = (24 + u * 60) * tam;
					return (
						<div
							key={`${lado}-${i}`}
							style={{position: 'absolute', left: x + lado * (separacion / 2 + u * 160 * tam) - r, top: y - u * 120 * tam - r, width: r * 2, height: r * 2, borderRadius: '50%', background: '#f4f4f4', border: `${5 * tam}px solid ${TINTA}`, opacity: 1 - u}}
						/>
					);
				}),
			)}
		</>
	);
};

/** gotas de sudor que saltan de la cabeza */
export const Sudor: React.FC<{x: number; y: number; desde: number; tam?: number}> = ({x, y, desde, tam = 1}) => {
	const f = useCurrentFrame();
	const t = f - desde;
	if (t < 0) return null;
	return (
		<>
			{Array.from({length: 6}, (_, i) => {
				const u = ((t + i * 5) % 18) / 18;
				const a = (-70 + i * 28) * (Math.PI / 180);
				const d = 120 * tam + u * 90 * tam;
				return <div key={i} style={{position: 'absolute', left: x + Math.sin(a) * d, top: y - Math.cos(a) * d * 0.8 + u * u * 80, width: 20 * tam, height: 30 * tam, background: '#9fd2f0', border: `${4 * tam}px solid ${TINTA}`, borderRadius: '50% 50% 50% 50% / 60% 60% 40% 40%', opacity: 1 - u}} />;
			})}
		</>
	);
};

/* ---------------- el carnet y los globos ---------------- */

export const Carnet: React.FC<{x: number; y: number; ancho: number; rot?: number}> = ({x, y, ancho, rot = -4}) => {
	const k = ancho / 800;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - (ancho * 0.6) / 2, width: ancho, height: ancho * 0.6, transform: `rotate(${rot}deg)`, background: '#efe2bd', border: `${10 * k}px solid ${TINTA}`, borderRadius: 18 * k, boxShadow: `${16 * k}px ${20 * k}px 0 rgba(0,0,0,0.35)`, fontFamily: SERIF, color: '#2a2218'}}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 110 * k, background: '#7a5230', borderBottom: `${8 * k}px solid ${TINTA}`, borderRadius: `${8 * k}px ${8 * k}px 0 0`, color: '#f6efdc', fontFamily: CONDENSADA, fontSize: 64 * k, textAlign: 'center', lineHeight: `${110 * k}px`, letterSpacing: 4 * k}}>PARTIDO OBRERO ALEMÁN</div>
			<div style={{position: 'absolute', left: 50 * k, top: 150 * k, width: 190 * k, height: 230 * k, background: '#d9cdb0', border: `${7 * k}px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 290 * k, top: 150 * k, fontSize: 40 * k, fontStyle: 'italic'}}>Miembro:</div>
			<div style={{position: 'absolute', left: 290 * k, top: 200 * k, fontSize: 56 * k, fontWeight: 700}}>A. Hitler</div>
			<div style={{position: 'absolute', left: 290 * k, top: 300 * k, fontFamily: CONDENSADA, fontSize: 120 * k, color: '#a8262e', letterSpacing: 4 * k}}>Nº 555</div>
		</div>
	);
};

/** números de globo («555»): `infla` 1 = inflados, 0 = desinflados y arrugados en el suelo */
export const GloboNumero: React.FC<{x: number; y: number; tam: number; texto: string; infla: number; color?: string}> = ({x, y, tam, texto, infla, color = '#d6262e'}) => {
	const f = useCurrentFrame();
	const s = 0.25 + 0.75 * infla;
	const bam = infla < 1 && infla > 0 ? Math.sin(f * 2.4) * 8 * (1 - infla) : Math.sin(f / 9) * 3;
	return (
		<div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, -100%) scale(${s}, ${0.15 + 0.85 * infla}) rotate(${bam}deg)`, transformOrigin: '50% 100%', fontFamily: "'Bowlby One', sans-serif", fontSize: tam, color, WebkitTextStroke: `${tam * 0.05}px ${TINTA}`, paintOrder: 'stroke', textShadow: `inset 0 0 0 #fff, ${tam * 0.03}px ${tam * 0.04}px 0 rgba(0,0,0,0.3)`, lineHeight: 1, whiteSpace: 'nowrap'}}>
			{texto}
			<div style={{position: 'absolute', left: '18%', top: '16%', width: tam * 0.12, height: tam * 0.26, borderRadius: '50%', background: 'rgba(255,255,255,0.55)', transform: 'rotate(20deg)'}} />
		</div>
	);
};

/* ---------------- billetes y pan (1923) ---------------- */

export const BilleteGrande: React.FC<{x: number; y: number; ancho: number; rot?: number; texto?: string; anio?: string}> = ({x, y, ancho, rot = 0, texto = '1.000.000.000', anio = '1923'}) => {
	const k = ancho / 1000;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.25, width: ancho, height: ancho * 0.5, transform: `rotate(${rot}deg)`, background: 'linear-gradient(135deg, #c9d9b0, #a9c08e)', border: `${10 * k}px solid ${TINTA}`, borderRadius: 14 * k, boxShadow: `${18 * k}px ${22 * k}px 0 rgba(0,0,0,0.4)`, overflow: 'hidden'}}>
			<div style={{position: 'absolute', inset: 22 * k, border: `${8 * k}px double #4a6a3a`, borderRadius: 10 * k}} />
			{Array.from({length: 8}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: -100 * k + i * 160 * k, top: -50 * k, width: 300 * k, height: 600 * k, borderRadius: '50%', border: `${3 * k}px solid rgba(74,106,58,0.25)`}} />
			))}
			<div style={{position: 'absolute', left: 60 * k, top: 60 * k, fontFamily: SERIF, fontWeight: 900, fontSize: 46 * k, color: '#3a5a2a', letterSpacing: 4 * k}}>REICHSBANKNOTE</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 150 * k, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 150 * k, color: '#2a3a1e', lineHeight: 1}}>{texto}</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 310 * k, textAlign: 'center', fontFamily: SERIF, fontWeight: 900, fontSize: 64 * k, color: '#3a5a2a', letterSpacing: 6 * k}}>MARCOS</div>
			<div style={{position: 'absolute', right: 70 * k, bottom: 46 * k, fontFamily: CONDENSADA, fontSize: 70 * k, color: '#7a2a24'}}>{anio}</div>
			<div style={{position: 'absolute', left: 70 * k, bottom: 46 * k, width: 120 * k, height: 120 * k, borderRadius: '50%', border: `${7 * k}px solid #4a6a3a`, background: 'rgba(74,106,58,0.15)'}} />
		</div>
	);
};

/** montaña de billetes (fondo del rótulo del capítulo 2) */
export const MontanaBilletes: React.FC<{y?: number}> = ({y = 0}) => (
	<>
		{Array.from({length: 90}, (_, i) => {
			const fila = Math.floor(i / 15);
			const bx = ((i * 137) % 2100) - 90 + (fila % 2) * 60;
			const by = 1080 - fila * 120 - ((i * 53) % 70) + y;
			const enMonte = Math.abs(bx - 960) < 1100 - fila * 130;
			if (!enMonte) return null;
			return <div key={i} style={{position: 'absolute', left: bx - 120, top: by - 60, width: 240, height: 120, background: i % 3 ? '#b9cf9a' : '#d9c9a0', border: `6px solid ${TINTA}`, borderRadius: 8, transform: `rotate(${((i * 37) % 50) - 25}deg)`}} />;
		})}
	</>
);

export const Pan: React.FC<{x: number; y: number; ancho: number; rot?: number}> = ({x, y, ancho, rot = 0}) => (
	<svg width={ancho} height={ancho * 0.45} viewBox="0 0 400 180" style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.45, transform: `rotate(${rot}deg)`, overflow: 'visible'}}>
		<path d="M 20 150 Q 0 60 120 40 Q 200 20 290 40 Q 400 60 380 150 Z" fill="#d99a48" stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
		{[120, 200, 280].map((cx) => (
			<path key={cx} d={`M ${cx - 30} 70 Q ${cx} 100 ${cx + 26} 60`} stroke="#a8682a" strokeWidth={9} fill="none" strokeLinecap="round" />
		))}
		<path d="M 60 120 Q 200 140 340 120" stroke="rgba(255,255,255,0.35)" strokeWidth={10} fill="none" strokeLinecap="round" />
	</svg>
);

/** etiqueta de precio que se desenrolla como un ticket larguísimo de ceros */
export const EtiquetaPrecio: React.FC<{x: number; y: number; ancho: number; desenrolla: number}> = ({x, y, ancho, desenrolla}) => {
	const largo = 120 + desenrolla * 1400;
	const k = ancho / 200;
	const ceros = '0 0 0 . 0 0 0 . 0 0 0 . 0 0 0 . 0 0 0 . 0 0 0 . 0 0 0 . 0 0 0 . 0 0 0 . 0 0 0';
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: largo * k, background: '#fbf8ef', border: `${6 * k}px solid ${TINTA}`, borderRadius: `${10 * k}px ${10 * k}px 0 0`, overflow: 'hidden', boxShadow: `${8 * k}px ${10 * k}px 0 rgba(0,0,0,0.3)`}}>
			<div style={{fontFamily: CONDENSADA, fontSize: 40 * k, textAlign: 'center', color: '#a8262e', borderBottom: `${4 * k}px dashed ${TINTA}`, padding: `${6 * k}px 0`}}>PAN</div>
			<div style={{fontFamily: CONDENSADA, fontSize: 52 * k, textAlign: 'center', color: '#2a2218', lineHeight: 1.05, padding: `${8 * k}px ${10 * k}px`, wordBreak: 'break-all'}}>
				1 {ceros} {ceros} {ceros}
			</div>
		</div>
	);
};

export const Carretilla: React.FC<{x: number; y: number; ancho: number; lleno?: number; voltear?: boolean}> = ({x, y, ancho, lleno = 1, voltear}) => (
	<div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.62, width: ancho, height: ancho * 0.62, transform: voltear ? 'scaleX(-1)' : undefined}}>
		{lleno > 0 &&
			Array.from({length: 16}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: `${12 + ((i * 23) % 60)}%`, top: `${(1 - lleno) * 40 + ((i * 17) % 30) - 8}%`, width: '26%', height: '16%', background: i % 2 ? '#b9cf9a' : '#d9c9a0', border: `5px solid ${TINTA}`, borderRadius: 6, transform: `rotate(${((i * 41) % 60) - 30}deg)`}} />
			))}
		<svg viewBox="0 0 500 310" width="100%" height="100%" style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
			<path d="M 40 110 L 380 110 L 340 220 L 90 220 Z" fill="#6a7a8a" stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
			<line x1={340} y1={130} x2={490} y2={90} stroke={TINTA} strokeWidth={14} strokeLinecap="round" />
			<line x1={120} y1={220} x2={110} y2={300} stroke={TINTA} strokeWidth={12} strokeLinecap="round" />
			<circle cx={330} cy={256} r={48} fill="#3a3a42" stroke={TINTA} strokeWidth={10} />
			<circle cx={330} cy={256} r={12} fill="#c9c9d0" />
		</svg>
	</div>
);

/* ---------------- el trono de barriles ---------------- */

export const TronoBarriles: React.FC<{x: number; y: number; ancho: number; corona?: boolean}> = ({x, y, ancho, corona = true}) => {
	const k = ancho / 700;
	const barril = (bx: number, by: number, w: number, h: number) => (
		<div style={{position: 'absolute', left: bx * k, top: by * k, width: w * k, height: h * k, background: 'linear-gradient(90deg, #5a3a1e, #8a5a30 50%, #5a3a1e)', border: `${8 * k}px solid ${TINTA}`, borderRadius: `${w * 0.2 * k}px / ${h * 0.5 * k}px`}}>
			<div style={{position: 'absolute', left: '22%', top: -8 * k, bottom: -8 * k, width: 8 * k, background: TINTA, opacity: 0.6}} />
			<div style={{position: 'absolute', right: '22%', top: -8 * k, bottom: -8 * k, width: 8 * k, background: TINTA, opacity: 0.6}} />
		</div>
	);
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - 760 * k, width: ancho, height: 760 * k}}>
			{barril(220, 0, 260, 330)}
			{barril(0, 300, 250, 220)}
			{barril(450, 300, 250, 220)}
			{barril(160, 480, 380, 280)}
			{/* corona de cartón en lo alto */}
			{corona && <svg viewBox="0 0 200 110" width={200 * k} height={110 * k} style={{position: 'absolute', left: 250 * k, top: -100 * k, overflow: 'visible'}}>
				<path d="M 10 100 L 10 30 L 55 70 L 100 10 L 145 70 L 190 30 L 190 100 Z" fill="#e0b23a" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
			</svg>}
		</div>
	);
};

/* ---------------- calle fría al amanecer y siluetas ---------------- */

export const EscCalleAlba: React.FC<{frio?: number}> = ({frio = 1}) => (
	<div style={{position: 'absolute', inset: 0, background: `linear-gradient(180deg, ${frio ? '#8a96a4' : '#c9a98a'} 0%, #c7ccd2 45%, #9aa2ac 100%)`}}>
		{/* fachadas */}
		{[
			[0, 260, 380],
			[360, 180, 300],
			[640, 300, 420],
			[1040, 220, 300],
			[1320, 140, 360],
			[1660, 260, 300],
		].map(([x, y, w], i) => (
			<div key={i} style={{position: 'absolute', left: x, top: y, width: w, height: 760 - y, background: i % 2 ? '#5f6874' : '#6c7682', border: `7px solid #3a414a`}}>
				{Array.from({length: 6}, (_, j) => (
					<div key={j} style={{position: 'absolute', left: 30 + (j % 3) * (w / 3.2), top: 40 + Math.floor(j / 3) * 150, width: w / 5, height: 90, background: '#3e4650', border: '5px solid #2c3238'}} />
				))}
			</div>
		))}
		{/* adoquines */}
		<div style={{position: 'absolute', left: 0, right: 0, top: 760, bottom: 0, background: 'linear-gradient(180deg, #7c848e, #5a616a)'}}>
			{Array.from({length: 10}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: 0, right: 0, top: 10 + i * i * 4, height: 3, background: 'rgba(0,0,0,0.18)'}} />
			))}
		</div>
		<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 0%, rgba(255,240,220,0.25), rgba(255,240,220,0) 60%)'}} />
	</div>
);

/** silueta oscura (sin rostro ni insignias): 'civil' con gorra, 'policia' con casco, 'sombrero' */
export const Silueta: React.FC<{x: number; y: number; alto: number; tipo?: 'civil' | 'policia' | 'sombrero'; paso?: number; color?: string; opacidad?: number}> = ({x, y, alto, tipo = 'civil', paso = 0, color = '#23272e', opacidad = 1}) => {
	const k = alto / 400;
	const p = Math.sin(paso) * 14;
	return (
		<svg width={140 * k} height={alto} viewBox="-70 0 140 400" style={{position: 'absolute', left: x - 70 * k, top: y - alto, overflow: 'visible', opacity: opacidad}}>
			<line x1={-14} y1={250} x2={-14 - p} y2={396} stroke={color} strokeWidth={26} strokeLinecap="round" />
			<line x1={14} y1={250} x2={14 + p} y2={396} stroke={color} strokeWidth={26} strokeLinecap="round" />
			<path d="M -46 110 Q -50 80 -20 76 L 20 76 Q 50 80 46 110 L 40 260 L -40 260 Z" fill={color} />
			<line x1={-40} y1={110} x2={-50 + p / 2} y2={230} stroke={color} strokeWidth={24} strokeLinecap="round" />
			<line x1={40} y1={110} x2={50 - p / 2} y2={230} stroke={color} strokeWidth={24} strokeLinecap="round" />
			<circle cx={0} cy={44} r={34} fill={color} />
			{tipo === 'policia' && <path d="M -44 40 Q -40 -4 0 -6 Q 40 -4 44 40 L 56 46 L -56 46 Z" fill={color} />}
			{tipo === 'civil' && <path d="M -36 24 Q 0 -4 36 24 L 50 30 L -28 30 Z" fill={color} />}
			{tipo === 'sombrero' && <path d="M -30 26 L -26 -14 L 26 -14 L 30 26 L 50 30 L -50 30 Z" fill={color} />}
		</svg>
	);
};

/** humareda gris que se expande (tiroteo, sin sangre) */
export const Humareda: React.FC<{x: number; y: number; desde: number; ancho?: number}> = ({x, y, desde, ancho = 900}) => {
	const f = useCurrentFrame();
	const t = f - desde;
	if (t < 0) return null;
	return (
		<>
			{Array.from({length: 9}, (_, i) => {
				const a = (i / 9) * Math.PI;
				const d = Math.min(1, t / 40) * ancho * 0.4;
				const r = 90 + Math.min(1, t / 50) * 160 + (i % 3) * 30;
				return (
					<div
						key={i}
						style={{position: 'absolute', left: x - Math.cos(a) * d - r, top: y - Math.sin(a) * d * 0.4 - r - t * 0.6, width: r * 2, height: r * 2, borderRadius: '50%', background: 'radial-gradient(circle, rgba(225,228,232,0.8), rgba(225,228,232,0) 70%)', filter: 'blur(8px)', opacity: interpolate(t, [0, 6, 90], [0, 0.9, 0.5], clamp)}}
					/>
				);
			})}
		</>
	);
};

/* ---------------- la casa del amigo, la puerta y las manos ---------------- */

export const CasaNoche: React.FC<{luz?: number}> = ({luz = 1}) => (
	<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #0e1424 0%, #1c2640 70%, #121624 100%)'}}>
		{Array.from({length: 40}, (_, i) => (
			<div key={i} style={{position: 'absolute', left: (i * 211) % 1920, top: (i * 97) % 420, width: 4, height: 4, borderRadius: 2, background: '#e9eef8', opacity: 0.5 + (i % 3) * 0.2}} />
		))}
		<div style={{position: 'absolute', left: 1560, top: 90, width: 120, height: 120, borderRadius: '50%', background: '#f4efd6', boxShadow: '0 0 80px 20px rgba(244,239,214,0.25)'}} />
		<div style={{position: 'absolute', left: 0, right: 0, top: 840, bottom: 0, background: '#e9eef5'}} />
		{/* la casa */}
		<div style={{position: 'absolute', left: 560, top: 420, width: 800, height: 440, background: '#3a3a4a', border: `9px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: 520, top: 220, width: 880, height: 220, background: '#2a2430', clipPath: 'polygon(50% 0, 100% 100%, 0 100%)'}} />
		<div style={{position: 'absolute', left: 520, top: 404, width: 880, height: 30, background: '#f0f4fa', borderRadius: 10}} />
		{[0, 1].map((i) => (
			<div key={i} style={{position: 'absolute', left: 640 + i * 460, top: 520, width: 180, height: 160, background: i === 1 ? `rgba(255,214,120,${0.4 + 0.6 * luz})` : '#1a1c26', border: `8px solid ${TINTA}`, boxShadow: i === 1 ? `0 0 ${60 * luz}px rgba(255,200,100,0.6)` : undefined}}>
				<div style={{position: 'absolute', left: '50%', top: 0, bottom: 0, width: 8, background: TINTA, marginLeft: -4}} />
			</div>
		))}
		<div style={{position: 'absolute', left: 890, top: 640, width: 140, height: 220, background: '#4a2e1e', border: `8px solid ${TINTA}`}} />
	</div>
);

/** sólo las manos: la de él sostiene la pistola; la de ella llega con calma y se la quita (toma 0..1) */
export const ManosPistola: React.FC<{toma: number}> = ({toma}) => {
	const lleva = Math.max(0, toma - 0.55) / 0.45;
	const llega = Math.min(1, toma / 0.55);
	const ella = {x: interpolate(llega, [0, 1], [1500, 1040]) + lleva * 520, y: 560 - lleva * 40};
	return (
		<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 50%, #3a3430 0%, #1a1614 75%)'}}>
			{/* mano de él, con la manga de la gabardina */}
			<div style={{position: 'absolute', left: -60, top: 520, width: 760, height: 150, background: '#7a6c4a', border: `9px solid ${TINTA}`, borderRadius: 40, transform: 'rotate(4deg)'}} />
			<div style={{position: 'absolute', left: 660, top: 520, width: 190, height: 150, background: '#f2e6d8', border: `9px solid ${TINTA}`, borderRadius: '60px 80px 80px 60px', transform: 'rotate(4deg)'}} />
			{/* la pistola (se la lleva ella) */}
			<svg width={320} height={200} viewBox="0 0 320 200" style={{position: 'absolute', left: 760 + lleva * 520, top: 480 - lleva * 40, overflow: 'visible', transform: `rotate(${-lleva * 8}deg)`}}>
				<rect x={20} y={40} width={260} height={56} rx={10} fill="#2a2a30" stroke={TINTA} strokeWidth={9} />
				<rect x={30} y={90} width={70} height={100} rx={12} fill="#3a3a42" stroke={TINTA} strokeWidth={9} />
			</svg>
			{/* mano de ella: puño de encaje y anillo */}
			<div style={{position: 'absolute', left: ella.x, top: ella.y, width: 900, height: 140}}>
				<div style={{position: 'absolute', left: 150, top: 0, width: 800, height: 140, background: '#4a5a7a', border: `9px solid ${TINTA}`, borderRadius: 40}} />
				<div style={{position: 'absolute', left: 120, top: -14, width: 70, height: 168, background: '#f4f1e8', border: `7px solid ${TINTA}`, borderRadius: 24}} />
				<div style={{position: 'absolute', left: 0, top: 6, width: 170, height: 128, background: '#f6e2d4', border: `9px solid ${TINTA}`, borderRadius: '70px 50px 50px 70px'}} />
				<div style={{position: 'absolute', left: 40, top: 60, width: 30, height: 30, borderRadius: '50%', border: '7px solid #e0b23a'}} />
			</div>
		</div>
	);
};

/** intertítulo de cine mudo */
export const Intertitulo: React.FC<{texto: string; sub?: string}> = ({texto, sub}) => {
	const f = useCurrentFrame();
	return (
		<div style={{position: 'absolute', inset: 0, background: '#0c0b0a'}}>
			<div style={{position: 'absolute', left: 300, right: 300, top: 160, bottom: 160, border: '8px solid #e9e2d0', borderRadius: 30, outline: '3px solid #e9e2d0', outlineOffset: -24}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 360, textAlign: 'center', fontFamily: SERIF, fontStyle: 'italic', fontWeight: 900, fontSize: 220, color: '#efe8d6', letterSpacing: 20}}>{texto}</div>
			{sub && <div style={{position: 'absolute', left: 0, right: 0, top: 660, textAlign: 'center', fontFamily: SERIF, fontSize: 50, color: '#cfc6b0'}}>{sub}</div>}
			{/* rayas y polvo de película */}
			{Array.from({length: 6}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: ((f * 37 + i * 311) % 1920), top: 0, width: 2, height: 1080, background: 'rgba(255,255,255,0.15)'}} />
			))}
			<div style={{position: 'absolute', inset: 0, opacity: 0.1 + 0.05 * Math.sin(f * 3), background: '#fff'}} />
		</div>
	);
};

/** periódico que llega girando (titular de época) */
export const Periodico: React.FC<{x: number; y: number; ancho: number; titular: string; sub?: string; desde: number; fecha?: string}> = ({x, y, ancho, titular, sub, desde, fecha = 'MÚNICH, 10 DE NOVIEMBRE DE 1923'}) => {
	const f = useCurrentFrame();
	const t = interpolate(f, [desde, desde + 16], [0, 1], {...clamp, easing: (u) => 1 - Math.pow(1 - u, 3)});
	const k = ancho / 1000;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.36, width: ancho, height: ancho * 0.72, transform: `rotate(${(1 - t) * 720 - 3}deg) scale(${0.1 + 0.9 * t})`, background: '#efe9d8', border: `${9 * k}px solid ${TINTA}`, boxShadow: `${16 * k}px ${20 * k}px 0 rgba(0,0,0,0.35)`, padding: `${26 * k}px ${40 * k}px`, boxSizing: 'border-box', color: '#1e1a14'}}>
			<div style={{textAlign: 'center', fontFamily: SERIF, fontWeight: 900, fontSize: 70 * k, borderBottom: `${5 * k}px solid #1e1a14`}}>Münchner Tageblatt</div>
			<div style={{textAlign: 'center', fontFamily: TITULAR, fontSize: 24 * k, padding: `${6 * k}px 0`, borderBottom: `${3 * k}px solid #1e1a14`}}>{fecha}</div>
			<div style={{textAlign: 'center', fontFamily: CONDENSADA, fontSize: 110 * k, lineHeight: 1.0, marginTop: 24 * k}}>{titular}</div>
			{sub && <div style={{textAlign: 'center', fontFamily: SERIF, fontStyle: 'italic', fontSize: 46 * k, marginTop: 14 * k}}>{sub}</div>}
			{Array.from({length: 4}, (_, i) => (
				<div key={i} style={{display: 'inline-block', width: '23%', marginRight: '2%', marginTop: 24 * k, verticalAlign: 'top'}}>
					{Array.from({length: 5}, (_, j) => (
						<div key={j} style={{height: 8 * k, background: 'rgba(30,26,20,0.35)', marginBottom: 12 * k, width: `${80 + ((i + j) % 3) * 10}%`}} />
					))}
				</div>
			))}
		</div>
	);
};

/* ---------------- la cárcel cómoda ---------------- */

export const EscCalabozo: React.FC = () => (
	<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #2a2a30, #121216)'}}>
		{Array.from({length: 40}, (_, i) => (
			<div key={i} style={{position: 'absolute', left: (i % 8) * 250 - (Math.floor(i / 8) % 2) * 125, top: Math.floor(i / 8) * 150, width: 240, height: 140, border: '6px solid #1a1a1e', background: '#34343c', borderRadius: 10}} />
		))}
		{[600, 1300].map((x) => (
			<svg key={x} width={120} height={500} viewBox="0 0 120 500" style={{position: 'absolute', left: x, top: 200}}>
				{Array.from({length: 9}, (_, i) => (
					<ellipse key={i} cx={60} cy={20 + i * 44} rx={22} ry={30} fill="none" stroke="#7a7a84" strokeWidth={10} />
				))}
			</svg>
		))}
		<div style={{position: 'absolute', left: 860, top: 160, width: 200, height: 160, background: '#0a0a0c', border: `8px solid ${TINTA}`}}>
			{[0, 1, 2, 3].map((i) => (
				<div key={i} style={{position: 'absolute', left: 20 + i * 48, top: 0, width: 14, height: 160, background: '#5a5a62'}} />
			))}
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 860, bottom: 0, background: '#1a1a1e'}} />
	</div>
);

export const EscCeldaPastel: React.FC = () => (
	<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #f6d6e0 0%, #f0c6d4 70%)'}}>
		{/* papel tapiz de flores */}
		{Array.from({length: 48}, (_, i) => (
			<div key={i} style={{position: 'absolute', left: (i % 12) * 170 + (Math.floor(i / 12) % 2) * 85, top: 40 + Math.floor(i / 12) * 170, width: 40, height: 40, borderRadius: '50%', background: '#fbe9a0', boxShadow: '0 0 0 10px rgba(255,255,255,0.45)'}} />
		))}
		{/* ventana con rejas... y cortinas con volantes */}
		<div style={{position: 'absolute', left: 1240, top: 140, width: 360, height: 300, background: 'linear-gradient(180deg, #bfe3f5, #e8f6fb)', border: `9px solid ${TINTA}`}}>
			{[0, 1, 2, 3].map((i) => (
				<div key={i} style={{position: 'absolute', left: 40 + i * 80, top: 0, width: 16, height: 300, background: '#8a8a94', borderLeft: `4px solid ${TINTA}`, borderRight: `4px solid ${TINTA}`}} />
			))}
		</div>
		{[1180, 1560].map((x, i) => (
			<div key={i} style={{position: 'absolute', left: x, top: 110, width: 100, height: 400, background: '#bfe8d0', border: `7px solid ${TINTA}`, borderRadius: '10px 10px 50px 50px'}} />
		))}
		<div style={{position: 'absolute', left: 0, right: 0, top: 820, bottom: 0, background: 'linear-gradient(180deg, #c9e8d6, #a9d6bc)'}} />
		{/* alfombra */}
		<div style={{position: 'absolute', left: 520, right: 520, top: 880, height: 140, borderRadius: '50%', background: '#f6b9c9', border: `7px solid ${TINTA}`}} />
	</div>
);

export const Cama: React.FC<{x: number; y: number; ancho: number}> = ({x, y, ancho}) => {
	const k = ancho / 600;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - 300 * k, width: ancho, height: 300 * k}}>
			<div style={{position: 'absolute', left: 0, top: 0, width: 60 * k, height: 300 * k, background: '#e9c9a0', border: `${8 * k}px solid ${TINTA}`, borderRadius: 14 * k}} />
			<div style={{position: 'absolute', left: 40 * k, right: 0, top: 120 * k, height: 120 * k, background: '#fbe0ea', border: `${8 * k}px solid ${TINTA}`, borderRadius: 20 * k}} />
			<div style={{position: 'absolute', left: 70 * k, top: 80 * k, width: 150 * k, height: 70 * k, background: '#ffffff', border: `${7 * k}px solid ${TINTA}`, borderRadius: 30 * k}} />
			<div style={{position: 'absolute', left: 240 * k, right: 10 * k, top: 110 * k, height: 110 * k, background: 'repeating-linear-gradient(45deg, #b9e3c9 0 20px, #f6efdc 20px 40px)', border: `${7 * k}px solid ${TINTA}`, borderRadius: 20 * k}} />
		</div>
	);
};

export const Flores: React.FC<{x: number; y: number; tam?: number}> = ({x, y, tam = 1}) => (
	<svg width={200 * tam} height={260 * tam} viewBox="0 0 200 260" style={{position: 'absolute', left: x - 100 * tam, top: y - 260 * tam, overflow: 'visible'}}>
		{[
			[60, 60, '#f05a7a'],
			[110, 40, '#ffd84a'],
			[150, 80, '#f08ad0'],
			[90, 100, '#ff9a4a'],
		].map(([cx, cy, c], i) => (
			<g key={i}>
				<line x1={100} y1={180} x2={cx as number} y2={cy as number} stroke="#3a8a4a" strokeWidth={7} />
				<circle cx={cx as number} cy={cy as number} r={26} fill={c as string} stroke={TINTA} strokeWidth={6} />
				<circle cx={cx as number} cy={cy as number} r={9} fill="#fff3a0" />
			</g>
		))}
		<path d="M 50 170 L 150 170 L 136 256 L 64 256 Z" fill="#7ab8e0" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
	</svg>
);

export const CestaFrutas: React.FC<{x: number; y: number; tam?: number}> = ({x, y, tam = 1}) => (
	<svg width={240 * tam} height={170 * tam} viewBox="0 0 240 170" style={{position: 'absolute', left: x - 120 * tam, top: y - 170 * tam, overflow: 'visible'}}>
		{[
			[70, 60, '#e3262e'],
			[120, 40, '#ffb02e'],
			[170, 60, '#8ac43a'],
			[100, 74, '#a04ad0'],
			[145, 76, '#ffd84a'],
		].map(([cx, cy, c], i) => (
			<circle key={i} cx={cx as number} cy={cy as number} r={30} fill={c as string} stroke={TINTA} strokeWidth={6} />
		))}
		<path d="M 20 80 L 220 80 L 196 166 L 44 166 Z" fill="#c98a3a" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
		<path d="M 40 110 L 200 110 M 52 140 L 188 140" stroke="#8a5a20" strokeWidth={6} />
	</svg>
);

/** montaña de cartas de admiradoras */
export const MontanaCartas: React.FC<{x: number; y: number; ancho: number; n?: number}> = ({x, y, ancho, n = 26}) => (
	<>
		{Array.from({length: n}, (_, i) => {
			const fila = Math.floor(i / 7);
			const bx = x - ancho / 2 + ((i % 7) / 6) * ancho * (1 - fila * 0.18) + fila * ancho * 0.09;
			const by = y - fila * 40;
			return (
				<div key={i} style={{position: 'absolute', left: bx - 50, top: by - 34, width: 100, height: 68, background: '#fbf8ef', border: `5px solid ${TINTA}`, transform: `rotate(${((i * 29) % 40) - 20}deg)`}}>
					<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 34, background: 'linear-gradient(160deg, transparent 49%, #2a2218 50%, transparent 54%), linear-gradient(20deg, transparent 49%, #2a2218 50%, transparent 54%)'}} />
					{i % 3 === 0 && <div style={{position: 'absolute', right: 8, bottom: 6, width: 18, height: 16, background: '#f05a7a', borderRadius: '50% 50% 0 50%', transform: 'rotate(45deg)'}} />}
				</div>
			);
		})}
	</>
);

/* ---------------- libro, portada y lápiz ---------------- */

/** portada lisa, sin símbolos: el título no cabe y se tacha */
export const PortadaLisa: React.FC<{x: number; y: number; ancho: number; titulo: string; tachado?: number; corto?: number; rot?: number; palabras?: number; ajustado?: boolean}> = ({x, y, ancho, titulo, tachado = 0, corto = 0, rot = 2, palabras = 1e9, ajustado = false}) => {
	const k = ancho / 600;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.7, width: ancho, height: ancho * 1.4, transform: `rotate(${rot}deg)`, background: '#8a7a64', border: `${10 * k}px solid ${TINTA}`, borderRadius: 10 * k, boxShadow: `${16 * k}px ${20 * k}px 0 rgba(0,0,0,0.35)`}}>
			<div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 50 * k, background: 'rgba(0,0,0,0.2)'}} />
			<div style={{position: 'absolute', left: 70 * k, width: ajustado ? ancho - 110 * k : ancho * 1.9, top: 120 * k, fontFamily: SERIF, fontWeight: 900, fontSize: (ajustado ? 54 : 64) * k, lineHeight: 1.15, color: '#f6efdc'}}>
				{titulo.split(' ').slice(0, Math.max(0, Math.floor(palabras))).map((w, i) => {
					const queda = false;
					return (
						<span key={i} style={{position: 'relative', marginRight: 16 * k, display: 'inline-block', opacity: corto > 0 ? Math.max(0, 1 - corto * 2) : 1}}>
							{w}
							{!queda && tachado > 0 && <span style={{position: 'absolute', left: -4 * k, top: '48%', height: 10 * k, width: `${Math.min(1, tachado * 1.4) * 108}%`, background: '#d6262e', borderRadius: 5 * k}} />}
						</span>
					);
				})}
			</div>
			{corto > 0 && (
				<div style={{position: 'absolute', left: 0, right: 0, top: 420 * k, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 130 * k, color: '#f6efdc', letterSpacing: 6 * k, opacity: Math.min(1, corto * 2), textShadow: `0 ${6 * k}px 0 rgba(0,0,0,0.35)`}}>
					MI LUCHA
				</div>
			)}
		</div>
	);
};

/** lápiz rojo del editor (en coordenadas del mundo, punta en (x, y)) */
export const LapizRojo: React.FC<{x: number; y: number; largo?: number; rot?: number}> = ({x, y, largo = 360, rot = -35}) => (
	<svg width={largo} height={60} viewBox="0 0 360 60" style={{position: 'absolute', left: x, top: y - 30, transform: `rotate(${rot}deg)`, transformOrigin: '0 50%', overflow: 'visible'}}>
		<path d="M 0 30 L 50 10 L 50 50 Z" fill="#f2d2a0" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
		<path d="M 0 30 L 16 24 L 16 36 Z" fill="#d6262e" />
		<rect x={50} y={10} width={290} height={40} fill="#d6262e" stroke={TINTA} strokeWidth={6} />
		<rect x={330} y={10} width={30} height={40} rx={6} fill="#f08ab0" stroke={TINTA} strokeWidth={6} />
	</svg>
);

/* ---------------- deportar: libro de leyes y mapa ---------------- */

export const LibroLeyes: React.FC<{x: number; y: number; ancho: number; resalta?: number}> = ({x, y, ancho, resalta = 0}) => {
	const k = ancho / 1200;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.33, width: ancho, height: ancho * 0.66, filter: `drop-shadow(0 ${20 * k}px 0 rgba(0,0,0,0.35))`}}>
			<div style={{position: 'absolute', inset: 0, background: '#2a3a5a', borderRadius: 18 * k, border: `${8 * k}px solid ${TINTA}`}} />
			{[0, 1].map((p) => (
				<div key={p} style={{position: 'absolute', top: 18 * k, bottom: 24 * k, left: p ? '50%' : 20 * k, right: p ? 20 * k : '50%', background: 'linear-gradient(90deg,#f3e8cc,#fbf4e2)', border: `${5 * k}px solid ${TINTA}`, padding: `${40 * k}px ${50 * k}px`, boxSizing: 'border-box'}}>
					{p === 0 ? (
						<>
							<div style={{fontFamily: SERIF, fontWeight: 900, fontSize: 44 * k, textAlign: 'center', color: '#2a1f14'}}>Ley de la República</div>
							{Array.from({length: 9}, (_, i) => (
								<div key={i} style={{height: 8 * k, marginTop: 26 * k, background: 'rgba(60,40,20,0.35)', width: `${70 + (i % 3) * 12}%`}} />
							))}
						</>
					) : (
						<>
							<div style={{fontFamily: SERIF, fontStyle: 'italic', fontSize: 34 * k, color: '#2a1f14', lineHeight: 1.4}}>
								Art. 9. Al extranjero condenado por alta traición se le debe
							</div>
							<div style={{display: 'inline-block', marginTop: 20 * k, padding: `${6 * k}px ${18 * k}px`, fontFamily: CONDENSADA, fontSize: 92 * k, letterSpacing: 6 * k, color: '#a8262e', background: `rgba(255,216,74,${0.8 * resalta})`, borderRadius: 8 * k}}>DEPORTAR</div>
							{Array.from({length: 4}, (_, i) => (
								<div key={i} style={{height: 8 * k, marginTop: 26 * k, background: 'rgba(60,40,20,0.35)', width: `${66 + (i % 3) * 12}%`}} />
							))}
						</>
					)}
				</div>
			))}
		</div>
	);
};

/** mapa simple de Alemania y Austria con flecha de Múnich a Austria (`flecha` 0..1, `desvanece` 0..1) */
export const MapaAustria: React.FC<{flecha: number; desvanece?: number}> = ({flecha, desvanece = 0}) => {
	const largo = 520;
	return (
		<div style={{position: 'absolute', inset: 0, background: '#c9b98a'}}>
			<svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0}}>
				{Array.from({length: 8}, (_, i) => <line key={i} x1={i * 280} y1={0} x2={i * 280} y2={1080} stroke="#5a4a2a" strokeWidth={2} opacity={0.2} />)}
				<path d="M 520 120 L 760 60 L 1000 110 L 1180 80 L 1300 200 L 1340 380 L 1260 520 L 1300 640 L 1200 720 L 1020 760 L 880 820 L 700 780 L 560 700 L 480 560 L 500 400 L 440 260 Z" fill="#e9dcb4" stroke="#5a4a2a" strokeWidth={9} strokeLinejoin="round" />
				<path d="M 880 820 L 1020 760 L 1200 720 L 1300 760 L 1520 740 L 1660 800 L 1620 900 L 1400 940 L 1160 930 L 980 900 Z" fill="#e2cfa0" stroke="#5a4a2a" strokeWidth={9} strokeLinejoin="round" />
				<text x={860} y={420} textAnchor="middle" fontFamily={CONDENSADA} fontSize={70} fill="#5a4a2a" letterSpacing={8}>ALEMANIA</text>
				<text x={1330} y={860} textAnchor="middle" fontFamily={CONDENSADA} fontSize={60} fill="#5a4a2a" letterSpacing={8}>AUSTRIA</text>
				<circle cx={960} cy={700} r={16} fill="#a8262e" stroke={TINTA} strokeWidth={5} />
				<text x={960} y={670} textAnchor="middle" fontFamily={TITULAR} fontWeight={800} fontSize={34} fill="#2a2218">Múnich</text>
				<g opacity={1 - desvanece}>
					<path d="M 990 720 Q 1120 640 1300 790" stroke="#d6262e" strokeWidth={22} fill="none" strokeLinecap="round" strokeDasharray={`${largo * flecha} ${largo}`} />
					{flecha > 0.95 && <path d="M 1300 790 L 1250 790 L 1290 750 Z" fill="#d6262e" stroke={TINTA} strokeWidth={6} transform="rotate(20 1300 790)" />}
				</g>
			</svg>
		</div>
	);
};

/* ---------------- la salida de la cárcel ---------------- */

export const PuertaCarcel: React.FC<{abre: number}> = ({abre}) => (
	<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #9aa6b2 0%, #c9d2da 60%, #8a8f96 100%)'}}>
		<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 860, background: '#7a7266'}}>
			{Array.from({length: 50}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: (i % 10) * 200 - (Math.floor(i / 10) % 2) * 100, top: Math.floor(i / 10) * 120, width: 190, height: 110, border: '5px solid #5a544a', background: '#8a8276'}} />
			))}
		</div>
		<div style={{position: 'absolute', left: 560, top: 140, width: 800, height: 720, background: '#141418', border: `12px solid ${TINTA}`, borderRadius: '400px 400px 0 0', overflow: 'hidden'}}>
			<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 70%, rgba(255,240,200,0.6), rgba(255,240,200,0) 70%)'}} />
			{[0, 1].map((lado) => (
				<div key={lado} style={{position: 'absolute', top: 0, bottom: 0, width: 400, left: lado ? 400 : 0, background: '#4a4a52', border: `9px solid ${TINTA}`, transform: `perspective(1400px) rotateY(${(lado ? 1 : -1) * abre * 80}deg)`, transformOrigin: lado ? '100% 50%' : '0% 50%'}}>
					{Array.from({length: 6}, (_, i) => (
						<div key={i} style={{position: 'absolute', left: 30 + i * 62, top: 0, bottom: 0, width: 16, background: '#2a2a30'}} />
					))}
				</div>
			))}
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 860, bottom: 0, background: '#9a9488'}} />
	</div>
);

/** flashes de cámaras que estallan alrededor */
export const Flashes: React.FC<{desde: number; n?: number}> = ({desde, n = 9}) => {
	const f = useCurrentFrame();
	const t = f - desde;
	if (t < 0) return null;
	return (
		<>
			{Array.from({length: n}, (_, i) => {
				const ti = t - i * 3;
				if (ti < 0 || ti > 8) return null;
				const x = 200 + ((i * 431) % 1520);
				const y = 160 + ((i * 263) % 640);
				const s = interpolate(ti, [0, 2, 8], [0.3, 1.2, 0.2]);
				return (
					<svg key={i} width={260} height={260} viewBox="-100 -100 200 200" style={{position: 'absolute', left: x - 130, top: y - 130, transform: `scale(${s})`, overflow: 'visible'}}>
						<polygon points="0,-100 18,-18 100,0 18,18 0,100 -18,18 -100,0 -18,-18" fill="#fffbe0" />
						<circle r={30} fill="#ffffff" />
					</svg>
				);
			})}
			<div style={{position: 'absolute', inset: 0, background: '#fff', opacity: Math.max(0, 0.35 - (t % 6) * 0.08) * (t < 30 ? 1 : 0)}} />
		</>
	);
};

export const Maleta: React.FC<{x: number; y: number; ancho: number; rot?: number}> = ({x, y, ancho, rot = 0}) => {
	const k = ancho / 300;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - 200 * k, width: ancho, height: 200 * k, transform: `rotate(${rot}deg)`, transformOrigin: '50% 100%'}}>
			<div style={{position: 'absolute', left: 110 * k, top: 0, width: 80 * k, height: 40 * k, border: `${9 * k}px solid ${TINTA}`, borderBottom: 'none', borderRadius: `${20 * k}px ${20 * k}px 0 0`}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 36 * k, bottom: 0, background: '#8a5a32', border: `${9 * k}px solid ${TINTA}`, borderRadius: 16 * k}}>
				<div style={{position: 'absolute', left: 60 * k, top: 0, bottom: 0, width: 20 * k, background: '#5a3a1e'}} />
				<div style={{position: 'absolute', right: 60 * k, top: 0, bottom: 0, width: 20 * k, background: '#5a3a1e'}} />
			</div>
		</div>
	);
};

/** libro (cerrado, liso, sin símbolos) para llevar en la mano izquierda */
export const LibroManoLiso: React.FC<{rot?: number}> = ({rot = 0}) => (
	<g transform={`rotate(${rot} 0 36)`}>
		<rect x={-50} y={10} width={100} height={140} rx={8} fill="#8a7a64" stroke={TINTA} strokeWidth={7} />
		<rect x={-50} y={10} width={16} height={140} fill="rgba(0,0,0,0.25)" />
	</g>
);

/** letrero de calle que apunta a Austria (se desvanece) */
export const LetreroAustria: React.FC<{x: number; y: number; opacidad: number}> = ({x, y, opacidad}) => (
	<div style={{position: 'absolute', left: x, top: y, opacity: opacidad}}>
		<div style={{position: 'absolute', left: -12, top: 0, width: 24, height: 520, background: '#6a4a2a', border: `7px solid ${TINTA}`}} />
		<svg width={440} height={130} viewBox="0 0 440 130" style={{position: 'absolute', left: -60, top: 20, overflow: 'visible'}}>
			<path d="M 6 10 L 360 10 L 432 65 L 360 120 L 6 120 Z" fill="#e8c58a" stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
			<text x={200} y={88} textAnchor="middle" fontFamily={CONDENSADA} fontSize={70} fill={TINTA} letterSpacing={4}>
				AUSTRIA
			</text>
		</svg>
	</div>
);

/** banquillo del acusado (va delante del personaje) */
export const Banquillo: React.FC<{x: number; y: number; ancho: number}> = ({x, y, ancho}) => (
	<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: 1080 - y + 40}}>
		<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 34, background: '#6b4a2b', border: `8px solid ${TINTA}`, borderRadius: 6}} />
		<div style={{position: 'absolute', left: 14, right: 14, top: 34, bottom: 0, background: 'linear-gradient(180deg, #4a3220, #2e1e12)', border: `8px solid ${TINTA}`, borderTop: 'none'}}>
			{[0, 1, 2].map((i) => (
				<div key={i} style={{position: 'absolute', left: 30 + i * ((ancho - 60) / 3), top: 30, width: (ancho - 120) / 3, height: 160, border: `6px solid ${TINTA}`, opacity: 0.5, borderRadius: 6}} />
			))}
		</div>
	</div>
);

/** pancarta de tela pintada a mano (letras desparejas, torcida) */
export const PancartaMano: React.FC<{x: number; y: number; ancho: number; texto?: string; rot?: number}> = ({x, y, ancho, texto = 'PARTIDO OBRERO ALEMÁN', rot = -3.5}) => {
	const k = ancho / 900;
	const palabras = texto.split(' ');
	let n = 0;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, transform: `rotate(${rot}deg)`, background: '#efe6cf', border: `${7 * k}px solid ${TINTA}`, borderRadius: `${6 * k}px ${18 * k}px ${10 * k}px ${22 * k}px`, padding: `${16 * k}px ${20 * k}px`, boxSizing: 'border-box', textAlign: 'center', boxShadow: `${10 * k}px ${12 * k}px 0 rgba(0,0,0,0.3)`}}>
			{palabras.map((w, i) => (
				<span key={i} style={{display: 'inline-block', marginRight: 22 * k}}>
					{w.split('').map((c) => {
						n++;
						return (
							<span key={n} style={{display: 'inline-block', fontFamily: TITULAR, fontWeight: 800, fontSize: (74 + ((n * 37) % 13) - 6) * k, color: '#5a1a14', transform: `rotate(${((n * 53) % 11) - 5}deg) translateY(${((n * 29) % 9) - 4}px)`, lineHeight: 1.15}}>
								{c}
							</span>
						);
					})}
				</span>
			))}
			<div style={{position: 'absolute', left: 30 * k, top: -30 * k, width: 8 * k, height: 34 * k, background: '#6a4a2a'}} />
			<div style={{position: 'absolute', right: 30 * k, top: -30 * k, width: 8 * k, height: 34 * k, background: '#6a4a2a'}} />
		</div>
	);
};

/** auto de los años 20 visto de lado. (x, y) = suelo bajo las ruedas */
export const AutoViejo: React.FC<{x: number; y: number; ancho: number; color?: string; rueda?: number; puerta?: number}> = ({x, y, ancho, color = '#2f4a3a', rueda = 0, puerta = 0}) => {
	const k = ancho / 600;
	return (
		<svg width={ancho} height={300 * k} viewBox="0 0 600 300" style={{position: 'absolute', left: x - ancho / 2, top: y - 300 * k, overflow: 'visible'}}>
			<ellipse cx={300} cy={292} rx={280} ry={12} fill="rgba(0,0,0,0.3)" />
			{/* guardabarros y estribo */}
			<path d="M 70 240 Q 80 168 150 168 Q 220 168 230 220 L 400 220 Q 410 168 480 168 Q 556 168 570 240 Z" fill="#1b1b22" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
			{/* capó y radiador */}
			<path d="M 380 130 L 560 140 L 560 214 L 380 214 Z" fill={color} stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
			<rect x={556} y={120} width={30} height={96} rx={6} fill="#c9c9d0" stroke={TINTA} strokeWidth={7} />
			{[136, 152, 168, 184, 200].map((yy) => (
				<line key={yy} x1={562} y1={yy} x2={580} y2={yy} stroke={TINTA} strokeWidth={3} />
			))}
			<circle cx={548} cy={124} r={16} fill="#fff6b0" stroke={TINTA} strokeWidth={6} />
			{/* cabina alta */}
			<path d="M 120 214 L 130 70 Q 134 50 160 50 L 360 50 Q 384 50 386 70 L 392 214 Z" fill={color} stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
			<rect x={110} y={40} width={292} height={20} rx={8} fill="#1b1b22" stroke={TINTA} strokeWidth={6} />
			<rect x={150} y={72} width={90} height={70} rx={6} fill="#9fb8c8" stroke={TINTA} strokeWidth={6} />
			<g transform={`translate(254 0) scale(${1 - puerta * 0.6} 1) translate(-254 0)`}>
				<path d="M 254 66 L 376 66 L 380 214 L 254 214 Z" fill={color} stroke={TINTA} strokeWidth={6} />
				<rect x={266} y={72} width={98} height={70} rx={6} fill="#9fb8c8" stroke={TINTA} strokeWidth={6} />
				<rect x={350} y={160} width={22} height={8} rx={4} fill={TINTA} />
			</g>
			{/* ruedas de rayos */}
			{[150, 480].map((cx) => (
				<g key={cx} transform={`rotate(${rueda} ${cx} 240)`}>
					<circle cx={cx} cy={240} r={50} fill="#1b1b22" stroke={TINTA} strokeWidth={6} />
					<circle cx={cx} cy={240} r={36} fill="#d9cdb0" stroke={TINTA} strokeWidth={4} />
					{Array.from({length: 8}, (_, i) => (
						<line key={i} x1={cx} y1={240} x2={cx + Math.cos((i * Math.PI) / 4) * 34} y2={240 + Math.sin((i * Math.PI) / 4) * 34} stroke={TINTA} strokeWidth={4} />
					))}
					<circle cx={cx} cy={240} r={9} fill={TINTA} />
				</g>
			))}
		</svg>
	);
};

/** lápiz rojo en la mano (punta hacia +y) */
export const LapizRojoMano: React.FC<{rot?: number}> = ({rot = 0}) => (
	<g transform={`rotate(${rot} 0 36)`}>
		<rect x={-14} y={0} width={28} height={230} fill="#d6262e" stroke={TINTA} strokeWidth={6} />
		<path d="M -14 230 L 14 230 L 0 280 Z" fill="#f2d2a0" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
		<path d="M -5 262 L 5 262 L 0 280 Z" fill="#d6262e" />
	</g>
);

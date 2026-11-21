import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Ropa} from '../componentes/Muneco';
import {Diseno} from '../componentes/Personaje';
import {CONDENSADA, MONO, SERIF, TITULAR} from '../fuentes';
import {TINTA, clamp} from './base';

/* Escenarios, utilería y vestuario del short de la Torre Eiffel (París, 1925; todo en vertical 1080x1920). */

const lleno: React.CSSProperties = {position: 'absolute', inset: 0};
const cabeza = (extra: Partial<Diseno>): Diseno => ({piel: '#ffffff', chaqueta: '', chaquetaSombra: '', botones: '', ...extra});

/* ---------------- vestuario ---------------- */

export const LUSTIG: Ropa = {
	cabeza: cabeza({pelo: 'raya', colorPelo: '#2a1c12', gorra: 'fedora', colorGorra: '#1c1c22', colorBanda: '#6a2a2a', bigote: 'fino', colorBigote: '#2a1c12', cicatriz: true}),
	casaca: '#2a2a34', casacaSombra: '#1a1a22', chaleco: '#e9e4d6', botones: '#c9c9c9', rayas: '#3a3a46', pantalon: '#2a2a34', zapatos: '#141418', corbata: '#8a1e2a', punos: '#ffffff',
};
export const LUSTIG_SIN_SOMBRERO: Ropa = {...LUSTIG, cabeza: {...LUSTIG.cabeza, gorra: undefined}};

const obrero = (casaca: string, gorra: Diseno['gorra'], extra: Partial<Diseno> = {}): Ropa => ({
	cabeza: cabeza({pelo: 'corto', colorPelo: '#3a2a1e', gorra, colorGorra: '#4a4a52', colorBanda: '#2a2a30', ...extra}),
	casaca, casacaSombra: '#00000033', chaleco: '#c9b48a', botones: '#3a3a3a', pantalon: '#4a4038', zapatos: '#2a1d14',
});
/** los seis chatarreros: gordo, muy alto, con lupa, desconfiado, dormido y el nervioso (el futuro comprador) */
export const CH_GORDO = obrero('#6a5a48', 'boina', {bigote: 'morsa', colorBigote: '#4a3a2a'});
export const CH_ALTO = obrero('#4a5a6a', 'fedora', {pelo: 'calvo'});
export const CH_LUPA = obrero('#5a6a4a', 'boina', {lentes: true});
export const CH_DESCONFIADO = obrero('#6a4a4a', 'fedora', {bigote: 'manubrio', colorBigote: '#2a1c12'});
export const CH_DORMIDO = obrero('#5a5a62', 'boina', {pelo: 'raya', colorPelo: '#8a8a8a'});
export const POISSON: Ropa = {
	cabeza: cabeza({pelo: 'raya', colorPelo: '#6b4a2b', gorra: 'boina', colorGorra: '#3a4a6a', bigote: 'manubrio', colorBigote: '#6b4a2b'}),
	casaca: '#7a6a3a', casacaSombra: '#5a4e2a', chaleco: '#e0d2a8', botones: '#3a3a3a', pantalon: '#4a4038', zapatos: '#2a1d14', corbata: '#2a4a6a',
};
export const POISSON_FRAC: Ropa = {...POISSON, cabeza: {...POISSON.cabeza, gorra: 'chistera', colorGorra: '#1c1c22'}, casaca: '#1c1c22', casacaSombra: '#0e0e12', chaleco: '#ffffff', faldones: true, corbata: '#ffffff', punos: '#ffffff'};
export const ESPOSA: Ropa = {
	cabeza: cabeza({pelo: 'melena', colorPelo: '#3a2414', lentes: false}),
	casaca: '#7a3a5a', casacaSombra: '#5a2a44', botones: '#e0b23a', pantalon: '#7a3a5a', zapatos: '#2a1d14',
	vestido: {color: '#7a3a5a', sombra: '#5a2a44', ancho: 110, lazos: '#e0b23a'},
};
export const POLICIA_FR: Ropa = {
	cabeza: cabeza({gorra: 'militar', colorGorra: '#1f2a4a', colorBanda: '#c8202a', bigote: 'manubrio', colorBigote: '#2a1c12'}),
	casaca: '#1f2a4a', casacaSombra: '#141c34', botones: '#e0b23a', pantalon: '#1f2a4a', botas: '#141418', cinturon: '#141418',
};

/* ---------------- París al atardecer y la torre ---------------- */

export const EscParisAtardecer: React.FC<{desplaza?: number}> = ({desplaza = 0}) => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #2a2a6a 0%, #8a4a8a 32%, #f08a5a 58%, #ffc97a 70%)'}}>
		<div style={{position: 'absolute', left: 620, top: 1060, width: 260, height: 260, borderRadius: '50%', background: '#ffe2a0', boxShadow: '0 0 120px 50px rgba(255,200,120,0.55)'}} />
		{/* tejados de París (paralaje) */}
		<div style={{position: 'absolute', left: -200 + desplaza * 0.4, right: -200 - desplaza * 0.4, top: 1240, height: 420, background: '#4a2a4a', clipPath: 'polygon(0 40%, 6% 40%, 6% 22%, 10% 22%, 10% 40%, 18% 40%, 22% 15%, 26% 40%, 34% 40%, 34% 25%, 40% 25%, 40% 45%, 50% 45%, 54% 18%, 58% 45%, 66% 45%, 66% 28%, 72% 28%, 72% 42%, 82% 42%, 86% 20%, 90% 42%, 100% 42%, 100% 100%, 0 100%)'}} />
		<div style={{position: 'absolute', left: -200 + desplaza * 0.8, right: -200 - desplaza * 0.8, top: 1420, height: 520, background: '#2a1830', clipPath: 'polygon(0 30%, 8% 30%, 8% 12%, 12% 12%, 12% 30%, 24% 30%, 28% 8%, 32% 30%, 44% 30%, 44% 18%, 52% 18%, 52% 32%, 64% 32%, 68% 10%, 72% 32%, 84% 32%, 84% 16%, 90% 16%, 90% 30%, 100% 30%, 100% 100%, 0 100%)'}} />
		{Array.from({length: 18}, (_, i) => (
			<div key={i} style={{position: 'absolute', left: ((i * 173 + desplaza) % 1300) - 100, top: 1560 + (i % 3) * 90, width: 22, height: 30, background: '#ffd27a', opacity: 0.7}} />
		))}
	</div>
);

/** la Torre Eiffel: celosía de hierro (y, base en el suelo). oxido 0..1; chatarra 0..1 la convierte en un montón de barras */
export const TorreEiffel: React.FC<{x: number; y: number; alto: number; oxido?: number; chatarra?: number; color?: string}> = ({x, y, alto, oxido = 0, chatarra = 0, color = '#6a4a3a'}) => {
	const f = useCurrentFrame();
	const k = alto / 1000;
	const ancho = 640 * k;
	if (chatarra > 0.5) {
		return (
			<svg width={ancho * 1.4} height={alto * 0.4} viewBox="0 0 900 400" style={{position: 'absolute', left: x - ancho * 0.7, top: y - alto * 0.4, overflow: 'visible'}}>
				{Array.from({length: 26}, (_, i) => (
					<line key={i} x1={100 + ((i * 97) % 700)} y1={400 - ((i * 53) % 200)} x2={160 + ((i * 131) % 660)} y2={400 - ((i * 71) % 260)} stroke={color} strokeWidth={22} strokeLinecap="round" />
				))}
				<path d="M 60 400 Q 450 120 840 400 Z" fill="rgba(0,0,0,0.12)" />
			</svg>
		);
	}
	const piernas = 'M 40 1000 Q 150 700 260 360 L 300 0 L 340 0 L 380 360 Q 490 700 600 1000 L 470 1000 Q 400 820 320 760 Q 240 820 170 1000 Z';
	return (
		<svg width={ancho} height={alto} viewBox="0 0 640 1000" style={{position: 'absolute', left: x - ancho / 2, top: y - alto, overflow: 'visible'}}>
			<defs>
				<pattern id="celosia" width="28" height="28" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
					<rect width="28" height="28" fill={color} />
					<line x1={0} y1={0} x2={0} y2={28} stroke="rgba(0,0,0,0.45)" strokeWidth={5} />
					<line x1={0} y1={0} x2={28} y2={0} stroke="rgba(0,0,0,0.45)" strokeWidth={5} />
				</pattern>
			</defs>
			<path d={piernas} fill="url(#celosia)" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
			{/* plataformas */}
			<rect x={150} y={600} width={340} height={30} fill={color} stroke={TINTA} strokeWidth={7} />
			<rect x={235} y={360} width={170} height={24} fill={color} stroke={TINTA} strokeWidth={7} />
			<path d="M 296 0 L 320 -60 L 344 0 Z" fill={color} stroke={TINTA} strokeWidth={6} />
			<path d="M 170 1000 Q 320 740 470 1000" fill="none" stroke={TINTA} strokeWidth={8} />
			{/* óxido y pintura que se cae */}
			{oxido > 0 &&
				Array.from({length: 22}, (_, i) => (
					<circle key={i} cx={180 + ((i * 113) % 290)} cy={120 + ((i * 211) % 820)} r={10 + (i % 4) * 6} fill="#b8582a" opacity={oxido * 0.85} />
				))}
			{oxido > 0 &&
				Array.from({length: 10}, (_, i) => {
					const t = (f * (2 + (i % 3)) + i * 37) % 240;
					return <rect key={`p${i}`} x={200 + ((i * 59) % 240)} y={200 + ((i * 131) % 500) + t * 2} width={14} height={8} fill="#8a6a5a" opacity={oxido * (1 - t / 240)} transform={`rotate(${t * 3} ${210 + ((i * 59) % 240)} ${204 + ((i * 131) % 500) + t * 2})`} />;
				})}
		</svg>
	);
};

/** cartel colgante «SE VENDE» */
export const Cartel: React.FC<{x: number; y: number; ancho: number; texto?: string; rot?: number; color?: string}> = ({x, y, ancho, texto = 'SE VENDE', rot = -4, color = '#d6262e'}) => {
	const k = ancho / 500;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, transform: `rotate(${rot}deg)`, transformOrigin: '50% 0'}}>
			<div style={{position: 'absolute', left: 60 * k, top: -60 * k, width: 6 * k, height: 70 * k, background: TINTA, transform: 'rotate(20deg)'}} />
			<div style={{position: 'absolute', right: 60 * k, top: -60 * k, width: 6 * k, height: 70 * k, background: TINTA, transform: 'rotate(-20deg)'}} />
			<div style={{background: '#f6efdc', border: `${10 * k}px solid ${TINTA}`, padding: `${12 * k}px 0`, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 110 * k, color, letterSpacing: 4 * k, lineHeight: 1.05, boxShadow: `${10 * k}px ${12 * k}px 0 rgba(0,0,0,0.35)`}}>{texto}</div>
		</div>
	);
};

/* ---------------- el plano original ---------------- */

export const PlanoTorre: React.FC = () => (
	<div style={{...lleno, background: '#1f4a8a'}}>
		<div style={{...lleno, background: 'repeating-linear-gradient(0deg, rgba(255,255,255,0.08) 0 2px, transparent 2px 60px), repeating-linear-gradient(90deg, rgba(255,255,255,0.08) 0 2px, transparent 2px 60px)'}} />
		<div style={{position: 'absolute', inset: 0, filter: 'brightness(0) invert(1)', opacity: 0.85}}>
			<TorreEiffel x={540} y={1500} alto={1150} color="#1f4a8a" />
		</div>
		<div style={{position: 'absolute', left: 60, top: 300, fontFamily: MONO, fontSize: 34, color: '#e8f0ff', lineHeight: 1.5}}>
			PLANO Nº 1 · EXPOSICIÓN 1889
			<br />
			ALTURA: 300 m
		</div>
	</div>
);

/* ---------------- interiores ---------------- */

export const EscCafe: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #6a3a2a 0%, #4a2a1e 60%, #2a1810 100%)'}}>
		<div style={{position: 'absolute', left: 120, top: 250, width: 840, height: 620, background: 'linear-gradient(180deg, #f0a06a, #ffd2a0)', border: `14px solid #3a2014`, outline: `6px solid ${TINTA}`}}>
			<div style={{position: 'absolute', left: 410, top: 0, width: 14, height: '100%', background: '#3a2014'}} />
			<div style={{position: 'absolute', left: 0, top: 300, width: '100%', height: 14, background: '#3a2014'}} />
		</div>
		{/* toldo a rayas */}
		<div style={{position: 'absolute', left: 80, top: 200, width: 920, height: 90, background: 'repeating-linear-gradient(90deg, #c8202a 0 60px, #f6efdc 60px 120px)', border: `6px solid ${TINTA}`, borderRadius: '0 0 30px 30px'}} />
		<div style={{position: 'absolute', left: 0, right: 0, top: 1300, bottom: 0, background: 'repeating-linear-gradient(90deg, #2a1810 0 80px, #3a2214 80px 160px)'}} />
	</div>
);

export const TazaCafe: React.FC<{x: number; y: number}> = ({x, y}) => (
	<svg width={120} height={90} viewBox="0 0 120 90" style={{position: 'absolute', left: x - 60, top: y - 90, overflow: 'visible'}}>
		<ellipse cx={56} cy={84} rx={56} ry={8} fill="#f4f1e8" stroke={TINTA} strokeWidth={4} />
		<path d="M 20 30 L 92 30 L 84 78 L 28 78 Z" fill="#f4f1e8" stroke={TINTA} strokeWidth={5} />
		<path d="M 92 40 Q 116 44 100 64" stroke={TINTA} strokeWidth={6} fill="none" />
		<path d="M 46 20 Q 40 6 50 -6 M 66 20 Q 60 6 70 -6" stroke="rgba(255,255,255,0.7)" strokeWidth={4} fill="none" />
	</svg>
);

export const EscHotelLujo: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<div style={{...lleno, background: 'linear-gradient(180deg, #5a1e2a 0%, #3a1018 60%, #1e080c 100%)'}}>
			{[0, 1, 2].map((i) => (
				<div key={i} style={{position: 'absolute', left: 60 + i * 340, top: 300, width: 280, height: 640, border: '10px solid rgba(224,178,58,0.45)', borderRadius: '140px 140px 8px 8px'}} />
			))}
			{[270, 810].map((x, i) => (
				<React.Fragment key={i}>
					<div style={{position: 'absolute', left: x - 3, top: 0, width: 6, height: 200, background: '#c9a43a'}} />
					<div style={{position: 'absolute', left: x - 140, top: 190, width: 280, height: 70, borderRadius: '0 0 140px 140px', border: '9px solid #c9a43a', borderTop: 'none'}} />
					{[0, 1, 2, 3, 4].map((k) => (
						<div key={k} style={{position: 'absolute', left: x - 130 + k * 62, top: 236 + Math.abs(2 - k) * -12, width: 16, height: 30, borderRadius: '50%', background: '#fff3c0', boxShadow: `0 0 ${28 + 6 * Math.sin(f / 5 + k)}px 10px rgba(255,230,160,0.7)`}} />
					))}
				</React.Fragment>
			))}
			<div style={{position: 'absolute', left: 0, right: 0, top: 1200, bottom: 0, background: 'linear-gradient(180deg, #7a1e2a, #4a0e18)'}} />
		</div>
	);
};

export const EscCasa: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #a89a6a 0%, #8a7a52 60%)'}}>
		<div style={{...lleno, background: 'repeating-linear-gradient(90deg, rgba(120,90,50,0.22) 0 30px, transparent 30px 90px)'}} />
		<div style={{position: 'absolute', left: 640, top: 300, width: 300, height: 380, background: '#c9a43a', border: `10px solid ${TINTA}`, padding: 16, boxSizing: 'border-box'}}>
			<div style={{width: '100%', height: '100%', background: 'linear-gradient(180deg, #8fa6b8, #6a7a5a)', border: `4px solid ${TINTA}`}} />
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 1240, bottom: 0, background: '#5a3a22', borderTop: `10px solid ${TINTA}`}} />
	</div>
);

export const EscPasillo: React.FC = () => (
	<div style={{...lleno, background: '#3a1820'}}>
		<div style={{position: 'absolute', left: 0, top: 0, width: 640, height: 1920, background: 'linear-gradient(90deg, #5a2430, #3a1820)'}} />
		<div style={{position: 'absolute', left: 630, top: 0, width: 14, height: 1920, background: 'rgba(0,0,0,0.4)'}} />
		<div style={{position: 'absolute', left: 760, top: 420, width: 220, height: 760, background: '#4a2a1a', border: `8px solid ${TINTA}`, borderRadius: 6}}>
			<div style={{position: 'absolute', left: 170, top: 380, width: 22, height: 22, borderRadius: '50%', background: '#c9a43a', border: `4px solid ${TINTA}`}} />
		</div>
		<div style={{position: 'absolute', left: 60, top: 420, width: 80, height: 120, borderRadius: '40px 40px 6px 6px', background: '#ffe2a0', boxShadow: '0 0 80px 30px rgba(255,220,150,0.5)'}} />
		<div style={{position: 'absolute', left: 0, right: 0, top: 1300, bottom: 0, background: 'repeating-linear-gradient(90deg, #6a1e2a 0 60px, #5a1824 60px 120px)'}} />
	</div>
);

/* ---------------- papeles falsos y el certificado ---------------- */

export const PapelMembrete: React.FC<{x: number; y: number; ancho: number; titulo?: string; lineas?: number}> = ({x, y, ancho, titulo = 'MINISTERIO DE CORREOS Y TELÉGRAFOS', lineas = 7}) => {
	const k = ancho / 800;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: ancho * 1.25, background: '#fbf6e8', border: `${8 * k}px solid ${TINTA}`, padding: `${40 * k}px ${50 * k}px`, boxSizing: 'border-box', boxShadow: `${14 * k}px ${18 * k}px 0 rgba(0,0,0,0.35)`}}>
			<div style={{textAlign: 'center', fontFamily: SERIF, fontWeight: 900, fontSize: 40 * k, color: '#1f2a4a', lineHeight: 1.2}}>RÉPUBLIQUE FRANÇAISE</div>
			<div style={{textAlign: 'center', fontFamily: TITULAR, fontWeight: 800, fontSize: 30 * k, color: '#1f2a4a', marginTop: 8 * k}}>{titulo}</div>
			<div style={{height: 4 * k, background: '#1f2a4a', margin: `${18 * k}px 0 ${30 * k}px`}} />
			{Array.from({length: lineas}, (_, i) => (
				<div key={i} style={{height: 10 * k, background: '#bfb6a0', borderRadius: 5 * k, margin: `${26 * k}px 0`, width: `${[92, 84, 90, 70, 88, 60, 80][i % 7]}%`}} />
			))}
		</div>
	);
};

export const Certificado: React.FC<{x: number; y: number; ancho: number; escribe?: number}> = ({x, y, ancho, escribe = 1}) => {
	const k = ancho / 800;
	const prof = 'Vendedor aprendiz';
	const filas: [string, string][] = [
		['Nombre:', 'Victor Lustig'],
		['Año:', '1947'],
		['Lugar:', 'Prisión federal'],
	];
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, background: '#f2ead4', border: `${8 * k}px solid ${TINTA}`, padding: `${44 * k}px ${54 * k}px`, boxSizing: 'border-box', boxShadow: `${14 * k}px ${18 * k}px 0 rgba(0,0,0,0.35)`, color: '#2a2218'}}>
			<div style={{textAlign: 'center', fontFamily: SERIF, fontWeight: 900, fontSize: 50 * k, lineHeight: 1.1}}>CERTIFICADO DE DEFUNCIÓN</div>
			<div style={{height: 4 * k, background: '#2a2218', margin: `${20 * k}px 0 ${30 * k}px`}} />
			{filas.map(([a, b]) => (
				<div key={a} style={{display: 'flex', gap: 20 * k, fontFamily: MONO, fontSize: 36 * k, margin: `${22 * k}px 0`, borderBottom: `${3 * k}px dotted #8a7a5a`}}>
					<span style={{fontWeight: 700}}>{a}</span>
					<span>{b}</span>
				</div>
			))}
			<div style={{display: 'flex', gap: 20 * k, fontFamily: MONO, fontSize: 40 * k, margin: `${30 * k}px 0 ${10 * k}px`, borderBottom: `${4 * k}px solid #2a2218`, paddingBottom: 6 * k}}>
				<span style={{fontWeight: 700}}>Profesión:</span>
				<span style={{fontFamily: "'Comic Sans MS', cursive", fontStyle: 'italic', color: '#1d2a6b', fontSize: 46 * k}}>{prof.slice(0, Math.round(prof.length * escribe))}</span>
			</div>
		</div>
	);
};

/* ---------------- la balanza dentro de la cabeza ---------------- */

export const CabezaBalanza: React.FC<{inclina: number; cae: number; real: number}> = ({inclina, cae, real}) => {
	const ang = -16 * inclina;
	const brazo = 300;
	const px = (s: number) => 540 + s * brazo * Math.cos((ang * Math.PI) / 180);
	const py = (s: number) => 900 + s * brazo * Math.sin((ang * Math.PI) / 180);
	const plato = (s: number, texto: string) => (
		<g>
			<line x1={px(s)} y1={py(s)} x2={px(s) - 90} y2={py(s) + 170} stroke={TINTA} strokeWidth={5} />
			<line x1={px(s)} y1={py(s)} x2={px(s) + 90} y2={py(s) + 170} stroke={TINTA} strokeWidth={5} />
			<path d={`M ${px(s) - 120} ${py(s) + 170} Q ${px(s)} ${py(s) + 240} ${px(s) + 120} ${py(s) + 170} Z`} fill="#c9a43a" stroke={TINTA} strokeWidth={7} />
			<rect x={px(s) - 130} y={py(s) + 245} width={260} height={60} rx={8} fill="#f6efdc" stroke={TINTA} strokeWidth={5} />
			<text x={px(s)} y={py(s) + 288} textAnchor="middle" fontFamily={CONDENSADA} fontSize={44} fill={TINTA}>{texto}</text>
		</g>
	);
	const cy = interpolate(cae, [0, 1], [380, py(1) + 140], clamp);
	return (
		<svg width={1080} height={1920} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
			{/* la cabeza en corte (perfil) */}
			<path d="M 540 260 C 900 260 1010 560 990 860 C 980 1040 900 1120 900 1220 L 900 1440 L 640 1440 L 640 1360 C 480 1380 360 1360 300 1300 C 250 1250 270 1180 230 1150 C 190 1120 160 1100 190 1060 C 210 1030 200 1000 170 980 C 140 960 160 920 190 900 C 120 700 220 260 540 260 Z" fill="#f6e4d4" stroke={TINTA} strokeWidth={12} />
			<path d="M 540 290 C 860 290 960 560 950 840 C 940 1000 860 1080 860 1160 L 860 1200 C 700 1210 560 1180 470 1120 C 330 1030 260 900 250 780 C 240 560 330 290 540 290 Z" fill="#f0c8c0" opacity={0.6} />
			<rect x={530} y={900} width={20} height={300} fill="#8a6a4a" stroke={TINTA} strokeWidth={5} />
			<rect x={470} y={1190} width={140} height={30} rx={8} fill="#8a6a4a" stroke={TINTA} strokeWidth={5} />
			<line x1={px(-1)} y1={py(-1)} x2={px(1)} y2={py(1)} stroke={TINTA} strokeWidth={16} strokeLinecap="round" />
			<circle cx={540} cy={900} r={18} fill="#c9a43a" stroke={TINTA} strokeWidth={5} />
			{plato(-1, 'ESTAFADOR')}
			{plato(1, 'FUNCIONARIO')}
			{cae > 0 && (
				<g transform={`translate(${px(1)} ${cy}) rotate(${(1 - cae) * 30})`}>
					<rect x={-110} y={-40} width={220} height={80} rx={10} fill="#f6efdc" stroke={TINTA} strokeWidth={6} />
					<text x={0} y={16} textAnchor="middle" fontFamily={CONDENSADA} fontSize={50} fill="#c8202a">SOBORNO</text>
				</g>
			)}
			{real > 0 && (
				<g opacity={real}>
					<rect x={360} y={420} width={360} height={130} rx={20} fill="#1a1a20" stroke={TINTA} strokeWidth={8} />
					<text x={540} y={510} textAnchor="middle" fontFamily={CONDENSADA} fontSize={84} fill="#7dff9a" style={{filter: 'drop-shadow(0 0 14px rgba(125,255,154,0.9))'}}>ES REAL</text>
				</g>
			)}
		</svg>
	);
};

/* ---------------- sobres, tren y comisaría ---------------- */

export const SobreGordo: React.FC<{x: number; y: number; tam: number; rot?: number}> = ({x, y, tam, rot = 0}) => (
	<div style={{position: 'absolute', left: x - tam / 2, top: y - tam * 0.35, width: tam, height: tam * 0.7, transform: `rotate(${rot}deg)`}}>
		<div style={{position: 'absolute', inset: 0, background: '#e9d8a8', border: `${tam * 0.03}px solid ${TINTA}`, borderRadius: tam * 0.04}} />
		{[0, 1, 2].map((i) => (
			<div key={i} style={{position: 'absolute', left: tam * (0.12 + i * 0.04), top: -tam * (0.12 - i * 0.02), width: tam * 0.6, height: tam * 0.24, background: '#7fb07a', border: `${tam * 0.015}px solid ${TINTA}`, transform: `rotate(${-6 + i * 5}deg)`}} />
		))}
		<svg viewBox="0 0 100 70" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
			<polyline points="0,0 50,36 100,0" fill="none" stroke={TINTA} strokeWidth={3} />
		</svg>
	</div>
);

export const Vagon: React.FC<{x: number; y: number; ancho: number; children?: React.ReactNode}> = ({x, y, ancho, children}) => {
	const k = ancho / 900;
	return (
		<div style={{position: 'absolute', left: x, top: y, width: ancho, height: 520 * k}}>
			<div style={{position: 'absolute', inset: 0, background: '#2f4a3a', border: `${10 * k}px solid ${TINTA}`, borderRadius: 20 * k}} />
			<div style={{position: 'absolute', left: 80 * k, top: 70 * k, width: 420 * k, height: 260 * k, background: '#f2d8a0', border: `${8 * k}px solid ${TINTA}`, overflow: 'hidden'}}>{children}</div>
			<div style={{position: 'absolute', left: 580 * k, top: 70 * k, width: 240 * k, height: 260 * k, background: '#f2d8a0', border: `${8 * k}px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 380 * k, height: 30 * k, background: '#c9a43a'}} />
			{[160, 740].map((cx) => (
				<div key={cx} style={{position: 'absolute', left: (cx - 70) * k, top: 440 * k, width: 140 * k, height: 140 * k, borderRadius: '50%', background: '#1a1a20', border: `${8 * k}px solid ${TINTA}`}} />
			))}
		</div>
	);
};

export const Vapor: React.FC<{x: number; y: number; desde: number}> = ({x, y, desde}) => {
	const f = useCurrentFrame();
	const t = Math.max(0, f - desde);
	return (
		<>
			{Array.from({length: 9}, (_, i) => {
				const r = 80 + i * 26 + t * 4;
				return <div key={i} style={{position: 'absolute', left: x - r + (i - 4) * 70, top: y - r - i * 30 - t * 3, width: r * 2, height: r * 2, borderRadius: '50%', background: 'rgba(240,240,245,0.85)', opacity: Math.max(0, 1 - t / 60)}} />;
			})}
		</>
	);
};

export const EscComisaria: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #9aa4b0 0%, #7a8490 60%, #4a525c 100%)'}}>
		<div style={{position: 'absolute', left: 140, top: 260, width: 800, height: 1100, background: '#d8d2c4', border: `10px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: 230, top: 330, width: 620, padding: '14px 0', background: '#1f2a4a', border: `8px solid ${TINTA}`, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 100, color: '#f6efdc', letterSpacing: 6}}>COMISARÍA</div>
		<div style={{position: 'absolute', left: 340, top: 540, width: 400, height: 820, background: '#4a2a1a', border: `10px solid ${TINTA}`, borderRadius: '200px 200px 0 0'}}>
			<div style={{position: 'absolute', left: 300, top: 440, width: 40, height: 40, borderRadius: '50%', background: '#c9a43a', border: `6px solid ${TINTA}`}} />
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 1360, bottom: 0, background: 'repeating-linear-gradient(90deg, #6a6a72 0 120px, #5a5a62 120px 240px)'}} />
	</div>
);

export const Escritorio: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #2a2420 0%, #1a1612 100%)'}}>
		<div style={{position: 'absolute', left: 260, top: 0, width: 560, height: 900, borderRadius: '50%', background: 'radial-gradient(ellipse at 50% 30%, rgba(255,226,170,0.35), rgba(255,226,170,0) 65%)'}} />
		<div style={{position: 'absolute', left: -40, right: -40, top: 980, bottom: -40, background: 'linear-gradient(180deg, #5a3a22, #2e1a0e)', borderTop: `12px solid ${TINTA}`}} />
	</div>
);

export {lleno};

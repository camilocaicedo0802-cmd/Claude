import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Ropa} from '../componentes/Muneco';
import {Diseno} from '../componentes/Personaje';
import {CONDENSADA, MONO, SERIF, TITULAR} from '../fuentes';
import {TINTA, clamp} from './base';

/* Escenarios, utilería y vestuario del short de Roswell (todo en vertical, 1080x1920). */

const lleno: React.CSSProperties = {position: 'absolute', inset: 0};
const cabeza = (extra: Partial<Diseno>): Diseno => ({piel: '#ffffff', chaqueta: '', chaquetaSombra: '', botones: '', ...extra});

/* ---------------- vestuario ---------------- */

export const GRANJERO: Ropa = {
	cabeza: cabeza({pelo: 'corto', colorPelo: '#8a7a68', gorra: 'vaquero', colorGorra: '#c9a46a', colorBanda: '#5a3a22', bigote: 'manubrio', colorBigote: '#8a7a68'}),
	casaca: '#b8442e', casacaSombra: '#8e3222', botones: '#f4ecd6', rayas: '#7a2a1a', pantalon: '#3a5a8a', pantalonSombra: '#2a4470', botas: '#6a4428', cinturon: '#3a2a1a',
};
export const GENERAL_47: Ropa = {
	cabeza: cabeza({gorra: 'militar', colorGorra: '#6b6648', colorBanda: '#4a4630'}),
	casaca: '#6b6648', casacaSombra: '#55513a', botones: '#e0b23a', pantalon: '#b8a88a', pantalonSombra: '#9a8a6e', zapatos: '#3a2a1e', corbata: '#5a5238', cinturon: '#4a3a22',
};
export const FOTOGRAFO: Ropa = {
	cabeza: cabeza({pelo: 'corto', colorPelo: '#3a2a1e', gorra: 'fedora', colorGorra: '#5a5a62', colorBanda: '#2a2a30'}),
	casaca: '#6a6a72', casacaSombra: '#52525a', chaleco: '#e9e4d6', pantalon: '#4a4a52', zapatos: '#1a1a1e', corbata: '#8a2a2a',
};
export const MILITAR_VIEJO: Ropa = {
	cabeza: cabeza({pelo: 'raya', colorPelo: '#e9e9e9', lentes: true, bigote: 'manubrio', colorBigote: '#e9e9e9'}),
	casaca: '#6b6648', casacaSombra: '#55513a', botones: '#e0b23a', pantalon: '#55513a', zapatos: '#2a2a2a', corbata: '#3a3628',
};
export const SOLDADO_47: Ropa = {
	cabeza: cabeza({gorra: 'casco', colorGorra: '#5a6040'}),
	casaca: '#6b6648', casacaSombra: '#55513a', botones: '#4a4630', pantalon: '#6b6648', botas: '#3a2a1e', cinturon: '#4a4630',
};

/* ---------------- desierto de noche con la base militar ---------------- */

export const Estrellas: React.FC<{n?: number; alto?: number}> = ({n = 90, alto = 1100}) => {
	const f = useCurrentFrame();
	return (
		<>
			{Array.from({length: n}, (_, i) => {
				const x = (i * 197) % 1080;
				const y = (i * 131) % alto;
				const r = 1.5 + (i % 4) * 0.9;
				const o = 0.45 + 0.55 * Math.abs(Math.sin(f / (14 + (i % 7)) + i));
				return <div key={i} style={{position: 'absolute', left: x, top: y, width: r * 2, height: r * 2, borderRadius: '50%', background: '#fff8e0', opacity: o}} />;
			})}
		</>
	);
};

export const EscDesiertoNoche: React.FC<{base?: boolean}> = ({base = true}) => {
	const f = useCurrentFrame();
	return (
		<div style={{...lleno, background: 'linear-gradient(180deg, #070a1e 0%, #141a44 45%, #3a2a5a 70%, #5a3a4a 80%)'}}>
			<Estrellas />
			<div style={{position: 'absolute', left: 760, top: 210, width: 150, height: 150, borderRadius: '50%', background: '#f6f0d6', boxShadow: '0 0 90px 30px rgba(246,240,214,0.35)'}} />
			{/* mesetas lejanas */}
			<div style={{position: 'absolute', left: -40, right: -40, top: 1180, height: 260, background: '#2a1e3a', clipPath: 'polygon(0 60%, 12% 20%, 26% 22%, 30% 55%, 48% 55%, 56% 10%, 70% 12%, 76% 50%, 100% 48%, 100% 100%, 0 100%)'}} />
			{base && (
				<>
					{/* reflectores que barren el cielo */}
					{[0, 1].map((i) => {
						const a = Math.sin(f / 30 + i * 2) * 22 + (i ? 14 : -14);
						return <div key={i} style={{position: 'absolute', left: 380 + i * 320, top: 380, width: 140, height: 1000, transformOrigin: '50% 100%', transform: `rotate(${a}deg)`, background: 'linear-gradient(0deg, rgba(255,250,200,0.32), rgba(255,250,200,0))', clipPath: 'polygon(40% 100%, 60% 100%, 100% 0, 0 0)'}} />;
					})}
					{/* hangares, torre y luces */}
					{[120, 420].map((x, i) => (
						<div key={i} style={{position: 'absolute', left: x, top: 1300, width: 280, height: 150, background: '#1a1628', borderRadius: '140px 140px 0 0', border: `5px solid #0a0812`}}>
							{[0, 1, 2].map((k) => (
								<div key={k} style={{position: 'absolute', left: 40 + k * 80, top: 90, width: 30, height: 18, background: '#ffd27a', opacity: 0.8}} />
							))}
						</div>
					))}
					<div style={{position: 'absolute', left: 780, top: 1170, width: 60, height: 280, background: '#1a1628', border: '5px solid #0a0812'}} />
					<div style={{position: 'absolute', left: 750, top: 1130, width: 120, height: 60, background: '#ffd27a', border: '6px solid #0a0812', opacity: 0.9}} />
					<div style={{position: 'absolute', left: 806, top: 1100, width: 10, height: 30, background: '#0a0812'}} />
					<div style={{position: 'absolute', left: 801, top: 1088, width: 20, height: 20, borderRadius: '50%', background: f % 30 < 15 ? '#ff3a2a' : '#5a1a1a'}} />
					<div style={{position: 'absolute', left: 0, right: 0, top: 1440, height: 14, background: 'repeating-linear-gradient(90deg, #ffe08a 0 20px, transparent 20px 70px)', opacity: 0.6}} />
				</>
			)}
			<div style={{position: 'absolute', left: 0, right: 0, top: 1440, bottom: 0, background: 'linear-gradient(180deg, #3a2a2a, #1a1214)'}} />
			{/* arbustos */}
			{[90, 300, 640, 930].map((x, i) => (
				<div key={i} style={{position: 'absolute', left: x, top: 1540 + (i % 2) * 120, width: 110, height: 70, borderRadius: '50%', background: '#1e1a14', boxShadow: '30px -10px 0 -6px #1e1a14, -30px -6px 0 -10px #1e1a14'}} />
			))}
		</div>
	);
};

/* ---------------- el rancho de día ---------------- */

export const EscRancho: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #7ab6e8 0%, #b8dcf2 45%, #f2dcb0 46%, #e2c088 100%)'}}>
		<div style={{position: 'absolute', left: 800, top: 140, width: 170, height: 170, borderRadius: '50%', background: '#fff1a8', boxShadow: '0 0 80px 30px rgba(255,240,160,0.6)'}} />
		{/* molino */}
		<div style={{position: 'absolute', left: 120, top: 440, width: 16, height: 460, background: '#5a4a3a', transform: 'skewX(-4deg)'}} />
		<div style={{position: 'absolute', left: 190, top: 440, width: 16, height: 460, background: '#5a4a3a', transform: 'skewX(4deg)'}} />
		<svg width={260} height={260} viewBox="-130 -130 260 260" style={{position: 'absolute', left: 30, top: 300}}>
			{Array.from({length: 12}, (_, i) => (
				<rect key={i} x={-8} y={-120} width={16} height={110} fill="#c9c4b8" stroke={TINTA} strokeWidth={4} transform={`rotate(${i * 30})`} />
			))}
			<circle r={16} fill="#5a4a3a" stroke={TINTA} strokeWidth={4} />
		</svg>
		{/* cerca */}
		{Array.from({length: 7}, (_, i) => (
			<div key={i} style={{position: 'absolute', left: 30 + i * 170, top: 820, width: 18, height: 150, background: '#8a6a4a', border: `4px solid ${TINTA}`}} />
		))}
		{[850, 900].map((y) => (
			<div key={y} style={{position: 'absolute', left: 0, right: 0, top: y, height: 6, background: '#5a4a3a'}} />
		))}
		{/* matorrales */}
		{[200, 520, 860].map((x, i) => (
			<div key={i} style={{position: 'absolute', left: x, top: 1060 + (i % 2) * 220, width: 140, height: 80, borderRadius: '50%', background: '#8a9a5a', border: `5px solid ${TINTA}`}} />
		))}
	</div>
);

export const Oveja: React.FC<{x: number; y: number; tam: number; voltear?: boolean; fase?: number}> = ({x, y, tam, voltear, fase = 0}) => {
	const f = useCurrentFrame();
	const giro = Math.sin(f / 10 + fase) * 8;
	return (
		<svg width={tam} height={tam * 0.8} viewBox="0 0 200 160" style={{position: 'absolute', left: x - tam / 2, top: y - tam * 0.8, transform: voltear ? 'scaleX(-1)' : undefined, overflow: 'visible'}}>
			{[50, 150].map((lx) => (
				<line key={lx} x1={lx} y1={120} x2={lx} y2={158} stroke={TINTA} strokeWidth={12} strokeLinecap="round" />
			))}
			{[[60, 80], [100, 64], [140, 80], [80, 108], [124, 108], [100, 92]].map(([cx, cy], i) => (
				<circle key={i} cx={cx} cy={cy} r={34} fill="#f6f4ec" stroke={TINTA} strokeWidth={6} />
			))}
			<g transform={`rotate(${giro} 30 70)`}>
				<ellipse cx={22} cy={72} rx={24} ry={30} fill="#2a2a30" stroke={TINTA} strokeWidth={5} />
				<circle cx={14} cy={66} r={7} fill="#fff" />
				<circle cx={12} cy={66} r={3.5} fill={TINTA} />
				<path d="M 4 50 Q -10 44 -6 58" fill="#2a2a30" stroke={TINTA} strokeWidth={4} />
			</g>
		</svg>
	);
};

/** los restos: papel de aluminio, tiras de goma y palitos */
export const Restos: React.FC<{x: number; y: number; tam: number; brillo?: number}> = ({x, y, tam, brillo = 0}) => {
	const f = useCurrentFrame();
	return (
		<svg width={tam} height={tam * 0.6} viewBox="0 0 400 240" style={{position: 'absolute', left: x - tam / 2, top: y - tam * 0.3, overflow: 'visible'}}>
			{/* palitos */}
			<line x1={30} y1={190} x2={250} y2={140} stroke="#c9a46a" strokeWidth={12} strokeLinecap="round" />
			<line x1={60} y1={60} x2={230} y2={210} stroke="#c9a46a" strokeWidth={10} strokeLinecap="round" />
			<line x1={260} y1={40} x2={380} y2={160} stroke="#b8925a" strokeWidth={10} strokeLinecap="round" />
			{/* goma */}
			<path d="M 120 30 C 170 0 200 80 250 50 S 330 20 360 70" stroke="#5a3a2a" strokeWidth={16} fill="none" strokeLinecap="round" />
			<path d="M 40 120 C 80 90 110 170 160 140" stroke="#5a3a2a" strokeWidth={14} fill="none" strokeLinecap="round" />
			{/* papel de aluminio */}
			{[[90, 110, 0], [210, 100, 30], [300, 150, -20], [170, 180, 15]].map(([cx, cy, r], i) => (
				<g key={i} transform={`translate(${cx} ${cy}) rotate(${r})`}>
					<polygon points="-50,-30 10,-44 54,-12 40,34 -18,40 -56,10" fill="#c9ced6" stroke={TINTA} strokeWidth={5} />
					<polygon points="-30,-18 8,-28 30,-6 6,10" fill="#eef2f6" opacity={0.85} />
					{brillo > 0 && <circle cx={10} cy={-10} r={8 + 4 * Math.sin(f / 3 + i)} fill="#fff" opacity={brillo} />}
				</g>
			))}
		</svg>
	);
};

/* ---------------- imprenta ---------------- */

export const Imprenta: React.FC<{x: number; y: number; ancho: number; sale: number; titular: string}> = ({x, y, ancho, sale, titular}) => {
	const f = useCurrentFrame();
	const k = ancho / 800;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: 1100 * k}}>
			{/* la hoja que sale */}
			<div style={{position: 'absolute', left: 140 * k, top: (330 + 520 * sale) * k, width: 520 * k, height: 640 * k, background: '#ece6d6', border: `${6 * k}px solid ${TINTA}`, padding: 22 * k, boxSizing: 'border-box', transform: `rotate(${(1 - sale) * 0 + sale * -3}deg)`}}>
				<div style={{fontFamily: SERIF, fontWeight: 900, fontSize: 40 * k, textAlign: 'center', borderBottom: `${4 * k}px double ${TINTA}`}}>Roswell Daily Record</div>
				<div style={{fontFamily: CONDENSADA, fontSize: 70 * k, lineHeight: 1, textAlign: 'center', marginTop: 16 * k, color: '#1a1a1a'}}>{titular}</div>
			</div>
			{/* rodillos */}
			<div style={{position: 'absolute', left: 40 * k, top: 120 * k, width: 720 * k, height: 260 * k, background: '#3a3a44', border: `${9 * k}px solid ${TINTA}`, borderRadius: 30 * k}}>
				{[0, 1].map((i) => (
					<div key={i} style={{position: 'absolute', left: 40 * k, right: 40 * k, top: (40 + i * 110) * k, height: 80 * k, borderRadius: 40 * k, background: 'repeating-linear-gradient(90deg, #6a6a74 0 30px, #4a4a54 30px 60px)', backgroundPositionX: `${(f * 18) % 60}px`, border: `${5 * k}px solid ${TINTA}`}} />
				))}
			</div>
			<div style={{position: 'absolute', left: 0, top: 0, width: 800 * k, height: 130 * k, background: '#5a5a64', border: `${9 * k}px solid ${TINTA}`, borderRadius: `${20 * k}px ${20 * k}px 0 0`}}>
				<div style={{position: 'absolute', left: 40 * k, top: 30 * k, fontFamily: CONDENSADA, fontSize: 56 * k, color: '#e9e4d6', letterSpacing: 4 * k}}>IMPRENTA</div>
			</div>
		</div>
	);
};

/* ---------------- el globo terráqueo que se ríe y el letrero que se sonroja ---------------- */

export const GloboRisa: React.FC<{x: number; y: number; tam: number}> = ({x, y, tam}) => {
	const f = useCurrentFrame();
	const salto = Math.abs(Math.sin(f / 3)) * 18;
	const giro = Math.sin(f / 4) * 6;
	return (
		<svg width={tam} height={tam} viewBox="-120 -120 240 240" style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2 - salto, transform: `rotate(${giro}deg)`, overflow: 'visible'}}>
			<circle r={110} fill="#2f7ad1" stroke={TINTA} strokeWidth={7} />
			<path d="M -80 -50 Q -50 -90 -10 -70 Q 10 -40 -30 -20 Q -70 -10 -80 -50 Z M 20 -90 Q 70 -80 80 -40 Q 60 -20 30 -40 Z M 40 30 Q 90 20 90 60 Q 60 90 30 70 Z M -90 30 Q -60 20 -50 50 Q -70 80 -95 60 Z" fill="#4aa84a" stroke={TINTA} strokeWidth={5} />
			{/* ojos cerrados de risa */}
			<path d="M -56 -14 Q -40 -30 -24 -14" stroke={TINTA} strokeWidth={9} fill="none" strokeLinecap="round" />
			<path d="M 24 -14 Q 40 -30 56 -14" stroke={TINTA} strokeWidth={9} fill="none" strokeLinecap="round" />
			{/* lágrimas */}
			<path d="M -64 -6 q -6 14 0 20 q 8 -6 0 -20 Z" fill="#bfe6ff" stroke={TINTA} strokeWidth={3} />
			<path d="M 64 -6 q 6 14 0 20 q -8 -6 0 -20 Z" fill="#bfe6ff" stroke={TINTA} strokeWidth={3} />
			{/* boca abierta */}
			<path d="M -50 14 Q 0 20 50 14 Q 44 76 0 80 Q -44 76 -50 14 Z" fill="#5a1a1a" stroke={TINTA} strokeWidth={6} />
			<path d="M -30 58 Q 0 44 30 58 Q 20 74 0 76 Q -20 74 -30 58 Z" fill="#e86a8a" />
			{/* ¡JA! */}
			{[0, 1, 2].map((i) => {
				const t = (f + i * 8) % 24;
				return (
					<text key={i} x={[-150, 130, 150][i]} y={[-80, -110, 40][i] - t * 2} fontFamily={CONDENSADA} fontSize={44} fill="#ffd84a" stroke={TINTA} strokeWidth={5} paintOrder="stroke" opacity={1 - t / 24}>
						¡JA!
					</text>
				);
			})}
		</svg>
	);
};

export const LetreroRoswell: React.FC<{x: number; y: number; ancho: number; rubor: number}> = ({x, y, ancho, rubor}) => {
	const k = ancho / 600;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: 640 * k}}>
			{[100, 460].map((px) => (
				<div key={px} style={{position: 'absolute', left: px * k, top: 260 * k, width: 40 * k, height: 380 * k, background: '#6a4a2a', border: `${6 * k}px solid ${TINTA}`}} />
			))}
			<div style={{position: 'absolute', left: 0, top: 0, width: 600 * k, height: 300 * k, background: '#2f6a3a', border: `${10 * k}px solid ${TINTA}`, borderRadius: 16 * k, textAlign: 'center', color: '#f6efdc'}}>
				<div style={{fontFamily: TITULAR, fontWeight: 700, fontSize: 36 * k, marginTop: 20 * k}}>BIENVENIDOS A</div>
				<div style={{fontFamily: CONDENSADA, fontSize: 120 * k, lineHeight: 1}}>ROSWELL</div>
				{/* cara avergonzada */}
				<div style={{position: 'absolute', left: 70 * k, top: 200 * k, width: 90 * k, height: 50 * k, borderRadius: '50%', background: '#ff6a8a', opacity: rubor * 0.9}} />
				<div style={{position: 'absolute', right: 70 * k, top: 200 * k, width: 90 * k, height: 50 * k, borderRadius: '50%', background: '#ff6a8a', opacity: rubor * 0.9}} />
				<svg viewBox="0 0 600 300" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: rubor}}>
					<path d="M 250 236 Q 300 220 350 236" stroke="#f6efdc" strokeWidth={8} fill="none" strokeLinecap="round" />
					<path d="M 540 40 q 14 24 0 34 q -14 -10 0 -34 Z" fill="#bfe6ff" stroke={TINTA} strokeWidth={4} />
				</svg>
			</div>
		</div>
	);
};

/* ---------------- polvo y telarañas ---------------- */

export const PolvoTelarana: React.FC<{t: number}> = ({t}) => (
	<>
		<div style={{...lleno, background: `rgba(160,140,110,${0.45 * t})`, mixBlendMode: 'multiply'}} />
		{Array.from({length: 80}, (_, i) => (
			<div key={i} style={{position: 'absolute', left: (i * 137) % 1080, top: 300 + ((i * 251) % 1300), width: 6, height: 6, borderRadius: 3, background: '#d8ccb4', opacity: Math.max(0, t * 1.4 - (i % 10) / 10)}} />
		))}
		{[
			[0, 0, 1],
			[1080, 0, -1],
		].map(([x, y, lado], i) => (
			<svg key={i} width={460} height={460} viewBox="0 0 200 200" style={{position: 'absolute', left: lado > 0 ? x : x - 460, top: y + 250, transform: lado > 0 ? undefined : 'scaleX(-1)', opacity: Math.min(1, t * 1.6)}}>
				{[0, 20, 40, 60, 80].map((a) => (
					<line key={a} x1={0} y1={0} x2={200 * Math.cos((a * Math.PI) / 180)} y2={200 * Math.sin((a * Math.PI) / 180)} stroke="#f2eee4" strokeWidth={2} />
				))}
				{[40, 80, 120, 160].map((r) => (
					<path key={r} d={`M ${r} 0 Q ${r * 0.8} ${r * 0.35} ${r * 0.94} ${r * 0.34} Q ${r * 0.62} ${r * 0.62} ${r * 0.77} ${r * 0.64} Q ${r * 0.35} ${r * 0.8} ${r * 0.5} ${r * 0.87} Q ${r * 0.1} ${r * 0.95} 0 ${r}`} stroke="#f2eee4" strokeWidth={2} fill="none" />
				))}
			</svg>
		))}
	</>
);

/* ---------------- tele de época (1978 / años 90) ---------------- */

export const TeleRetro: React.FC<{x: number; y: number; ancho: number; children?: React.ReactNode; borrosa?: number; madera?: string}> = ({x, y, ancho, children, borrosa = 0, madera = '#7a4a26'}) => {
	const f = useCurrentFrame();
	const k = ancho / 600;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: 520 * k}}>
			{[0, 1].map((i) => (
				<div key={i} style={{position: 'absolute', left: (250 + i * 60) * k, top: -120 * k, width: 8 * k, height: 150 * k, background: '#9a9aa4', transformOrigin: '50% 100%', transform: `rotate(${i ? 28 : -28}deg)`}} />
			))}
			<div style={{position: 'absolute', inset: 0, background: madera, border: `${10 * k}px solid ${TINTA}`, borderRadius: 30 * k}}>
				<div style={{position: 'absolute', left: 30 * k, top: 30 * k, width: 420 * k, height: 440 * k, background: '#0a0a0c', border: `${8 * k}px solid ${TINTA}`, borderRadius: `${60 * k}px / ${50 * k}px`, overflow: 'hidden'}}>
					<div style={{position: 'absolute', inset: 0, filter: borrosa > 0 ? `blur(${borrosa}px) contrast(0.9) saturate(0.6)` : undefined}}>{children}</div>
					{/* líneas de barrido y estática */}
					<div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.25) 0 3px, transparent 3px 7px)', backgroundPositionY: `${(f * 3) % 7}px`}} />
					<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 40% 35%, rgba(255,255,255,0.18), rgba(255,255,255,0) 60%)'}} />
				</div>
				{[0, 1, 2].map((i) => (
					<div key={i} style={{position: 'absolute', left: 485 * k, top: (60 + i * 110) * k, width: 70 * k, height: 70 * k, borderRadius: '50%', background: '#c9c4b8', border: `${6 * k}px solid ${TINTA}`}} />
				))}
				<div style={{position: 'absolute', left: 480 * k, top: 380 * k, width: 80 * k, height: 60 * k, background: 'repeating-linear-gradient(0deg, #2a1a10 0 6px, transparent 6px 12px)'}} />
			</div>
		</div>
	);
};

/* ---------------- informe oficial de 1994 ---------------- */

export const Informe1994: React.FC<{x: number; y: number; ancho: number; tacha: number}> = ({x, y, ancho, tacha}) => {
	const k = ancho / 800;
	const lineas = ['Asunto: los restos recuperados', 'cerca de Roswell, Nuevo México,', 'en julio de 1947.', '', 'Conclusión: los restos NO', 'corresponden a un'];
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, background: '#f4f1e6', border: `${8 * k}px solid ${TINTA}`, padding: `${40 * k}px ${50 * k}px ${60 * k}px`, boxSizing: 'border-box', boxShadow: `${16 * k}px ${20 * k}px 0 rgba(0,0,0,0.4)`, fontFamily: MONO, color: '#1a1a1a'}}>
			<div style={{fontFamily: TITULAR, fontWeight: 800, fontSize: 34 * k, letterSpacing: 2 * k, textAlign: 'center'}}>FUERZA AÉREA DE LOS EE. UU.</div>
			<div style={{fontFamily: CONDENSADA, fontSize: 80 * k, textAlign: 'center', margin: `${10 * k}px 0 ${20 * k}px`}}>INFORME · 1994</div>
			<div style={{height: 4 * k, background: '#1a1a1a', marginBottom: 26 * k}} />
			{lineas.map((l, i) => (
				<div key={i} style={{fontSize: 34 * k, lineHeight: 1.5, minHeight: 34 * k}}>{l}</div>
			))}
			<div style={{position: 'relative', display: 'inline-block', fontFamily: CONDENSADA, fontSize: 130 * k, lineHeight: 1.05, marginTop: 6 * k}}>
				OVNI
				<svg viewBox="0 0 100 40" preserveAspectRatio="none" style={{position: 'absolute', left: -10 * k, top: 0, width: `calc(100% + ${20 * k}px)`, height: '100%', overflow: 'visible'}}>
					<line x1={0} y1={22} x2={100 * tacha} y2={18} stroke="#e3262e" strokeWidth={6} strokeLinecap="round" />
					<line x1={0} y1={10} x2={100 * Math.max(0, tacha * 1.4 - 0.4)} y2={30} stroke="#e3262e" strokeWidth={6} strokeLinecap="round" />
				</svg>
			</div>
		</div>
	);
};

/* ---------------- el cielo en corte: la cadena de globos espía ---------------- */

export const Microfono: React.FC<{x: number; y: number; tam: number}> = ({x, y, tam}) => (
	<svg width={tam} height={tam * 1.6} viewBox="0 0 100 160" style={{position: 'absolute', left: x - tam / 2, top: y, overflow: 'visible'}}>
		<line x1={50} y1={0} x2={50} y2={40} stroke={TINTA} strokeWidth={5} />
		<rect x={26} y={40} width={48} height={74} rx={24} fill="#9aa3ad" stroke={TINTA} strokeWidth={6} />
		{[56, 70, 84, 98].map((yy) => (
			<line key={yy} x1={32} y1={yy} x2={68} y2={yy} stroke={TINTA} strokeWidth={3} />
		))}
		<rect x={40} y={112} width={20} height={30} fill="#5a5a64" stroke={TINTA} strokeWidth={5} />
	</svg>
);

/** cadena de globos con reflectores; `sube` desplaza la cadena (la cámara va subiendo) */
export const CadenaGlobos: React.FC<{x: number; abajo: number; arriba: number}> = ({x, abajo, arriba}) => {
	const f = useCurrentFrame();
	const n = 9;
	const paso = (abajo - arriba) / n;
	return (
		<>
			<div style={{position: 'absolute', left: x - 2, top: arriba, width: 4, height: abajo - arriba, background: '#1a1a20'}} />
			{Array.from({length: n}, (_, i) => {
				const y = arriba + i * paso + Math.sin(f / 20 + i) * 6;
				const dx = Math.sin(f / 26 + i * 0.7) * 14;
				return (
					<React.Fragment key={i}>
						<div style={{position: 'absolute', left: x - 70 + dx, top: y - 80, width: 140, height: 160, borderRadius: '50%', background: 'radial-gradient(circle at 35% 30%, #ffffff, #d8dce4 60%, #aab0bc)', border: `6px solid ${TINTA}`}} />
						{i % 3 === 1 && (
							<svg width={120} height={120} viewBox="-60 -60 120 120" style={{position: 'absolute', left: x + 70 + dx, top: y + 10, overflow: 'visible'}}>
								<polygon points="0,-50 46,0 0,50 -46,0" fill="#dfe6ee" stroke={TINTA} strokeWidth={5} />
								<line x1={0} y1={-50} x2={0} y2={50} stroke={TINTA} strokeWidth={3} />
								<line x1={-46} y1={0} x2={46} y2={0} stroke={TINTA} strokeWidth={3} />
								<line x1={-60} y1={-10} x2={-20} y2={0} stroke={TINTA} strokeWidth={3} />
							</svg>
						)}
					</React.Fragment>
				);
			})}
		</>
	);
};

export const Nube: React.FC<{x: number; y: number; ancho: number; opacidad?: number}> = ({x, y, ancho, opacidad = 0.9}) => (
	<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: ancho * 0.36, opacity: opacidad}}>
		{[[0.1, 0.4, 0.35], [0.3, 0.1, 0.45], [0.55, 0.2, 0.4], [0.75, 0.42, 0.3]].map(([l, t, w], i) => (
			<div key={i} style={{position: 'absolute', left: `${l * 100}%`, top: `${t * 100}%`, width: `${w * 100}%`, paddingBottom: `${w * 100}%`, borderRadius: '50%', background: '#f4f6fa'}} />
		))}
	</div>
);

/* ---------------- muñeco de prueba con paracaídas ---------------- */

export const MunecoPrueba: React.FC<{x: number; y: number; tam: number}> = ({x, y, tam}) => {
	const f = useCurrentFrame();
	const vaiven = Math.sin(f / 8) * 8;
	return (
		<div style={{position: 'absolute', left: x - tam / 2, top: y, width: tam, height: tam * 2, transform: `rotate(${vaiven}deg)`, transformOrigin: '50% 0'}}>
			<svg width={tam} height={tam * 2} viewBox="0 0 300 600" style={{overflow: 'visible'}}>
				{/* paracaídas */}
				<path d="M 10 120 Q 150 -60 290 120 Q 255 100 220 120 Q 185 100 150 120 Q 115 100 80 120 Q 45 100 10 120 Z" fill="#f4f1e8" stroke={TINTA} strokeWidth={8} />
				<path d="M 80 120 Q 150 -20 220 120" stroke="#e86a2a" strokeWidth={14} fill="none" />
				{[10, 80, 150, 220, 290].map((cx) => (
					<line key={cx} x1={cx} y1={120} x2={150} y2={300} stroke={TINTA} strokeWidth={3} />
				))}
				{/* muñeco: cabeza con marcas de prueba y cara de susto pintada */}
				<circle cx={150} cy={340} r={52} fill="#f2d24a" stroke={TINTA} strokeWidth={7} />
				<path d="M 150 288 A 52 52 0 0 1 202 340 L 150 340 Z" fill={TINTA} />
				<path d="M 150 392 A 52 52 0 0 1 98 340 L 150 340 Z" fill={TINTA} />
				<circle cx={130} cy={330} r={12} fill="#fff" stroke={TINTA} strokeWidth={4} />
				<circle cx={170} cy={330} r={12} fill="#fff" stroke={TINTA} strokeWidth={4} />
				<ellipse cx={150} cy={364} rx={12} ry={14} fill={TINTA} />
				<rect x={110} y={392} width={80} height={120} rx={20} fill="#f2d24a" stroke={TINTA} strokeWidth={7} />
				<line x1={110} y1={410} x2={60} y2={360} stroke={TINTA} strokeWidth={18} strokeLinecap="round" />
				<line x1={190} y1={410} x2={240} y2={360} stroke={TINTA} strokeWidth={18} strokeLinecap="round" />
				<line x1={130} y1={510} x2={110} y2={590} stroke={TINTA} strokeWidth={20} strokeLinecap="round" />
				<line x1={170} y1={510} x2={190} y2={590} stroke={TINTA} strokeWidth={20} strokeLinecap="round" />
			</svg>
			<div style={{position: 'absolute', left: tam * 0.3, top: tam * 1.52, width: tam * 0.4, padding: `${tam * 0.01}px 0`, background: '#f6efdc', border: `${tam * 0.012}px solid ${TINTA}`, textAlign: 'center', fontFamily: CONDENSADA, fontSize: tam * 0.07, color: TINTA}}>AÑOS 50</div>
		</div>
	);
};

/* ---------------- el «ovni» brillante y el globo dentro ---------------- */

export const OvniBrillante: React.FC<{x: number; y: number; tam: number; revela: number}> = ({x, y, tam, revela}) => {
	const f = useCurrentFrame();
	return (
		<div style={{position: 'absolute', left: x - tam / 2, top: y - tam * 0.35, width: tam, height: tam * 0.7}}>
			<div style={{position: 'absolute', left: -tam * 0.3, top: -tam * 0.4, width: tam * 1.6, height: tam * 1.5, borderRadius: '50%', background: `radial-gradient(circle, rgba(140,255,200,${0.45 * (1 - revela)}) 0%, rgba(140,255,200,0) 60%)`}} />
			<svg width={tam} height={tam * 0.7} viewBox="0 0 300 210" style={{position: 'absolute', inset: 0, overflow: 'visible', opacity: 1 - revela}}>
				<ellipse cx={150} cy={130} rx={150} ry={46} fill="#9aa8b4" stroke={TINTA} strokeWidth={8} />
				<path d="M 80 112 Q 90 40 150 36 Q 210 40 220 112 Z" fill="#aaf2d8" stroke={TINTA} strokeWidth={8} opacity={0.9} />
				{[40, 100, 150, 200, 260].map((cx, i) => (
					<circle key={cx} cx={cx} cy={140} r={10} fill={(f + i * 4) % 16 < 8 ? '#ffe27a' : '#ff7a5a'} stroke={TINTA} strokeWidth={3} />
				))}
			</svg>
			{revela > 0 && (
				<div style={{position: 'absolute', inset: 0, transform: `scale(${0.6 + 0.4 * revela})`, opacity: revela}}>
					<div style={{position: 'absolute', left: tam * 0.28, top: -tam * 0.1, width: tam * 0.44, height: tam * 0.55, borderRadius: '50%', background: 'radial-gradient(circle at 35% 30%, #ffffff, #d8dce4 60%, #aab0bc)', border: `${tam * 0.02}px solid ${TINTA}`}} />
					<div style={{position: 'absolute', left: tam * 0.08, top: tam * 0.48, width: tam * 0.84, padding: `${tam * 0.012}px 0`, background: '#f6efdc', border: `${tam * 0.012}px solid ${TINTA}`, textAlign: 'center', fontFamily: CONDENSADA, fontSize: tam * 0.065, lineHeight: 1.1, color: TINTA}}>
						PROPIEDAD DEL
						<br />
						EJÉRCITO
					</div>
				</div>
			)}
		</div>
	);
};

/** la red del soldado (palo + bolsa), en coordenadas del cuadro */
export const Red: React.FC<{x1: number; y1: number; x2: number; y2: number; radio: number}> = ({x1, y1, x2, y2, radio}) => (
	<svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
		<line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#8a6a4a" strokeWidth={16} strokeLinecap="round" />
		<line x1={x1} y1={y1} x2={x2} y2={y2} stroke={TINTA} strokeWidth={4} strokeLinecap="round" opacity={0.4} />
		<circle cx={x2} cy={y2 - radio} r={radio} fill="none" stroke="#5a5a64" strokeWidth={10} />
		{Array.from({length: 8}, (_, i) => (
			<line key={i} x1={x2 - radio + (i * radio * 2) / 7} y1={y2 - radio * 2} x2={x2 - radio + (i * radio * 2) / 7} y2={y2} stroke="rgba(240,240,240,0.55)" strokeWidth={3} />
		))}
		{Array.from({length: 6}, (_, i) => (
			<line key={`h${i}`} x1={x2 - radio} y1={y2 - radio * 2 + (i * radio * 2) / 5} x2={x2 + radio} y2={y2 - radio * 2 + (i * radio * 2) / 5} stroke="rgba(240,240,240,0.55)" strokeWidth={3} />
		))}
	</svg>
);

export const clampR = clamp;
export const interpolarR = interpolate;

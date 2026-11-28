import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Ropa} from '../componentes/Muneco';
import {Diseno} from '../componentes/Personaje';
import {CONDENSADA, MONO, SERIF, TITULAR} from '../fuentes';
import {TINTA, clamp} from './base';

/* Escenarios, utilería y vestuario del short «La llave del Titanic» (1912; todo en vertical 1080x1920). */

const lleno: React.CSSProperties = {position: 'absolute', inset: 0};
const cabeza = (extra: Partial<Diseno>): Diseno => ({piel: '#ffffff', chaqueta: '', chaquetaSombra: '', botones: '', ...extra});
const ORO = '#e0b23a';
const MARINO = '#1c2340';

/* ---------------- vestuario ---------------- */

/** el oficial de la llave (al que dejan en tierra): uniforme azul marino con botones y puños dorados */
export const BLAIR: Ropa = {
	cabeza: cabeza({pelo: 'raya', colorPelo: '#3a2a1e', gorra: 'naval'}),
	casaca: MARINO, casacaSombra: '#121830', chaleco: '#ffffff', botones: ORO, pantalon: MARINO, zapatos: '#111114', corbata: '#111114', punos: ORO,
};
export const BLAIR_CIVIL: Ropa = {...BLAIR, cabeza: {...BLAIR.cabeza, gorra: 'fedora', colorGorra: '#3a3a44', colorBanda: '#1c1c22'}, casaca: '#4a4a56', casacaSombra: '#34343e', botones: '#2a2a2a', pantalon: '#3a3a44', punos: '#ffffff'};
/** el oficial del puente (con bigote, para distinguirlo) */
export const OFICIAL: Ropa = {...BLAIR, cabeza: {...BLAIR.cabeza, pelo: 'corto', colorPelo: '#6b4a2b', bigote: 'manubrio', colorBigote: '#6b4a2b'}};
/** los vigías: jersey de lana y gorra */
export const VIGIA: Ropa = {
	cabeza: cabeza({pelo: 'corto', colorPelo: '#2a1c12', gorra: 'boina', colorGorra: '#1c1c22'}),
	casaca: '#2a3a5a', casacaSombra: '#1c2a44', botones: '#2a3a5a', pantalon: '#1c1c22', zapatos: '#111114',
};
export const VIGIA2: Ropa = {...VIGIA, cabeza: {...VIGIA.cabeza, bigote: 'morsa', colorBigote: '#4a3a2a'}, casaca: '#3a3a4a', casacaSombra: '#2a2a36'};
/** el senador de la audiencia de 1912 */
export const SENADOR: Ropa = {
	cabeza: cabeza({pelo: 'raya', colorPelo: '#9a9a9a', bigote: 'mostacho', colorBigote: '#9a9a9a'}),
	casaca: '#3a3a44', casacaSombra: '#26262e', chaleco: '#d8d2c2', botones: '#2a2a2a', pantalon: '#3a3a44', zapatos: '#111114', corbata: '#6a1e2a', punos: '#ffffff',
};
export const MARINERO: Ropa = {...VIGIA, cabeza: {...VIGIA.cabeza, gorra: 'naval'}, casaca: '#ffffff', casacaSombra: '#d8d8e0', botones: MARINO, pantalon: MARINO};

/* ---------------- el mar de noche ---------------- */

const ESTRELLAS = Array.from({length: 90}, (_, i) => ({x: (i * 397) % 1080, y: (i * 233) % 1060, r: 1.5 + ((i * 7) % 5) * 0.7, t: i * 1.7}));

/** cielo sin luna (o con luna, `luna` 0..1) y mar oscuro; `espejo` = mar en calma total que refleja las estrellas */
export const EscNocheMar: React.FC<{luna?: number; espejo?: number; horizonte?: number}> = ({luna = 0, espejo = 1, horizonte = 1150}) => {
	const f = useCurrentFrame();
	return (
		<div style={{...lleno, background: `linear-gradient(180deg, #03060f 0%, #0a1326 ${(horizonte / 1920) * 100}%, #050a16 ${(horizonte / 1920) * 100}%, #02050c 100%)`}}>
			<svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
				{ESTRELLAS.filter((e) => e.y < horizonte - 20).map((e, i) => (
					<circle key={i} cx={e.x} cy={e.y} r={e.r} fill="#e8f0ff" opacity={0.55 + 0.45 * Math.sin(f / 9 + e.t)} />
				))}
				{/* reflejo de las estrellas en el mar quieto */}
				{espejo > 0 &&
					ESTRELLAS.filter((e) => e.y < horizonte - 20).map((e, i) => (
						<ellipse key={`r${i}`} cx={e.x + Math.sin(f / 14 + e.t) * 2} cy={2 * horizonte - e.y} rx={e.r * 1.5} ry={e.r * 0.8} fill="#c8d8ff" opacity={espejo * 0.75 * (0.6 + 0.4 * Math.sin(f / 9 + e.t))} />
					))}
				{/* oleaje suave cuando NO es espejo */}
				{espejo < 1 &&
					Array.from({length: 14}, (_, i) => {
						const y = horizonte + 30 + i * i * 4.5;
						const x0 = ((i * 211 + f * (1 + i * 0.2)) % 1300) - 200;
						return <path key={`o${i}`} d={`M ${x0} ${y} q 40 -12 80 0 q 40 12 80 0`} stroke="#3a5a8a" strokeWidth={3 + i * 0.4} fill="none" opacity={(1 - espejo) * 0.8} />;
					})}
				<line x1={0} y1={horizonte} x2={1080} y2={horizonte} stroke="#24365a" strokeWidth={3} />
			</svg>
			{luna > 0 && (
				<div style={{position: 'absolute', left: 700, top: 260, width: 190, height: 190, borderRadius: '50%', background: '#f4f0d8', boxShadow: '0 0 90px 30px rgba(244,240,216,0.35)', opacity: luna}} />
			)}
		</div>
	);
};

/* ---------------- el Titanic de perfil ---------------- */

/** el barco de perfil mirando a la derecha; `y` es la línea de flotación; `luces` enciende ojos de buey y ventanas */
export const Titanic: React.FC<{x: number; y: number; ancho: number; luces?: number; humo?: boolean; voltear?: boolean; noche?: boolean}> = ({x, y, ancho, luces = 0, humo = true, voltear, noche}) => {
	const f = useCurrentFrame();
	const k = ancho / 1000;
	const casco = noche ? '#0c0c10' : '#1a1a1e';
	const blanco = noche ? '#9aa2b4' : '#f2efe6';
	const chimenea = noche ? '#8a6a3a' : '#d9a04a';
	const CH = [300, 430, 560, 690];
	return (
		<svg width={ancho} height={420 * k} viewBox="0 -170 1000 420" style={{position: 'absolute', left: x - ancho / 2, top: y - 400 * k, overflow: 'visible', transform: voltear ? 'scaleX(-1)' : undefined}}>
			{/* humo */}
			{humo &&
				CH.slice(0, 3).map((c, i) =>
					[0, 1, 2].map((j) => {
						const t = ((f * 0.8 + j * 30 + i * 13) % 90) / 90;
						return <circle key={`${i}-${j}`} cx={c - 20 - t * 160} cy={-70 - t * 90} r={18 + t * 40} fill={noche ? '#2a2e3a' : '#cfcac0'} opacity={0.55 * (1 - t)} />;
					}),
				)}
			{/* palos y cables */}
			<line x1={880} y1={105} x2={872} y2={-150} stroke={TINTA} strokeWidth={7} />
			<line x1={110} y1={115} x2={118} y2={-130} stroke={TINTA} strokeWidth={7} />
			<line x1={118} y1={-128} x2={872} y2={-148} stroke={TINTA} strokeWidth={2.5} />
			{/* cofa */}
			<rect x={862} y={-40} width={24} height={22} rx={3} fill={blanco} stroke={TINTA} strokeWidth={4} />
			{/* chimeneas, inclinadas hacia atrás */}
			{CH.map((c, i) => (
				<g key={i} transform={`skewX(-8) translate(${-5} 0)`}>
					<path d={`M ${c - 24} 60 L ${c - 24} -60 L ${c + 24} -60 L ${c + 24} 60 Z`} fill={chimenea} stroke={TINTA} strokeWidth={6} />
					<rect x={c - 24} y={-60} width={48} height={22} fill={TINTA} />
				</g>
			))}
			{/* superestructura */}
			<rect x={220} y={58} width={560} height={30} fill={blanco} stroke={TINTA} strokeWidth={6} />
			<rect x={180} y={84} width={660} height={36} fill={blanco} stroke={TINTA} strokeWidth={6} />
			{Array.from({length: 26}, (_, i) => (
				<rect key={i} x={196 + i * 24.5} y={94} width={12} height={12} fill={luces ? `rgba(255,214,120,${0.4 + 0.6 * luces})` : '#7a8494'} />
			))}
			{/* casco */}
			<path d="M 40 118 L 958 104 L 992 110 L 966 232 L 64 232 Q 22 196 40 118 Z" fill={casco} stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
			<line x1={44} y1={128} x2={986} y2={114} stroke={noche ? '#5a4a2a' : '#d9a04a'} strokeWidth={4} />
			{Array.from({length: 38}, (_, i) => (
				<circle key={i} cx={90 + i * 23} cy={160 - i * 0.3} r={4.5} fill={luces ? `rgba(255,214,120,${0.3 + 0.7 * luces})` : '#3a3a44'} />
			))}
			{Array.from({length: 34}, (_, i) => (
				<circle key={`b${i}`} cx={120 + i * 23} cy={188 - i * 0.2} r={4} fill={luces ? `rgba(255,214,120,${0.25 + 0.6 * luces})` : '#3a3a44'} />
			))}
			{!noche && <text x={900} y={150} fontFamily={SERIF} fontSize={16} fontWeight={900} fill="#d9a04a" textAnchor="middle">TITANIC</text>}
			{/* línea de flotación */}
			<path d="M 0 236 Q 250 226 500 236 Q 750 246 1000 236" stroke={noche ? '#3a5a8a' : '#e8f4ff'} strokeWidth={6} fill="none" opacity={0.8} />
		</svg>
	);
};

/* ---------------- el iceberg ---------------- */

/** iceberg (`y` = línea de flotación). `espuma` 0..1 dibuja la espuma blanca que lo delataría con oleaje */
export const Iceberg: React.FC<{x: number; y: number; ancho: number; noche?: boolean; espuma?: number; silueta?: number}> = ({x, y, ancho, noche, espuma = 0, silueta = 0}) => {
	const f = useCurrentFrame();
	const k = ancho / 400;
	const cara = noche ? '#3e4a62' : '#eef6ff';
	const sombra = noche ? '#263048' : '#b8d4ee';
	return (
		<svg width={ancho} height={520 * k} viewBox="0 -300 400 520" style={{position: 'absolute', left: x - ancho / 2, top: y - 300 * k, overflow: 'visible'}}>
			{/* la parte de abajo, bajo el agua */}
			<path d="M 20 0 L 0 90 L 70 200 L 260 210 L 390 120 L 380 0 Z" fill={noche ? '#141c2e' : '#7aa8d0'} opacity={0.55} />
			<path d="M 20 0 L 60 -140 L 110 -120 L 150 -260 L 200 -170 L 240 -230 L 300 -90 L 350 -110 L 380 0 Z" fill={cara} stroke={silueta ? '#9ab0d8' : TINTA} strokeWidth={7} strokeLinejoin="round" />
			<path d="M 150 -260 L 170 -120 L 200 -170 Z M 240 -230 L 250 -60 L 300 -90 Z M 60 -140 L 90 -30 L 110 -120 Z" fill={sombra} />
			{espuma > 0 &&
				Array.from({length: 9}, (_, i) => (
					<ellipse key={i} cx={10 + i * 46} cy={4 + Math.sin(f / 5 + i) * 3} rx={30} ry={12} fill="#ffffff" opacity={espuma * (0.7 + 0.3 * Math.sin(f / 4 + i * 2))} />
				))}
		</svg>
	);
};

/* ---------------- la cofa (nido del vigía) ---------------- */

/** el barril de la cofa visto de lado, con la campana; los vigías van ANTES (detrás) en el orden de dibujo */
export const CofaFrente: React.FC<{x: number; y: number; ancho: number; campana?: number}> = ({x, y, ancho, campana = 0}) => {
	const k = ancho / 600;
	const giro = Math.sin(campana * Math.PI * 6) * 18 * (1 - campana);
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: 1920}}>
			<svg width={ancho} height={560 * k} viewBox="0 0 600 560" style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
				<rect x={270} y={-1000} width={60} height={1600} fill="#c9b48a" stroke={TINTA} strokeWidth={8} />
				<path d="M 20 40 L 580 40 L 560 380 L 40 380 Z" fill="#f2efe6" stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
				<rect x={10} y={20} width={580} height={36} rx={10} fill="#d9d4c4" stroke={TINTA} strokeWidth={8} />
				{[110, 200, 290].map((yy) => (
					<line key={yy} x1={30} y1={yy} x2={570} y2={yy} stroke="#c9c2b0" strokeWidth={6} />
				))}
				{/* la campana en su soporte */}
				<g transform={`rotate(${giro} 520 -10)`}>
					<line x1={520} y1={-40} x2={520} y2={-10} stroke={TINTA} strokeWidth={8} />
					<path d="M 485 50 Q 488 -6 520 -10 Q 552 -6 555 50 Z" fill={ORO} stroke={TINTA} strokeWidth={7} />
					<circle cx={520} cy={58} r={9} fill={TINTA} />
				</g>
				<line x1={470} y1={-40} x2={570} y2={-40} stroke={TINTA} strokeWidth={10} />
			</svg>
		</div>
	);
};

/* ---------------- el armario de los prismáticos, la llave y los prismáticos ---------------- */

export const Prismaticos: React.FC<{x: number; y: number; tam: number; rot?: number}> = ({x, y, tam, rot = 0}) => (
	<svg width={tam} height={tam * 0.6} viewBox="0 0 200 120" style={{position: 'absolute', left: x - tam / 2, top: y - tam * 0.3, transform: `rotate(${rot}deg)`, overflow: 'visible'}}>
		<rect x={10} y={20} width={70} height={90} rx={14} fill="#1c1c22" stroke={TINTA} strokeWidth={8} />
		<rect x={120} y={20} width={70} height={90} rx={14} fill="#1c1c22" stroke={TINTA} strokeWidth={8} />
		<rect x={74} y={44} width={52} height={30} rx={8} fill="#3a3a44" stroke={TINTA} strokeWidth={6} />
		<ellipse cx={45} cy={22} rx={30} ry={10} fill="#8fb4d8" stroke={TINTA} strokeWidth={5} />
		<ellipse cx={155} cy={22} rx={30} ry={10} fill="#8fb4d8" stroke={TINTA} strokeWidth={5} />
		<rect x={18} y={60} width={54} height={10} fill={ORO} opacity={0.7} />
		<rect x={128} y={60} width={54} height={10} fill={ORO} opacity={0.7} />
	</svg>
);

/** llave de latón con etiqueta (COFA); `brillo` 0..1 */
export const Llave: React.FC<{x: number; y: number; tam: number; rot?: number; brillo?: number; etiqueta?: boolean}> = ({x, y, tam, rot = 0, brillo = 0, etiqueta = true}) => (
	<svg width={tam} height={tam * 0.5} viewBox="0 0 300 150" style={{position: 'absolute', left: x - tam / 2, top: y - tam * 0.25, transform: `rotate(${rot}deg)`, overflow: 'visible', filter: brillo ? `drop-shadow(0 0 ${30 * brillo}px rgba(255,214,120,0.95))` : undefined}}>
		{etiqueta && (
			<g transform="rotate(-18 40 75)">
				<line x1={40} y1={75} x2={-10} y2={120} stroke="#8a7a5a" strokeWidth={4} />
				<rect x={-70} y={110} width={110} height={50} rx={8} fill="#f2e6c8" stroke={TINTA} strokeWidth={5} />
				<circle cx={-56} cy={135} r={6} fill="none" stroke={TINTA} strokeWidth={3} />
				<text x={-8} y={146} textAnchor="middle" fontFamily={CONDENSADA} fontSize={34} fill={TINTA}>COFA</text>
			</g>
		)}
		<circle cx={60} cy={75} r={48} fill="#d4a93a" stroke={TINTA} strokeWidth={9} />
		<circle cx={60} cy={75} r={20} fill="none" stroke={TINTA} strokeWidth={8} />
		<rect x={104} y={64} width={170} height={24} rx={6} fill="#d4a93a" stroke={TINTA} strokeWidth={8} />
		<path d="M 224 86 L 224 120 L 244 120 L 244 104 L 258 104 L 258 120 L 274 120 L 274 86 Z" fill="#d4a93a" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
		<path d="M 40 50 Q 60 40 80 52" stroke="#fff4c0" strokeWidth={6} fill="none" opacity={0.8} />
	</svg>
);

/** armario de madera con placa «PRISMÁTICOS» y cerradura de latón; `abierto` 0..1 muestra los prismáticos dentro */
export const Armario: React.FC<{x: number; y: number; ancho: number; abierto?: number; cerradura?: number}> = ({x, y, ancho, abierto = 0, cerradura = 0}) => {
	const k = ancho / 500;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: 640 * k}}>
			<div style={{position: 'absolute', inset: 0, background: '#5a3a22', border: `${10 * k}px solid ${TINTA}`, borderRadius: 10 * k}} />
			<div style={{position: 'absolute', left: 40 * k, top: 120 * k, width: 420 * k, height: 470 * k, background: '#2a1a10', border: `${7 * k}px solid ${TINTA}`}}>
				<Prismaticos x={210 * k} y={240 * k} tam={280 * k} rot={-6} />
			</div>
			{/* puerta (se abre hacia la izquierda) */}
			<div style={{position: 'absolute', left: 40 * k, top: 120 * k, width: 420 * k, height: 470 * k, background: 'linear-gradient(90deg, #7a5232, #6a4628)', border: `${7 * k}px solid ${TINTA}`, transformOrigin: '0% 50%', transform: `perspective(${1400 * k}px) rotateY(${-100 * abierto}deg)`, boxSizing: 'border-box'}}>
				{[0, 1, 2].map((i) => (
					<div key={i} style={{position: 'absolute', left: 30 * k, right: 30 * k, top: (40 + i * 140) * k, height: 110 * k, border: `${5 * k}px solid #4a2e18`, borderRadius: 6 * k}} />
				))}
				<div style={{position: 'absolute', right: 26 * k, top: 210 * k, width: 46 * k, height: 70 * k, background: '#d4a93a', border: `${6 * k}px solid ${TINTA}`, borderRadius: 10 * k, boxShadow: cerradura ? `0 0 ${40 * cerradura * k}px ${16 * cerradura * k}px rgba(255,214,120,0.8)` : undefined}}>
					<div style={{position: 'absolute', left: '50%', top: '30%', width: 12 * k, height: 26 * k, marginLeft: -6 * k, background: TINTA, borderRadius: `${6 * k}px ${6 * k}px ${2 * k}px ${2 * k}px`}} />
				</div>
			</div>
			<div style={{position: 'absolute', left: 90 * k, top: 30 * k, width: 320 * k, height: 64 * k, background: '#d4a93a', border: `${6 * k}px solid ${TINTA}`, borderRadius: 8 * k, fontFamily: CONDENSADA, fontSize: 44 * k, color: TINTA, textAlign: 'center', lineHeight: `${54 * k}px`}}>PRISMÁTICOS</div>
		</div>
	);
};

/* ---------------- el muelle (Southampton, 1912) ---------------- */

export const EscMuelle: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #a8c8e0 0%, #d8e6ee 55%, #c8d4d8 100%)'}}>
		{/* nubes */}
		{[[160, 260, 260], [720, 180, 320], [520, 420, 200]].map(([x, y, w], i) => (
			<div key={i} style={{position: 'absolute', left: x - w / 2, top: y, width: w, height: w * 0.32, borderRadius: w, background: '#f4f8fb', opacity: 0.9}} />
		))}
		{/* grúas del puerto */}
		{[120, 940].map((x, i) => (
			<svg key={i} width={300} height={700} viewBox="0 0 300 700" style={{position: 'absolute', left: x - 150, top: 640}}>
				<path d="M 140 700 L 140 100 L 160 100 L 160 700 M 150 110 L 290 60 M 150 110 L 20 200" stroke="#5a6470" strokeWidth={14} fill="none" />
			</svg>
		))}
		{/* agua del puerto y muelle de tablones */}
		<div style={{position: 'absolute', left: 0, right: 0, top: 1320, height: 140, background: '#4a6a82'}} />
		<div style={{position: 'absolute', left: -20, right: -20, top: 1440, bottom: -20, background: 'repeating-linear-gradient(90deg, #8a6a48 0 90px, #7a5c3e 90px 96px)', borderTop: `10px solid ${TINTA}`}} />
		{[180, 900].map((x) => (
			<div key={x} style={{position: 'absolute', left: x - 34, top: 1400, width: 68, height: 70, background: '#2a2a30', border: `7px solid ${TINTA}`, borderRadius: '20px 20px 6px 6px'}} />
		))}
	</div>
);

/** pasarela entre el muelle y el barco; `retira` 0..1 la quita */
export const Pasarela: React.FC<{retira?: number}> = ({retira = 0}) => (
	<div style={{position: 'absolute', left: 560 + retira * 300, top: 1180, width: 380, height: 40, background: '#c9b48a', border: `7px solid ${TINTA}`, transform: 'rotate(-14deg)', transformOrigin: '100% 50%', opacity: 1 - retira * 0.3}} />
);

/* ---------------- el puente de mando ---------------- */

export const EscPuente: React.FC<{children?: React.ReactNode}> = ({children}) => (
	<div style={{...lleno, background: '#3a2a1e'}}>
		{/* ventanales con la noche detrás */}
		<div style={{position: 'absolute', left: 60, top: 260, width: 960, height: 640, overflow: 'hidden', border: `12px solid ${TINTA}`, background: '#050a16'}}>
			<div style={{position: 'absolute', left: -60, top: -260, width: 1080, height: 1920}}>{children}</div>
			{[1, 2, 3].map((i) => (
				<div key={i} style={{position: 'absolute', left: i * 240 - 9, top: 0, width: 18, height: 640, background: '#6a4a2e', borderLeft: `5px solid ${TINTA}`, borderRight: `5px solid ${TINTA}`}} />
			))}
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 900, bottom: 0, background: 'linear-gradient(180deg, #5a3e28, #3a2818)', borderTop: `10px solid ${TINTA}`}} />
	</div>
);

/** telégrafo de máquinas / indicador de velocidad: aguja en `nudos` (0..25) */
export const Nudos: React.FC<{x: number; y: number; tam: number; nudos: number; tacha?: number}> = ({x, y, tam, nudos, tacha = 0}) => {
	const a = interpolate(nudos, [0, 25], [-120, 120]);
	return (
		<svg width={tam} height={tam} viewBox="-120 -120 240 240" style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, overflow: 'visible'}}>
			<circle r={110} fill={ORO} stroke={TINTA} strokeWidth={8} />
			<circle r={94} fill="#f6efdc" stroke={TINTA} strokeWidth={5} />
			<path d={`M ${Math.sin((60 * Math.PI) / 180) * 80} ${-Math.cos((60 * Math.PI) / 180) * 80} A 80 80 0 0 1 ${Math.sin((120 * Math.PI) / 180) * 80} ${-Math.cos((120 * Math.PI) / 180) * 80}`} stroke="#c8202a" strokeWidth={14} fill="none" />
			{Array.from({length: 6}, (_, i) => {
				const g = -120 + i * 48;
				const r = (g * Math.PI) / 180;
				return (
					<g key={i}>
						<line x1={Math.sin(r) * 70} y1={-Math.cos(r) * 70} x2={Math.sin(r) * 88} y2={-Math.cos(r) * 88} stroke={TINTA} strokeWidth={5} />
						<text x={Math.sin(r) * 52} y={-Math.cos(r) * 52 + 8} textAnchor="middle" fontFamily={CONDENSADA} fontSize={22} fill={TINTA}>{i * 5}</text>
					</g>
				);
			})}
			<text y={52} textAnchor="middle" fontFamily={CONDENSADA} fontSize={26} fill={TINTA}>NUDOS</text>
			<line x1={0} y1={0} x2={Math.sin((a * Math.PI) / 180) * 84} y2={-Math.cos((a * Math.PI) / 180) * 84} stroke={TINTA} strokeWidth={9} strokeLinecap="round" />
			<circle r={12} fill={TINTA} />
			{tacha > 0 && <path d="M -70 -70 L 70 70 M 70 -70 L -70 70" stroke="#c8202a" strokeWidth={18} strokeLinecap="round" opacity={tacha} />}
		</svg>
	);
};

/* ---------------- la audiencia de 1912 ---------------- */

export const EscAudiencia: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #6a4a32 0%, #4a321e 100%)'}}>
		{[90, 990].map((x) => (
			<div key={x} style={{position: 'absolute', left: x - 50, top: 0, width: 100, height: 1100, background: 'linear-gradient(90deg, #d8cdb4, #f2e9d4, #c9bea4)', borderLeft: `6px solid ${TINTA}`, borderRight: `6px solid ${TINTA}`}} />
		))}
		{[300, 540, 780].map((x) => (
			<div key={x} style={{position: 'absolute', left: x - 90, top: 240, width: 180, height: 420, border: `8px solid #3a2414`, borderRadius: '90px 90px 0 0', background: '#5a3c26'}} />
		))}
		<div style={{position: 'absolute', left: 190, top: 120, width: 700, height: 80, background: '#f2e9d4', border: `6px solid ${TINTA}`, fontFamily: SERIF, fontWeight: 900, fontSize: 38, color: '#2a1c12', textAlign: 'center', lineHeight: '68px'}}>AUDIENCIA · NUEVA YORK · 1912</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 1100, bottom: 0, background: 'repeating-linear-gradient(90deg, #7a5232 0 120px, #6a4628 120px 126px)', borderTop: `10px solid ${TINTA}`}} />
	</div>
);

/** mesa de la audiencia con paño verde (se dibuja DELANTE de los personajes) */
export const MesaAudiencia: React.FC<{y?: number}> = ({y = 1300}) => (
	<>
		<div style={{position: 'absolute', left: -30, right: -30, top: y, height: 50, background: '#2f5a3a', border: `9px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: -30, right: -30, top: y + 50, height: 700, background: 'linear-gradient(180deg, #5a3a22, #3a2414)', borderTop: `6px solid ${TINTA}`}} />
	</>
);

/* ---------------- avisos de hielo, carta y titular ---------------- */

/** marconigrama: «AVISO DE HIELO» */
export const Telegrama: React.FC<{x: number; y: number; ancho: number; n: number; rot?: number}> = ({x, y, ancho, n, rot = 0}) => {
	const k = ancho / 500;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, background: '#f4ecd2', border: `${7 * k}px solid ${TINTA}`, padding: `${18 * k}px ${24 * k}px`, boxSizing: 'border-box', transform: `rotate(${rot}deg)`, boxShadow: `${10 * k}px ${12 * k}px 0 rgba(0,0,0,0.35)`}}>
			<div style={{display: 'flex', justifyContent: 'space-between', fontFamily: MONO, fontSize: 22 * k, color: '#5a4a2a'}}>
				<span>MARCONIGRAMA</span>
				<span>14·IV·1912</span>
			</div>
			<div style={{height: 3 * k, background: '#5a4a2a', margin: `${8 * k}px 0`}} />
			<div style={{fontFamily: CONDENSADA, fontSize: 64 * k, color: '#1d2a6b', lineHeight: 1.05}}>AVISO DE HIELO</div>
			<div style={{fontFamily: MONO, fontSize: 24 * k, color: '#3a3020', marginTop: 8 * k}}>ICEBERGS EN LA RUTA. STOP.</div>
			<div style={{position: 'absolute', right: 18 * k, bottom: 12 * k, width: 64 * k, height: 64 * k, borderRadius: '50%', background: '#c8202a', border: `${5 * k}px solid ${TINTA}`, color: '#fff', fontFamily: CONDENSADA, fontSize: 40 * k, textAlign: 'center', lineHeight: `${56 * k}px`}}>{n}</div>
		</div>
	);
};

/** la carta del oficial: se escribe sola (`escribe` 0..1) */
export const Carta: React.FC<{x: number; y: number; ancho: number; escribe?: number; rot?: number}> = ({x, y, ancho, escribe = 1, rot = 0}) => {
	const k = ancho / 700;
	const frase = 'Qué pena no hacer su primer viaje.';
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, background: '#fbf6e8', border: `${7 * k}px solid ${TINTA}`, padding: `${44 * k}px ${52 * k}px`, boxSizing: 'border-box', transform: `rotate(${rot}deg)`, boxShadow: `${12 * k}px ${14 * k}px 0 rgba(0,0,0,0.3)`, fontFamily: "'Comic Sans MS', cursive", fontStyle: 'italic', color: '#1d2a6b'}}>
			<div style={{fontSize: 40 * k, marginBottom: 26 * k}}>Querida hermana:</div>
			{[0, 1].map((i) => (
				<div key={i} style={{height: 6 * k, background: '#c9c0a8', margin: `${22 * k}px 0`, width: `${88 - i * 14}%`}} />
			))}
			<div style={{fontSize: 52 * k, lineHeight: 1.25, minHeight: 140 * k, marginTop: 18 * k}}>{frase.slice(0, Math.round(frase.length * escribe))}</div>
			<div style={{fontSize: 36 * k, textAlign: 'right', marginTop: 20 * k}}>— D.</div>
		</div>
	);
};

/** cuenta atrás tipo marcador: segundos que quedan */
export const CuentaAtras: React.FC<{x: number; y: number; ancho: number; segundos: number; brillo?: number}> = ({x, y, ancho, segundos, brillo = 1}) => {
	const k = ancho / 500;
	const s = Math.max(0, Math.ceil(segundos));
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, padding: `${14 * k}px 0`, background: '#120808', border: `${9 * k}px solid ${TINTA}`, borderRadius: 24 * k, textAlign: 'center', fontFamily: MONO, fontWeight: 700, fontSize: 170 * k, lineHeight: 1, color: '#ff3a30', textShadow: `0 0 ${24 * brillo * k}px rgba(255,58,48,0.9)`, boxShadow: `0 0 ${60 * brillo * k}px rgba(255,58,48,0.35)`}}>
			0:{String(s).padStart(2, '0')}
		</div>
	);
};

/** cartel de fecha y hora (cuaderno de bitácora) */
export const Bitacora: React.FC<{x: number; y: number; ancho: number; aparece: number}> = ({x, y, ancho, aparece}) => {
	const k = ancho / 600;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, opacity: aparece, transform: `translateY(${(1 - aparece) * 40}px) rotate(-3deg)`, background: '#f2e6c8', border: `${8 * k}px solid ${TINTA}`, padding: `${22 * k}px`, boxSizing: 'border-box', textAlign: 'center', color: '#2a1c12', boxShadow: `${12 * k}px ${14 * k}px 0 rgba(0,0,0,0.4)`}}>
			<div style={{fontFamily: TITULAR, fontSize: 30 * k, letterSpacing: 4 * k}}>DIARIO DE NAVEGACIÓN</div>
			<div style={{fontFamily: CONDENSADA, fontSize: 96 * k, lineHeight: 1.05}}>14 DE ABRIL</div>
			<div style={{fontFamily: MONO, fontWeight: 700, fontSize: 80 * k, color: '#c8202a'}}>23:40</div>
		</div>
	);
};

export const opacidadEntre = (f: number, a: number, b: number) => interpolate(f, [a, b], [0, 1], clamp);

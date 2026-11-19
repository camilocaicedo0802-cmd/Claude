import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Actor, Muneco, Ropa, alcanzar, manosEn, manosFrente} from '../componentes/Muneco';
import {Boca, CabezaSVG, Cejas, Ojos} from '../componentes/Personaje';
import {Cara, SelloPostal} from '../componentes/Recurrentes';
import {HINDENBURG, HITLER_TRAJE} from '../componentes/Vestuario';
import {Humo} from '../escenarios/Epoca';
import {CONDENSADA, SERIF, TITULAR} from '../fuentes';
import {TINTA, clamp, pop, tramo} from './base';
import {brazo} from './compartidas';

/* Escenarios y utilería de los capítulos 3 (La fiera domada), 4 (La crisis) y 5 (El cartero). Mundo de 1920 x 1080. */

const lleno: React.CSSProperties = {position: 'absolute', inset: 0};

/* ============================== vestuario propio ============================== */

/** ayudantes de Hindenburg (oficiales viejos, sin insignias) */
export const AYUDANTE: Ropa = {
	cabeza: {piel: '#ffffff', chaqueta: '', chaquetaSombra: '', botones: '', pelo: 'calvo', colorPelo: '#bdbdbd', bigote: 'manubrio', colorBigote: '#cfcfcf', monoculo: true},
	casaca: '#4f5d72',
	casacaSombra: '#38445a',
	botones: '#e0b23a',
	cuello: '#7a2a24',
	pantalon: '#3a4558',
	botas: '#141418',
};
export const AYUDANTE_2: Ropa = {...AYUDANTE, cabeza: {...AYUDANTE.cabeza, pelo: 'plano', colorPelo: '#9a9a9a', monoculo: false, bigote: 'morsa', colorBigote: '#e0e0e0'}};

/* ============================== escenarios ============================== */

/** pared de ladrillo de la calle (cartel de circo pegado) */
export const EscLadrillo: React.FC<{tono?: string}> = ({tono = '#7a3a2a'}) => (
	<div style={{...lleno, background: tono}}>
		{Array.from({length: 24}, (_, r) => (
			<div key={r} style={{position: 'absolute', left: (r % 2) * -60, top: r * 46, width: 2100, height: 46, display: 'flex'}}>
				{Array.from({length: 18}, (_, c) => (
					<div key={c} style={{width: 120, height: 46, boxSizing: 'border-box', border: '4px solid rgba(40,20,14,0.55)', background: (r * 7 + c * 3) % 5 === 0 ? 'rgba(0,0,0,0.08)' : 'rgba(255,255,255,0.03)'}} />
				))}
			</div>
		))}
		<div style={{position: 'absolute', left: 0, right: 0, top: 900, bottom: 0, background: 'linear-gradient(180deg, #4a4a50, #2a2a30)'}} />
		<div style={{position: 'absolute', left: 300, top: -200, width: 1300, height: 1300, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,214,150,0.22), rgba(255,214,150,0) 60%)'}} />
	</div>
);

/** despacho del primer ministro de Baviera (verde grisáceo, ventana alta) */
export const EscDespachoBavaro: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #4a5a4a 0%, #36443a 75%)'}}>
		{[0, 1, 2, 3, 4, 5].map((i) => (
			<div key={i} style={{position: 'absolute', left: 60 + i * 310, top: 100, width: 250, height: 520, border: '6px solid rgba(20,28,20,0.4)', borderRadius: 6}} />
		))}
		{/* ventana */}
		<div style={{position: 'absolute', left: 1380, top: 110, width: 380, height: 520, background: 'linear-gradient(180deg, #9fb4c4, #d9e2e6)', border: `10px solid #3a2a1e`, outline: `6px solid ${TINTA}`}}>
			<div style={{position: 'absolute', left: 180, top: 0, width: 10, height: 520, background: '#3a2a1e'}} />
			<div style={{position: 'absolute', left: 0, top: 250, width: 380, height: 10, background: '#3a2a1e'}} />
		</div>
		{/* estantería */}
		<div style={{position: 'absolute', left: 120, top: 180, width: 420, height: 460, background: '#4a3020', border: `8px solid ${TINTA}`}}>
			{[0, 1, 2].map((r) => (
				<div key={r} style={{position: 'absolute', left: 0, right: 0, top: 30 + r * 145, height: 110, display: 'flex', gap: 6, padding: '0 14px', borderBottom: `7px solid ${TINTA}`}}>
					{Array.from({length: 11}, (_, c) => (
						<div key={c} style={{width: 26, height: 80 + ((c * 13 + r * 7) % 30), alignSelf: 'flex-end', background: ['#7a2a24', '#2f4a3a', '#c9a43a', '#2a3a5a'][(c + r) % 4], border: `3px solid ${TINTA}`}} />
					))}
				</div>
			))}
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 640, bottom: 0, background: 'linear-gradient(180deg, #3a2a1e, #22180f)'}} />
		<div style={{position: 'absolute', left: 1200, top: 60, width: 900, height: 900, borderRadius: '50%', background: 'radial-gradient(circle, rgba(230,240,255,0.25), rgba(230,240,255,0) 60%)'}} />
	</div>
);

/** escritorio de frente (va delante de los personajes) */
export const EscritorioFrente: React.FC<{x: number; y: number; ancho: number; color?: string; children?: React.ReactNode}> = ({x, y, ancho, color = '#6a3e26', children}) => (
	<>
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: 44, background: color, border: `8px solid ${TINTA}`, borderRadius: 8}} />
		<div style={{position: 'absolute', left: x - ancho / 2 + 26, top: y + 44, width: ancho - 52, height: 500, background: `linear-gradient(180deg, ${color}, #2a160c)`, border: `8px solid ${TINTA}`, borderTop: 'none'}} />
		{children}
	</>
);

/** pista de circo: lona roja y dorada, foco */
export const EscCirco: React.FC<{foco?: [number, number]}> = ({foco = [960, 600]}) => (
	<div style={{...lleno, background: '#3a0a10'}}>
		{Array.from({length: 14}, (_, i) => (
			<div key={i} style={{position: 'absolute', left: 960, top: -200, width: 140, height: 1400, background: i % 2 ? '#c4262e' : '#e9c46a', transformOrigin: '0 0', transform: `rotate(${-70 + i * 10}deg)`, opacity: 0.85}} />
		))}
		<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 120, background: 'repeating-linear-gradient(90deg, #e0b23a 0 60px, #c4262e 60px 120px)', borderBottom: `8px solid ${TINTA}`, clipPath: 'polygon(0 0, 100% 0, 100% 70%, 97% 100%, 94% 70%, 91% 100%, 88% 70%, 85% 100%, 82% 70%, 79% 100%, 76% 70%, 73% 100%, 70% 70%, 67% 100%, 64% 70%, 61% 100%, 58% 70%, 55% 100%, 52% 70%, 49% 100%, 46% 70%, 43% 100%, 40% 70%, 37% 100%, 34% 70%, 31% 100%, 28% 70%, 25% 100%, 22% 70%, 19% 100%, 16% 70%, 13% 100%, 10% 70%, 7% 100%, 4% 70%, 1% 100%, 0 70%)'}} />
		{/* pista */}
		<div style={{position: 'absolute', left: -200, right: -200, top: 760, height: 520, borderRadius: '50%', background: '#c9a06a', border: `22px solid #c4262e`, outline: `8px solid ${TINTA}`}} />
		<div style={{position: 'absolute', inset: 0, background: `radial-gradient(ellipse 520px 640px at ${foco[0]}px ${foco[1]}px, rgba(255,240,200,0.35), rgba(0,0,0,0.45) 75%)`}} />
	</div>
);

/** sala de museo: pared de terciopelo y moldura */
export const EscMuseoSala: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #5a1e24, #3a1216)'}}>
		<div style={{position: 'absolute', left: 0, right: 0, top: 130, height: 16, background: '#c9a43a', opacity: 0.7}} />
		<div style={{position: 'absolute', left: 0, right: 0, top: 780, bottom: 0, background: 'linear-gradient(180deg, #3a2a1e, #1a120c)'}} />
		<div style={{position: 'absolute', left: 560, top: -100, width: 800, height: 900, background: 'linear-gradient(180deg, rgba(255,240,200,0.28), rgba(255,240,200,0))', clipPath: 'polygon(40% 0, 60% 0, 100% 100%, 0 100%)'}} />
	</div>
);

/** sala de reuniones gris (inversionistas) */
export const EscSalaJuntas: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #5a5048 0%, #3e3630 80%)'}}>
		{[0, 1, 2].map((i) => (
			<div key={i} style={{position: 'absolute', left: 140 + i * 600, top: 110, width: 420, height: 480, border: '8px solid rgba(0,0,0,0.25)'}} />
		))}
		<div style={{position: 'absolute', left: 0, right: 0, top: 700, bottom: 0, background: 'linear-gradient(180deg, #3a2a20, #20160f)'}} />
		{/* puerta de salida a la izquierda */}
		<div style={{position: 'absolute', left: 40, top: 300, width: 220, height: 420, background: '#2a1c12', border: `8px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: 70, top: 250, padding: '4px 14px', background: '#2f8a4a', color: '#fff', fontFamily: CONDENSADA, fontSize: 34, border: `5px solid ${TINTA}`}}>SALIDA</div>
	</div>
);

/** calle gris de la oficina de empleo (tono neutro) */
export const EscOficinaEmpleo: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #8a8e94 0%, #6a6e74 100%)'}}>
		<div style={{position: 'absolute', left: 1180, top: 60, width: 760, height: 760, background: '#5a5e64', border: `9px solid ${TINTA}`}}>
			{[0, 1, 2].map((i) => (
				<div key={i} style={{position: 'absolute', left: 60 + i * 230, top: 90, width: 150, height: 200, background: '#3a3e44', border: `6px solid ${TINTA}`}} />
			))}
			<div style={{position: 'absolute', left: 80, top: 440, width: 200, height: 320, background: '#2a2a2e', border: `7px solid ${TINTA}`}} />
		</div>
		<div style={{position: 'absolute', left: 1240, top: 360, padding: '10px 26px', background: '#e6e2d6', border: `7px solid ${TINTA}`, fontFamily: CONDENSADA, fontSize: 48, color: '#2a2a2e', letterSpacing: 3}}>OFICINA DE EMPLEO</div>
		<div style={{position: 'absolute', left: 1520, top: 470, padding: '6px 22px', background: '#2a2a2e', border: `6px solid ${TINTA}`, fontFamily: CONDENSADA, fontSize: 64, color: '#e6e2d6', letterSpacing: 2}}>6.000.000</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 820, bottom: 0, background: '#4a4e54', borderTop: `8px solid ${TINTA}`}} />
	</div>
);

/** pasillo con la puerta enorme del PRESIDENTE */
export const EscPasilloPresidente: React.FC<{silueta?: number; cerrada?: number}> = ({silueta = 1, cerrada = 1}) => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #2a3248 0%, #1a2032 100%)'}}>
		{[0, 1].map((i) => (
			<div key={i} style={{position: 'absolute', left: i ? 1500 : 120, top: 0, width: 300, height: 1080, background: 'linear-gradient(90deg, #22283a, #343c56 50%, #22283a)', border: `6px solid ${TINTA}`}} />
		))}
		<div style={{position: 'absolute', left: 0, right: 0, top: 900, bottom: 0, background: 'linear-gradient(180deg, #5a1e24, #2a0e10)'}} />
		<PuertaPresidente x={960} y={900} alto={820} silueta={silueta} cerrada={cerrada} />
	</div>
);

/** la puerta: hoja de madera, vidrio esmerilado con la silueta del bigotazo y placa de bronce */
export const PuertaPresidente: React.FC<{x: number; y: number; alto: number; silueta?: number; cerrada?: number}> = ({x, y, alto, silueta = 1, cerrada = 1}) => {
	const ancho = alto * 0.6;
	const k = alto / 820;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto, width: ancho, height: alto}}>
			<div style={{position: 'absolute', left: -30 * k, top: -30 * k, right: -30 * k, bottom: 0, background: '#3a2414', border: `${9 * k}px solid ${TINTA}`}} />
			<div style={{position: 'absolute', inset: 0, background: '#0a0a0e'}} />
			<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(90deg, #6a3e22, #8a5a32 50%, #5a321a)', border: `${8 * k}px solid ${TINTA}`, transformOrigin: '0 50%', transform: `perspective(${1400 * k}px) rotateY(${(1 - cerrada) * -70}deg)`}}>
				{/* vidrio esmerilado */}
				<div style={{position: 'absolute', left: 50 * k, right: 50 * k, top: 60 * k, height: 380 * k, background: 'linear-gradient(180deg, #e6e2c8, #c9c4a8)', border: `${7 * k}px solid ${TINTA}`, overflow: 'hidden'}}>
					{silueta > 0 && (
						<svg viewBox="0 0 400 400" style={{position: 'absolute', left: 0, top: 30 * k, width: '100%', height: '100%', opacity: 0.75 * silueta, filter: `blur(${3 * k}px)`}}>
							<path d="M 120 400 L 110 300 Q 120 240 200 230 Q 280 240 290 300 L 280 400 Z" fill="#2a2a30" />
							<path d="M 116 160 Q 114 74 136 62 L 264 62 Q 286 74 284 160 Q 282 238 200 242 Q 118 238 116 160 Z" fill="#2a2a30" />
							<path d="M 200 180 Q 120 160 40 186 Q 0 200 -10 160 Q -20 230 60 230 Q 140 232 200 206 Q 260 232 340 230 Q 420 230 410 160 Q 400 200 360 186 Q 280 160 200 180 Z" fill="#1a1a20" />
						</svg>
					)}
				</div>
				{/* placa de bronce */}
				<div style={{position: 'absolute', left: 70 * k, right: 70 * k, top: 480 * k, padding: `${10 * k}px 0`, background: 'linear-gradient(180deg, #e9c46a, #b8862a)', border: `${6 * k}px solid ${TINTA}`, textAlign: 'center', fontFamily: SERIF, fontWeight: 900, fontSize: 44 * k, color: '#3a2a10', letterSpacing: 4 * k}}>PRESIDENTE</div>
				<div style={{position: 'absolute', right: 40 * k, top: 600 * k, width: 40 * k, height: 40 * k, borderRadius: '50%', background: '#e9c46a', border: `${5 * k}px solid ${TINTA}`}} />
			</div>
		</div>
	);
};

/** salón imperial: azul, columnas, oro */
export const EscImperial: React.FC<{brillo?: number}> = ({brillo = 0}) => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #1c2c5a 0%, #2f4f8f 60%, #14203e 100%)'}}>
		{[0, 1, 2, 3].map((i) => (
			<div key={i} style={{position: 'absolute', left: 160 + i * 480, top: 0, width: 110, height: 1080, background: 'linear-gradient(90deg, #c9a43a, #f0d27a 50%, #a8862a)', opacity: 0.32}} />
		))}
		<div style={{position: 'absolute', left: 0, right: 0, top: 860, bottom: 0, background: 'linear-gradient(180deg, #7a1a22, #3a0a10)'}} />
		<div style={{position: 'absolute', left: 560, top: 40, width: 800, height: 800, borderRadius: '50%', background: `radial-gradient(circle, rgba(255,226,140,${0.22 + 0.3 * brillo}) 0%, rgba(255,226,140,0) 65%)`}} />
	</div>
);

/** comedor elegante (mantel blanco, candelabro) */
export const EscComedor: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #24304e, #182036)'}}>
		{[0, 1, 2, 3, 4].map((i) => (
			<div key={i} style={{position: 'absolute', left: 60 + i * 380, top: 100, width: 300, height: 560, border: '8px solid rgba(201,164,58,0.3)', borderRadius: '150px 150px 0 0'}} />
		))}
		<div style={{position: 'absolute', left: 0, right: 0, top: 700, bottom: 0, background: '#2a1a14'}} />
		<div style={{position: 'absolute', left: 360, top: -200, width: 1200, height: 1200, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,226,160,0.28), rgba(255,226,160,0) 60%)'}} />
	</div>
);

export const MesaMantel: React.FC<{x: number; y: number; ancho: number}> = ({x, y, ancho}) => (
	<>
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: 340, background: 'linear-gradient(180deg, #ffffff, #e6e2d6)', border: `8px solid ${TINTA}`, borderRadius: '12px 12px 0 0'}}>
			{Array.from({length: Math.floor(ancho / 60)}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: i * 60 + 20, top: 40, width: 4, height: 300, background: 'rgba(0,0,0,0.06)'}} />
			))}
		</div>
	</>
);

/** ventanilla de oficina pública */
export const EscVentanilla: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #8a8270, #6a6252)'}}>
		<div style={{position: 'absolute', left: 520, top: 120, width: 880, height: 560, background: '#d9d2bc', border: `10px solid ${TINTA}`}}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 80, background: '#4a3a2a', borderBottom: `7px solid ${TINTA}`, color: '#efe6cf', fontFamily: CONDENSADA, fontSize: 52, textAlign: 'center', lineHeight: '80px', letterSpacing: 4}}>REGISTRO CIVIL</div>
			{Array.from({length: 9}, (_, i) => (
				<div key={i} style={{position: 'absolute', top: 80, bottom: 0, left: 40 + i * 100, width: 10, background: '#3a3a40', border: `3px solid ${TINTA}`}} />
			))}
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 680, height: 60, background: '#6a4a2a', border: `9px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: 0, right: 0, top: 740, bottom: 0, background: 'linear-gradient(180deg, #5a3e22, #2a1c10)'}} />
	</div>
);

/* ============================== utilería del capítulo 3 ============================== */

/** cartel de circo pegado en la pared */
export const CartelCirco: React.FC<{x: number; y: number; ancho: number; rot?: number}> = ({x, y, ancho, rot = -2}) => {
	const k = ancho / 900;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: ancho * 1.25, transform: `rotate(${rot}deg)`, background: '#f2e2b8', border: `${8 * k}px solid ${TINTA}`, boxShadow: `${14 * k}px ${18 * k}px 0 rgba(0,0,0,0.35)`, clipPath: 'polygon(0 2%, 3% 0, 97% 1%, 100% 4%, 99% 97%, 96% 100%, 2% 99%, 0 95%)', overflow: 'hidden', textAlign: 'center', fontFamily: CONDENSADA, color: '#c4262e'}}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 200 * k, background: 'repeating-linear-gradient(90deg, #c4262e 0 70px, #e0b23a 70px 140px)', opacity: 0.9}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 230 * k, fontFamily: SERIF, fontStyle: 'italic', fontSize: 64 * k, color: '#2a2218'}}>Gran Circo de Baviera</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 330 * k, fontSize: 210 * k, lineHeight: 1, letterSpacing: 10 * k, color: '#2a2218'}}>1925</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 560 * k, fontSize: 130 * k, lineHeight: 0.95, letterSpacing: 4 * k, textShadow: `${5 * k}px ${5 * k}px 0 #e0b23a`}}>
				LA FIERA
				<br />
				DOMADA
			</div>
			{/* el látigo y el taburete dibujados */}
			<svg viewBox="0 0 900 240" style={{position: 'absolute', left: 0, bottom: 20 * k, width: ancho, height: 240 * k}}>
				<path d="M 220 210 L 300 120 Q 380 40 520 70 Q 640 100 700 60" stroke="#2a2218" strokeWidth={10} fill="none" strokeLinecap="round" />
				<rect x={370} y={150} width={160} height={70} rx={10} fill="#c4262e" stroke="#2a2218" strokeWidth={8} />
			</svg>
		</div>
	);
};

/** el gatito con flequillo y bigote de cepillo (Hitler «domado») */
export const Gatito: React.FC<{x: number; y: number; tam: number; ruge?: number; voltear?: boolean}> = ({x, y, tam, ruge = 0, voltear = false}) => {
	const f = useCurrentFrame();
	const ronr = ruge < 0.5 ? Math.sin(f / 2) * 1.5 : 0;
	const r = ruge > 0.5;
	return (
		<svg width={tam} height={tam} viewBox="0 0 300 300" style={{position: 'absolute', left: x - tam / 2, top: y - tam, overflow: 'visible', transform: `${voltear ? 'scaleX(-1)' : ''} scale(${1 + 0.18 * ruge})`, transformOrigin: '50% 100%'}}>
			<path d="M 230 250 Q 300 230 280 160 Q 270 130 290 110" stroke={TINTA} strokeWidth={22} fill="none" strokeLinecap="round" />
			<path d="M 230 250 Q 300 230 280 160 Q 270 130 290 110" stroke="#9a9aa4" strokeWidth={12} fill="none" strokeLinecap="round" />
			<ellipse cx={160} cy={220} rx={90 + ronr} ry={62} fill="#9a9aa4" stroke={TINTA} strokeWidth={8} />
			{/* orejas */}
			<path d="M 92 92 L 100 20 L 150 70 Z" fill="#9a9aa4" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
			<path d="M 228 92 L 220 20 L 170 70 Z" fill="#9a9aa4" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
			<circle cx={160} cy={120} r={74} fill="#a8a8b2" stroke={TINTA} strokeWidth={8} />
			{/* flequillo de lado */}
			<path d="M 96 92 Q 120 50 210 58 Q 190 70 168 104 Q 150 84 96 92 Z" fill="#1a1410" stroke={TINTA} strokeWidth={5} />
			{r ? (
				<>
					<path d="M 112 102 L 146 116" stroke={TINTA} strokeWidth={8} strokeLinecap="round" />
					<path d="M 208 102 L 174 116" stroke={TINTA} strokeWidth={8} strokeLinecap="round" />
					<circle cx={132} cy={124} r={9} fill={TINTA} />
					<circle cx={188} cy={124} r={9} fill={TINTA} />
				</>
			) : (
				<>
					<path d="M 118 124 Q 132 112 146 124" stroke={TINTA} strokeWidth={7} fill="none" strokeLinecap="round" />
					<path d="M 174 124 Q 188 112 202 124" stroke={TINTA} strokeWidth={7} fill="none" strokeLinecap="round" />
				</>
			)}
			<path d="M 152 142 L 168 142 L 160 152 Z" fill="#e6a0b0" stroke={TINTA} strokeWidth={4} />
			{/* bigote de cepillo */}
			<rect x={146} y={152} width={28} height={13} rx={2} fill="#1a1410" />
			{r ? (
				<path d="M 128 170 Q 160 158 192 170 Q 186 210 160 212 Q 134 210 128 170 Z" fill="#6a1a1a" stroke={TINTA} strokeWidth={6} />
			) : (
				<path d="M 144 172 Q 152 178 160 170 Q 168 178 176 172" stroke={TINTA} strokeWidth={5} fill="none" strokeLinecap="round" />
			)}
			{r && (
				<>
					<path d="M 140 172 L 146 186 L 152 172" fill="#fff" stroke={TINTA} strokeWidth={3} />
					<path d="M 168 172 L 174 186 L 180 172" fill="#fff" stroke={TINTA} strokeWidth={3} />
				</>
			)}
			{/* bigotes de gato */}
			{[-1, 1].map((l) => (
				<g key={l}>
					<line x1={160 + l * 30} y1={150} x2={160 + l * 86} y2={140} stroke={TINTA} strokeWidth={3} />
					<line x1={160 + l * 30} y1={158} x2={160 + l * 86} y2={162} stroke={TINTA} strokeWidth={3} />
				</g>
			))}
			{/* collar */}
			<path d="M 104 172 Q 160 210 216 172" stroke="#c4262e" strokeWidth={14} fill="none" />
			<circle cx={160} cy={196} r={10} fill="#e0b23a" stroke={TINTA} strokeWidth={4} />
			{/* patitas */}
			<ellipse cx={120} cy={278} rx={26} ry={16} fill="#9a9aa4" stroke={TINTA} strokeWidth={7} />
			<ellipse cx={196} cy={278} rx={26} ry={16} fill="#9a9aa4" stroke={TINTA} strokeWidth={7} />
			{!r && ruge === 0 && (
				<text x={250} y={70} fontFamily={TITULAR} fontWeight={800} fontSize={34} fill="#fff3c0" stroke={TINTA} strokeWidth={2} opacity={0.6 + 0.4 * Math.sin(f / 4)}>
					rrr
				</text>
			)}
		</svg>
	);
};

/** taburete de circo (se rompe con `rompe` 0..1) */
export const Taburete: React.FC<{x: number; y: number; ancho: number; rompe?: number}> = ({x, y, ancho, rompe = 0}) => {
	const alto = ancho * 0.9;
	const pieza = (lado: -1 | 1) => (
		<div style={{position: 'absolute', left: lado < 0 ? 0 : ancho / 2, top: 0, width: ancho / 2, height: alto, overflow: 'hidden', transform: `translate(${lado * rompe * 160}px, ${rompe * 60}px) rotate(${lado * rompe * 40}deg)`}}>
			<div style={{position: 'absolute', left: lado < 0 ? 0 : -ancho / 2, top: 0, width: ancho, height: alto}}>
				<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 50, borderRadius: '50%', background: '#e0b23a', border: `7px solid ${TINTA}`}} />
				<div style={{position: 'absolute', left: 14, right: 14, top: 26, bottom: 0, background: 'repeating-linear-gradient(90deg, #c4262e 0 40px, #e9c46a 40px 80px)', border: `7px solid ${TINTA}`, borderTop: 'none', borderRadius: '0 0 30px 30px'}} />
			</div>
		</div>
	);
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto, width: ancho, height: alto}}>
			{pieza(-1)}
			{pieza(1)}
		</div>
	);
};

/** látigo en la mano */
export const Latigo: React.FC<{rot?: number; chasquido?: number}> = ({rot = 0, chasquido = 0}) => (
	<g transform={`rotate(${rot} 0 36)`}>
		<rect x={-10} y={20} width={20} height={110} rx={6} fill="#3a2414" stroke={TINTA} strokeWidth={5} />
		<path d={`M 0 130 Q ${60 + 80 * chasquido} 220 ${-40 + 120 * chasquido} 330 Q ${-120 + 200 * chasquido} 420 ${60 - 60 * chasquido} 470`} stroke={TINTA} strokeWidth={9} fill="none" strokeLinecap="round" />
	</g>
);

/** hojas de calendario que se arrancan */
export const CalendarioHojas: React.FC<{x: number; y: number; ancho: number; textos: string[]; cambios: number[]; cabecera?: string; color?: string}> = ({x, y, ancho, textos, cambios, cabecera = '1925', color = '#c4262e'}) => {
	const f = useCurrentFrame();
	let idx = 0;
	cambios.forEach((c, i) => {
		if (f >= c) idx = i + 1;
	});
	idx = Math.min(idx, textos.length - 1);
	const ult = idx > 0 ? cambios[idx - 1] : -999;
	const k = ancho / 300;
	const hoja = (t: string, estilo: React.CSSProperties) => (
		<div style={{position: 'absolute', inset: 0, background: '#fbf6e9', border: `${6 * k}px solid ${TINTA}`, borderRadius: 8 * k, textAlign: 'center', fontFamily: CONDENSADA, color: '#2a2218', overflow: 'hidden', ...estilo}}>
			<div style={{background: color, color: '#fbf6e9', fontSize: 40 * k, letterSpacing: 3 * k, borderBottom: `${5 * k}px solid ${TINTA}`}}>{cabecera}</div>
			<div style={{fontSize: 74 * k, lineHeight: 1.6}}>{t}</div>
		</div>
	);
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: ancho * 0.8, perspective: 900}}>
			{hoja(textos[idx], {})}
			{idx > 0 && f - ult < 7 && hoja(textos[idx - 1], {transform: `rotateX(${interpolate(f - ult, [0, 7], [0, 110], clamp)}deg) translateY(${(f - ult) * -6}px)`, transformOrigin: '50% 0', opacity: interpolate(f - ult, [4, 7], [1, 0], clamp)})}
		</div>
	);
};

/** lupa (sostenida en el mundo) */
export const LupaMundo: React.FC<{x: number; y: number; tam: number; rot?: number}> = ({x, y, tam, rot = -30}) => (
	<svg width={tam} height={tam} viewBox="0 0 200 200" style={{position: 'absolute', left: x - tam / 2, top: y - tam * 0.4, transform: `rotate(${rot}deg)`, transformOrigin: '50% 40%', overflow: 'visible'}}>
		<rect x={88} y={140} width={26} height={100} rx={10} fill="#6b3f20" stroke={TINTA} strokeWidth={8} />
		<circle cx={100} cy={80} r={68} fill="rgba(190,230,255,0.25)" stroke={TINTA} strokeWidth={22} />
		<circle cx={100} cy={80} r={68} fill="none" stroke="#c9a43a" strokeWidth={10} />
		<path d="M 64 58 Q 76 40 98 36" stroke="#fff" strokeWidth={9} strokeLinecap="round" fill="none" opacity={0.8} />
	</svg>
);

/** pizarra con un gráfico que se desploma */
export const GraficoCaida: React.FC<{x: number; y: number; ancho: number; cae: number; titulo?: string}> = ({x, y, ancho, cae, titulo = 'VOTOS'}) => {
	const alto = ancho * 0.72;
	const pts = [
		[40, 300],
		[140, 250],
		[240, 200],
		[340, 170],
	];
	const caidaY = 170 + cae * 260;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: alto, background: '#f6f2e6', border: `9px solid ${TINTA}`, boxShadow: '12px 14px 0 rgba(0,0,0,0.3)'}}>
			<div style={{position: 'absolute', left: 20, top: 10, fontFamily: CONDENSADA, fontSize: ancho * 0.07, color: '#2a2218'}}>{titulo}</div>
			<svg viewBox="0 0 500 360" style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
				{[100, 180, 260].map((yy) => (
					<line key={yy} x1={30} y1={yy} x2={480} y2={yy} stroke="#cfc4a8" strokeWidth={3} />
				))}
				<path d={`M ${pts.map((p) => p.join(' ')).join(' L ')} L 440 ${caidaY}`} stroke={cae > 0.2 ? '#c4262e' : '#2f8a4a'} strokeWidth={12} fill="none" strokeLinejoin="round" strokeLinecap="round" />
				<polygon points={`440,${caidaY + 30} 420,${caidaY - 6} 460,${caidaY - 6}`} fill={cae > 0.2 ? '#c4262e' : '#2f8a4a'} />
			</svg>
		</div>
	);
};

/** marco dorado de museo con su plaquita */
export const MarcoMuseo: React.FC<{x: number; y: number; ancho: number; placa: string; texto?: string}> = ({x, y, ancho, placa, texto}) => {
	const alto = ancho * 0.7;
	const k = ancho / 700;
	return (
		<>
			<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: alto, background: 'linear-gradient(135deg, #f0d27a, #a8862a)', border: `${8 * k}px solid ${TINTA}`, padding: 46 * k, boxSizing: 'border-box', boxShadow: `${16 * k}px ${20 * k}px 0 rgba(0,0,0,0.35)`}}>
				<div style={{width: '100%', height: '100%', background: '#f2ead6', border: `${6 * k}px solid ${TINTA}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: SERIF, fontStyle: 'italic', fontSize: 48 * k, color: '#2a2218', textAlign: 'center', padding: 20 * k, boxSizing: 'border-box'}}>{texto}</div>
			</div>
			<div style={{position: 'absolute', left: x - 170 * k, top: y + alto + 30 * k, width: 340 * k, padding: `${10 * k}px 0`, background: 'linear-gradient(180deg, #e9c46a, #b8862a)', border: `${5 * k}px solid ${TINTA}`, textAlign: 'center', fontFamily: TITULAR, fontWeight: 800, fontSize: 26 * k, color: '#3a2a10', letterSpacing: 2 * k}}>{placa}</div>
			{/* cordón de terciopelo */}
			<div style={{position: 'absolute', left: x - ancho * 0.75, top: y + alto + 170 * k, width: ancho * 1.5, height: 70 * k, borderBottom: `${16 * k}px solid #8a1a22`, borderRadius: '0 0 50% 50%'}} />
			{[-1, 1].map((l) => (
				<div key={l} style={{position: 'absolute', left: x + l * ancho * 0.75 - 14 * k, top: y + alto + 140 * k, width: 28 * k, height: 240 * k, background: '#c9a43a', border: `${5 * k}px solid ${TINTA}`, borderRadius: 8 * k}} />
			))}
		</>
	);
};

/* ============================== utilería del capítulo 4 ============================== */

/** máquina de teletipo con su cinta (rótulo «OCT 1929») */
export const Teletipo: React.FC<{x: number; y: number; ancho: number; desde: number}> = ({x, y, ancho, desde}) => {
	const f = useCurrentFrame();
	const k = ancho / 800;
	const corre = Math.max(0, f - desde) * 9 * k;
	return (
		<>
			{/* cinta que sale y cuelga */}
			<div style={{position: 'absolute', left: x + 140 * k, top: y - 40 * k, width: 2200 * k, height: 90 * k, background: '#f4eedc', border: `${5 * k}px solid ${TINTA}`, transform: `translateX(${-corre}px)`, display: 'flex', alignItems: 'center', gap: 60 * k, paddingLeft: 40 * k, fontFamily: "'Liberation Mono', 'DejaVu Sans Mono', monospace", fontWeight: 700, fontSize: 52 * k, color: '#2a2218', whiteSpace: 'nowrap'}}>
				<span>GM 45 ▼ 12</span>
				<span>US STEEL 204 ▼ 22</span>
				<span style={{color: '#c4262e', fontSize: 70 * k}}>OCT 1929</span>
				<span>RCA 68 ▼ 33</span>
				<span>NY ▼▼▼</span>
			</div>
			<div style={{position: 'absolute', left: x - 260 * k, top: y - 160 * k, width: 420 * k, height: 300 * k, background: 'linear-gradient(180deg, #4a4a52, #2a2a30)', border: `${9 * k}px solid ${TINTA}`, borderRadius: 30 * k}}>
				<div style={{position: 'absolute', left: 60 * k, top: -140 * k, width: 300 * k, height: 160 * k, borderRadius: '50% 50% 0 0', background: 'rgba(220,236,242,0.4)', border: `${7 * k}px solid ${TINTA}`}} />
				<div style={{position: 'absolute', left: 150 * k, top: -100 * k, width: 120 * k, height: 100 * k, borderRadius: '50%', background: '#c9a43a', border: `${6 * k}px solid ${TINTA}`, transform: `rotate(${f * 20}deg)`}} />
			</div>
		</>
	);
};

/** el edificio de la Bolsa (fachada de columnas) con cara: estornuda en `estornudo` */
export const BolsaNY: React.FC<{x: number; y: number; ancho: number; estornudo: number}> = ({x, y, ancho, estornudo}) => {
	const f = useCurrentFrame();
	const t = f - estornudo;
	const aspira = t < 0 ? interpolate(t, [-14, 0], [0, 1], clamp) : 0;
	const sacude = t >= 0 && t < 12 ? Math.sin(t * 2.4) * 10 * (1 - t / 12) : 0;
	const k = ancho / 900;
	const alto = ancho * 0.8;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto, width: ancho, height: alto, transform: `translateX(${sacude}px) scaleY(${1 + aspira * 0.06}) scaleX(${1 - aspira * 0.03})`, transformOrigin: '50% 100%'}}>
			{/* frontón */}
			<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 200 * k, background: '#d9d4c6', border: `${9 * k}px solid ${TINTA}`, clipPath: 'polygon(50% 0, 100% 100%, 0 100%)'}} />
			<div style={{position: 'absolute', left: -20 * k, right: -20 * k, top: 190 * k, height: 60 * k, background: '#cfc8b6', border: `${8 * k}px solid ${TINTA}`, fontFamily: SERIF, fontWeight: 900, fontSize: 40 * k, textAlign: 'center', lineHeight: `${44 * k}px`, letterSpacing: 6 * k, color: '#2a2218'}}>STOCK EXCHANGE</div>
			{/* columnas */}
			{Array.from({length: 6}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: (40 + i * 150) * k, top: 250 * k, width: 80 * k, height: 390 * k, background: 'linear-gradient(90deg, #bfb8a6, #ece6d6 50%, #bfb8a6)', border: `${6 * k}px solid ${TINTA}`}} />
			))}
			<div style={{position: 'absolute', left: -30 * k, right: -30 * k, top: 640 * k, height: 80 * k, background: '#bfb8a6', border: `${8 * k}px solid ${TINTA}`}} />
			{/* la cara sobre el frontón */}
			<svg viewBox="0 0 900 260" style={{position: 'absolute', left: 0, top: -60 * k, width: ancho, height: 260 * k, overflow: 'visible'}}>
				{t >= 0 && t < 14 ? (
					<>
						<path d="M 360 120 L 410 140 M 540 120 L 490 140" stroke={TINTA} strokeWidth={12} strokeLinecap="round" />
						<ellipse cx={450} cy={196} rx={60} ry={40} fill="#5a1414" stroke={TINTA} strokeWidth={9} />
					</>
				) : (
					<>
						<ellipse cx={390} cy={136} rx={16} ry={aspira > 0.3 ? 6 : 20} fill={TINTA} />
						<ellipse cx={510} cy={136} rx={16} ry={aspira > 0.3 ? 6 : 20} fill={TINTA} />
						<path d={`M 410 ${200 - aspira * 10} Q 450 ${186 - aspira * 20} 490 ${200 - aspira * 10}`} stroke={TINTA} strokeWidth={10} fill="none" strokeLinecap="round" />
					</>
				)}
			</svg>
		</div>
	);
};

/** nube de estornudo (gotitas y «¡ACHÚ!») que viaja de (x1,y1) a (x2,y2) */
export const Estornudo: React.FC<{x1: number; y1: number; x2: number; y2: number; desde: number; dur: number; texto?: boolean}> = ({x1, y1, x2, y2, desde, dur, texto = true}) => {
	const f = useCurrentFrame();
	const t = interpolate(f, [desde, desde + dur], [0, 1], clamp);
	if (f < desde) return null;
	const x = x1 + (x2 - x1) * t;
	const y = y1 + (y2 - y1) * t - Math.sin(Math.PI * t) * 120;
	return (
		<>
			{Array.from({length: 12}, (_, i) => {
				const a = (i / 12) * Math.PI * 2;
				const r = 40 + 80 * Math.min(1, (f - desde) / 8) + (i % 3) * 20;
				return <div key={i} style={{position: 'absolute', left: x + Math.cos(a) * r, top: y + Math.sin(a) * r * 0.6, width: 22, height: 22, borderRadius: '50%', background: 'rgba(200,236,255,0.85)', border: `4px solid ${TINTA}`}} />;
			})}
			<div style={{position: 'absolute', left: x - 180, top: y - 110, width: 360, height: 220, borderRadius: '50%', background: 'radial-gradient(ellipse, rgba(230,246,255,0.9), rgba(230,246,255,0) 70%)'}} />
			{texto && (
				<div style={{position: 'absolute', left: x - 200, top: y - 60, width: 400, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 110, color: '#fff', WebkitTextStroke: `6px ${TINTA}`, transform: `scale(${0.6 + 0.4 * Math.min(1, (f - desde) / 5)})`}}>¡ACHÚ!</div>
			)}
		</>
	);
};

/** Alemania como personaje en el mapa: una mancha con cara, termómetro y bufanda */
export const AlemaniaEnferma: React.FC<{x: number; y: number; tam: number; enferma: number}> = ({x, y, tam, enferma}) => {
	const f = useCurrentFrame();
	const tirita = enferma > 0.5 ? Math.sin(f * 1.6) * 3 : 0;
	return (
		<svg width={tam} height={tam} viewBox="0 0 300 300" style={{position: 'absolute', left: x - tam / 2 + tirita, top: y - tam / 2, overflow: 'visible'}}>
			<path d="M 80 40 L 170 20 L 230 50 L 250 120 L 240 200 L 270 260 L 180 280 L 120 260 L 60 270 L 70 190 L 40 130 Z" fill={enferma > 0.5 ? '#c9d9a6' : '#e9dcb4'} stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
			<text x={150} y={250} textAnchor="middle" fontFamily={CONDENSADA} fontSize={34} fill="#2a2218" letterSpacing={2}>
				ALEMANIA
			</text>
			{enferma > 0.5 ? (
				<>
					<path d="M 104 120 Q 118 110 132 120 M 168 120 Q 182 110 196 120" stroke={TINTA} strokeWidth={7} fill="none" strokeLinecap="round" />
					<path d="M 120 180 Q 150 166 180 180" stroke={TINTA} strokeWidth={7} fill="none" strokeLinecap="round" />
					<ellipse cx={110} cy={150} rx={16} ry={9} fill="#e88" opacity={0.7} />
					<ellipse cx={190} cy={150} rx={16} ry={9} fill="#e88" opacity={0.7} />
					{/* termómetro */}
					<g transform="translate(176 168) rotate(-30)">
						<rect x={0} y={-8} width={110} height={16} rx={8} fill="#fff" stroke={TINTA} strokeWidth={5} />
						<rect x={40} y={-3} width={66} height={6} fill="#c4262e" />
						<circle cx={108} cy={0} r={12} fill="#c4262e" stroke={TINTA} strokeWidth={5} />
					</g>
					{/* bufanda */}
					<path d="M 70 200 Q 150 230 240 200 L 244 226 Q 150 256 66 226 Z" fill="#2f6fd1" stroke={TINTA} strokeWidth={6} />
					<path d="M 200 220 L 214 290 L 236 286 L 226 214 Z" fill="#2f6fd1" stroke={TINTA} strokeWidth={6} />
				</>
			) : (
				<>
					<circle cx={118} cy={120} r={10} fill={TINTA} />
					<circle cx={182} cy={120} r={10} fill={TINTA} />
					<path d="M 124 170 Q 150 186 176 170" stroke={TINTA} strokeWidth={7} fill="none" strokeLinecap="round" />
				</>
			)}
		</svg>
	);
};

/** mano gigante que tira de una cuerda de monedas */
export const ManoCuerda: React.FC<{x: number; y: number; tira: number}> = ({x, y, tira}) => (
	<>
		{/* cuerda con monedas, desde la mano hacia la derecha (los bancos) */}
		<div style={{position: 'absolute', left: x + 120 - tira * 700, top: y + 40, width: 1400, height: 14, background: '#8a6a3a', border: `4px solid ${TINTA}`}} />
		{Array.from({length: 12}, (_, i) => (
			<div key={i} style={{position: 'absolute', left: x + 200 + i * 110 - tira * 700, top: y + 10, width: 70, height: 70, borderRadius: '50%', background: 'radial-gradient(circle at 35% 35%, #ffe28a, #c9a43a)', border: `6px solid ${TINTA}`, fontFamily: CONDENSADA, fontSize: 34, textAlign: 'center', lineHeight: '58px', color: '#7a5a10'}}>
				$
			</div>
		))}
		<svg width={460} height={320} viewBox="0 0 460 320" style={{position: 'absolute', left: x - 380 - tira * 700, top: y - 110, overflow: 'visible'}}>
			<rect x={-400} y={120} width={480} height={150} fill="#2a3a5a" stroke={TINTA} strokeWidth={10} />
			<rect x={60} y={110} width={60} height={170} fill="#ffffff" stroke={TINTA} strokeWidth={8} />
			<path d="M 120 120 Q 220 70 320 110 Q 420 120 440 170 Q 430 210 380 214 L 380 240 Q 330 280 230 270 Q 150 266 120 250 Z" fill="#ffe0c4" stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
			<path d="M 300 150 Q 360 150 380 180 M 290 190 Q 350 196 380 214" stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" />
		</svg>
	</>
);

/** fachada de banco alemán */
export const Banco: React.FC<{x: number; y: number; ancho: number; vacio?: number}> = ({x, y, ancho, vacio = 0}) => {
	const k = ancho / 400;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - 420 * k, width: ancho, height: 420 * k}}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 90 * k, background: '#cfc8b6', border: `${7 * k}px solid ${TINTA}`, clipPath: 'polygon(50% 0, 100% 100%, 0 100%)'}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 86 * k, height: 50 * k, background: '#bfb8a6', border: `${6 * k}px solid ${TINTA}`, textAlign: 'center', fontFamily: SERIF, fontWeight: 900, fontSize: 30 * k, lineHeight: `${40 * k}px`, color: '#2a2218', letterSpacing: 4 * k}}>BANK</div>
			<div style={{position: 'absolute', left: 30 * k, right: 30 * k, top: 136 * k, bottom: 0, background: '#e6e0d0', border: `${6 * k}px solid ${TINTA}`}}>
				<div style={{position: 'absolute', left: '35%', right: '35%', top: 70 * k, bottom: 0, background: vacio > 0.5 ? '#141418' : '#5a3a22', border: `${6 * k}px solid ${TINTA}`}} />
			</div>
		</div>
	);
};

/** una persona de la fila, vista de lado (tono gris y digno) */
const ROPA_FILA: Ropa[] = [0, 1, 2, 3, 4, 5].map((i) => ({
	cabeza: {piel: '#ffffff', chaqueta: '', chaquetaSombra: '', botones: '', pelo: (['corto', 'raya', 'calvo', 'liso', 'corto', 'raya'] as const)[i], colorPelo: ['#3a2a1e', '#6b6b6b', '#8a8a8a', '#2a1c12', '#5a4a3a', '#1a1410'][i], gorra: i % 3 === 0 ? 'boina' : i % 3 === 1 ? 'fedora' : undefined, colorGorra: ['#4a4a50', '#3a3a44', '#5a5048'][i % 3], colorBanda: '#2a2a30'},
	casaca: ['#5a5a60', '#4a4e54', '#6a6458', '#3e4248', '#5e5850', '#4a4a50'][i],
	casacaSombra: '#3a3a40',
	pantalon: '#3a3a40',
	zapatos: '#1a1a1e',
	botones: '#2a2a30',
}));

export const Fila: React.FC<{x0: number; y: number; n: number; paso: number; alto: number; giran?: number}> = ({x0, y, n, paso, alto, giran = 0}) => (
	<>
		{Array.from({length: n}, (_, i) => {
			const gira = giran > 0 && i * 0.06 < giran;
			return (
				<Actor key={i} x={x0 + i * paso} y={y} alto={alto} voltear={!gira}>
					<Muneco ropa={ROPA_FILA[i % ROPA_FILA.length]} pose={{...manosFrente([180, 520], [220, 520]), mi: 'agarra', md: 'agarra', cabeza: gira ? -8 : 0}} ojos={gira ? 'grandes' : 'normal'} cejas={gira ? 'sorprendido' : 'preocupado'} boca="seria" semilla={i} sombra />
				</Actor>
			);
		})}
	</>
);

/** puesto de teletienda con el cartel ¡SOLUCIÓN MÁGICA! */
export const PuestoTeletienda: React.FC<{x: number; y: number; ancho: number; aparece: number}> = ({x, y, ancho, aparece}) => {
	const f = useCurrentFrame();
	const k = ancho / 700;
	const brillo = 0.6 + 0.4 * Math.abs(Math.sin(f / 4));
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, transform: `scale(${aparece})`, transformOrigin: '50% 100%'}}>
			<div style={{margin: '0 auto', width: ancho * 0.9, padding: `${16 * k}px 0`, background: '#c4262e', border: `${8 * k}px solid ${TINTA}`, borderRadius: 16 * k, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 82 * k, color: '#ffe86a', letterSpacing: 2 * k, boxShadow: `0 0 ${60 * brillo * k}px rgba(255,230,100,${0.6 * brillo})`}}>¡SOLUCIÓN MÁGICA!</div>
			<div style={{display: 'flex', justifyContent: 'space-around', marginTop: 10 * k}}>
				{Array.from({length: 8}, (_, i) => (
					<div key={i} style={{width: 26 * k, height: 26 * k, borderRadius: '50%', background: (Math.floor(f / 3) + i) % 2 ? '#ffe86a' : '#7a5a10', border: `${4 * k}px solid ${TINTA}`}} />
				))}
			</div>
		</div>
	);
};

/** cohete pegado a la jarra (llama animada) */
export const Cohete: React.FC<{x: number; y: number; tam: number; llama: number}> = ({x, y, tam, llama}) => {
	const f = useCurrentFrame();
	const l = llama * (1 + 0.25 * Math.sin(f * 1.7));
	return (
		<svg width={tam} height={tam * 1.6} viewBox="0 0 200 320" style={{position: 'absolute', left: x - tam / 2, top: y - tam * 0.6, overflow: 'visible'}}>
			{l > 0.05 && (
				<>
					<path d={`M 60 170 Q 100 ${170 + 160 * l} 140 170 Z`} fill="#ff8a2a" stroke={TINTA} strokeWidth={6} />
					<path d={`M 78 170 Q 100 ${170 + 100 * l} 122 170 Z`} fill="#ffe86a" />
				</>
			)}
			<path d="M 100 0 Q 150 50 146 170 L 54 170 Q 50 50 100 0 Z" fill="#e6e6ea" stroke={TINTA} strokeWidth={8} />
			<circle cx={100} cy={80} r={22} fill="#2f6fd1" stroke={TINTA} strokeWidth={6} />
			<path d="M 54 120 L 20 180 L 56 170 Z M 146 120 L 180 180 L 144 170 Z" fill="#c4262e" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
		</svg>
	);
};

/** gráfico de criptomonedas (parodia, sin logos) */
export const GraficoCripto: React.FC<{x: number; y: number; ancho: number; dibuja: number}> = ({x, y, ancho, dibuja}) => {
	const alto = ancho * 0.8;
	const velas = [
		[60, 40, 280, 320],
		[100, 200, 230, 300],
		[140, 210, 180, 240],
		[180, 150, 200, 260],
		[220, 120, 150, 200],
		[260, 130, 180, 230],
		[300, 100, 120, 170],
		[340, 110, 150, 210],
	];
	const n = Math.floor(velas.length * dibuja);
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto, width: ancho, height: alto, background: '#14161e', border: `9px solid ${TINTA}`, borderRadius: 14}}>
			<div style={{position: 'absolute', left: 20, top: 10, fontFamily: CONDENSADA, fontSize: ancho * 0.08, color: '#7af0a0', letterSpacing: 3}}>CRIPTO ↑</div>
			<svg viewBox="0 0 400 340" style={{position: 'absolute', inset: 0}}>
				{velas.slice(0, n).map(([cx, top, a, b], i) => {
					const sube = i % 3 !== 1;
					return (
						<g key={i}>
							<line x1={cx} y1={top} x2={cx} y2={Math.max(a, b) + 20} stroke="#9aa" strokeWidth={3} />
							<rect x={cx - 12} y={Math.min(a, b)} width={24} height={Math.abs(b - a)} fill={sube ? '#3ac46a' : '#e04a4a'} />
						</g>
					);
				})}
			</svg>
		</div>
	);
};

/** trofeo de MÁS VOTADO */
export const Trofeo: React.FC<{x: number; y: number; tam: number; rot?: number}> = ({x, y, tam, rot = 0}) => (
	<div style={{position: 'absolute', left: x - tam / 2, top: y - tam * 1.2, width: tam, height: tam * 1.2, transform: `rotate(${rot}deg)`}}>
		<svg viewBox="0 0 200 240" width={tam} height={tam * 1.2} style={{overflow: 'visible'}}>
			<path d="M 40 20 L 160 20 Q 160 120 100 140 Q 40 120 40 20 Z" fill="#f0c43a" stroke={TINTA} strokeWidth={8} />
			<path d="M 40 40 Q 0 40 10 80 Q 20 110 52 104 M 160 40 Q 200 40 190 80 Q 180 110 148 104" stroke={TINTA} strokeWidth={9} fill="none" />
			<rect x={88} y={138} width={24} height={40} fill="#d9a82a" stroke={TINTA} strokeWidth={6} />
			<rect x={44} y={176} width={112} height={54} rx={6} fill="#5a3a22" stroke={TINTA} strokeWidth={7} />
			<path d="M 70 40 L 74 110" stroke="#fff3c0" strokeWidth={9} strokeLinecap="round" opacity={0.8} />
		</svg>
		<div style={{position: 'absolute', left: tam * 0.22, top: tam * 0.92, width: tam * 0.56, textAlign: 'center', fontFamily: CONDENSADA, fontSize: tam * 0.1, color: '#f0c43a', lineHeight: 1}}>MÁS VOTADO</div>
	</div>
);

/** muñequito (silueta simple) para los «seis de cada diez» */
export const Munequito: React.FC<{x: number; y: number; alto: number; color: string; opacidad?: number}> = ({x, y, alto, color, opacidad = 1}) => (
	<svg width={alto * 0.5} height={alto} viewBox="0 0 100 200" style={{position: 'absolute', left: x - alto * 0.25, top: y - alto, opacity: opacidad, overflow: 'visible'}}>
		<circle cx={50} cy={34} r={28} fill={color} stroke={TINTA} strokeWidth={7} />
		<path d="M 14 196 L 18 100 Q 22 72 50 70 Q 78 72 82 100 L 86 196 Z" fill={color} stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
	</svg>
);

/** urna de votación de madera (serio). `sobres` = cuántos han caído (puede ser fraccional) */
export const Urna: React.FC<{x: number; y: number; ancho: number; lleno?: number; cerrada?: boolean}> = ({x, y, ancho, lleno = 0, cerrada = false}) => {
	const k = ancho / 500;
	const alto = 460 * k;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto, width: ancho, height: alto}}>
			<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(90deg, #5a3a22, #7a5230 50%, #4a3020)', border: `${9 * k}px solid ${TINTA}`, borderRadius: 8 * k, overflow: 'hidden'}}>
				<div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: `${Math.min(1, lleno) * 92}%`, background: 'repeating-linear-gradient(170deg, #efe6cf 0 26px, #d9cfb4 26px 30px)', opacity: 0.0}} />
				<div style={{position: 'absolute', left: 40 * k, right: 40 * k, top: 120 * k, padding: `${12 * k}px 0`, background: '#efe6cf', border: `${5 * k}px solid ${TINTA}`, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 52 * k, color: '#2a2218', letterSpacing: 4 * k}}>URNA</div>
			</div>
			<div style={{position: 'absolute', left: -20 * k, right: -20 * k, top: -36 * k, height: 44 * k, background: '#6a4428', border: `${8 * k}px solid ${TINTA}`, borderRadius: 6 * k}}>
				{!cerrada && <div style={{position: 'absolute', left: '30%', right: '30%', top: 10 * k, height: 12 * k, background: '#0a0a0c', borderRadius: 4 * k}} />}
				{cerrada && <div style={{position: 'absolute', left: '44%', top: -10 * k, width: 50 * k, height: 60 * k, borderRadius: 10 * k, background: '#c9a43a', border: `${6 * k}px solid ${TINTA}`}} />}
			</div>
		</div>
	);
};

/** sobres que caen en la urna (serio): uno cada `cada` cuadros */
export const SobresCayendo: React.FC<{x: number; y: number; desde: number; cada?: number; n?: number}> = ({x, y, desde, cada = 6, n = 30}) => {
	const f = useCurrentFrame();
	return (
		<>
			{Array.from({length: n}, (_, i) => {
				const t0 = desde + i * cada;
				const t = f - t0;
				if (t < 0 || t > 22) return null;
				const yy = interpolate(t, [0, 22], [y - 520, y], clamp);
				const r = Math.sin(i * 1.7) * 14 * (1 - t / 22);
				return <div key={i} style={{position: 'absolute', left: x - 70 + Math.sin(i) * 20, top: yy, width: 140, height: 90, background: '#efe6cf', border: `6px solid ${TINTA}`, transform: `rotate(${r}deg)`, opacity: interpolate(t, [18, 22], [1, 0], clamp)}}>
					<svg viewBox="0 0 140 90" style={{position: 'absolute', inset: 0}}>
						<path d="M 0 0 L 70 50 L 140 0" stroke={TINTA} strokeWidth={5} fill="none" />
					</svg>
				</div>;
			})}
		</>
	);
};

/* ============================== utilería del capítulo 5 ============================== */

/** sobre con matasellos de 1932 (rótulo del capítulo) */
export const SobreMatasellos: React.FC<{x: number; y: number; ancho: number; rot?: number; matasellos?: number}> = ({x, y, ancho, rot = -3, matasellos = -1e9}) => {
	const f = useCurrentFrame();
	const k = ancho / 900;
	const alto = ancho * 0.58;
	const g = f - matasellos;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, transform: `rotate(${rot}deg)`, background: '#efe2bf', border: `${8 * k}px solid ${TINTA}`, boxShadow: `${16 * k}px ${20 * k}px 0 rgba(0,0,0,0.35)`}}>
			<svg viewBox="0 0 900 522" style={{position: 'absolute', inset: 0}}>
				<path d="M 0 0 L 450 260 L 900 0" stroke="#c9b48a" strokeWidth={6} fill="none" />
			</svg>
			<SelloPostal x={760 * k} y={120 * k} ancho={150 * k} rot={4} />
			{g >= 0 && (
				<div style={{position: 'absolute', left: 520 * k, top: 40 * k, width: 230 * k, height: 230 * k, borderRadius: '50%', border: `${8 * k}px solid rgba(30,30,40,0.85)`, transform: `rotate(-14deg) scale(${1 + 0.3 * Math.max(0, 1 - g / 4)})`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: CONDENSADA, color: 'rgba(30,30,40,0.85)', lineHeight: 1}}>
					<div style={{fontSize: 34 * k, letterSpacing: 3 * k}}>BERLIN</div>
					<div style={{fontSize: 74 * k}}>1932</div>
					<div style={{fontSize: 26 * k}}>12-3-32</div>
				</div>
			)}
			{g >= 0 && [0, 1, 2, 3].map((i) => <div key={i} style={{position: 'absolute', left: 740 * k, top: (60 + i * 30) * k, width: 140 * k, height: 6 * k, background: 'rgba(30,30,40,0.7)', borderRadius: 3}} />)}
			<div style={{position: 'absolute', left: 140 * k, top: 290 * k, fontFamily: SERIF, fontStyle: 'italic', fontSize: 50 * k, color: '#2a2218', lineHeight: 1.35}}>
				Sr. Presidente
				<br />
				<b style={{fontStyle: 'normal'}}>Paul von Hindenburg</b>
				<br />
				Berlín
			</div>
		</div>
	);
};

/** medallas colgando del pecho (tintinean) */
export const Medallas: React.FC<{x: number; y: number; tam: number; n?: number}> = ({x, y, tam, n = 5}) => {
	const f = useCurrentFrame();
	return (
		<>
			{Array.from({length: n}, (_, i) => {
				const r = Math.sin(f / 3 + i * 1.3) * 10;
				return (
					<div key={i} style={{position: 'absolute', left: x + i * tam * 0.62, top: y, width: tam * 0.5, height: tam * 1.3, transform: `rotate(${r}deg)`, transformOrigin: '50% 0'}}>
						<div style={{width: '100%', height: tam * 0.55, background: ['#c4262e', '#2f6fd1', '#ffffff', '#2f8a4a', '#e0b23a'][i % 5], border: `${tam * 0.06}px solid ${TINTA}`}} />
						<div style={{width: tam * 0.5, height: tam * 0.5, marginTop: -tam * 0.02, borderRadius: '50%', background: 'radial-gradient(circle at 35% 35%, #ffe8a0, #c9a43a)', border: `${tam * 0.06}px solid ${TINTA}`}} />
					</div>
				);
			})}
		</>
	);
};

/** el bigote de Hindenburg en primer plano, que frunce el ceño solo (`frunce` 0..1) */
export const BigoteVivo: React.FC<{x: number; y: number; ancho: number; frunce: number}> = ({x, y, ancho, frunce}) => {
	const f = useCurrentFrame();
	const g = frunce * (1 + 0.08 * Math.sin(f * 1.4));
	const puntas = 34 * g;
	return (
		<svg width={ancho} height={ancho * 0.36} viewBox="0 0 400 144" style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.18, overflow: 'visible'}}>
			<path
				d={`M 200 ${50 + 8 * g} Q 140 ${32 - 14 * g} 92 ${52} Q 52 ${70 + puntas} 40 ${36 + puntas * 2.2} Q 30 ${84 + puntas} 82 ${94} Q 140 104 200 ${84} Q 260 104 318 ${94} Q 370 ${84 + puntas} 360 ${36 + puntas * 2.2} Q 348 ${70 + puntas} 308 ${52} Q 260 ${32 - 14 * g} 200 ${50 + 8 * g} Z`}
				fill="#e9e9e9"
				stroke={TINTA}
				strokeWidth={7}
				strokeLinejoin="round"
			/>
			<path d="M 120 66 Q 160 60 196 70 M 280 66 Q 240 60 204 70" stroke="#b8b8b8" strokeWidth={5} fill="none" />
			{/* las cejitas del propio bigote */}
			{g > 0.2 && (
				<>
					<path d={`M 120 ${30 - 6 * g} L 170 ${42}`} stroke={TINTA} strokeWidth={9} strokeLinecap="round" opacity={g} />
					<path d={`M 280 ${30 - 6 * g} L 230 ${42}`} stroke={TINTA} strokeWidth={9} strokeLinecap="round" opacity={g} />
				</>
			)}
		</svg>
	);
};

/** sopera y plato con la sopa derramada */
export const Sopa: React.FC<{x: number; y: number; derrama: number}> = ({x, y, derrama}) => (
	<>
		<div style={{position: 'absolute', left: x - 90, top: y - 30, width: 180, height: 40, borderRadius: '50%', background: '#fff', border: `6px solid ${TINTA}`}} />
		{derrama > 0 && (
			<div style={{position: 'absolute', left: x - 40, top: y - 10, width: 80 + 320 * derrama, height: 30 + 40 * derrama, borderRadius: '40% 60% 50% 50%', background: '#e9a03a', border: `5px solid ${TINTA}`, opacity: 0.95}} />
		)}
	</>
);

/** sopera en la mano (bandeja con plato hondo) */
export const BandejaSopa: React.FC<{inclina?: number}> = ({inclina = 0}) => (
	<g transform={`rotate(${180 + inclina * 40} 0 36)`}>
		<ellipse cx={0} cy={0} rx={90} ry={16} fill="#d9d9de" stroke={TINTA} strokeWidth={6} />
		<path d="M -50 -6 Q 0 50 50 -6 Z" fill="#ffffff" stroke={TINTA} strokeWidth={6} />
		<ellipse cx={0} cy={-6} rx={50} ry={10} fill="#e9a03a" stroke={TINTA} strokeWidth={4} />
	</g>
);

/** mapa con los dos Braunau */
export const MapaBraunau: React.FC<{marca: number; equis: number; check: number; puntero: number}> = ({marca, equis, check, puntero}) => {
	const f = useCurrentFrame();
	const A = [620, 470]; // Braunau de Bohemia
	const B = [1260, 640]; // Braunau am Inn (Austria)
	const pun = interpolate(puntero, [0, 1], [-600, 0]);
	return (
		<div style={{...lleno, background: '#c9b98a'}}>
			<svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0}}>
				{Array.from({length: 8}, (_, i) => <line key={i} x1={i * 260} y1={0} x2={i * 260} y2={1080} stroke="#5a4a2a" strokeWidth={2} opacity={0.2} />)}
				<path d="M 200 200 L 900 140 L 1100 260 L 1000 420 L 760 460 L 560 380 L 300 400 Z" fill="#e9dcb4" stroke="#5a4a2a" strokeWidth={8} strokeLinejoin="round" />
				<path d="M 760 460 L 1000 420 L 1200 520 L 1700 500 L 1800 700 L 1400 820 L 900 780 L 700 640 Z" fill="#efe4c4" stroke="#5a4a2a" strokeWidth={8} strokeLinejoin="round" />
				<text x={420} y={300} fontFamily={SERIF} fontStyle="italic" fontSize={56} fill="#5a4a2a">
					Bohemia
				</text>
				<text x={1300} y={760} fontFamily={SERIF} fontStyle="italic" fontSize={56} fill="#5a4a2a">
					Austria
				</text>
				{/* el río Inn */}
				<path d="M 900 800 Q 1100 700 1260 660 Q 1400 620 1600 560" stroke="#6f8fca" strokeWidth={14} fill="none" />
			</svg>
			{[A, B].map(([x, y], i) => (
				<React.Fragment key={i}>
					<div style={{position: 'absolute', left: x - 18, top: y - 18, width: 36, height: 36, borderRadius: '50%', background: '#2a2218', border: '6px solid #efe4c4'}} />
					<div style={{position: 'absolute', left: x + 30, top: y - 40, fontFamily: CONDENSADA, fontSize: 64, color: '#2a2218', letterSpacing: 2}}>BRAUNAU</div>
				</React.Fragment>
			))}
			{marca > 0 && <div style={{position: 'absolute', left: A[0] - 70, top: A[1] - 70, width: 140, height: 140, borderRadius: '50%', border: '10px solid #c4262e', opacity: marca, transform: `scale(${1 + 0.1 * Math.sin(f / 3)})`}} />}
			{equis > 0 && (
				<svg viewBox="-100 -100 200 200" style={{position: 'absolute', left: A[0] - 140, top: A[1] - 140, width: 280, height: 280, transform: `scale(${pop(f, equis)})`, overflow: 'visible'}}>
					<path d="M -70 -70 L 70 70 M 70 -70 L -70 70" stroke="#c4262e" strokeWidth={30} strokeLinecap="round" />
				</svg>
			)}
			{check > 0 && (
				<svg viewBox="-100 -100 200 200" style={{position: 'absolute', left: B[0] - 140, top: B[1] - 160, width: 280, height: 280, transform: `scale(${pop(f, check)})`, overflow: 'visible'}}>
					<path d="M -70 0 L -20 50 L 80 -60" stroke="#2f8a4a" strokeWidth={30} strokeLinecap="round" strokeLinejoin="round" fill="none" />
				</svg>
			)}
			{/* puntero de Hindenburg (guante blanco con bastón) */}
			<div style={{position: 'absolute', left: A[0] + 20 + pun * -0.2, top: A[1] + 10 - pun, width: 30, height: 600, background: '#3a2414', border: `6px solid ${TINTA}`, transform: 'rotate(-25deg)', transformOrigin: '50% 0'}} />
		</div>
	);
};

/** cartel de campaña con una cara */
export const CartelCampana: React.FC<{x: number; y: number; ancho: number; cara: 'hindenburg' | 'hitler'; nombre: string; rot?: number; letraChica?: string; pega?: number}> = ({x, y, ancho, cara, nombre, rot = 0, letraChica, pega = 1}) => {
	const k = ancho / 500;
	const d = cara === 'hindenburg' ? HINDENBURG.cabeza : HITLER_TRAJE.cabeza;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: ancho * 1.4, transform: `rotate(${rot}deg) scaleY(${pega})`, transformOrigin: '50% 0', background: cara === 'hindenburg' ? '#24407a' : '#d9cfb4', border: `${8 * k}px solid ${TINTA}`, boxShadow: `${12 * k}px ${16 * k}px 0 rgba(0,0,0,0.35)`, overflow: 'hidden'}}>
			<Cara d={d} tam={360 * k} cejas={cara === 'hindenburg' ? 'enojado' : 'arrogante'} style={{position: 'absolute', left: 70 * k, top: 40 * k}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 440 * k, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 90 * k, color: cara === 'hindenburg' ? '#f4ecd6' : '#2a2218', letterSpacing: 3 * k}}>{nombre}</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 560 * k, textAlign: 'center', fontFamily: TITULAR, fontWeight: 800, fontSize: 34 * k, color: cara === 'hindenburg' ? '#e0b23a' : '#7a2a24', letterSpacing: 2 * k}}>PRESIDENTE 1932</div>
			{letraChica && <div style={{position: 'absolute', left: 30 * k, right: 30 * k, top: 630 * k, textAlign: 'center', fontFamily: TITULAR, fontWeight: 600, fontSize: 14 * k, color: '#2a2218'}}>{letraChica}</div>}
		</div>
	);
};

/** pasaporte abierto (vacío) */
export const Pasaporte: React.FC<{x: number; y: number; ancho: number; rot?: number; sello?: {texto: string; desde: number; color: string}}> = ({x, y, ancho, rot = 0, sello}) => {
	const f = useCurrentFrame();
	const k = ancho / 600;
	const g = sello ? f - sello.desde : -1;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.36, width: ancho, height: ancho * 0.72, transform: `rotate(${rot}deg)`}}>
			<div style={{position: 'absolute', left: -14 * k, top: -14 * k, right: -14 * k, bottom: -14 * k, background: '#5a1e24', border: `${7 * k}px solid ${TINTA}`, borderRadius: 12 * k}} />
			{[0, 1].map((i) => (
				<div key={i} style={{position: 'absolute', left: i * ancho * 0.5, top: 0, width: ancho * 0.5, height: '100%', background: '#efe6cf', border: `${5 * k}px solid ${TINTA}`, boxSizing: 'border-box', padding: 26 * k}}>
					{i === 0 ? (
						<>
							<div style={{width: 130 * k, height: 160 * k, border: `${5 * k}px dashed #8a7a5a`}} />
							<div style={{fontFamily: CONDENSADA, fontSize: 30 * k, color: '#5a4a2a', marginTop: 14 * k}}>PASAPORTE</div>
						</>
					) : (
						[0, 1, 2, 3, 4].map((j) => <div key={j} style={{height: 6 * k, background: '#cfc4a8', margin: `${30 * k}px 0`, borderRadius: 3}} />)
					)}
				</div>
			))}
			{sello && g >= 0 && (
				<div style={{position: 'absolute', left: ancho * 0.55, top: ancho * 0.22, transform: `rotate(-14deg) scale(${1 + 0.4 * Math.max(0, 1 - g / 4)})`, border: `${8 * k}px solid ${sello.color}`, borderRadius: 12 * k, padding: `${4 * k}px ${16 * k}px`, fontFamily: CONDENSADA, fontSize: 42 * k, color: sello.color, whiteSpace: 'nowrap', mixBlendMode: 'multiply', lineHeight: 1.1, textAlign: 'center'}}>
					{sello.texto}
				</div>
			)}
		</div>
	);
};

/** montaña de papeles (vista de frente) */
export const MontonPapeles: React.FC<{x: number; y: number; ancho: number; alto: number}> = ({x, y, ancho, alto}) => {
	const f = useCurrentFrame();
	return (
		<>
			{Array.from({length: Math.floor(alto / 26)}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: x - ancho / 2 + Math.sin(i * 2.3) * 24, top: y - (i + 1) * 26, width: ancho, height: 30, background: i % 3 ? '#f4efe0' : '#e6dcc0', border: `5px solid ${TINTA}`, transform: `rotate(${Math.sin(i * 1.7) * 4 + (i > alto / 26 - 4 ? Math.sin(f / 5 + i) : 0)}deg)`}} />
			))}
		</>
	);
};

/** bota gigante que baja y aplasta */
export const BotaGigante: React.FC<{x: number; y: number; baja: number}> = ({x, y, baja}) => {
	const yy = interpolate(baja, [0, 1], [-900, 0]);
	return (
		<svg width={900} height={1200} viewBox="0 0 900 1200" style={{position: 'absolute', left: x - 450, top: y - 1200 + yy, overflow: 'visible'}}>
			<rect x={260} y={-200} width={360} height={1000} fill="#3a4558" stroke={TINTA} strokeWidth={12} />
			<path d="M 230 700 L 650 700 L 660 1020 L 860 1060 Q 900 1100 880 1180 L 160 1180 Q 140 1100 200 1040 Z" fill="#141418" stroke={TINTA} strokeWidth={12} strokeLinejoin="round" />
			<path d="M 300 760 L 300 1000" stroke="#3a3a42" strokeWidth={12} />
			<rect x={150} y={1166} width={740} height={30} fill="#2a2a30" stroke={TINTA} strokeWidth={8} />
		</svg>
	);
};

/** papeleta presidencial de 1932 */
export const Papeleta: React.FC<{x: number; y: number; ancho: number}> = ({x, y, ancho}) => {
	const k = ancho / 900;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.5, width: ancho, height: ancho * 0.5, background: '#f4efe0', border: `${8 * k}px solid ${TINTA}`, transform: 'perspective(1200px) rotateX(55deg)', transformOrigin: '50% 100%'}}>
			<div style={{textAlign: 'center', fontFamily: CONDENSADA, fontSize: 60 * k, color: '#2a2218', marginTop: 16 * k}}>PAPELETA · PRESIDENTE 1932</div>
			{['HINDENBURG', 'HITLER'].map((n, i) => (
				<div key={n} style={{display: 'flex', alignItems: 'center', gap: 30 * k, margin: `${30 * k}px ${80 * k}px`, fontFamily: CONDENSADA, fontSize: 70 * k, color: '#2a2218'}}>
					<div style={{width: 70 * k, height: 70 * k, borderRadius: '50%', border: `${7 * k}px solid ${TINTA}`, background: i === 0 ? '#2a2218' : 'transparent'}} />
					{n}
				</div>
			))}
		</div>
	);
};

/** reloj de arena (cortísimo) */
export const RelojArena: React.FC<{x: number; y: number; alto: number; t: number}> = ({x, y, alto, t}) => (
	<svg width={alto * 0.6} height={alto} viewBox="0 0 120 200" style={{position: 'absolute', left: x - alto * 0.3, top: y - alto, overflow: 'visible'}}>
		<rect x={6} y={0} width={108} height={16} rx={4} fill="#7a5230" stroke={TINTA} strokeWidth={6} />
		<rect x={6} y={184} width={108} height={16} rx={4} fill="#7a5230" stroke={TINTA} strokeWidth={6} />
		<path d="M 20 16 Q 20 80 56 100 Q 20 120 20 184 L 100 184 Q 100 120 64 100 Q 100 80 100 16 Z" fill="rgba(220,236,242,0.5)" stroke={TINTA} strokeWidth={6} />
		<path d={`M ${24 + 30 * t} ${30 + 60 * t} L ${96 - 30 * t} ${30 + 60 * t} L 60 96 Z`} fill="#e9c46a" opacity={t < 1 ? 1 : 0} />
		<path d={`M 24 180 L 96 180 L ${96 - 30 * (1 - t)} ${180 - 60 * t} L ${24 + 30 * (1 - t)} ${180 - 60 * t} Z`} fill="#e9c46a" />
		{t > 0 && t < 1 && <line x1={60} y1={100} x2={60} y2={180} stroke="#e9c46a" strokeWidth={4} />}
	</svg>
);

/** hoja de sellos de Hindenburg (en el mundo) */
export const HojaSellos: React.FC<{x: number; y: number; ancho: number; rot?: number}> = ({x, y, ancho, rot = 0}) => {
	const col = 4;
	const fil = 3;
	const w = ancho / col;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: w * 1.22 * fil, transform: `rotate(${rot}deg)`}}>
			{Array.from({length: col * fil}, (_, i) => (
				<SelloPostal key={i} x={(i % col) * w + w / 2} y={Math.floor(i / col) * w * 1.22 + w * 0.61} ancho={w * 0.94} />
			))}
		</div>
	);
};

/**
 * El álbum de filatelia. API para reutilizar en el capítulo 9:
 *   <AlbumSellos x y ancho abre={0..1} despega={0..1} />
 * - abre: 0 = cerrado (tapa encima), 1 = abierto (tapa girada a la izquierda; se ve la página con el sello de Hindenburg).
 * - despega: 0..1 el sello de Hindenburg se levanta de la página (se curva y sale volando hacia arriba a la izquierda)
 *   y debajo aparece el sello con la cara de Hitler.
 * - entra: 0..1 (opcional, para el cap. 5): el sello de Hindenburg baja desde arriba hasta su sitio en la página.
 * - brillo: brillo dorado del sello de Hindenburg.
 * (x, y) es el centro del álbum abierto; ancho = ancho de UNA página.
 */
export const AlbumSellos: React.FC<{x: number; y: number; ancho: number; abre: number; despega?: number; entra?: number; brillo?: number}> = ({x, y, ancho, abre, despega = 0, entra = 1, brillo = 0}) => {
	const k = ancho / 600;
	const alto = ancho * 1.3;
	const sx = ancho * 0.5;
	const sy = alto * 0.42;
	const tapa = interpolate(abre, [0, 1], [0, -178]);
	return (
		<div style={{position: 'absolute', left: x - ancho, top: y - alto / 2, width: ancho * 2, height: alto, perspective: 2400 * k}}>
			{/* página derecha (la de los sellos) */}
			<div style={{position: 'absolute', left: ancho, top: 0, width: ancho, height: alto, background: '#2a3a2e', border: `${9 * k}px solid ${TINTA}`, borderRadius: `0 ${16 * k}px ${16 * k}px 0`, boxSizing: 'border-box', padding: 20 * k}}>
				<div style={{position: 'absolute', inset: 22 * k, background: '#efe6cf', border: `${5 * k}px solid ${TINTA}`}}>
					<div style={{textAlign: 'center', fontFamily: SERIF, fontStyle: 'italic', fontSize: 40 * k, color: '#5a4a2a', marginTop: 20 * k}}>Deutsches Reich</div>
					{/* tiras transparentes de la colección */}
					{[0.42, 0.78].map((v, i) => (
						<div key={i} style={{position: 'absolute', left: 30 * k, right: 30 * k, top: alto * v - 140 * k, height: 40 * k, background: 'rgba(255,255,255,0.35)', borderBottom: `${3 * k}px solid rgba(0,0,0,0.15)`}} />
					))}
					{/* el hueco y el sello de Hitler debajo (aparece al despegar) */}
					{despega > 0 && <SelloPostal x={sx - 22 * k} y={sy - 22 * k} ancho={230 * k} cara="hitler" rot={-2} />}
					{/* el sello de Hindenburg */}
					{despega < 1 && (
						<SelloPostal
							x={sx - 22 * k + despega * -500 * k}
							y={sy - 22 * k - (1 - entra) * 700 * k - despega * 520 * k}
							ancho={230 * k}
							rot={-2 - despega * 40}
							brillo={brillo}
							style={{transform: `rotate(${-2 - despega * 40}deg) perspective(${800 * k}px) rotateX(${despega * 50}deg)`, transformOrigin: '50% 0'}}
						/>
					)}
					{[0, 1, 2].map((i) => (
						<div key={i} style={{position: 'absolute', left: (40 + i * 170) * k, top: alto * 0.78 - 60 * k, width: 120 * k, height: 146 * k, border: `${4 * k}px dashed #b8a888`}} />
					))}
				</div>
			</div>
			{/* página izquierda */}
			<div style={{position: 'absolute', left: 0, top: 0, width: ancho, height: alto, background: '#2a3a2e', border: `${9 * k}px solid ${TINTA}`, borderRadius: `${16 * k}px 0 0 ${16 * k}px`, opacity: abre > 0.5 ? 1 : 0}}>
				<div style={{position: 'absolute', inset: 22 * k, background: '#efe6cf', border: `${5 * k}px solid ${TINTA}`}} />
			</div>
			{/* tapa (gira sobre el lomo) */}
			<div style={{position: 'absolute', left: ancho, top: 0, width: ancho, height: alto, transformOrigin: '0 50%', transform: `rotateY(${tapa}deg)`, backfaceVisibility: 'hidden', background: 'linear-gradient(135deg, #3a5a42, #24382a)', border: `${9 * k}px solid ${TINTA}`, borderRadius: `0 ${16 * k}px ${16 * k}px 0`, display: abre > 0.98 ? 'none' : 'block'}}>
				<div style={{position: 'absolute', left: 60 * k, right: 60 * k, top: 160 * k, padding: `${20 * k}px 0`, border: `${6 * k}px solid #c9a43a`, textAlign: 'center', fontFamily: SERIF, fontWeight: 900, fontSize: 62 * k, color: '#e9c46a', letterSpacing: 4 * k}}>ÁLBUM DE SELLOS</div>
			</div>
			<div style={{position: 'absolute', left: ancho - 10 * k, top: 0, width: 20 * k, height: alto, background: '#1a2a1e', border: `${5 * k}px solid ${TINTA}`}} />
		</div>
	);
};

/** Hindenburg con el sello de su cara, idéntico al adelanto pero hablando (la cita de la frase 139) */
export const HindenburgSelloHabla: React.FC<{habla: boolean; brillo?: number}> = ({habla, brillo = 0}) => (
	<>
		<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #1c2c5a 0%, #2f4f8f 60%, #14203e 100%)'}} />
		{[0, 1, 2, 3].map((i) => (
			<div key={i} style={{position: 'absolute', left: 160 + i * 480, top: 0, width: 110, height: 1080, background: 'linear-gradient(90deg, #c9a43a, #f0d27a 50%, #a8862a)', opacity: 0.32}} />
		))}
		<div style={{position: 'absolute', left: 560, top: 60, width: 800, height: 800, borderRadius: '50%', background: `radial-gradient(circle, rgba(255,226,140,${0.25 + 0.3 * brillo}) 0%, rgba(255,226,140,0) 65%)`}} />
		<Actor x={960} y={1180} alto={1180}>
			<Muneco ropa={HINDENBURG} pose={{...brazo(1, alcanzar(1, 330, 300)), md: 'agarra', ...manosEn([160, 520]), mi: 'puno'}} ojos="normal" cejas="enojado" boca="seria" hablando={habla} />
		</Actor>
		<SelloPostal x={1290} y={360} ancho={210} rot={8} brillo={brillo} />
	</>
);

/** un close-up de cara (para la cremallera y los gestos) */
export const CaraGrande: React.FC<{x: number; y: number; tam: number; ropa?: Ropa; ojos?: Ojos; cejas?: Cejas; boca?: Boca}> = ({x, y, tam, ropa = HITLER_TRAJE, ojos = 'normal', cejas = 'neutral', boca = 'seria'}) => (
	<svg width={tam} height={tam} viewBox="0 0 400 400" style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, overflow: 'visible'}}>
		<CabezaSVG d={ropa.cabeza} ojos={ojos} cejas={cejas} boca={boca} />
	</svg>
);

/** cremallera que se cierra sobre la boca (coordenadas del close-up de CaraGrande: boca en (200, 282)) */
export const Cremallera: React.FC<{x: number; y: number; tam: number; cierra: number}> = ({x, y, tam, cierra}) => {
	const k = tam / 400;
	const x0 = x + (150 - 200) * k;
	const largo = 100 * k;
	const pos = x0 + largo * cierra;
	return (
		<>
			<div style={{position: 'absolute', left: x0 - 6 * k, top: y + (282 - 200) * k - 10 * k, width: largo + 12 * k, height: 20 * k, background: '#c9c9cf', border: `${3 * k}px solid ${TINTA}`, borderRadius: 4 * k}} />
			{Array.from({length: 10}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: x0 + i * 10 * k, top: y + (282 - 200) * k - (i % 2 ? 12 : 2) * k, width: 6 * k, height: 12 * k, background: '#8a8a92', opacity: x0 + i * 10 * k < pos ? 1 : 0.35}} />
			))}
			<div style={{position: 'absolute', left: pos - 10 * k, top: y + (282 - 200) * k - 16 * k, width: 20 * k, height: 32 * k, background: '#e0b23a', border: `${3 * k}px solid ${TINTA}`, borderRadius: 4 * k}}>
				<div style={{position: 'absolute', left: 4 * k, top: 26 * k, width: 8 * k, height: 22 * k, background: '#e0b23a', border: `${3 * k}px solid ${TINTA}`, borderRadius: 3 * k}} />
			</div>
		</>
	);
};

export {Humo, pop, tramo};

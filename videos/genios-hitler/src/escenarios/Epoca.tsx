import React from 'react';
import {useCurrentFrame} from 'remotion';
import {CONDENSADA, SERIF, TITULAR} from '../fuentes';

/* Escenarios del video largo (1920 x 1080), dibujados con luz de cine: capas, conos de luz, humo y viñeta.
   El suelo de las escenas de pie está en y ≈ 940. */

const TINTA = '#14141a';
const lleno: React.CSSProperties = {position: 'absolute', inset: 0};

/** humo que se desplaza despacio (capas de elipses difusas) */
export const Humo: React.FC<{color?: string; densidad?: number; y?: number; alto?: number}> = ({color = '255,236,200', densidad = 0.18, y = 0, alto = 1080}) => {
	const f = useCurrentFrame();
	return (
		<div style={{position: 'absolute', left: 0, top: y, width: 1920, height: alto, overflow: 'hidden', pointerEvents: 'none'}}>
			{Array.from({length: 7}, (_, i) => {
				const vx = ((f * (0.6 + (i % 3) * 0.25) + i * 420) % 2600) - 340;
				const vy = alto * (0.12 + ((i * 37) % 70) / 100);
				return (
					<div
						key={i}
						style={{
							position: 'absolute',
							left: vx - 420,
							top: vy - 160 + Math.sin(f / 40 + i) * 30,
							width: 840,
							height: 320,
							borderRadius: '50%',
							background: `radial-gradient(ellipse at center, rgba(${color},${densidad}) 0%, rgba(${color},0) 70%)`,
							filter: 'blur(18px)',
						}}
					/>
				);
			})}
		</div>
	);
};

/** cono de luz cálida (lámpara, foco) */
export const ConoLuz: React.FC<{x: number; y: number; ancho: number; alto: number; color?: string; fuerza?: number}> = ({x, y, ancho, alto, color = '255,214,150', fuerza = 0.35}) => (
	<div
		style={{
			position: 'absolute',
			left: x - ancho / 2,
			top: y,
			width: ancho,
			height: alto,
			background: `linear-gradient(180deg, rgba(${color},${fuerza}) 0%, rgba(${color},${fuerza * 0.4}) 55%, rgba(${color},0) 100%)`,
			clipPath: 'polygon(42% 0, 58% 0, 100% 100%, 0 100%)',
			filter: 'blur(6px)',
			mixBlendMode: 'screen',
		}}
	/>
);

/** nieve que cae (detrás de una ventana) */
export const Nieve: React.FC<{ancho: number; alto: number; n?: number}> = ({ancho, alto, n = 60}) => {
	const f = useCurrentFrame();
	return (
		<>
			{Array.from({length: n}, (_, i) => {
				const vel = 1.2 + (i % 5) * 0.35;
				const y = ((f * vel + i * 97) % (alto + 40)) - 20;
				const x = (i * 131) % ancho + Math.sin(f / 18 + i) * 12;
				const r = 3 + (i % 4) * 1.6;
				return <div key={i} style={{position: 'absolute', left: x, top: y, width: r * 2, height: r * 2, borderRadius: '50%', background: 'rgba(240,246,255,0.85)'}} />;
			})}
		</>
	);
};

/* ======================= oficina de Berlín, enero de 1933 ======================= */

export const VENTANA_OFICINA = {x: 150, y: 110, w: 520, h: 600};
export const ESCRITORIO = {x: 700, y: 700, w: 1120};

export const EscOficinaBerlin: React.FC<{lampara?: number; nieve?: boolean}> = ({lampara = 1, nieve = true}) => {
	const V = VENTANA_OFICINA;
	return (
		<div style={{...lleno, background: 'linear-gradient(180deg, #3b4654 0%, #2e3742 70%, #232a33 100%)'}}>
			{/* paneles de madera de la pared */}
			{[0, 1, 2, 3, 4].map((i) => (
				<div key={i} style={{position: 'absolute', left: 760 + i * 236, top: 120, width: 200, height: 520, border: '6px solid rgba(20,24,30,0.55)', borderRadius: 6, background: 'linear-gradient(180deg, rgba(255,255,255,0.03), rgba(0,0,0,0.12))'}} />
			))}
			<div style={{position: 'absolute', left: 0, right: 0, top: 640, height: 22, background: '#1e242c'}} />
			{/* ventana con nieve */}
			<div style={{position: 'absolute', left: V.x - 40, top: V.y - 40, width: V.w + 80, height: V.h + 80, background: '#5b3a2a', border: `8px solid ${TINTA}`, borderRadius: 8}} />
			<div style={{position: 'absolute', left: V.x, top: V.y, width: V.w, height: V.h, overflow: 'hidden', background: 'linear-gradient(180deg, #1c2a44 0%, #3b5378 60%, #7f95b5 100%)', border: `6px solid ${TINTA}`}}>
				{/* tejados de Berlín */}
				<div style={{position: 'absolute', left: -20, bottom: 0, width: V.w + 40, height: 220, background: '#22304a', clipPath: 'polygon(0 40%, 12% 40%, 12% 10%, 22% 10%, 22% 35%, 38% 35%, 44% 0, 50% 35%, 66% 35%, 66% 18%, 80% 18%, 80% 45%, 100% 45%, 100% 100%, 0 100%)'}} />
				<div style={{position: 'absolute', left: 0, bottom: 0, width: V.w, height: 60, background: '#e6edf5'}} />
				{nieve && <Nieve ancho={V.w} alto={V.h} />}
				<div style={{position: 'absolute', left: V.w / 2 - 6, top: 0, width: 12, height: V.h, background: '#5b3a2a', borderLeft: `4px solid ${TINTA}`, borderRight: `4px solid ${TINTA}`}} />
				<div style={{position: 'absolute', top: V.h * 0.45, left: 0, width: V.w, height: 12, background: '#5b3a2a', borderTop: `4px solid ${TINTA}`, borderBottom: `4px solid ${TINTA}`}} />
			</div>
			{/* cortinas */}
			<div style={{position: 'absolute', left: V.x - 110, top: V.y - 70, width: 150, height: V.h + 260, background: 'linear-gradient(90deg, #5a1e24, #7a2a30 40%, #4a161c)', border: `7px solid ${TINTA}`, borderRadius: '10px 10px 30px 30px'}} />
			<div style={{position: 'absolute', left: V.x + V.w - 40, top: V.y - 70, width: 150, height: V.h + 260, background: 'linear-gradient(90deg, #4a161c, #7a2a30 60%, #5a1e24)', border: `7px solid ${TINTA}`, borderRadius: '10px 10px 30px 30px'}} />
			{/* retrato de paisaje (sin personas reales) */}
			<div style={{position: 'absolute', left: 1240, top: 190, width: 300, height: 220, background: '#c9a43a', border: `7px solid ${TINTA}`, padding: 16, boxSizing: 'border-box'}}>
				<div style={{width: '100%', height: '100%', background: 'linear-gradient(180deg, #8fa6b8 0%, #b9c4a0 60%, #6a7a4a 100%)', border: `4px solid ${TINTA}`}} />
			</div>
			{/* suelo y alfombra */}
			<div style={{position: 'absolute', left: 0, right: 0, top: 662, bottom: 0, background: 'linear-gradient(180deg, #3a2a22 0%, #2a1e18 100%)'}} />
			<div style={{position: 'absolute', left: 260, right: 120, top: 860, bottom: -40, background: '#5a2028', border: `6px solid ${TINTA}`, borderRadius: 14, transform: 'perspective(900px) rotateX(48deg)', transformOrigin: '50% 0'}} />
			{/* el calor de la lámpara */}
			<div style={{position: 'absolute', left: 1300, top: 280, width: 900, height: 700, borderRadius: '50%', background: `radial-gradient(ellipse at center, rgba(255,196,110,${0.42 * lampara}) 0%, rgba(255,170,80,0) 65%)`, mixBlendMode: 'screen'}} />
		</div>
	);
};

/** el escritorio de la oficina, en primer plano (va DELANTE de los personajes) */
export const EscritorioBerlin: React.FC<{lampara?: number; children?: React.ReactNode}> = ({lampara = 1, children}) => {
	const E = ESCRITORIO;
	return (
		<>
			<div style={{position: 'absolute', left: E.x, top: E.y, width: E.w, height: 50, background: '#6a3e26', border: `8px solid ${TINTA}`, borderRadius: 8, boxShadow: 'inset 0 -10px 0 rgba(0,0,0,0.2)'}} />
			<div style={{position: 'absolute', left: E.x + 30, top: E.y + 50, width: E.w - 60, height: 400, background: 'linear-gradient(180deg, #4e2c1a, #3a2014)', border: `8px solid ${TINTA}`, borderTop: 'none'}}>
				{[0, 1].map((i) => (
					<div key={i} style={{position: 'absolute', left: 60 + i * 560, top: 40, width: 420, height: 220, border: `6px solid ${TINTA}`, borderRadius: 6, opacity: 0.7}}>
						<div style={{position: 'absolute', left: '44%', top: 40, width: '12%', height: 14, background: '#c9a43a', borderRadius: 6, border: `3px solid ${TINTA}`}} />
					</div>
				))}
			</div>
			{/* lámpara de banquero */}
			<div style={{position: 'absolute', left: E.x + E.w - 250, top: E.y - 170, width: 200, height: 170}}>
				<div style={{position: 'absolute', left: 90, top: 60, width: 20, height: 100, background: '#c9a43a', border: `5px solid ${TINTA}`}} />
				<div style={{position: 'absolute', left: 40, top: 150, width: 120, height: 24, background: '#c9a43a', border: `5px solid ${TINTA}`, borderRadius: 8}} />
				<div style={{position: 'absolute', left: 0, top: 10, width: 200, height: 70, background: '#2f6b4a', border: `6px solid ${TINTA}`, borderRadius: '100px 100px 14px 14px'}} />
				<div style={{position: 'absolute', left: 30, top: 74, width: 140, height: 16, background: `rgba(255,226,160,${0.6 + 0.4 * lampara})`, borderRadius: 8, boxShadow: `0 0 ${50 * lampara}px rgba(255,210,130,${lampara})`}} />
			</div>
			{children}
		</>
	);
};

/** un rincón de la oficina (zócalo, dos paredes y un agujero de ratón) */
export const EscRincon: React.FC<{tono?: 'oficina' | 'oscuro'}> = ({tono = 'oficina'}) => {
	const pared = tono === 'oficina' ? ['#3b4654', '#323b47'] : ['#1e2228', '#16191e'];
	return (
		<div style={{...lleno, background: pared[1]}}>
			<div style={{position: 'absolute', left: 0, top: 0, width: 980, height: 1080, background: `linear-gradient(90deg, ${pared[0]}, ${pared[1]})`, clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)'}} />
			<div style={{position: 'absolute', left: 960, top: 0, width: 12, height: 1080, background: 'rgba(0,0,0,0.35)'}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 860, height: 70, background: '#2a1e18', borderTop: `7px solid ${TINTA}`, borderBottom: `7px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 930, bottom: 0, background: 'linear-gradient(180deg, #3a2a22, #22180f)'}} />
			{/* agujero de ratón */}
			<div style={{position: 'absolute', left: 1180, top: 790, width: 120, height: 140, background: '#0a0a0c', borderRadius: '60px 60px 0 0', border: `7px solid ${TINTA}`, borderBottom: 'none'}} />
		</div>
	);
};

/* ======================= cervecería de Múnich ======================= */

export const EscCerveceria: React.FC<{tono?: 'sepia' | 'ambar' | 'noche'; humo?: number; pancarta?: string; vacia?: boolean}> = ({tono = 'sepia', humo = 0.16, pancarta, vacia = false}) => {
	const t = {
		sepia: {pared: ['#6b5236', '#4a3824'], arco: '#3a2a1a', luz: '255,214,150', suelo: ['#4a3624', '#2e2014']},
		ambar: {pared: ['#7a4a1e', '#4a2a10'], arco: '#2e1a0a', luz: '255,190,90', suelo: ['#4a2c14', '#24140a']},
		noche: {pared: ['#3a2a1e', '#22180f'], arco: '#160e08', luz: '255,170,80', suelo: ['#2a1c10', '#120a04']},
	}[tono];
	return (
		<div style={{...lleno, background: `linear-gradient(180deg, ${t.pared[0]} 0%, ${t.pared[1]} 75%)`}}>
			{/* bóvedas */}
			{[0, 1, 2, 3].map((i) => (
				<div key={i} style={{position: 'absolute', left: -120 + i * 560, top: -260, width: 620, height: 900, borderRadius: '50%', border: `26px solid ${t.arco}`, borderBottomColor: 'transparent', opacity: 0.85}} />
			))}
			{/* barriles al fondo */}
			{[0, 1, 2, 3, 4, 5].map((i) => (
				<div key={i} style={{position: 'absolute', left: 120 + i * 300 + (i % 2) * 40, top: 520 + (i % 2) * 30, width: 190, height: 150, background: 'linear-gradient(90deg, #5a3a1e, #7a5230 50%, #5a3a1e)', border: `7px solid ${TINTA}`, borderRadius: '40px / 75px', opacity: 0.9}}>
					<div style={{position: 'absolute', left: 40, top: -7, width: 7, height: 150, background: TINTA, opacity: 0.6}} />
					<div style={{position: 'absolute', right: 40, top: -7, width: 7, height: 150, background: TINTA, opacity: 0.6}} />
				</div>
			))}
			{/* lámparas colgantes */}
			{[360, 960, 1560].map((x, i) => (
				<React.Fragment key={i}>
					<div style={{position: 'absolute', left: x - 3, top: 0, width: 6, height: 190, background: TINTA}} />
					<div style={{position: 'absolute', left: x - 70, top: 180, width: 140, height: 56, background: '#2a2014', border: `6px solid ${TINTA}`, borderRadius: '70px 70px 8px 8px'}} />
					<div style={{position: 'absolute', left: x - 420, top: 150, width: 840, height: 840, borderRadius: '50%', background: `radial-gradient(circle at 50% 18%, rgba(${t.luz},0.42) 0%, rgba(${t.luz},0) 55%)`, mixBlendMode: 'screen'}} />
				</React.Fragment>
			))}
			{pancarta && (
				<div style={{position: 'absolute', left: 560, top: 290, width: 800, padding: '18px 0', background: '#efe6cf', border: `7px solid ${TINTA}`, transform: 'rotate(-3.5deg)', textAlign: 'center', fontFamily: "'Comic Sans MS', 'Bradley Hand', cursive", fontWeight: 700, fontSize: 64, color: '#2a2218', boxShadow: '10px 12px 0 rgba(0,0,0,0.3)'}}>
					{pancarta}
				</div>
			)}
			{/* suelo de tablones */}
			<div style={{position: 'absolute', left: 0, right: 0, top: 700, bottom: 0, background: `linear-gradient(180deg, ${t.suelo[0]}, ${t.suelo[1]})`}}>
				{Array.from({length: 9}, (_, i) => (
					<div key={i} style={{position: 'absolute', left: 0, right: 0, top: 30 + i * i * 6, height: 3, background: 'rgba(0,0,0,0.3)'}} />
				))}
			</div>
			{!vacia && <MesaLarga x={960} y={930} ancho={1500} />}
			{humo > 0 && <Humo densidad={humo} color={t.luz} />}
		</div>
	);
};

export const MesaLarga: React.FC<{x: number; y: number; ancho: number; jarras?: number}> = ({x, y, ancho, jarras = 5}) => (
	<>
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - 40, width: ancho, height: 46, background: '#7a5230', border: `8px solid ${TINTA}`, borderRadius: 8}} />
		<div style={{position: 'absolute', left: x - ancho / 2 + 60, top: y, width: 30, height: 160, background: '#5a3a1e', border: `6px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: x + ancho / 2 - 90, top: y, width: 30, height: 160, background: '#5a3a1e', border: `6px solid ${TINTA}`}} />
		{Array.from({length: jarras}, (_, i) => (
			<Jarra key={i} x={x - ancho / 2 + 140 + i * ((ancho - 280) / Math.max(1, jarras - 1))} y={y - 40} alto={110} />
		))}
	</>
);

/** jarra de cerveza pequeña (utilería) */
export const Jarra: React.FC<{x: number; y: number; alto: number; tiembla?: number; espuma?: number}> = ({x, y, alto, tiembla = 0, espuma = 1}) => {
	const f = useCurrentFrame();
	const dx = tiembla * Math.sin(f * 2.7 + x);
	return (
		<svg width={alto * 0.9} height={alto} viewBox="0 0 90 100" style={{position: 'absolute', left: x - alto * 0.38 + dx, top: y - alto, overflow: 'visible'}}>
			<path d="M 64 30 Q 88 30 86 52 Q 84 72 62 72" stroke={TINTA} strokeWidth={9} fill="none" />
			<rect x={10} y={22} width={56} height={74} rx={6} fill="#e8a528" stroke={TINTA} strokeWidth={6} />
			<path d={`M 6 ${26} Q 14 ${8 - 6 * espuma} 30 ${16} Q 40 ${4 - 8 * espuma} 52 ${14} Q 66 ${6 - 6 * espuma} 70 ${26} Z`} fill="#fbf6ea" stroke={TINTA} strokeWidth={5} />
			<line x1={22} y1={40} x2={22} y2={84} stroke="rgba(255,255,255,0.5)" strokeWidth={5} strokeLinecap="round" />
		</svg>
	);
};

/* ======================= mesa vista desde arriba (expediente, papeles) ======================= */

export const EscMesaArriba: React.FC<{tono?: 'madera' | 'oscura' | 'gris'; luz?: [number, number]}> = ({tono = 'madera', luz = [960, 480]}) => {
	const c = {madera: ['#6a3e26', '#4a2a18'], oscura: ['#2a1c14', '#140c08'], gris: ['#4a4a4e', '#2a2a2e']}[tono];
	return (
		<div style={{...lleno, background: c[1]}}>
			{Array.from({length: 12}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: 0, right: 0, top: i * 92, height: 92, background: i % 2 ? c[0] : c[1], opacity: 0.55, borderBottom: '3px solid rgba(0,0,0,0.25)'}} />
			))}
			{Array.from({length: 18}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: (i * 263) % 1920, top: (i * 151) % 1080, width: 220, height: 4, borderRadius: 3, background: 'rgba(0,0,0,0.18)', transform: `rotate(${(i % 5) - 2}deg)`}} />
			))}
			<div style={{position: 'absolute', left: luz[0] - 900, top: luz[1] - 700, width: 1800, height: 1400, borderRadius: '50%', background: 'radial-gradient(ellipse at center, rgba(255,214,150,0.38) 0%, rgba(255,200,120,0) 60%)', mixBlendMode: 'screen'}} />
		</div>
	);
};

/* ======================= fondo liso con foco (insertos) ======================= */

export const EscLiso: React.FC<{color?: string; foco?: boolean; luz?: string}> = ({color = '#1d2028', foco = true, luz = '255,220,170'}) => (
	<div style={{...lleno, background: color}}>
		{foco && <div style={{position: 'absolute', left: 260, top: -200, width: 1400, height: 1400, borderRadius: '50%', background: `radial-gradient(circle at center, rgba(${luz},0.26) 0%, rgba(${luz},0) 62%)`}} />}
	</div>
);

/* ======================= el hemiciclo ======================= */

/** Hemiciclo de ~490 asientos: `encendidos` se iluminan de izquierda a derecha (o los que digas). */
export const Hemiciclo: React.FC<{x: number; y: number; radio: number; encendidos: number; total?: number; color?: string; apagado?: string; oscuro?: number}> = ({x, y, radio, encendidos, total = 491, color = '#c97a3a', apagado = '#3a3a44', oscuro = 0}) => {
	const filas = 9;
	const asientos: [number, number][] = [];
	for (let fi = 0; fi < filas; fi++) {
		const r = radio * (0.42 + (fi / (filas - 1)) * 0.58);
		const n = Math.round(total * (r / radio) / ((filas * (0.42 + 1)) / 2));
		for (let k = 0; k < n; k++) {
			const a = Math.PI * (k / Math.max(1, n - 1));
			asientos.push([a, r]);
		}
	}
	asientos.sort((p, q) => p[0] - q[0] || p[1] - q[1]);
	const tam = radio * 0.035;
	return (
		<svg width={radio * 2 + 80} height={radio + 80} viewBox={`${-radio - 40} ${-radio - 40} ${radio * 2 + 80} ${radio + 80}`} style={{position: 'absolute', left: x - radio - 40, top: y - radio - 40, overflow: 'visible'}}>
			<path d={`M ${-radio - 30} 10 A ${radio + 30} ${radio + 30} 0 0 1 ${radio + 30} 10 Z`} fill={`rgba(20,20,26,${0.4 + oscuro * 0.4})`} />
			{asientos.map(([a, r], i) => {
				const on = i < encendidos;
				return <circle key={i} cx={-Math.cos(a) * r} cy={-Math.sin(a) * r} r={tam} fill={on ? color : apagado} stroke={TINTA} strokeWidth={tam * 0.3} style={on ? {filter: `drop-shadow(0 0 ${tam}px ${color})`} : undefined} />;
			})}
			<rect x={-radio * 0.16} y={-radio * 0.2} width={radio * 0.32} height={radio * 0.16} fill="#5a3a22" stroke={TINTA} strokeWidth={tam * 0.4} />
		</svg>
	);
};

/* ======================= mapa de época ======================= */

/** Mapa de pergamino del Atlántico Norte: América a la izquierda y Europa a la derecha (formas estilizadas). */
export const EscMapa: React.FC<{tono?: 'pergamino' | 'oscuro'; marcas?: boolean}> = ({tono = 'pergamino', marcas = true}) => {
	const mar = tono === 'pergamino' ? '#c9b98a' : '#14181e';
	const tierra = tono === 'pergamino' ? '#e9dcb4' : '#2a2e36';
	const linea = tono === 'pergamino' ? '#5a4a2a' : '#4a505c';
	return (
		<div style={{position: 'absolute', left: 0, top: 0, width: 3840, height: 1080, background: mar}}>
			<svg width={3840} height={1080} viewBox="0 0 3840 1080" style={{position: 'absolute', left: 0, top: 0}}>
				{marcas &&
					Array.from({length: 14}, (_, i) => <line key={i} x1={i * 300} y1={0} x2={i * 300} y2={1080} stroke={linea} strokeWidth={2} opacity={0.25} />)}
				{marcas && Array.from({length: 5}, (_, i) => <line key={i} x1={0} y1={i * 240 + 60} x2={3840} y2={i * 240 + 60} stroke={linea} strokeWidth={2} opacity={0.25} />)}
				{/* Norteamérica (costa este) */}
				<path d="M -40 120 L 260 80 L 420 160 L 520 300 L 600 360 L 560 460 L 470 520 L 440 640 L 380 760 L 300 900 L 200 1000 L -40 1080 Z" fill={tierra} stroke={linea} strokeWidth={8} strokeLinejoin="round" />
				{/* Europa */}
				<path d="M 3840 60 L 3200 40 L 2960 120 L 2840 220 L 2900 300 L 2780 380 L 2700 470 L 2760 560 L 2660 640 L 2600 760 L 2700 860 L 2860 820 L 3000 900 L 3120 860 L 3260 960 L 3400 900 L 3600 980 L 3840 960 Z" fill={tierra} stroke={linea} strokeWidth={8} strokeLinejoin="round" />
				{/* Islas británicas */}
				<path d="M 2560 220 L 2640 180 L 2680 260 L 2650 360 L 2590 420 L 2540 360 L 2570 300 Z" fill={tierra} stroke={linea} strokeWidth={7} strokeLinejoin="round" />
				{/* rosa de los vientos */}
				{marcas && (
					<g transform="translate(1700 760)" opacity={0.55}>
						<circle r={90} fill="none" stroke={linea} strokeWidth={4} />
						<path d="M 0 -120 L 18 0 L 0 120 L -18 0 Z M -120 0 L 0 18 L 120 0 L 0 -18 Z" fill={linea} />
					</g>
				)}
			</svg>
		</div>
	);
};
/** Alemania y Austria en el mapa (coordenadas del EscMapa ancho: 3840) */
export const PUNTOS_MAPA = {berlin: [3170, 360] as [number, number], munich: [3110, 560] as [number, number], austria: [3260, 640] as [number, number], nuevaYork: [420, 420] as [number, number]};

/* ======================= tribunal (Múnich 1924 / Núremberg 1946) ======================= */

export const EscTribunal: React.FC<{tono?: 'munich' | 'nuremberg'}> = ({tono = 'munich'}) => {
	const c = tono === 'munich' ? ['#6b4a2b', '#4a3220', '#2e1e12'] : ['#5a3a22', '#3a2414', '#1e140a'];
	return (
		<div style={{...lleno, background: `linear-gradient(180deg, ${c[0]}, ${c[2]})`}}>
			{Array.from({length: 8}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: 30 + i * 240, top: 60, width: 200, height: 560, border: '6px solid rgba(0,0,0,0.35)', borderRadius: 8, background: 'linear-gradient(180deg, rgba(255,255,255,0.05), rgba(0,0,0,0.15))'}} />
			))}
			{/* estrado del juez */}
			<div style={{position: 'absolute', left: 560, top: 470, width: 800, height: 300, background: `linear-gradient(180deg, ${c[1]}, ${c[2]})`, border: `9px solid ${TINTA}`, borderRadius: 8}}>
				{[0, 1, 2].map((i) => (
					<div key={i} style={{position: 'absolute', left: 50 + i * 250, top: 50, width: 200, height: 200, border: `6px solid ${TINTA}`, opacity: 0.5, borderRadius: 6}} />
				))}
			</div>
			<div style={{position: 'absolute', left: 540, top: 450, width: 840, height: 40, background: c[0], border: `9px solid ${TINTA}`, borderRadius: 8}} />
			{/* suelo */}
			<div style={{position: 'absolute', left: 0, right: 0, top: 770, bottom: 0, background: `linear-gradient(180deg, ${c[2]}, #0e0804)`}} />
			{/* baranda */}
			<div style={{position: 'absolute', left: 0, right: 0, top: 860, height: 22, background: c[0], border: `7px solid ${TINTA}`}} />
			{Array.from({length: 22}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: 20 + i * 90, top: 880, width: 22, height: 200, background: c[1], border: `5px solid ${TINTA}`}} />
			))}
			<div style={{position: 'absolute', left: 360, top: -100, width: 1200, height: 1100, borderRadius: '50%', background: 'radial-gradient(ellipse at 50% 30%, rgba(255,220,160,0.3) 0%, rgba(255,220,160,0) 60%)', mixBlendMode: 'screen'}} />
		</div>
	);
};

/* ======================= letreros y rótulos de época ======================= */

/** Pizarra (menú de cervecería): rótulo del capítulo escrito con tiza */
export const Pizarra: React.FC<{x: number; y: number; ancho: number; lineas: string[]; titulo?: string; rot?: number}> = ({x, y, ancho, lineas, titulo, rot = -2}) => {
	const k = ancho / 700;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, padding: `${30 * k}px ${40 * k}px`, background: '#26302a', border: `${18 * k}px solid #6a4a2a`, outline: `${6 * k}px solid ${TINTA}`, transform: `rotate(${rot}deg)`, color: '#f2f0e6', textAlign: 'center', boxShadow: `${14 * k}px ${18 * k}px 0 rgba(0,0,0,0.35)`}}>
			{titulo && <div style={{fontFamily: SERIF, fontStyle: 'italic', fontSize: 44 * k, opacity: 0.85}}>{titulo}</div>}
			{lineas.map((l, i) => (
				<div key={i} style={{fontFamily: i === 0 ? CONDENSADA : TITULAR, fontWeight: 700, fontSize: (i === 0 ? 96 : 40) * k, letterSpacing: 3 * k, lineHeight: 1.15, opacity: 0.95}}>
					{l}
				</div>
			))}
		</div>
	);
};

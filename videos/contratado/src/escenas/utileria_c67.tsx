import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Ropa} from '../componentes/Muneco';
import {CabezaSVG} from '../componentes/Personaje';
import {GolpeSello} from '../componentes/Recurrentes';
import {HITLER_TRAJE} from '../componentes/Vestuario';
import {Humo} from '../escenarios/Epoca';
import {CONDENSADA, SERIF, TITULAR} from '../fuentes';
import {TINTA, clamp} from './base';

/* Utilería y escenarios de los capítulos 6 (Acabado) y 7 (Los genios). */

const lleno: React.CSSProperties = {position: 'absolute', inset: 0};

/** posición en el mundo de un punto del lienzo (400 x 900) de un Actor */
export const aMundo = (ax: number, ay: number, alto: number, cx: number, cy: number, voltear = false): [number, number] => {
	const k = alto / 900;
	const ancho = 400 * k;
	const suela = (alto * 880) / 900;
	const lx = voltear ? 400 - cx : cx;
	return [ax - ancho / 2 + lx * k, ay - suela + cy * k];
};

/* ---------------- vestuario propio ---------------- */

/** Hitler viejito con boina (el futuro imaginado del profesor) */
export const HITLER_VIEJO: Ropa = {
	...HITLER_TRAJE,
	cabeza: {...HITLER_TRAJE.cabeza, colorPelo: '#d9d9d9', colorBigote: '#e6e6e6', gorra: 'boina', colorGorra: '#3a3a44'},
	casaca: '#6b6258',
	casacaSombra: '#524a42',
	chaleco: '#c9bfa8',
	corbata: undefined,
};

/** el profesor británico: tweed, lentes, calvo */
export const PROFESOR: Ropa = {
	cabeza: {piel: '#ffffff', chaqueta: '', chaquetaSombra: '', botones: '', pelo: 'calvo', colorPelo: '#9a8a7a', lentes: true, bigote: 'manubrio', colorBigote: '#8a7a6a'},
	casaca: '#8a6a4a',
	casacaSombra: '#6a4e34',
	chaleco: '#c9b48a',
	botones: '#3a2a1a',
	pantalon: '#5a4a3a',
	zapatos: '#2a1d14',
	corbata: '#2a5a3a',
	punos: '#8a6a4a',
};

/** empleado del partido que se va con su caja */
export const EMPLEADO: Ropa = {
	cabeza: {piel: '#ffffff', chaqueta: '', chaquetaSombra: '', botones: '', pelo: 'raya', colorPelo: '#4a3a2a'},
	casaca: '#5a5a60',
	casacaSombra: '#44444a',
	chaleco: '#d9d4c8',
	pantalon: '#4a4a50',
	zapatos: '#1a1a1e',
	corbata: '#3a3a40',
};

/* ---------------- periódico ---------------- */

export const Periodico: React.FC<{x: number; y: number; ancho: number; rot?: number; fecha: string; titular: string; sub?: string; foto?: React.ReactNode; gris?: boolean}> = ({x, y, ancho, rot = 0, fecha, titular, sub, foto, gris = false}) => {
	const k = ancho / 800;
	const alto = ancho * 1.25;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, transform: `rotate(${rot}deg)`, background: gris ? '#dcd8cc' : '#efe8d4', border: `${7 * k}px solid ${TINTA}`, boxShadow: `${16 * k}px ${20 * k}px 0 rgba(0,0,0,0.35)`, padding: `${26 * k}px ${34 * k}px`, boxSizing: 'border-box', color: '#1e1a14', overflow: 'hidden'}}>
			<div style={{fontFamily: SERIF, fontWeight: 900, fontSize: 84 * k, textAlign: 'center', lineHeight: 1, letterSpacing: 1 * k}}>Diario de Berlín</div>
			<div style={{display: 'flex', justifyContent: 'space-between', borderTop: `${4 * k}px solid #1e1a14`, borderBottom: `${4 * k}px solid #1e1a14`, margin: `${12 * k}px 0 ${18 * k}px`, padding: `${4 * k}px 0`, fontFamily: TITULAR, fontWeight: 700, fontSize: 24 * k}}>
				<span>{fecha}</span>
				<span>EDICIÓN DE LA MAÑANA</span>
			</div>
			<div style={{fontFamily: CONDENSADA, fontSize: 104 * k, lineHeight: 0.98, textAlign: 'center', letterSpacing: 1 * k}}>{titular}</div>
			{sub && <div style={{fontFamily: SERIF, fontStyle: 'italic', fontSize: 38 * k, textAlign: 'center', marginTop: 12 * k}}>{sub}</div>}
			<div style={{display: 'flex', gap: 24 * k, marginTop: 20 * k}}>
				<div style={{flex: 1}}>
					{Array.from({length: 9}, (_, i) => (
						<div key={i} style={{height: 9 * k, background: 'rgba(30,26,20,0.35)', margin: `${13 * k}px 0`, width: `${[96, 88, 94, 70, 92, 84, 96, 60, 90][i]}%`}} />
					))}
				</div>
				<div style={{flex: 1, height: 300 * k, background: gris ? '#9a968c' : '#b9ae94', border: `${5 * k}px solid ${TINTA}`, position: 'relative', overflow: 'hidden'}}>{foto}</div>
			</div>
		</div>
	);
};

/* ---------------- alcancía, polilla, facturas, cajas ---------------- */

export const Alcancia: React.FC<{x: number; y: number; tam: number; polilla?: number}> = ({x, y, tam, polilla = 1e9}) => {
	const f = useCurrentFrame();
	const t = f - polilla;
	return (
		<>
			<svg width={tam * 1.4} height={tam} viewBox="0 0 280 200" style={{position: 'absolute', left: x - tam * 0.7, top: y - tam, overflow: 'visible'}}>
				<ellipse cx={140} cy={110} rx={110} ry={74} fill="#d99aa8" stroke={TINTA} strokeWidth={9} />
				<ellipse cx={248} cy={108} rx={26} ry={30} fill="#e6b0bc" stroke={TINTA} strokeWidth={8} />
				<circle cx={240} cy={102} r={5} fill={TINTA} />
				<circle cx={256} cy={102} r={5} fill={TINTA} />
				<path d="M 70 52 L 60 18 L 96 42 Z" fill="#d99aa8" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
				<circle cx={196} cy={84} r={7} fill={TINTA} />
				<rect x={110} y={34} width={60} height={12} rx={6} fill={TINTA} />
				{[70, 120, 170, 210].map((lx) => (
					<rect key={lx} x={lx - 12} y={166} width={24} height={34} rx={6} fill="#c98a98" stroke={TINTA} strokeWidth={7} />
				))}
				<path d="M 30 100 Q 6 92 14 70" stroke={TINTA} strokeWidth={7} fill="none" strokeLinecap="round" />
			</svg>
			{t >= 0 && <Polilla x={x + Math.sin(t / 5) * 60 + t * 2.2} y={y - tam * 0.83 - t * 6} tam={tam * 0.35} />}
		</>
	);
};

export const Polilla: React.FC<{x: number; y: number; tam: number}> = ({x, y, tam}) => {
	const f = useCurrentFrame();
	const ala = 0.5 + 0.5 * Math.abs(Math.sin(f * 1.3));
	return (
		<svg width={tam} height={tam} viewBox="-50 -50 100 100" style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, overflow: 'visible'}}>
			<ellipse cx={-22} cy={0} rx={26 * ala} ry={20} fill="#b8ad98" stroke={TINTA} strokeWidth={5} transform="rotate(-20)" />
			<ellipse cx={22} cy={0} rx={26 * ala} ry={20} fill="#b8ad98" stroke={TINTA} strokeWidth={5} transform="rotate(20)" />
			<ellipse cx={0} cy={4} rx={8} ry={20} fill="#6a5e4a" stroke={TINTA} strokeWidth={5} />
			<path d="M -4 -14 Q -12 -30 -20 -34 M 4 -14 Q 12 -30 20 -34" stroke={TINTA} strokeWidth={4} fill="none" />
		</svg>
	);
};

export const Factura: React.FC<{x: number; y: number; ancho: number; rot?: number; sello?: number; concepto?: string}> = ({x, y, ancho, rot = 0, sello = 1e9, concepto = 'Alquiler del local'}) => {
	const k = ancho / 420;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, transform: `rotate(${rot}deg)`, background: '#f2ecdc', border: `${6 * k}px solid ${TINTA}`, padding: `${20 * k}px ${24 * k}px ${30 * k}px`, boxShadow: `${10 * k}px ${12 * k}px 0 rgba(0,0,0,0.3)`, fontFamily: TITULAR, color: '#2a2218', boxSizing: 'border-box'}}>
			<div style={{fontFamily: CONDENSADA, fontSize: 52 * k, letterSpacing: 3 * k}}>FACTURA</div>
			<div style={{fontSize: 22 * k, fontWeight: 600, margin: `${8 * k}px 0 ${12 * k}px`}}>{concepto}</div>
			{[0, 1, 2].map((i) => (
				<div key={i} style={{height: 7 * k, background: '#cfc4a8', margin: `${12 * k}px 0`, width: `${[90, 70, 80][i]}%`}} />
			))}
			<div style={{display: 'flex', justifyContent: 'space-between', fontWeight: 800, fontSize: 26 * k, borderTop: `${3 * k}px solid #2a2218`, paddingTop: 8 * k}}>
				<span>TOTAL</span>
				<span>RM ···</span>
			</div>
			<GolpeSello x={ancho / 2} y={ancho * 0.45} desde={sello} texto="IMPAGO" tam={64 * k} rot={-16} />
		</div>
	);
};

/** caja de mudanza en el pecho de un muñeco (va en `delante`, coordenadas del lienzo) */
export const CajaPecho: React.FC = () => (
	<g>
		<rect x={110} y={390} width={180} height={150} rx={6} fill="#c99a5a" stroke={TINTA} strokeWidth={8} />
		<line x1={110} y1={430} x2={290} y2={430} stroke={TINTA} strokeWidth={6} />
		<rect x={140} y={350} width={60} height={50} fill="#f2ecdc" stroke={TINTA} strokeWidth={6} transform="rotate(-8 170 375)" />
		<rect x={210} y={340} width={14} height={70} fill="#2f6b4a" stroke={TINTA} strokeWidth={5} transform="rotate(12 217 375)" />
	</g>
);

/* ---------------- página de diario (serio) ---------------- */

export const PaginaDiario: React.FC<{x: number; y: number; ancho: number; rot?: number; escribe?: number}> = ({x, y, ancho, rot = -2, escribe = 1}) => {
	const k = ancho / 1000;
	const lineas = 11;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.36, width: ancho, height: ancho * 0.72, transform: `rotate(${rot}deg)`}}>
			<div style={{position: 'absolute', inset: `${-18 * k}px`, background: '#2a2420', borderRadius: 14 * k, border: `${6 * k}px solid ${TINTA}`}} />
			{[0, 1].map((p) => (
				<div key={p} style={{position: 'absolute', left: p * ancho * 0.5, top: 0, width: ancho * 0.5, height: '100%', background: p ? 'linear-gradient(90deg, #cfc6b0, #e6dfcc 12%)' : 'linear-gradient(270deg, #cfc6b0, #e6dfcc 12%)', border: `${4 * k}px solid ${TINTA}`, boxSizing: 'border-box'}}>
					<svg width="100%" height="100%" viewBox="0 0 500 720" preserveAspectRatio="none" style={{position: 'absolute', inset: 0}}>
						{p === 0 && (
							<text x={40} y={70} fontFamily={SERIF} fontStyle="italic" fontSize={34} fill="#3a3024">
								8 de diciembre de 1932
							</text>
						)}
						{Array.from({length: lineas}, (_, i) => {
							const idx = p * lineas + i;
							const vis = interpolate(escribe * lineas * 2 - idx, [0, 1], [0, 1], clamp);
							const y0 = 120 + i * 54;
							const w = 380 - ((idx * 37) % 120);
							let d = `M 40 ${y0}`;
							for (let s = 0; s < 14; s++) d += ` q ${w / 28} ${s % 2 ? -14 : 12} ${w / 14} ${(s * 7) % 5 - 2}`;
							return <path key={i} d={d} stroke="#3a3024" strokeWidth={3.5} fill="none" opacity={0.8} strokeDasharray={w * 1.6} strokeDashoffset={w * 1.6 * (1 - vis)} />;
						})}
					</svg>
				</div>
			))}
		</div>
	);
};

/* ---------------- la postal sepia del futuro imaginado ---------------- */

export const Perro: React.FC<{x: number; y: number; tam: number; bosteza?: number}> = ({x, y, tam, bosteza = 0}) => (
	<svg width={tam * 1.6} height={tam} viewBox="0 0 320 200" style={{position: 'absolute', left: x - tam * 0.8, top: y - tam, overflow: 'visible'}}>
		<path d="M 290 120 Q 320 100 312 80" stroke={TINTA} strokeWidth={9} fill="none" strokeLinecap="round" />
		<ellipse cx={180} cy={140} rx={120} ry={44} fill="#9a6a3a" stroke={TINTA} strokeWidth={8} />
		{[90, 130, 230, 270].map((lx) => (
			<rect key={lx} x={lx - 10} y={160} width={20} height={36} rx={8} fill="#8a5a2e" stroke={TINTA} strokeWidth={6} />
		))}
		<ellipse cx={74} cy={100} rx={58} ry={46} fill="#a87444" stroke={TINTA} strokeWidth={8} />
		<path d="M 50 70 Q 30 130 64 150 Q 80 120 74 76 Z" fill="#7a4a24" stroke={TINTA} strokeWidth={7} />
		<ellipse cx={20} cy={112 + bosteza * 6} rx={34} ry={16 + bosteza * 14} fill="#a87444" stroke={TINTA} strokeWidth={7} />
		{bosteza > 0.2 && <ellipse cx={14} cy={118 + bosteza * 6} rx={18} ry={bosteza * 12} fill="#7a1a24" />}
		<circle cx={0} cy={104} r={8} fill={TINTA} />
		{bosteza > 0.5 ? <path d="M 76 88 Q 86 82 96 88" stroke={TINTA} strokeWidth={5} fill="none" /> : <circle cx={86} cy={88} r={6} fill={TINTA} />}
	</svg>
);

/** marco de postal antigua: el contenido va en sepia */
export const Postal: React.FC<{x: number; y: number; ancho: number; rot?: number; children?: React.ReactNode}> = ({x, y, ancho, rot = 0, children}) => {
	const alto = ancho * 0.66;
	const k = ancho / 1400;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, transform: `rotate(${rot}deg)`, background: '#efe4c8', border: `${8 * k}px solid ${TINTA}`, boxShadow: `${20 * k}px ${24 * k}px 0 rgba(0,0,0,0.35)`, padding: 40 * k, boxSizing: 'border-box'}}>
			<div style={{position: 'relative', width: '100%', height: '88%', overflow: 'hidden', border: `${6 * k}px solid ${TINTA}`, filter: 'sepia(0.85) contrast(0.95) brightness(1.02)'}}>
				<div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transform: `scale(${(ancho - 80 * k - 12 * k) / 1920})`, transformOrigin: '0 0'}}>{children}</div>
			</div>
			<div style={{fontFamily: SERIF, fontStyle: 'italic', fontSize: 52 * k, color: '#5a4a2a', textAlign: 'center', marginTop: 8 * k}}>Recuerdo de Baviera · 19??</div>
		</div>
	);
};

/** jardín de cerveza al aire libre (dentro de la postal) */
export const EscJardinCerveza: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #a8c4d8 0%, #d8e4d0 55%, #8aa86a 56%, #6a8a4a 100%)'}}>
		{[200, 640, 1300, 1720].map((x, i) => (
			<React.Fragment key={i}>
				<div style={{position: 'absolute', left: x - 18, top: 260, width: 36, height: 360, background: '#6a4a2a', border: `6px solid ${TINTA}`}} />
				<div style={{position: 'absolute', left: x - 170, top: 80, width: 340, height: 260, borderRadius: '50%', background: '#5a7a3a', border: `7px solid ${TINTA}`}} />
			</React.Fragment>
		))}
		{/* guirnalda de bombillas */}
		<svg width={1920} height={300} style={{position: 'absolute', left: 0, top: 220}}>
			<path d="M 0 40 Q 480 140 960 40 Q 1440 140 1920 40" stroke={TINTA} strokeWidth={4} fill="none" />
			{Array.from({length: 16}, (_, i) => {
				const t = i / 15;
				const xx = t * 1920;
				const yy = 40 + 100 * Math.sin(((t * 2) % 1) * Math.PI);
				return <circle key={i} cx={xx} cy={yy + 10} r={10} fill="#fff4c0" stroke={TINTA} strokeWidth={3} />;
			})}
		</svg>
	</div>
);

/* ---------------- archivador «CASOS CERRADOS» ---------------- */

export const Archivador: React.FC<{x: number; y: number; ancho: number; abre: number}> = ({x, y, ancho, abre}) => {
	const k = ancho / 600;
	const alto = 900 * k;
	const cajon = 260 * k;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto, width: ancho, height: alto}}>
			<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(90deg, #5a5e62, #6e7378 50%, #4e5256)', border: `${9 * k}px solid ${TINTA}`, borderRadius: 8 * k}} />
			{[0, 1, 2].map((i) => (
				<div key={i} style={{position: 'absolute', left: 40 * k, right: 40 * k, top: (40 + i * 285) * k, height: 240 * k, background: '#62676c', border: `${7 * k}px solid ${TINTA}`, borderRadius: 6 * k}}>
					<div style={{position: 'absolute', left: '30%', right: '30%', top: 40 * k, height: 50 * k, background: '#efe8d4', border: `${5 * k}px solid ${TINTA}`, fontFamily: CONDENSADA, fontSize: 30 * k, textAlign: 'center', lineHeight: `${40 * k}px`, color: '#2a2218'}}>
						{i === 0 ? 'CASOS CERRADOS' : i === 1 ? 'ARCHIVO' : 'VARIOS'}
					</div>
					<div style={{position: 'absolute', left: '40%', right: '40%', top: 130 * k, height: 26 * k, background: '#c9c9c9', border: `${5 * k}px solid ${TINTA}`, borderRadius: 13 * k}} />
				</div>
			))}
			{/* el cajón de arriba, abierto hacia la cámara */}
			{abre > 0.01 && (
				<div style={{position: 'absolute', left: (40 - 30 * abre) * k, right: (40 - 30 * abre) * k, top: (40 + 240) * k, height: cajon * abre, background: 'linear-gradient(180deg, #3a3e42, #55595e)', border: `${7 * k}px solid ${TINTA}`, borderTop: 'none'}}>
					{[0, 1, 2, 3, 4].map((i) => (
						<div key={i} style={{position: 'absolute', left: `${8 + i * 18}%`, top: 6 * k, width: '14%', height: 30 * k * abre, background: '#d9ab58', border: `${4 * k}px solid ${TINTA}`, borderRadius: `${8 * k}px ${8 * k}px 0 0`}} />
					))}
				</div>
			)}
		</div>
	);
};

/* ---------------- el estudio de televisión (concurso) ---------------- */

export const EscEstudioTV: React.FC<{luces?: number}> = ({luces = 1}) => {
	const f = useCurrentFrame();
	return (
		<div style={{...lleno, background: 'linear-gradient(180deg, #1a0e22 0%, #2a1630 60%, #120a14 100%)'}}>
			{/* telón */}
			{[0, 1].map((l) => (
				<div key={l} style={{position: 'absolute', left: l ? 1560 : -40, top: 0, width: 400, height: 1080, background: 'repeating-linear-gradient(90deg, #8a1a24 0 50px, #6a1018 50px 100px)', borderRight: l ? undefined : `9px solid ${TINTA}`, borderLeft: l ? `9px solid ${TINTA}` : undefined}} />
			))}
			{/* arco de bombillas */}
			<svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
				<path d="M 420 1000 L 420 340 Q 960 -40 1500 340 L 1500 1000" stroke="#c9a43a" strokeWidth={34} fill="none" />
				<path d="M 420 1000 L 420 340 Q 960 -40 1500 340 L 1500 1000" stroke={TINTA} strokeWidth={6} fill="none" />
				{Array.from({length: 34}, (_, i) => {
					const t = i / 33;
					let px: number;
					let py: number;
					if (t < 0.25) {
						px = 420;
						py = 1000 - (t / 0.25) * 660;
					} else if (t > 0.75) {
						px = 1500;
						py = 340 + ((t - 0.75) / 0.25) * 660;
					} else {
						const u = (t - 0.25) / 0.5;
						px = (1 - u) * (1 - u) * 420 + 2 * (1 - u) * u * 960 + u * u * 1500;
						py = (1 - u) * (1 - u) * 340 + 2 * (1 - u) * u * -40 + u * u * 340;
					}
					const on = luces > 0.5 && (Math.floor(f / 4) + i) % 3 !== 0;
					return <circle key={i} cx={px} cy={py} r={13} fill={on ? '#fff3b0' : '#6a5a3a'} stroke={TINTA} strokeWidth={3} style={on ? {filter: 'drop-shadow(0 0 8px #ffd84a)'} : undefined} />;
				})}
			</svg>
			{/* cartel */}
			<div style={{position: 'absolute', left: 660, top: 18, width: 600, padding: '6px 0', background: '#1b1b22', border: `8px solid #c9a43a`, outline: `5px solid ${TINTA}`, textAlign: 'center', color: '#ffd84a', fontFamily: CONDENSADA, fontSize: 54, letterSpacing: 4, lineHeight: 1.1}}>
				ESTA NOCHE
				<div style={{fontSize: 40, color: '#f4f1e8'}}>FRANZ VON PAPEN</div>
			</div>
			{/* suelo brillante */}
			<div style={{position: 'absolute', left: 0, right: 0, top: 900, bottom: 0, background: 'linear-gradient(180deg, #3a2a40, #160c18)'}} />
			<div style={{position: 'absolute', left: 560, top: 880, width: 800, height: 120, borderRadius: '50%', background: 'radial-gradient(ellipse, rgba(255,240,200,0.45), rgba(255,240,200,0) 70%)'}} />
			{/* foco */}
			<div style={{position: 'absolute', left: 560, top: -40, width: 800, height: 1000, background: `linear-gradient(180deg, rgba(255,244,210,${0.28 * luces}), rgba(255,244,210,0))`, clipPath: 'polygon(40% 0, 60% 0, 100% 100%, 0 100%)', filter: 'blur(8px)', mixBlendMode: 'screen'}} />
		</div>
	);
};

/** caballo con pajarita (de perfil, mirando a la izquierda) */
export const Caballo: React.FC<{x: number; y: number; tam: number}> = ({x, y, tam}) => {
	const f = useCurrentFrame();
	const cola = Math.sin(f / 6) * 8;
	return (
		<svg width={tam * 1.3} height={tam} viewBox="0 0 520 400" style={{position: 'absolute', left: x - tam * 0.65, top: y - tam, overflow: 'visible'}}>
			<path d={`M 440 170 Q ${500 + cola} 220 ${480 + cola} 320`} stroke="#3a2414" strokeWidth={30} fill="none" strokeLinecap="round" />
			<ellipse cx={330} cy={200} rx={140} ry={76} fill="#8a5a32" stroke={TINTA} strokeWidth={9} />
			{[230, 280, 380, 430].map((lx) => (
				<rect key={lx} x={lx - 14} y={250} width={28} height={140} rx={10} fill="#7a4e2a" stroke={TINTA} strokeWidth={8} />
			))}
			<path d="M 230 170 L 170 40 L 220 20 L 290 150 Z" fill="#8a5a32" stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
			<path d="M 175 30 Q 120 30 60 70 Q 30 100 56 120 Q 110 120 180 100 Z" fill="#8a5a32" stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
			<path d="M 200 20 L 260 140" stroke="#3a2414" strokeWidth={22} strokeLinecap="round" />
			<path d="M 190 22 L 204 -8 L 214 24" fill="#8a5a32" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
			<circle cx={146} cy={58} r={9} fill={TINTA} />
			<circle cx={74} cy={98} r={6} fill={TINTA} />
			{/* pajarita */}
			<g transform="translate(232 162) rotate(20)">
				<path d="M 0 0 L -40 -22 L -40 22 Z M 0 0 L 40 -22 L 40 22 Z" fill="#c8202a" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
				<circle r={10} fill="#a8161e" stroke={TINTA} strokeWidth={5} />
			</g>
		</svg>
	);
};

export const Grillo: React.FC<{x: number; y: number; tam: number}> = ({x, y, tam}) => {
	const f = useCurrentFrame();
	const pata = Math.sin(f * 1.7) * 6;
	return (
		<svg width={tam * 1.5} height={tam} viewBox="0 0 150 100" style={{position: 'absolute', left: x - tam * 0.75, top: y - tam, overflow: 'visible'}}>
			<path d={`M 90 60 L 130 ${20 + pata} L 146 80`} stroke={TINTA} strokeWidth={6} fill="none" strokeLinejoin="round" />
			<ellipse cx={70} cy={66} rx={48} ry={20} fill="#3a5a2a" stroke={TINTA} strokeWidth={6} />
			<circle cx={22} cy={58} r={16} fill="#4a6a32" stroke={TINTA} strokeWidth={6} />
			<path d="M 14 46 Q 0 10 -20 0 M 22 44 Q 20 8 6 -6" stroke={TINTA} strokeWidth={4} fill="none" />
			<line x1={50} y1={82} x2={40} y2={100} stroke={TINTA} strokeWidth={5} />
			<line x1={74} y1={84} x2={70} y2={100} stroke={TINTA} strokeWidth={5} />
		</svg>
	);
};

/* ---------------- marcador de estadio ---------------- */

const Digito: React.FC<{n: string; tam: number; encendido?: boolean}> = ({n, tam, encendido = true}) => (
	<span style={{display: 'inline-block', width: tam * 0.62, textAlign: 'center', color: '#ffd84a', opacity: encendido ? 1 : 0, textShadow: `0 0 ${tam * 0.15}px #ffb020`}}>{n}</span>
);

export const Marcador: React.FC<{x: number; y: number; ancho: number; izq: number; der: number; tituloIzq?: string; tituloDer?: string}> = ({x, y, ancho, izq, der, tituloIzq = 'PARLAMENTO', tituloDer = 'PAPEN'}) => {
	const k = ancho / 1200;
	const tam = 230 * k;
	const fmt = (v: number, n: number) => String(Math.round(v)).padStart(n, ' ');
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, background: '#141418', border: `${14 * k}px solid #2a2a32`, outline: `${8 * k}px solid ${TINTA}`, borderRadius: 12 * k, padding: `${24 * k}px ${30 * k}px`, boxSizing: 'border-box', boxShadow: `0 ${24 * k}px 0 rgba(0,0,0,0.4)`}}>
			<div style={{display: 'flex', justifyContent: 'space-between', fontFamily: CONDENSADA, fontSize: 64 * k, color: '#f4f1e8', letterSpacing: 4 * k}}>
				<span>{tituloIzq}</span>
				<span>{tituloDer}</span>
			</div>
			<div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontFamily: "'Liberation Mono', 'DejaVu Sans Mono', monospace", fontWeight: 700, fontSize: tam, lineHeight: 1}}>
				<span>
					{fmt(izq, 3)
						.split('')
						.map((c, i) => (
							<Digito key={i} n={c === ' ' ? '8' : c} tam={tam} encendido={c !== ' '} />
						))}
				</span>
				<span style={{color: '#ffd84a', fontSize: tam * 0.6}}>–</span>
				<span>
					{fmt(der, 3)
						.split('')
						.map((c, i) => (
							<Digito key={i} n={c === ' ' ? '8' : c} tam={tam} encendido={c !== ' '} />
						))}
				</span>
			</div>
		</div>
	);
};

/* ---------------- la vela, el tablero y el peón con bigote ---------------- */

export const Vela: React.FC<{x: number; y: number; alto: number}> = ({x, y, alto}) => {
	const f = useCurrentFrame();
	const t = Math.sin(f / 2.3) * 0.08 + Math.sin(f / 5.1) * 0.06;
	const k = alto / 300;
	return (
		<>
			<div style={{position: 'absolute', left: x - 700, top: y - alto - 600, width: 1400, height: 1400, borderRadius: '50%', background: `radial-gradient(circle, rgba(255,190,90,${0.42 + t}) 0%, rgba(255,160,60,0.12) 35%, rgba(255,160,60,0) 62%)`, mixBlendMode: 'screen', pointerEvents: 'none'}} />
			<svg width={120 * k} height={alto} viewBox="0 0 120 300" style={{position: 'absolute', left: x - 60 * k, top: y - alto, overflow: 'visible'}}>
				<ellipse cx={60} cy={292} rx={56} ry={12} fill="#c9a43a" stroke={TINTA} strokeWidth={6} />
				<rect x={34} y={120} width={52} height={170} rx={6} fill="#efe6cf" stroke={TINTA} strokeWidth={6} />
				<path d="M 40 122 Q 36 150 44 160" stroke="#d9cfb6" strokeWidth={8} fill="none" />
				<line x1={60} y1={120} x2={60} y2={104} stroke={TINTA} strokeWidth={4} />
				<path d={`M 60 ${30 - t * 40} Q ${80 + t * 30} 80 60 106 Q ${40 + t * 30} 80 60 ${30 - t * 40} Z`} fill="#ffd84a" stroke="#ff8a2a" strokeWidth={4} />
				<ellipse cx={60} cy={92} rx={6} ry={10} fill="#fff6d0" />
			</svg>
		</>
	);
};

/** tablero de ajedrez en perspectiva (centro x, borde de delante y) */
export const Tablero: React.FC<{x: number; y: number; ancho: number}> = ({x, y, ancho}) => (
	<div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho, width: ancho, height: ancho, transform: 'perspective(1400px) rotateX(58deg)', transformOrigin: '50% 100%'}}>
		<div style={{position: 'absolute', inset: -ancho * 0.04, background: '#3a2414', border: `8px solid ${TINTA}`}} />
		{Array.from({length: 64}, (_, i) => (
			<div key={i} style={{position: 'absolute', left: (i % 8) * (ancho / 8), top: Math.floor(i / 8) * (ancho / 8), width: ancho / 8, height: ancho / 8, background: (i + Math.floor(i / 8)) % 2 ? '#2a3a2a' : '#d9cfb0'}} />
		))}
	</div>
);

/** peón de ajedrez con bigote de cepillo y raya al lado */
export const PeonBigote: React.FC<{x: number; y: number; alto: number; rot?: number}> = ({x, y, alto, rot = 0}) => (
	<svg width={alto * 0.6} height={alto} viewBox="0 0 120 200" style={{position: 'absolute', left: x - alto * 0.3, top: y - alto, overflow: 'visible', transform: `rotate(${rot}deg)`, transformOrigin: '50% 100%'}}>
		<ellipse cx={60} cy={188} rx={52} ry={12} fill="#1e1e22" stroke={TINTA} strokeWidth={6} />
		<path d="M 14 186 Q 20 150 42 130 L 78 130 Q 100 150 106 186 Z" fill="#2a2a30" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
		<rect x={30} y={112} width={60} height={20} rx={8} fill="#2a2a30" stroke={TINTA} strokeWidth={6} />
		<circle cx={60} cy={72} r={42} fill="#f4f1e8" stroke={TINTA} strokeWidth={6} />
		<path d="M 20 64 Q 26 28 66 28 Q 90 30 100 52 Q 70 40 50 58 Q 34 50 20 64 Z" fill="#1a1410" />
		<rect x={50} y={82} width={20} height={9} rx={2} fill="#1a1410" />
		<circle cx={46} cy={66} r={4.5} fill={TINTA} />
		<circle cx={74} cy={66} r={4.5} fill={TINTA} />
	</svg>
);

/* ---------------- la casa del banquero, de noche ---------------- */

export const EscCasaNoche: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<div style={{...lleno, background: 'linear-gradient(180deg, #070b16 0%, #121a30 60%, #0a0e18 100%)'}}>
			{Array.from({length: 40}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: (i * 211) % 1920, top: (i * 97) % 380, width: 4, height: 4, borderRadius: 2, background: '#e8eefc', opacity: 0.4 + 0.4 * Math.abs(Math.sin(f / 20 + i))}} />
			))}
			<div style={{position: 'absolute', left: 1500, top: 80, width: 120, height: 120, borderRadius: '50%', background: '#e8e4d0', boxShadow: '0 0 80px 20px rgba(232,228,208,0.25)'}} />
			{/* la casa */}
			<div style={{position: 'absolute', left: 360, top: 330, width: 1200, height: 620, background: '#1a2030', border: `9px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 300, top: 160, width: 1320, height: 190, background: '#141826', clipPath: 'polygon(6% 100%, 50% 0, 94% 100%)'}} />
			{[0, 1, 2, 3].map((i) =>
				[0, 1].map((r) => (i === 2 && r === 1 ? null : <div key={`${i}-${r}`} style={{position: 'absolute', left: 450 + i * 270, top: 420 + r * 240, width: 160, height: 180, background: '#0c1018', border: `7px solid ${TINTA}`}} />)),
			)}
			{/* la única ventana encendida, con dos siluetas y la caja fuerte */}
			<div style={{position: 'absolute', left: 990, top: 660, width: 160, height: 180, background: 'linear-gradient(180deg, #ffcf7a, #e89a3a)', border: `7px solid ${TINTA}`, overflow: 'hidden', boxShadow: '0 0 90px 30px rgba(255,190,100,0.35)'}}>
				<div style={{position: 'absolute', left: 52, top: 30, width: 56, height: 60, background: '#6a6e74', border: `4px solid ${TINTA}`, borderRadius: 4}}>
					<div style={{position: 'absolute', left: 16, top: 16, width: 18, height: 18, borderRadius: '50%', border: `3px solid ${TINTA}`}} />
				</div>
				{/* silueta con chistera (izq) y silueta con raya y bigote (der) */}
				<svg width={160} height={180} viewBox="0 0 160 180" style={{position: 'absolute', inset: 0}}>
					<path d="M 10 180 L 14 130 Q 30 112 46 130 L 50 180 Z" fill="#1a1006" />
					<circle cx={30} cy={110} r={20} fill="#1a1006" />
					<rect x={16} y={58} width={28} height={40} fill="#1a1006" />
					<rect x={8} y={94} width={44} height={6} fill="#1a1006" />
					<path d="M 110 180 L 114 132 Q 130 114 146 132 L 150 180 Z" fill="#1a1006" />
					<circle cx={130} cy={112} r={20} fill="#1a1006" />
				</svg>
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 940, bottom: 0, background: '#0a0d14'}} />
		</div>
	);
};

/* ---------------- la mesa de consejo ---------------- */

/** fila de 11 sillas tras la mesa larga; `colores[i]` y `marca` (de 0 a 1: realce de las marrones) */
export const MesaConsejo: React.FC<{y: number; marca?: number; ocupadas?: React.ReactNode}> = ({y, marca = 0, ocupadas}) => {
	const colores = ['#8a8a92', '#8a8a92', '#7a5232', '#8a8a92', '#8a8a92', '#8a8a92', '#8a8a92', '#7a5232', '#8a8a92', '#7a5232', '#8a8a92'];
	return (
		<>
			{colores.map((c, i) => {
				const x = 160 + i * 160;
				const marron = c === '#7a5232';
				const s = marron ? 1 + 0.12 * marca : 1;
				return (
					<div key={i} style={{position: 'absolute', left: x - 60, top: y - 260, width: 120, height: 220, transform: `scale(${s})`, transformOrigin: '50% 100%', filter: marron && marca > 0 ? `drop-shadow(0 0 ${18 * marca}px rgba(255,170,90,0.9))` : marca > 0 ? `brightness(${1 - 0.35 * marca})` : undefined}}>
						<div style={{position: 'absolute', inset: 0, background: c, border: `7px solid ${TINTA}`, borderRadius: '50px 50px 8px 8px'}} />
						<div style={{position: 'absolute', left: 18, right: 18, top: 22, bottom: 30, borderRadius: '40px 40px 6px 6px', background: 'rgba(0,0,0,0.15)'}} />
					</div>
				);
			})}
			{ocupadas}
			<div style={{position: 'absolute', left: 40, right: 40, top: y - 60, height: 60, background: '#3a2414', border: `9px solid ${TINTA}`, borderRadius: 10}} />
			<div style={{position: 'absolute', left: 60, right: 60, top: y - 10, height: 300, background: 'linear-gradient(180deg, #2a5a3a, #1a3a26)', border: `9px solid ${TINTA}`, borderTop: 'none'}} />
		</>
	);
};

/** salón de madera oscura con terciopelo verde y humo de puros (la paleta de «Los genios») */
export const EscSalonGenios: React.FC<{humo?: number}> = ({humo = 0.16}) => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #2a1a10 0%, #1e120a 70%, #140c06 100%)'}}>
		{[0, 1, 2, 3, 4, 5, 6].map((i) => (
			<div key={i} style={{position: 'absolute', left: 20 + i * 280, top: 70, width: 230, height: 560, background: 'linear-gradient(180deg, #24402c, #183020)', border: '8px solid #3a2414', outline: `4px solid ${TINTA}`, borderRadius: 6}} />
		))}
		<div style={{position: 'absolute', left: 0, right: 0, top: 640, height: 26, background: '#3a2414', borderTop: `6px solid ${TINTA}`, borderBottom: `6px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: 0, right: 0, top: 666, bottom: 0, background: 'linear-gradient(180deg, #2a1a10, #120a04)'}} />
		{humo > 0 && <Humo densidad={humo} color="220,214,196" />}
	</div>
);

/* ---------------- urna cerrada y puerta que se cierra sobre el humo ---------------- */

export const UrnaCerrada: React.FC<{x: number; y: number; ancho: number}> = ({x, y, ancho}) => {
	const k = ancho / 500;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - 460 * k, width: ancho, height: 460 * k}}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 60 * k, bottom: 0, background: 'linear-gradient(90deg, #7a5230, #9a6a3e 50%, #6a4426)', border: `${9 * k}px solid ${TINTA}`, borderRadius: 8 * k}} />
			<div style={{position: 'absolute', left: -20 * k, right: -20 * k, top: 30 * k, height: 50 * k, background: '#5a3a22', border: `${9 * k}px solid ${TINTA}`, borderRadius: 8 * k}} />
			<div style={{position: 'absolute', left: 170 * k, right: 170 * k, top: 46 * k, height: 14 * k, background: TINTA, borderRadius: 7 * k}} />
			{/* cinta y candado */}
			<div style={{position: 'absolute', left: 60 * k, right: 60 * k, top: 30 * k, height: 50 * k, background: 'repeating-linear-gradient(45deg, #c8202a 0 22px, #f4ecd6 22px 44px)', border: `${5 * k}px solid ${TINTA}`, opacity: 0.95}} />
			<div style={{position: 'absolute', left: 200 * k, top: 140 * k, width: 100 * k, height: 90 * k, background: '#c9a43a', border: `${8 * k}px solid ${TINTA}`, borderRadius: 12 * k}} />
			<div style={{position: 'absolute', left: 218 * k, top: 80 * k, width: 64 * k, height: 80 * k, border: `${14 * k}px solid #9aa0a8`, borderBottom: 'none', borderRadius: `${40 * k}px ${40 * k}px 0 0`, boxSizing: 'border-box'}} />
			<div style={{position: 'absolute', left: 242 * k, top: 170 * k, width: 16 * k, height: 30 * k, background: TINTA, borderRadius: 8 * k}} />
			<div style={{position: 'absolute', left: 0, right: 0, bottom: 60 * k, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 70 * k, color: '#f4ecd6', letterSpacing: 6 * k, textShadow: `0 ${4 * k}px 0 ${TINTA}`}}>URNA</div>
		</div>
	);
};

/** una puerta que se cierra sobre un cuarto lleno de humo de puros y chisteras; `cierra` 0 → abierta, 1 → cerrada */
export const PuertaPuros: React.FC<{cierra: number}> = ({cierra}) => (
	<>
		<div style={{...lleno, background: '#1e140c'}} />
		{/* el cuarto */}
		<div style={{position: 'absolute', left: 560, top: 120, width: 800, height: 900, background: 'linear-gradient(180deg, #24402c, #3a2414)', overflow: 'hidden', border: `10px solid ${TINTA}`}}>
			<div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 300, background: '#3a2414'}} />
			{[120, 330, 560].map((cx, i) => (
				<svg key={i} width={200} height={420} viewBox="0 0 200 420" style={{position: 'absolute', left: cx - 100, top: 360 + (i % 2) * 30}}>
					<rect x={64} y={0} width={72} height={90} fill="#0e0a06" />
					<rect x={44} y={86} width={112} height={12} fill="#0e0a06" />
					<circle cx={100} cy={140} r={46} fill="#0e0a06" />
					<path d="M 20 420 L 30 220 Q 100 180 170 220 L 180 420 Z" fill="#0e0a06" />
					<rect x={140} y={150} width={40} height={10} fill="#d98a3a" />
					<circle cx={182} cy={155} r={6} fill="#ff6a2a" />
				</svg>
			))}
			<div style={{position: 'absolute', inset: 0}}>
				<Humo densidad={0.42} color="230,222,200" alto={900} />
			</div>
		</div>
		{/* la hoja de la puerta */}
		<div style={{position: 'absolute', left: 560, top: 120, width: 800, height: 900, transformOrigin: '0% 50%', transform: `perspective(1600px) rotateY(${(1 - cierra) * -100}deg)`, background: 'linear-gradient(90deg, #5a3420, #6a4026 50%, #4a2a18)', border: `10px solid ${TINTA}`, boxSizing: 'border-box'}}>
			{[0, 1].map((r) => (
				<div key={r} style={{position: 'absolute', left: 80, right: 80, top: 70 + r * 420, height: 340, border: `8px solid ${TINTA}`, opacity: 0.5, borderRadius: 8}} />
			))}
			<div style={{position: 'absolute', right: 60, top: 440, width: 50, height: 50, borderRadius: '50%', background: '#c9a43a', border: `6px solid ${TINTA}`}} />
		</div>
		<div style={{position: 'absolute', left: 530, top: 90, width: 860, height: 40, background: '#3a2414', border: `8px solid ${TINTA}`}} />
	</>
);

/* ---------------- tarjeta de visita en bandeja de plata ---------------- */

export const BandejaTarjeta: React.FC<{x: number; y: number; ancho: number}> = ({x, y, ancho}) => {
	const k = ancho / 900;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.32, width: ancho, height: ancho * 0.64}}>
			<div style={{position: 'absolute', inset: 0, borderRadius: '50%', background: 'radial-gradient(ellipse at 40% 35%, #f4f6fa 0%, #b9bec8 45%, #7a808c 100%)', border: `${10 * k}px solid ${TINTA}`}} />
			<div style={{position: 'absolute', inset: 40 * k, borderRadius: '50%', border: `${6 * k}px solid rgba(20,20,26,0.45)`}} />
			<div style={{position: 'absolute', left: 220 * k, top: 150 * k, width: 460 * k, height: 270 * k, background: '#fbf8ef', border: `${6 * k}px solid ${TINTA}`, transform: 'rotate(-6deg)', boxShadow: `${10 * k}px ${12 * k}px 0 rgba(0,0,0,0.3)`, textAlign: 'center', color: '#2a2218'}}>
				<div style={{fontFamily: SERIF, fontStyle: 'italic', fontWeight: 700, fontSize: 62 * k, marginTop: 66 * k}}>F. von Papen</div>
				<div style={{height: 3 * k, background: '#2a2218', margin: `${16 * k}px ${80 * k}px`}} />
				<div style={{fontFamily: TITULAR, fontSize: 24 * k, letterSpacing: 4 * k, fontWeight: 600}}>CABALLERO · BERLÍN</div>
			</div>
		</div>
	);
};

/* ---------------- la sombra de Hitler (perfil) ---------------- */

export const SombraHitler: React.FC<{x: number; y: number; alto: number; opacidad?: number}> = ({x, y, alto, opacidad = 0.55}) => (
	<svg width={alto * 0.8} height={alto} viewBox="0 0 320 400" style={{position: 'absolute', left: x - alto * 0.4, top: y - alto, opacity: opacidad, filter: 'blur(3px)', mixBlendMode: 'multiply', overflow: 'visible'}}>
		<path
			d="M 60 400 L 70 300 Q 80 250 130 240 L 150 226 Q 120 210 112 180 L 100 168 Q 96 150 106 142 L 98 120 Q 90 60 150 40 Q 210 20 250 50 Q 280 80 270 130 Q 270 170 250 200 L 240 230 Q 300 250 310 300 L 320 400 Z"
			fill="#0a0806"
		/>
		{/* raya y mechón */}
		<path d="M 98 120 Q 110 70 170 76 L 120 96 Z" fill="#0a0806" />
		{/* bigote */}
		<rect x={92} y={160} width={22} height={14} fill="#0a0806" />
	</svg>
);

/* ---------------- el desayuno del socio arrepentido ---------------- */

export const EscDesayuno: React.FC = () => (
	<div style={{...lleno, background: 'linear-gradient(180deg, #5a4a3a 0%, #4a3a2c 70%, #2e2218 100%)'}}>
		<div style={{position: 'absolute', left: 1240, top: 90, width: 520, height: 560, background: 'linear-gradient(180deg, #e8eef4, #c8d4de)', border: `10px solid ${TINTA}`}}>
			<div style={{position: 'absolute', left: 250, top: 0, width: 12, height: 560, background: '#5b3a2a'}} />
			<div style={{position: 'absolute', top: 270, left: 0, width: 520, height: 12, background: '#5b3a2a'}} />
		</div>
		<div style={{position: 'absolute', left: 900, top: 0, width: 1100, height: 1080, background: 'linear-gradient(240deg, rgba(255,240,210,0.35), rgba(255,240,210,0) 60%)', mixBlendMode: 'screen'}} />
		{/* papel tapiz */}
		{Array.from({length: 7}, (_, i) => (
			<div key={i} style={{position: 'absolute', left: 60 + i * 160, top: 60, width: 6, height: 620, background: 'rgba(255,255,255,0.06)'}} />
		))}
	</div>
);

export const MesaDesayuno: React.FC<{y: number}> = ({y}) => (
	<>
		<div style={{position: 'absolute', left: 120, right: 120, top: y, height: 40, background: '#f2ecdc', border: `8px solid ${TINTA}`, borderRadius: 8}} />
		<div style={{position: 'absolute', left: 140, right: 140, top: y + 40, height: 400, background: 'linear-gradient(180deg, #e6dfcc, #b9ae94)', border: `8px solid ${TINTA}`, borderTop: 'none'}} />
		{/* taza y huevo */}
		<svg width={260} height={160} viewBox="0 0 260 160" style={{position: 'absolute', left: 1180, top: y - 150, overflow: 'visible'}}>
			<ellipse cx={80} cy={150} rx={78} ry={12} fill="#f4f4f0" stroke={TINTA} strokeWidth={6} />
			<path d="M 30 60 L 40 140 Q 80 156 120 140 L 130 60 Z" fill="#f4f4f0" stroke={TINTA} strokeWidth={7} />
			<path d="M 128 76 Q 160 80 152 110 Q 146 130 124 126" stroke={TINTA} strokeWidth={7} fill="none" />
			<path d="M 60 40 Q 70 20 60 4 M 90 40 Q 100 20 90 4" stroke="rgba(255,255,255,0.7)" strokeWidth={6} fill="none" strokeLinecap="round" />
			<path d="M 196 150 L 200 112 Q 220 100 240 112 L 244 150 Z" fill="#c9a43a" stroke={TINTA} strokeWidth={6} />
			<ellipse cx={220} cy={90} rx={24} ry={30} fill="#fbf8ef" stroke={TINTA} strokeWidth={6} />
		</svg>
	</>
);

/** mano con pluma (vista desde arriba): firma; la punta está en (x, y) */
export const ManoPluma: React.FC<{x: number; y: number; tam: number}> = ({x, y, tam}) => (
	<svg width={tam} height={tam} viewBox="0 0 200 200" style={{position: 'absolute', left: x - tam * 0.12, top: y - tam * 0.9, overflow: 'visible'}}>
		{/* manga del uniforme con su puño rojo */}
		<path d="M 150 120 L 250 160 L 250 240 L 120 200 Z" fill="#4f5d72" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
		<path d="M 138 118 L 172 128 L 150 196 L 116 186 Z" fill="#7a2a24" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
		{/* la pluma */}
		<line x1={24} y1={180} x2={130} y2={44} stroke="#1a1a22" strokeWidth={12} strokeLinecap="round" />
		<path d="M 18 186 L 30 168 L 36 176 Z" fill="#c9a43a" stroke={TINTA} strokeWidth={4} />
		{/* el puño que la agarra (visto desde arriba): dorso y cuatro dedos doblados sobre la pluma */}
		<path d="M 96 70 Q 150 50 172 96 Q 186 130 160 158 Q 130 176 104 156 Z" fill="#ffffff" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
		{[0, 1, 2, 3].map((i) => (
			<rect key={i} x={70 + i * 9} y={84 + i * 20} width={44} height={24} rx={12} fill="#ffffff" stroke={TINTA} strokeWidth={6} transform={`rotate(${-38} ${92 + i * 9} ${96 + i * 20})`} />
		))}
		<path d="M 104 66 Q 92 58 82 66 L 72 92" stroke={TINTA} strokeWidth={7} fill="#ffffff" strokeLinecap="round" />
	</svg>
);

/** la cabeza de Hitler sola, para retratos (viewBox de la cabeza) */
export const CaraHitler: React.FC<{tam: number}> = ({tam}) => (
	<svg width={tam} height={tam} viewBox="20 0 360 380" style={{overflow: 'visible'}}>
		<CabezaSVG d={HITLER_TRAJE.cabeza} ojos="normal" cejas="arrogante" boca="seria" />
	</svg>
);

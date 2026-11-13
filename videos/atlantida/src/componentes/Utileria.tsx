import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {SERIF, TITULAR} from '../fuentes';
import {ESPIA_MUERTO, Personaje} from './Personaje';

/* Utilería animada de las escenas: todo en coordenadas del mundo 1080x1920. */

const TINTA = '#1b1b1f';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export const usePop = (desde: number, rigidez = 190, amortiguacion = 9) => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	return spring({frame: f - desde, fps, config: {damping: amortiguacion, stiffness: rigidez, mass: 0.6}});
};

const Caja: React.FC<{x: number; y: number; w: number; h: number; rot?: number; escala?: number; origen?: string; children: React.ReactNode; estilo?: React.CSSProperties}> = ({
	x,
	y,
	w,
	h,
	rot = 0,
	escala = 1,
	origen = '50% 50%',
	children,
	estilo,
}) => (
	<div style={{position: 'absolute', left: x - w / 2, top: y - h / 2, width: w, height: h, transform: `rotate(${rot}deg) scale(${escala})`, transformOrigin: origen, ...estilo}}>{children}</div>
);

/** Globo de diálogo con cola. */
export const Bocadillo: React.FC<{x: number; y: number; texto: string; desde: number; hasta?: number; cola?: 'izq' | 'der'; tam?: number; ancho?: number}> = ({
	x,
	y,
	texto,
	desde,
	hasta = 99999,
	cola = 'izq',
	tam = 70,
	ancho = 420,
}) => {
	const f = useCurrentFrame();
	const p = usePop(desde, 260);
	if (f < desde || f >= hasta) return null;
	const alto = tam * 2.2;
	return (
		<Caja x={x} y={y} w={ancho} h={alto + 60} escala={p} origen={cola === 'izq' ? '15% 100%' : '85% 100%'}>
			<svg viewBox={`0 0 ${ancho} ${alto + 60}`} width="100%" height="100%" style={{overflow: 'visible', position: 'absolute', inset: 0}}>
				<path
					d={cola === 'izq' ? `M 60 ${alto - 6} L 30 ${alto + 54} L 130 ${alto - 6} Z` : `M ${ancho - 60} ${alto - 6} L ${ancho - 30} ${alto + 54} L ${ancho - 130} ${alto - 6} Z`}
					fill="#fff"
					stroke={TINTA}
					strokeWidth={9}
					strokeLinejoin="round"
				/>
				<rect x={5} y={5} width={ancho - 10} height={alto - 10} rx={alto / 2.4} fill="#fff" stroke={TINTA} strokeWidth={9} />
				<path d={cola === 'izq' ? `M 66 ${alto - 12} L 124 ${alto - 12}` : `M ${ancho - 66} ${alto - 12} L ${ancho - 124} ${alto - 12}`} stroke="#fff" strokeWidth={14} />
			</svg>
			<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: alto, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: TITULAR, fontWeight: 900, fontSize: tam, color: TINTA}}>
				{texto}
			</div>
		</Caja>
	);
};

/** Hoja de papel tipo "ALTO SECRETO". */
export const Documento: React.FC<{x: number; y: number; ancho?: number; desde: number; rot?: number; titulo?: string; volando?: boolean}> = ({x, y, ancho = 420, desde, rot = -4, titulo = 'ALTO SECRETO', volando}) => {
	const f = useCurrentFrame();
	const p = usePop(desde, 170, 11);
	if (f < desde) return null;
	const l = f - desde;
	const dx = volando ? Math.sin(l / 6) * 30 : 0;
	const dr = volando ? Math.sin(l / 5) * 12 : Math.sin(l / 14) * 2;
	const alto = ancho * 1.3;
	return (
		<Caja x={x + dx} y={y} w={ancho} h={alto} rot={rot + dr} escala={p}>
			<div style={{position: 'absolute', inset: 0, background: '#fbf6e6', border: `9px solid ${TINTA}`, borderRadius: 12, boxShadow: '0 14px 24px rgba(0,0,0,0.35)', padding: ancho * 0.08, boxSizing: 'border-box'}}>
				<div style={{border: `${ancho * 0.014}px solid #c3342b`, color: '#c3342b', fontFamily: TITULAR, fontWeight: 900, fontSize: ancho * 0.085, textAlign: 'center', padding: '6px 0', letterSpacing: 2, transform: 'rotate(-3deg)'}}>{titulo}</div>
				{Array.from({length: 7}).map((_, i) => (
					<div key={i} style={{height: ancho * 0.03, background: 'rgba(27,27,31,0.55)', borderRadius: 4, marginTop: ancho * 0.06, width: `${[92, 80, 96, 70, 88, 60, 84][i]}%`}} />
				))}
			</div>
		</Caja>
	);
};

/** Sello que golpea la pantalla: "FALSO", "APROBADO", "VERDAD"... */
export const Sello: React.FC<{x: number; y: number; texto: string; desde: number; color?: string; rot?: number; tam?: number; icono?: string}> = ({x, y, texto, desde, color = '#d6262e', rot = -12, tam = 120, icono}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	const l = f - desde;
	const escala = interpolate(l, [0, 4, 7, 10], [2.6, 0.92, 1.05, 1], {...clamp, easing: Easing.out(Easing.quad)});
	const op = interpolate(l, [0, 2], [0, 1], clamp);
	const ancho = texto.length * tam * 0.78 + tam * (icono ? 1.4 : 0.8);
	return (
		<Caja x={x} y={y} w={ancho} h={tam * 1.6} rot={rot} escala={escala} estilo={{opacity: op}}>
			<div
				style={{
					position: 'absolute',
					inset: 0,
					border: `${tam * 0.1}px solid ${color}`,
					borderRadius: tam * 0.22,
					outline: `${tam * 0.04}px solid ${color}`,
					outlineOffset: -tam * 0.2,
					display: 'flex',
					alignItems: 'center',
					justifyContent: 'center',
					gap: tam * 0.2,
					color,
					fontFamily: TITULAR,
					fontWeight: 900,
					fontSize: tam,
					letterSpacing: tam * 0.05,
					background: 'rgba(255,255,255,0.12)',
					mixBlendMode: 'multiply',
				}}
			>
				{icono && <span>{icono}</span>}
				{texto}
			</div>
		</Caja>
	);
};

/** Cabeza del espía para retratos y carnés. */
const CabezaEspia: React.FC<{tam: number; ojos?: 'x' | 'normal'}> = ({tam, ojos = 'x'}) => (
	<div style={{width: tam, height: tam, overflow: 'hidden', position: 'relative'}}>
		<div style={{position: 'absolute', left: -tam * 0.06, top: tam * 0.02, width: tam * 1.12, height: tam * 2.12}}>
			<Personaje diseno={ESPIA_MUERTO} ojos={ojos} cejas="ninguna" boca={ojos === 'x' ? 'lengua' : 'seria'} sombra={false} respira={false} parpadea={false} />
		</div>
	</div>
);

/** Carné de identidad falso del espía. */
export const Carne: React.FC<{x: number; y: number; ancho?: number; desde: number}> = ({x, y, ancho = 760, desde}) => {
	const f = useCurrentFrame();
	const llega = interpolate(f, [desde, desde + 10], [900, 0], {...clamp, easing: Easing.out(Easing.back(1.4))});
	if (f < desde) return null;
	const alto = ancho * 0.62;
	return (
		<Caja x={x} y={y + llega} w={ancho} h={alto} rot={-3}>
			<div style={{position: 'absolute', inset: 0, background: '#e9dcb8', border: `10px solid ${TINTA}`, borderRadius: 26, boxShadow: '0 18px 30px rgba(0,0,0,0.4)', overflow: 'hidden'}}>
				<div style={{background: '#2a4f8a', color: '#fff', fontFamily: TITULAR, fontWeight: 900, fontSize: ancho * 0.05, padding: `${ancho * 0.02}px ${ancho * 0.04}px`, borderBottom: `8px solid ${TINTA}`, letterSpacing: 2}}>
					NAVAL IDENTITY CARD
				</div>
				<div style={{display: 'flex', gap: ancho * 0.04, padding: ancho * 0.04}}>
					<div style={{border: `7px solid ${TINTA}`, background: '#cfd8c8', borderRadius: 8}}>
						<CabezaEspia tam={ancho * 0.3} ojos="normal" />
					</div>
					<div style={{fontFamily: SERIF, fontWeight: 900, color: TINTA, fontSize: ancho * 0.055, lineHeight: 1.35}}>
						<div style={{fontFamily: TITULAR, fontSize: ancho * 0.03, opacity: 0.6}}>NOMBRE</div>
						<div>William Martin</div>
						<div style={{fontFamily: TITULAR, fontSize: ancho * 0.03, opacity: 0.6, marginTop: 8}}>RANGO</div>
						<div>Capitán</div>
						<div style={{fontFamily: TITULAR, fontSize: ancho * 0.03, opacity: 0.6, marginTop: 8}}>CUERPO</div>
						<div>Royal Marines</div>
					</div>
				</div>
			</div>
		</Caja>
	);
};

/** Retrato enmarcado con placa del nombre. */
export const Retrato: React.FC<{x: number; y: number; ancho?: number; desde: number; placaDesde: number}> = ({x, y, ancho = 600, desde, placaDesde}) => {
	const f = useCurrentFrame();
	const p = usePop(desde, 150, 12);
	const placa = usePop(placaDesde, 220);
	if (f < desde) return null;
	const alto = ancho * 1.2;
	return (
		<>
			<Caja x={x} y={y + alto / 2} w={ancho} h={alto} escala={p} rot={Math.sin(f / 12) * 1.5} origen="50% 0%">
				<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(135deg,#d9a441,#8a5a1c)', border: `10px solid ${TINTA}`, borderRadius: 18, padding: ancho * 0.07, boxSizing: 'border-box', boxShadow: '0 22px 36px rgba(0,0,0,0.45)'}}>
					<div style={{width: '100%', height: '100%', background: 'radial-gradient(circle at 50% 35%, #f3e8c9, #b9a57a)', border: `8px solid ${TINTA}`, overflow: 'hidden', display: 'flex', justifyContent: 'center'}}>
						<div style={{width: ancho * 0.8, height: alto * 1.4, marginTop: ancho * 0.08}}>
							<Personaje diseno={ESPIA_MUERTO} ojos="x" cejas="ninguna" boca="lengua" sombra={false} respira={false} parpadea={false} cabeza={-8} />
						</div>
					</div>
				</div>
			</Caja>
			{f >= placaDesde && (
				<Caja x={x} y={y + alto + 70} w={ancho * 1.25} h={150} escala={placa}>
					<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(#f6d77a,#c99a2e)', border: `9px solid ${TINTA}`, borderRadius: 20, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', boxShadow: '0 12px 0 rgba(0,0,0,0.35)'}}>
						<div style={{fontFamily: SERIF, fontWeight: 900, fontSize: 70, color: TINTA, lineHeight: 1}}>William Martin</div>
						<div style={{fontFamily: TITULAR, fontWeight: 900, fontSize: 28, color: TINTA, letterSpacing: 3, marginTop: 6}}>CAPITÁN · ROYAL MARINES</div>
					</div>
				</Caja>
			)}
		</>
	);
};

/** Maletín grande que se abre y escupe papeles. */
export const Maletin: React.FC<{x: number; y: number; ancho?: number; abre: number; papeles?: number; cadena?: boolean}> = ({x, y, ancho = 680, abre, papeles = 6, cadena = true}) => {
	const f = useCurrentFrame();
	const tapa = interpolate(f, [abre, abre + 10], [0, -118], {...clamp, easing: Easing.out(Easing.back(1.6))});
	const alto = ancho * 0.62;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto}}>
			{cadena && (
				<svg viewBox={`0 0 ${ancho} ${alto}`} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
					<path d={`M ${ancho * 0.5} ${-alto * 0.05} Q ${ancho * 0.2} ${-alto * 0.5} ${-ancho * 0.7} ${-alto * 0.3}`} stroke="#8e9399" strokeWidth={14} fill="none" strokeDasharray="22 10" strokeLinecap="round" />
				</svg>
			)}
			{/* papeles que salen volando */}
			{Array.from({length: papeles}).map((_, i) => {
				const ini = abre + 6 + i * 4;
				const l = f - ini;
				if (l < 0) return null;
				const vx = (random(`px${i}`) - 0.5) * 34;
				const vy = -26 - random(`py${i}`) * 14;
				const px = ancho / 2 + vx * l;
				const py = alto * 0.3 + vy * l + 0.9 * l * l;
				const r = (random(`pr${i}`) - 0.5) * 30 * l * 0.3;
				if (py > alto * 3) return null;
				return (
					<div key={i} style={{position: 'absolute', left: px - 90, top: py - 115, width: 180, height: 230, transform: `rotate(${r}deg)`, background: '#fbf6e6', border: `7px solid ${TINTA}`, borderRadius: 8, padding: 12, boxSizing: 'border-box', zIndex: 0}}>
						<div style={{color: '#c3342b', fontFamily: TITULAR, fontWeight: 900, fontSize: 22, border: '4px solid #c3342b', textAlign: 'center'}}>SECRETO</div>
						{[80, 95, 70, 88].map((w, k) => (
							<div key={k} style={{height: 8, width: `${w}%`, background: 'rgba(0,0,0,0.5)', marginTop: 14, borderRadius: 3}} />
						))}
					</div>
				);
			})}
			<svg viewBox="0 0 680 420" width="100%" height="100%" style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
				<path d="M 260 40 Q 260 -10 340 -10 Q 420 -10 420 40" stroke={TINTA} strokeWidth={22} fill="none" />
				<path d="M 260 40 Q 260 -10 340 -10 Q 420 -10 420 40" stroke="#5a3418" strokeWidth={10} fill="none" />
				<rect x={10} y={40} width={660} height={370} rx={34} fill="#7a4522" stroke={TINTA} strokeWidth={12} />
				<rect x={10} y={40} width={660} height={60} rx={20} fill="#8d5329" />
				<g transform={`rotate(${tapa} 10 120)`}>
					<rect x={10} y={40} width={660} height={130} rx={30} fill="#8d5329" stroke={TINTA} strokeWidth={12} />
					<rect x={300} y={140} width={80} height={46} rx={8} fill="#e2b93f" stroke={TINTA} strokeWidth={8} />
				</g>
				<line x1={20} y1={290} x2={660} y2={290} stroke={TINTA} strokeWidth={6} opacity={0.5} />
			</svg>
		</div>
	);
};

/** Lupa que se pasea sobre algo. */
export const Lupa: React.FC<{x: number; y: number; tam?: number; desde: number; radio?: number}> = ({x, y, tam = 300, desde, radio = 60}) => {
	const f = useCurrentFrame();
	const p = usePop(desde, 200);
	if (f < desde) return null;
	const a = (f - desde) / 8;
	return (
		<Caja x={x + Math.cos(a) * radio} y={y + Math.sin(a * 1.3) * radio * 0.6} w={tam} h={tam} escala={p} rot={-30}>
			<svg viewBox="0 0 200 200" width="100%" height="100%" style={{overflow: 'visible'}}>
				<rect x={88} y={130} width={26} height={90} rx={10} fill="#6b3f20" stroke={TINTA} strokeWidth={8} />
				<circle cx={100} cy={80} r={68} fill="rgba(190,230,255,0.35)" stroke={TINTA} strokeWidth={22} />
				<circle cx={100} cy={80} r={68} fill="none" stroke="#c9a43a" strokeWidth={10} />
				<path d="M 64 58 Q 76 40 98 36" stroke="#fff" strokeWidth={9} strokeLinecap="round" fill="none" opacity={0.8} />
			</svg>
		</Caja>
	);
};

type Icono = 'interrogacion' | 'exclamacion' | 'carta' | 'entrada' | 'foto' | 'dinero' | 'libro' | 'estrella' | 'enojo';

/** Iconos sueltos que aparecen con rebote. */
export const Icono: React.FC<{tipo: Icono; x: number; y: number; desde: number; tam?: number; rot?: number; hasta?: number}> = ({tipo, x, y, desde, tam = 180, rot = 0, hasta = 99999}) => {
	const f = useCurrentFrame();
	const p = usePop(desde, 220);
	if (f < desde || f >= hasta) return null;
	const flota = Math.sin((f - desde) / 7) * 8;
	const contenido = (() => {
		switch (tipo) {
			case 'interrogacion':
			case 'exclamacion':
				return (
					<div style={{fontFamily: TITULAR, fontWeight: 900, fontSize: tam, color: tipo === 'interrogacion' ? '#ffd84a' : '#ff5a4e', WebkitTextStroke: `${tam * 0.07}px ${TINTA}`, lineHeight: 1, textAlign: 'center'}}>
						{tipo === 'interrogacion' ? '?' : '!'}
					</div>
				);
			case 'enojo':
				return (
					<svg viewBox="0 0 100 100" width="100%" height="100%">
						{[0, 90, 180, 270].map((a) => (
							<path key={a} d="M 40 10 Q 44 34 20 40" stroke="#e3262e" strokeWidth={12} fill="none" strokeLinecap="round" transform={`rotate(${a} 50 50)`} />
						))}
					</svg>
				);
			case 'carta':
				return (
					<svg viewBox="0 0 200 140" width="100%" height="100%" style={{overflow: 'visible'}}>
						<rect x={6} y={6} width={188} height={128} rx={12} fill="#fff4f4" stroke={TINTA} strokeWidth={9} />
						<path d="M 6 14 L 100 80 L 194 14" stroke={TINTA} strokeWidth={8} fill="none" />
						<path d="M 100 112 C 60 84 76 58 100 76 C 124 58 140 84 100 112 Z" fill="#e3262e" stroke={TINTA} strokeWidth={6} />
					</svg>
				);
			case 'entrada':
				return (
					<svg viewBox="0 0 220 110" width="100%" height="100%" style={{overflow: 'visible'}}>
						<path d="M 6 6 L 214 6 L 214 40 Q 196 55 214 70 L 214 104 L 6 104 L 6 70 Q 24 55 6 40 Z" fill="#ffd84a" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
						<line x1={60} y1={14} x2={60} y2={96} stroke={TINTA} strokeWidth={5} strokeDasharray="10 8" />
						<text x={138} y={68} textAnchor="middle" fontFamily={TITULAR} fontWeight={900} fontSize={32} fill={TINTA}>TEATRO</text>
					</svg>
				);
			case 'foto':
				return (
					<svg viewBox="0 0 160 190" width="100%" height="100%" style={{overflow: 'visible'}}>
						<rect x={6} y={6} width={148} height={178} rx={6} fill="#fff" stroke={TINTA} strokeWidth={8} />
						<rect x={20} y={20} width={120} height={120} fill="#bcd3e6" stroke={TINTA} strokeWidth={5} />
						<circle cx={80} cy={70} r={30} fill="#fff" stroke={TINTA} strokeWidth={6} />
						<path d="M 50 70 Q 50 30 80 34 Q 112 30 110 76 Q 104 56 80 52 Q 58 54 50 70 Z" fill="#7a4a2a" stroke={TINTA} strokeWidth={4} />
						<path d="M 50 140 Q 52 106 80 104 Q 108 106 110 140" fill="#e3626b" stroke={TINTA} strokeWidth={5} />
						<path d="M 80 172 C 62 160 68 148 80 156 C 92 148 98 160 80 172 Z" fill="#e3262e" />
					</svg>
				);
			case 'dinero':
				return (
					<svg viewBox="0 0 200 220" width="100%" height="100%" style={{overflow: 'visible'}}>
						<path d="M 70 40 Q 100 64 130 40 L 120 24 Q 100 34 80 24 Z" fill="#c9a86a" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
						<path d="M 80 56 Q 10 100 22 170 Q 30 214 100 214 Q 170 214 178 170 Q 190 100 120 56 Z" fill="#d9b878" stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
						<line x1={74} y1={56} x2={126} y2={56} stroke={TINTA} strokeWidth={10} strokeLinecap="round" />
						<text x={100} y={168} textAnchor="middle" fontFamily={TITULAR} fontWeight={900} fontSize={64} fill="#2f6b2f" stroke={TINTA} strokeWidth={3}>RM</text>
					</svg>
				);
			case 'libro':
				return (
					<svg viewBox="0 0 220 170" width="100%" height="100%" style={{overflow: 'visible'}}>
						<path d="M 110 30 Q 60 8 8 22 L 8 158 Q 60 144 110 164 Q 160 144 212 158 L 212 22 Q 160 8 110 30 Z" fill="#fff8e6" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
						<line x1={110} y1={30} x2={110} y2={164} stroke={TINTA} strokeWidth={6} />
						<rect x={20} y={-20} width={180} height={50} rx={10} fill="#c3342b" stroke={TINTA} strokeWidth={7} />
						<text x={110} y={14} textAnchor="middle" fontFamily={TITULAR} fontWeight={900} fontSize={34} fill="#fff">CUENTO</text>
						{[60, 84, 108, 132].map((yy) => (
							<g key={yy}>
								<line x1={26} y1={yy} x2={94} y2={yy - 4} stroke={TINTA} strokeWidth={5} opacity={0.4} />
								<line x1={126} y1={yy - 4} x2={194} y2={yy} stroke={TINTA} strokeWidth={5} opacity={0.4} />
							</g>
						))}
					</svg>
				);
			case 'estrella':
				return (
					<svg viewBox="0 0 100 100" width="100%" height="100%">
						<path d="M 50 4 L 60 40 L 96 50 L 60 60 L 50 96 L 40 60 L 4 50 L 40 40 Z" fill="#fff6a8" stroke="#ffd84a" strokeWidth={4} />
					</svg>
				);
		}
	})();
	return (
		<Caja x={x} y={y + flota} w={tam} h={tam} escala={p} rot={rot + (1 - p) * -25}>
			{contenido}
		</Caja>
	);
};

/** Destellos/estrellitas alrededor de un punto. */
export const Brillos: React.FC<{x: number; y: number; desde: number; radio?: number; n?: number}> = ({x, y, desde, radio = 260, n = 7}) => {
	const f = useCurrentFrame();
	const l = f - desde;
	if (l < 0 || l > 30) return null;
	return (
		<>
			{Array.from({length: n}).map((_, i) => {
				const a = (i / n) * Math.PI * 2 + random(`b${i}`);
				const d = interpolate(l, [0, 18], [radio * 0.4, radio], {...clamp, easing: Easing.out(Easing.cubic)});
				const s = interpolate(l, [0, 6, 30], [0, 1, 0], clamp);
				const t = 70 + random(`t${i}`) * 50;
				return (
					<div key={i} style={{position: 'absolute', left: x + Math.cos(a) * d - t / 2, top: y + Math.sin(a) * d - t / 2, width: t, height: t, transform: `scale(${s}) rotate(${l * 6}deg)`}}>
						<svg viewBox="0 0 100 100" width="100%" height="100%">
							<path d="M 50 0 L 60 40 L 100 50 L 60 60 L 50 100 L 40 60 L 0 50 L 40 40 Z" fill="#fff8c4" stroke="#f5c400" strokeWidth={5} />
						</svg>
					</div>
				);
			})}
		</>
	);
};

/** Nube de humo "¡puf!" (cambio de ropa, aparición). */
export const Puf: React.FC<{x: number; y: number; desde: number; tam?: number}> = ({x, y, desde, tam = 700}) => {
	const f = useCurrentFrame();
	const l = f - desde;
	if (l < 0 || l > 22) return null;
	return (
		<>
			{Array.from({length: 9}).map((_, i) => {
				const a = (i / 9) * Math.PI * 2;
				const d = interpolate(l, [0, 14], [tam * 0.08, tam * 0.36], {...clamp, easing: Easing.out(Easing.cubic)});
				const r = interpolate(l, [0, 6, 22], [tam * 0.1, tam * 0.26, tam * 0.05], clamp);
				const o = interpolate(l, [0, 3, 16, 22], [0, 1, 0.9, 0], clamp);
				return (
					<div
						key={i}
						style={{position: 'absolute', left: x + Math.cos(a) * d - r, top: y + Math.sin(a) * d * 1.3 - r, width: r * 2, height: r * 2, borderRadius: '50%', background: '#f4f4f4', border: `8px solid ${TINTA}`, opacity: o}}
					/>
				);
			})}
		</>
	);
};

/** Confeti cayendo por toda la pantalla. */
export const Confeti: React.FC<{desde: number; n?: number}> = ({desde, n = 70}) => {
	const f = useCurrentFrame();
	const l = f - desde;
	if (l < 0) return null;
	const colores = ['#e3262e', '#ffd84a', '#2a79e3', '#3cc46b', '#ff7ac8', '#ffffff'];
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			{Array.from({length: n}).map((_, i) => {
				const x0 = random(`cx${i}`) * 1080;
				const v = 18 + random(`cv${i}`) * 16;
				const y = -60 + l * v - random(`cy${i}`) * 400;
				const x = x0 + Math.sin(l / 6 + i) * 40;
				return (
					<div
						key={i}
						style={{position: 'absolute', left: x, top: y, width: 22, height: 34, background: colores[i % colores.length], border: `3px solid ${TINTA}`, transform: `rotate(${l * 12 + i * 40}deg) scaleX(${Math.cos(l / 3 + i)})`}}
					/>
				);
			})}
		</AbsoluteFill>
	);
};

/** Rayos de sol girando (fondo de "victoria"). */
export const Rayos: React.FC<{x: number; y: number; color?: string; opacidad?: number}> = ({x, y, color = '#fff2a8', opacidad = 0.35}) => {
	const f = useCurrentFrame();
	return (
		<div style={{position: 'absolute', left: x - 1600, top: y - 1600, width: 3200, height: 3200, opacity: opacidad, transform: `rotate(${f * 0.6}deg)`, mixBlendMode: 'screen'}}>
			<svg viewBox="-100 -100 200 200" width="100%" height="100%">
				{Array.from({length: 16}).map((_, i) => (
					<path key={i} d="M 0 0 L -7 -100 L 7 -100 Z" fill={color} transform={`rotate(${i * 22.5})`} />
				))}
			</svg>
		</div>
	);
};

/** Banda de olas que tapa la parte de abajo de lo que flota en el mar. */
export const Olas: React.FC<{y: number; color?: string}> = ({y, color = 'rgba(16,52,96,0.82)'}) => {
	const f = useCurrentFrame();
	const puntos = Array.from({length: 25}).map((_, i) => {
		const x = (i / 24) * 1280 - 100;
		return `${x},${y + Math.sin(i * 0.9 + f / 6) * 18 + Math.sin(i * 0.37 - f / 9) * 10}`;
	});
	return (
		<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
			<polygon points={`${puntos.join(' ')} 1180,2100 -100,2100`} fill={color} />
			<polyline points={puntos.join(' ')} fill="none" stroke="rgba(220,240,255,0.85)" strokeWidth={10} strokeLinecap="round" />
		</svg>
	);
};

/** Escritura de tiza que aparece de izquierda a derecha. */
export const Tiza: React.FC<{x: number; y: number; texto: string; desde: number; tam?: number; rot?: number; duracion?: number}> = ({x, y, texto, desde, tam = 80, rot = -3, duracion = 10}) => {
	const f = useCurrentFrame();
	const p = interpolate(f, [desde, desde + duracion], [0, 100], clamp);
	if (f < desde) return null;
	return (
		<div
			style={{
				position: 'absolute',
				left: x,
				top: y,
				transform: `rotate(${rot}deg)`,
				fontFamily: TITULAR,
				fontWeight: 900,
				fontSize: tam,
				color: 'rgba(250,250,245,0.92)',
				letterSpacing: 2,
				whiteSpace: 'nowrap',
				clipPath: `inset(0 ${100 - p}% 0 0)`,
				textShadow: '0 0 6px rgba(255,255,255,0.4)',
			}}
		>
			{texto}
		</div>
	);
};

/** Tablas de un letrero de cruce de caminos. */
export const Letrero: React.FC<{x: number; y: number; tablas: {texto: string; dir: 'izq' | 'der'; color?: string}[]; desde: number; giro?: number}> = ({x, y, tablas, desde, giro = 0}) => {
	const p = usePop(desde, 200);
	const f = useCurrentFrame();
	if (f < desde) return null;
	return (
		<div style={{position: 'absolute', left: x - 330, top: y, width: 660, transform: `scale(${p})`, transformOrigin: '50% 0%'}}>
			{tablas.map((t, i) => (
				<div key={i} style={{display: 'flex', justifyContent: t.dir === 'izq' ? 'flex-start' : 'flex-end', marginBottom: 26, transform: `rotate(${(i % 2 ? 3 : -3) + (i === 1 ? giro : 0)}deg)`}}>
					<svg viewBox="0 0 440 130" width={440} height={130} style={{overflow: 'visible'}}>
						<path
							d={t.dir === 'der' ? 'M 6 10 L 360 10 L 432 65 L 360 120 L 6 120 Z' : 'M 434 10 L 80 10 L 8 65 L 80 120 L 434 120 Z'}
							fill={t.color ?? '#e8c58a'}
							stroke={TINTA}
							strokeWidth={10}
							strokeLinejoin="round"
						/>
						<text x={220} y={86} textAnchor="middle" fontFamily={TITULAR} fontWeight={900} fontSize={62} fill={TINTA}>
							{t.texto}
						</text>
					</svg>
				</div>
			))}
		</div>
	);
};

/** Fundido a negro al final. */
export const Fundido: React.FC<{desde: number; duracion?: number}> = ({desde, duracion = 12}) => {
	const f = useCurrentFrame();
	const o = interpolate(f, [desde, desde + duracion], [0, 1], clamp);
	if (o <= 0) return null;
	return <AbsoluteFill style={{background: '#000', opacity: o}} />;
};

import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {CONDENSADA, MONO, ROTULADO, TITULAR} from '../fuentes';

/*
 * Utilería y fondos del short «Hackeó GTA 6 desde la tele de un hotel».
 * Nada de logos reales: la tele, el "Fire Stick", el chat y el foro son dibujos genéricos.
 * Paleta: azul noche (hotel), neón morado/rosa (digital), ámbar→rojo (oficina), blanco frío y negro (final).
 */

const TINTA = '#14141a';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
export const NEON_M = '#b44dff';
export const NEON_R = '#ff4fa3';
export const NEON_C = '#3ee8ff';
export const NOCHE = '#0d1530';

/* =============================== EL APARATITO =============================== */

/** El "Fire Stick" genérico: llave negra con conector HDMI y una luz. (x, y) = centro. */
export const Stick: React.FC<{x: number; y: number; largo: number; rot?: number; led?: number; etiqueta?: string; etiquetaDesde?: number; tamEtiqueta?: number}> = ({x, y, largo, rot = 0, led = 1, etiqueta, etiquetaDesde = 0, tamEtiqueta = 1}) => {
	const f = useCurrentFrame();
	const k0 = largo / 300;
	const k = k0 * tamEtiqueta;
	const pulso = 0.7 + 0.3 * Math.sin(f / 6);
	const tag = interpolate(f, [etiquetaDesde, etiquetaDesde + 8], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.6))});
	return (
		<div style={{position: 'absolute', left: x - largo / 2, top: y - 50 * k0, width: largo, height: 100 * k0, transform: `rotate(${rot}deg)`}}>
			<svg viewBox="0 0 300 100" width="100%" height="100%" style={{overflow: 'visible'}}>
				{led > 0 && <ellipse cx={170} cy={50} rx={190} ry={95} fill={NEON_M} opacity={0.22 * led * pulso} />}
				<rect x={0} y={34} width={58} height={32} rx={4} fill="#b9bec8" stroke={TINTA} strokeWidth={5} />
				<rect x={8} y={42} width={42} height={8} fill="#7d838c" />
				<rect x={52} y={18} width={240} height={64} rx={16} fill="#1c1d24" stroke={TINTA} strokeWidth={6} />
				<path d="M 70 30 L 270 30" stroke="#3a3c48" strokeWidth={5} strokeLinecap="round" />
				<circle cx={268} cy={50} r={8} fill={led > 0 ? NEON_M : '#333'} stroke={TINTA} strokeWidth={3} />
				{led > 0 && <circle cx={268} cy={50} r={20} fill={NEON_M} opacity={0.4 * led * pulso} />}
			</svg>
			{etiqueta && tag > 0 && (
				<div style={{position: 'absolute', left: largo * 0.62, top: 100 * k0 * 0.9, transformOrigin: '20% 0%', transform: `rotate(${12 - 6 * Math.sin(f / 9)}deg) scale(${tag})`}}>
					<svg width={4} height={60 * k} style={{position: 'absolute', left: 20 * k, top: -20 * k}}>
						<line x1={2} y1={0} x2={2} y2={60 * k} stroke="#ffffff" strokeWidth={3} />
					</svg>
					<div style={{marginTop: 34 * k, padding: `${8 * k}px ${18 * k}px`, background: '#fff8e1', border: `${5 * k}px solid ${TINTA}`, borderRadius: 10 * k, fontFamily: CONDENSADA, fontSize: 60 * k, color: TINTA, whiteSpace: 'nowrap', boxShadow: `0 ${8 * k}px 0 rgba(0,0,0,0.35)`}}>{etiqueta}</div>
				</div>
			)}
		</div>
	);
};

/** Candado que se abre (abre: 0..1). */
export const Candado: React.FC<{x: number; y: number; tam: number; abre: number; color?: string}> = ({x, y, tam, abre, color = NEON_C}) => (
	<div style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, width: tam, height: tam}}>
		<svg viewBox="-100 -100 200 200" width="100%" height="100%" style={{overflow: 'visible', filter: `drop-shadow(0 0 ${tam * 0.06}px ${color})`}}>
			<g transform={`translate(${abre * 34} ${-abre * 34})`}>
				<path d="M -40 -6 L -40 -46 Q -40 -86 0 -86 Q 40 -86 40 -46 L 40 -6" fill="none" stroke={color} strokeWidth={16} strokeLinecap="round" />
			</g>
			<rect x={-60} y={-14} width={120} height={96} rx={16} fill="rgba(10,10,30,0.85)" stroke={color} strokeWidth={10} />
			<circle cx={0} cy={22} r={13} fill={color} />
			<rect x={-5} y={26} width={10} height={30} rx={4} fill={color} />
		</svg>
	</div>
);

/* =============================== LA TELE =============================== */

/**
 * Televisor plano. `giro` (grados) lo hace girar sobre su eje: de 90 a 270 se ve la parte de atrás
 * en corte (puertos HDMI y el aparatito conectado). `encendida` 1 → 0 la apaga como un tubo (se cierra en una línea).
 */
export const Tele: React.FC<{
	x: number;
	y: number;
	ancho: number;
	children?: React.ReactNode;
	encendida?: number;
	giro?: number;
	brilloStick?: number;
	/** 0..1: cuánto entra el aparatito en el puerto (vista trasera) */
	enchufe?: number;
	pie?: boolean;
}> = ({x, y, ancho, children, encendida = 1, giro = 0, brilloStick = 0, enchufe = 1, pie = true}) => {
	const alto = ancho * 0.6;
	const rad = (giro * Math.PI) / 180;
	const cos = Math.cos(rad);
	const atras = cos < 0;
	const sx = Math.max(0.02, Math.abs(cos));
	const colapsoY = interpolate(encendida, [0, 0.35, 1], [0.004, 0.012, 1], clamp);
	const colapsoX = interpolate(encendida, [0, 0.25, 0.35], [0.002, 0.04, 1], clamp);
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto}}>
			{brilloStick > 0 && !atras && <div style={{position: 'absolute', right: -ancho * 0.18, top: alto * 0.1, width: ancho * 0.5, height: alto * 0.8, borderRadius: '50%', background: `radial-gradient(circle, ${NEON_M}cc, ${NEON_M}00 70%)`, opacity: brilloStick}} />}
			{pie && (
				<>
					<div style={{position: 'absolute', left: ancho * 0.44, top: alto * 0.98, width: ancho * 0.12, height: alto * 0.14, background: '#2a2c36', border: `${ancho * 0.008}px solid ${TINTA}`, transform: `scaleX(${sx})`}} />
					<div style={{position: 'absolute', left: ancho * 0.3, top: alto * 1.1, width: ancho * 0.4, height: alto * 0.05, borderRadius: 8, background: '#2a2c36', border: `${ancho * 0.008}px solid ${TINTA}`}} />
				</>
			)}
			<div style={{position: 'absolute', inset: 0, transform: `scaleX(${sx})`}}>
				{!atras ? (
					<div style={{position: 'absolute', inset: 0, background: '#1a1b22', border: `${ancho * 0.014}px solid ${TINTA}`, borderRadius: ancho * 0.02, boxSizing: 'border-box', padding: ancho * 0.022}}>
						<div style={{position: 'relative', width: '100%', height: '100%', background: '#000', overflow: 'hidden'}}>
							<div style={{position: 'absolute', inset: 0, transform: `scale(${colapsoX}, ${colapsoY})`, filter: encendida < 1 ? `brightness(${1 + (1 - encendida) * 2})` : undefined}}>{children}</div>
							<div style={{position: 'absolute', left: '-10%', top: '-30%', width: '60%', height: '80%', background: 'linear-gradient(120deg, rgba(255,255,255,0.10), rgba(255,255,255,0))', transform: 'rotate(-12deg)'}} />
						</div>
					</div>
				) : (
					<TeleTrasera ancho={ancho} alto={alto} enchufe={enchufe} />
				)}
			</div>
		</div>
	);
};

/** La tele por detrás, en corte: tapa transparente, puertos HDMI y el aparatito. */
const TeleTrasera: React.FC<{ancho: number; alto: number; enchufe: number}> = ({ancho, alto, enchufe}) => {
	const f = useCurrentFrame();
	return (
		<div style={{position: 'absolute', inset: 0, transform: 'scaleX(-1)'}}>
			<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg,#2a2c38,#1c1d26)', border: `${ancho * 0.014}px solid ${TINTA}`, borderRadius: ancho * 0.03, boxSizing: 'border-box'}} />
			{/* rejillas */}
			{Array.from({length: 7}).map((_, i) => (
				<div key={i} style={{position: 'absolute', left: ancho * 0.12, top: alto * (0.14 + i * 0.06), width: ancho * 0.36, height: alto * 0.025, borderRadius: 6, background: '#121219'}} />
			))}
			{/* panel de puertos (en corte) */}
			<div style={{position: 'absolute', left: ancho * 0.56, top: alto * 0.16, width: ancho * 0.34, height: alto * 0.62, background: 'rgba(60,232,255,0.08)', border: `${ancho * 0.008}px dashed ${NEON_C}`, borderRadius: ancho * 0.015}}>
				{[0, 1].map((i) => (
					<div key={i} style={{position: 'absolute', left: '12%', top: `${16 + i * 40}%`, width: '34%', height: '18%', background: '#0b0b10', border: `${ancho * 0.006}px solid #b9bec8`, borderRadius: 4}}>
						<div style={{position: 'absolute', left: '120%', top: '0%', fontFamily: CONDENSADA, fontSize: ancho * 0.035, color: '#d9dce6', whiteSpace: 'nowrap'}}>HDMI {i + 1}</div>
					</div>
				))}
			</div>
			{/* el aparatito entrando en HDMI 1 */}
			<div style={{position: 'absolute', left: ancho * 0.56 + ancho * 0.34 * 0.12 - ancho * 0.36 + (1 - enchufe) * -ancho * 0.18, top: alto * 0.16 + alto * 0.62 * 0.25 - ancho * 0.04, width: ancho * 0.4, height: ancho * 0.11, transform: 'scaleX(-1)'}}>
				<Stick x={ancho * 0.2} y={ancho * 0.055} largo={ancho * 0.4} rot={180} led={enchufe > 0.95 ? 1 : 0.2 + 0.2 * Math.sin(f)} />
			</div>
		</div>
	);
};

/** Pantalla de la tele del hotel: el candado se abre sobre líneas de código. */
export const PantallaHackeo: React.FC<{abre: number; w: number; h: number; tinte?: string}> = ({abre, w, h, tinte = NEON_M}) => {
	const f = useCurrentFrame();
	return (
		<AbsoluteFill style={{background: 'radial-gradient(circle at 50% 50%, #2a1450, #07040f)'}}>
			{Array.from({length: 9}).map((_, i) => (
				<div key={i} style={{position: 'absolute', left: '6%', top: `${6 + i * 10.5}%`, height: '4%', width: `${30 + ((i * 37 + Math.floor(f / 3)) % 55)}%`, background: i % 3 === 0 ? NEON_R : tinte, opacity: 0.35, borderRadius: 3}} />
			))}
			<Candado x={w / 2} y={h * 0.52} tam={h * 0.62} abre={abre} color={abre > 0.5 ? '#5dff8a' : NEON_C} />
			{abre > 0.6 && <div style={{position: 'absolute', left: 0, right: 0, bottom: h * 0.06, textAlign: 'center', fontFamily: MONO, fontWeight: 700, fontSize: h * 0.08, color: '#5dff8a'}}>ACCESO CONCEDIDO</div>}
		</AbsoluteFill>
	);
};

/* =============================== OBJETOS DE LA HISTORIA =============================== */

/** Laptop abierta de frente; los hijos van en la pantalla. (x, y) = base. */
export const Laptop: React.FC<{x: number; y: number; ancho: number; children?: React.ReactNode}> = ({x, y, ancho, children}) => {
	const alto = ancho * 0.62;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto - ancho * 0.06, width: ancho, height: alto + ancho * 0.08}}>
			<div style={{position: 'absolute', left: ancho * 0.06, top: 0, width: ancho * 0.88, height: alto, background: '#22242e', border: `${ancho * 0.014}px solid ${TINTA}`, borderRadius: ancho * 0.02, boxSizing: 'border-box', padding: ancho * 0.02}}>
				<div style={{position: 'relative', width: '100%', height: '100%', background: '#06060c', overflow: 'hidden'}}>{children}</div>
			</div>
			<div style={{position: 'absolute', left: 0, top: alto - ancho * 0.005, width: ancho, height: ancho * 0.07, background: '#b9bec8', border: `${ancho * 0.012}px solid ${TINTA}`, borderRadius: `${ancho * 0.01}px ${ancho * 0.01}px ${ancho * 0.04}px ${ancho * 0.04}px`, boxSizing: 'border-box'}} />
		</div>
	);
};

/** Bolsa de evidencia que baja sobre algo y se sella. (x, y) = centro final. */
export const BolsaEvidencia: React.FC<{x: number; y: number; ancho: number; alto: number; baja: number; sello: number}> = ({x, y, ancho, alto, baja, sello}) => {
	const dy = (1 - baja) * -1400;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2 + dy, width: ancho, height: alto}}>
			<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(160deg, rgba(220,235,255,0.22), rgba(200,220,255,0.08) 45%, rgba(255,255,255,0.22) 50%, rgba(200,220,255,0.06) 60%)', border: `8px solid rgba(230,240,255,0.85)`, borderRadius: 24}} />
			{/* cierre arriba */}
			<div style={{position: 'absolute', left: 16, right: 16, top: 26, height: 16, background: 'rgba(255,255,255,0.3)', borderRadius: 8}} />
			<div style={{position: 'absolute', left: 16, top: 26, height: 16, width: `calc(${sello * 100}% - ${sello * 32}px)`, background: '#e3262e', borderRadius: 8}} />
			{/* banda roja de evidencia */}
			<div style={{position: 'absolute', left: 0, right: 0, bottom: alto * 0.1, height: alto * 0.17, background: '#e3262e', border: `6px solid ${TINTA}`, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: 'rotate(-3deg)'}}>
				<div style={{fontFamily: CONDENSADA, fontSize: alto * 0.11, color: '#ffffff', letterSpacing: 6}}>EVIDENCIA</div>
			</div>
		</div>
	);
};

/** Celular grande (en el mundo) con un chat; el mensaje se escribe letra a letra. */
export const CelularChat: React.FC<{x: number; y: number; ancho: number; mensaje: string; desde: number; hasta: number; titulo?: string}> = ({x, y, ancho, mensaje, desde, hasta, titulo = '# empleados'}) => {
	const f = useCurrentFrame();
	const alto = ancho * 2;
	const n = Math.floor(interpolate(f, [desde, hasta], [0, mensaje.length], clamp));
	const cursor = Math.floor(f / 8) % 2 === 0 && n < mensaje.length;
	const enviado = f >= hasta + 4;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, background: '#111216', border: `${ancho * 0.03}px solid ${TINTA}`, borderRadius: ancho * 0.12, boxShadow: `0 0 ${ancho * 0.3}px ${NEON_M}66`, boxSizing: 'border-box', padding: ancho * 0.05}}>
			<div style={{position: 'relative', width: '100%', height: '100%', background: 'linear-gradient(180deg,#1a1033,#0b0818)', borderRadius: ancho * 0.08, overflow: 'hidden'}}>
				<div style={{padding: `${ancho * 0.05}px ${ancho * 0.06}px`, fontFamily: CONDENSADA, fontSize: ancho * 0.075, color: '#d9c8ff', borderBottom: '3px solid rgba(255,255,255,0.12)'}}>{titulo}</div>
				{[0.55, 0.8, 0.45].map((w, i) => (
					<div key={i} style={{margin: `${ancho * 0.04}px ${ancho * 0.06}px`, height: ancho * 0.06, width: `${w * 100}%`, borderRadius: 10, background: 'rgba(255,255,255,0.14)'}} />
				))}
				<div style={{position: 'absolute', left: ancho * 0.06, right: ancho * 0.06, bottom: ancho * 0.08}}>
					<div style={{marginLeft: 'auto', maxWidth: '92%', padding: `${ancho * 0.04}px ${ancho * 0.05}px`, borderRadius: `${ancho * 0.05}px ${ancho * 0.05}px 6px ${ancho * 0.05}px`, background: enviado ? NEON_R : '#2a2240', border: enviado ? 'none' : `3px dashed ${NEON_M}`, fontFamily: MONO, fontWeight: 700, fontSize: ancho * 0.062, lineHeight: 1.25, color: '#ffffff'}}>
						{mensaje.slice(0, n)}
						{cursor && <span style={{opacity: 0.8}}>▌</span>}
					</div>
				</div>
			</div>
		</div>
	);
};

/** Billetes volando (en el mundo), con la física hecha a mano. */
export const Billetes: React.FC<{desde: number; n?: number; x?: number; y?: number}> = ({desde, n = 26, x = 540, y = 1100}) => {
	const f = useCurrentFrame();
	const l = f - desde;
	if (l < 0) return null;
	return (
		<>
			{Array.from({length: n}).map((_, i) => {
				const a = ((i * 137.5) % 360) * (Math.PI / 180);
				const v = 14 + (i % 5) * 4;
				const bx = x + Math.cos(a) * v * l;
				const by = y + Math.sin(a) * v * l * 0.8 + 0.5 * l * l * 0.35;
				const rot = l * (i % 2 ? 9 : -7) + i * 20;
				const flip = Math.cos(l / 4 + i);
				return (
					<div key={i} style={{position: 'absolute', left: bx - 90, top: by - 42, width: 180, height: 84, transform: `rotate(${rot}deg) scaleY(${flip})`, background: '#7fc98a', border: `6px solid ${TINTA}`, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', boxSizing: 'border-box'}}>
						<div style={{width: 46, height: 46, borderRadius: '50%', border: `5px solid #2f7a3e`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: CONDENSADA, fontSize: 36, color: '#1f5a2c'}}>$</div>
					</div>
				);
			})}
		</>
	);
};

/** Reloj digital rojo (cuenta regresiva desde 24:00:00). */
export const Reloj: React.FC<{x: number; y: number; tam: number; desde: number}> = ({x, y, tam, desde}) => {
	const f = useCurrentFrame();
	const seg = Math.max(0, 24 * 3600 - Math.max(0, Math.floor((f - desde) / 30)));
	const hh = String(Math.floor(seg / 3600)).padStart(2, '0');
	const mm = String(Math.floor((seg % 3600) / 60)).padStart(2, '0');
	const ss = String(seg % 60).padStart(2, '0');
	return (
		<div style={{position: 'absolute', left: x - tam * 2.6, top: y - tam * 0.75, width: tam * 5.2, height: tam * 1.5, background: '#140507', border: `${tam * 0.08}px solid ${TINTA}`, borderRadius: tam * 0.18, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: `0 0 ${tam * 0.5}px #ff2a2a88`}}>
			<div style={{fontFamily: MONO, fontWeight: 700, fontSize: tam, color: '#ff3b3b', letterSpacing: tam * 0.04, textShadow: `0 0 ${tam * 0.2}px #ff2a2a`}}>{`${hh}:${mm}:${ss}`}</div>
		</div>
	);
};

/** Pantalla de alarma de la oficina: el mensaje del chat en grande. */
export const PantallaAlarma: React.FC<{mensaje: string; parpadeo?: boolean; tam?: number}> = ({mensaje, parpadeo = true, tam = 52}) => {
	const f = useCurrentFrame();
	const on = !parpadeo || Math.floor(f / 10) % 2 === 0;
	return (
		<AbsoluteFill style={{background: on ? '#3a0508' : '#22030a', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '8%'}}>
			<div style={{fontFamily: MONO, fontWeight: 700, fontSize: tam, color: '#ffd6d6', textAlign: 'center', lineHeight: 1.25, textShadow: '0 0 12px #ff2a2a'}}>{mensaje}</div>
		</AbsoluteFill>
	);
};

/** Cartel colgado de la manija (NO MOLESTAR). (x, y) = agujero. */
export const Colgante: React.FC<{x: number; y: number; texto: string; tam?: number; color?: string}> = ({x, y, texto, tam = 1, color = '#ffd23f'}) => {
	const f = useCurrentFrame();
	return (
		<div style={{position: 'absolute', left: x - 70 * tam, top: y - 30 * tam, width: 140 * tam, height: 300 * tam, transformOrigin: '50% 10%', transform: `rotate(${Math.sin(f / 25) * 2}deg)`}}>
			<div style={{position: 'absolute', inset: 0, background: color, border: `${6 * tam}px solid ${TINTA}`, borderRadius: 14 * tam}} />
			<div style={{position: 'absolute', left: '50%', top: 34 * tam, width: 46 * tam, height: 46 * tam, marginLeft: -23 * tam, borderRadius: '50%', background: '#1a1b22', border: `${5 * tam}px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 110 * tam, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 44 * tam, lineHeight: 1, color: TINTA, whiteSpace: 'pre'}}>{texto}</div>
		</div>
	);
};

/* =============================== FONDOS =============================== */

const Lienzo: React.FC<{children: React.ReactNode; vb?: string}> = ({children, vb = '0 0 1080 1920'}) => (
	<svg viewBox={vb} width="100%" height="100%" preserveAspectRatio="xMidYMid slice" style={{position: 'absolute', inset: 0}}>
		{children}
	</svg>
);

/** mezcla dos colores #rrggbb (t = 0 → a, 1 → b) */
export const mezclaColor = (a: string, b: string, t: number) => {
	const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
	const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
	return `rgb(${pa.map((v, i) => Math.round(v + (pb[i] - v) * t)).join(',')})`;
};

/** Cuarto de hotel de noche, iluminado solo por la tele. `frio` lo pasa a blanco frío y negro; `apagado` quita el brillo de la tele. */
export const EscHotel: React.FC<{frio?: number; luzTele?: number}> = ({frio = 0, luzTele = 1}) => {
	const f = useCurrentFrame();
	const mezcla = (a: string, b: string) => mezclaColor(a, b, frio);
	const pared = mezcla('#16224a', '#cfd3da');
	const zocalo = mezcla('#0f1834', '#9aa0aa');
	const piso = mezcla('#141a33', '#b7bcc6');
	const titila = 0.85 + 0.15 * Math.sin(f / 3.3) * Math.sin(f / 7.1);
	return (
		<AbsoluteFill>
			<Lienzo>
				<rect x={0} y={0} width={1080} height={1920} fill={pared} />
				{/* ventana con la ciudad */}
				<rect x={430} y={330} width={330} height={420} fill={mezcla('#0a1030', '#e6e9ef')} stroke={TINTA} strokeWidth={10} />
				{frio < 1 &&
					Array.from({length: 14}).map((_, i) => (
						<rect key={i} x={450 + ((i * 53) % 290)} y={520 + ((i * 37) % 200)} width={14} height={18} fill="#ffd86a" opacity={0.6 * (1 - frio)} />
					))}
				<line x1={595} y1={330} x2={595} y2={750} stroke={TINTA} strokeWidth={8} />
				<rect x={410} y={300} width={370} height={40} fill={mezcla('#2a2f55', '#a8adb6')} stroke={TINTA} strokeWidth={6} />
				{/* puerta */}
				<rect x={860} y={600} width={220} height={900} fill={mezcla('#1f2a55', '#e9ecf1')} stroke={TINTA} strokeWidth={10} />
				<rect x={890} y={640} width={160} height={360} fill="none" stroke={TINTA} strokeWidth={5} opacity={0.4} />
				<circle cx={985} cy={1080} r={16} fill="#c9a43a" stroke={TINTA} strokeWidth={5} />
				<rect x={0} y={1440} width={1080} height={60} fill={zocalo} />
				<rect x={0} y={1500} width={1080} height={420} fill={piso} />
				{/* luz de la tele */}
				{frio < 1 && <ellipse cx={330} cy={1020} rx={760} ry={640} fill="#4f7dff" opacity={0.16 * luzTele * titila * (1 - frio)} />}
				{frio < 1 && <ellipse cx={330} cy={1020} rx={380} ry={320} fill="#9f6dff" opacity={0.12 * luzTele * titila * (1 - frio)} />}
			</Lienzo>
		</AbsoluteFill>
	);
};

/** Cama del hotel: cabecera y almohadas (detrás) o la cobija (delante). */
export const Cama: React.FC<{capa: 'atras' | 'delante'; frio?: number; vacia?: boolean}> = ({capa, frio = 0, vacia}) => {
	const m = (a: string, b: string) => mezclaColor(a, b, frio);
	if (capa === 'atras')
		return (
			<>
				<div style={{position: 'absolute', left: 420, top: 1000, width: 560, height: 360, background: m('#3a2a4a', '#8d939e'), border: `10px solid ${TINTA}`, borderRadius: '40px 40px 0 0'}} />
				{[470, 700].map((x) => (
					<div key={x} style={{position: 'absolute', left: x, top: 1240, width: 230, height: 110, background: m('#b8c0e8', '#f2f3f6'), border: `8px solid ${TINTA}`, borderRadius: 40}} />
				))}
			</>
		);
	return (
		<>
			<div style={{position: 'absolute', left: 380, top: vacia ? 1330 : 1380, width: 640, height: vacia ? 210 : 170, background: m('#5a6fd1', '#ffffff'), border: `10px solid ${TINTA}`, borderRadius: '30px 30px 10px 10px'}} />
			<div style={{position: 'absolute', left: 380, top: vacia ? 1440 : 1470, width: 640, height: 26, background: m('#4256b0', '#d9dce2'), borderLeft: `10px solid ${TINTA}`, borderRight: `10px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 380, top: 1530, width: 640, height: 80, background: m('#2a2040', '#7d838c'), border: `10px solid ${TINTA}`}} />
		</>
	);
};

/** Mesa de evidencias bajo una lámpara colgante. */
export const EscEvidencias: React.FC = () => (
	<AbsoluteFill>
		<Lienzo>
			<rect x={0} y={0} width={1080} height={1920} fill="#0c1228" />
			<line x1={540} y1={0} x2={540} y2={420} stroke="#05070f" strokeWidth={10} />
			<path d="M 420 500 L 660 500 L 600 420 L 480 420 Z" fill="#2a2f45" stroke={TINTA} strokeWidth={8} />
			<path d="M 420 500 L 120 1500 L 960 1500 L 660 500 Z" fill="#fff4c2" opacity={0.07} />
			<ellipse cx={540} cy={1330} rx={460} ry={70} fill="#fff4c2" opacity={0.12} />
			<rect x={60} y={1330} width={960} height={70} fill="#3a3550" stroke={TINTA} strokeWidth={10} />
			<rect x={100} y={1400} width={60} height={520} fill="#2a2640" stroke={TINTA} strokeWidth={8} />
			<rect x={920} y={1400} width={60} height={520} fill="#2a2640" stroke={TINTA} strokeWidth={8} />
		</Lienzo>
	</AbsoluteFill>
);

/** Fachada del hotel de noche, alta (la cámara sube por ella como una grúa). El mundo va de y=-1600 a 1920. */
export const FACHADA_VENTANA = {x: 700, y: -1080, w: 180, h: 220};
export const EscFachadaHotel: React.FC = () => {
	const f = useCurrentFrame();
	const neon = Math.floor(f / 7) % 11 === 0 ? 0.35 : 1;
	return (
		<div style={{position: 'absolute', left: 0, top: -1600, width: 1080, height: 3520}}>
			<svg viewBox="0 -1600 1080 3520" width="100%" height="100%" style={{position: 'absolute', inset: 0}}>
				<defs>
					<linearGradient id="cieloHotel" x1={0} y1={0} x2={0} y2={1}>
						<stop offset={0} stopColor="#060b22" />
						<stop offset={1} stopColor="#1a2550" />
					</linearGradient>
				</defs>
				<rect x={0} y={-1600} width={1080} height={3520} fill="url(#cieloHotel)" />
				{Array.from({length: 30}).map((_, i) => (
					<circle key={i} cx={(i * 211) % 1080} cy={-1550 + ((i * 97) % 500)} r={i % 4 ? 2.5 : 4} fill="#ffffff" opacity={0.6} />
				))}
				<rect x={140} y={-1400} width={800} height={2900} fill="#1d2a5a" stroke={TINTA} strokeWidth={12} />
				{Array.from({length: 13}).map((_, r) =>
					Array.from({length: 3}).map((__, c) => {
						const x = 220 + c * 240;
						const y = -1300 + r * 230;
						const esLa = Math.abs(x - FACHADA_VENTANA.x) < 30 && Math.abs(y - FACHADA_VENTANA.y) < 30;
						const luz = esLa || (r * 3 + c) % 5 === 0;
						return <rect key={`${r}-${c}`} x={x - 90} y={y - 110} width={180} height={220} fill={esLa ? '#7aa2ff' : luz ? '#ffd86a' : '#0e1636'} stroke={TINTA} strokeWidth={8} opacity={esLa ? 1 : luz ? 0.75 : 1} />;
					}),
				)}
				{/* letrero de neón */}
				<rect x={330} y={1020} width={420} height={140} rx={20} fill="#120a24" stroke={TINTA} strokeWidth={10} />
				<text x={540} y={1120} textAnchor="middle" fontFamily={ROTULADO} fontSize={96} fill={NEON_R} opacity={neon} style={{filter: `drop-shadow(0 0 14px ${NEON_R})`}}>
					HOTEL
				</text>
				{/* entrada */}
				<rect x={430} y={1240} width={220} height={260} fill="#ffd86a" opacity={0.85} stroke={TINTA} strokeWidth={10} />
				<rect x={0} y={1500} width={1080} height={420} fill="#232838" />
				<rect x={0} y={1500} width={1080} height={30} fill="#3a4058" />
			</svg>
		</div>
	);
};

/** Edificio ancho de noche, con ventanas (para el paneo lateral). Coordenadas de -400 a 1480 en x. */
export const VENTANAS_EDIFICIO: [number, number][] = [];
for (let r = 0; r < 4; r++) for (let c = 0; c < 6; c++) VENTANAS_EDIFICIO.push([-200 + c * 300, 560 + r * 330]);
export const EscEdificio: React.FC<{congelado?: boolean}> = ({congelado}) => (
	<div style={{position: 'absolute', left: -400, top: 0, width: 1880, height: 1920}}>
		<svg viewBox="-400 0 1880 1920" width="100%" height="100%" style={{position: 'absolute', inset: 0}}>
			<defs>
				<linearGradient id="cieloNeon" x1={0} y1={0} x2={0} y2={1}>
					<stop offset={0} stopColor="#12062a" />
					<stop offset={0.7} stopColor="#3a0f5a" />
					<stop offset={1} stopColor="#7a1a6a" />
				</linearGradient>
			</defs>
			<rect x={-400} y={0} width={1880} height={1920} fill="url(#cieloNeon)" />
			<rect x={-360} y={380} width={1800} height={1540} fill={congelado ? '#2a2f45' : '#251a45'} stroke={TINTA} strokeWidth={12} />
			{VENTANAS_EDIFICIO.map(([x, y], i) => (
				<rect key={i} x={x - 120} y={y - 130} width={240} height={260} fill={congelado ? '#b9c3d6' : i % 3 ? '#ffd0f0' : '#d8c8ff'} stroke={TINTA} strokeWidth={10} />
			))}
			{[-200, 400, 1000].map((x) => (
				<rect key={x} x={x + 120} y={420} width={20} height={1460} fill={NEON_R} opacity={congelado ? 0.15 : 0.5} />
			))}
		</svg>
	</div>
);

/** Oficina: luz ámbar que pasa a alarma roja (`rojo` 0..1). */
export const EscOficinaAlarma: React.FC<{rojo: number}> = ({rojo}) => {
	const f = useCurrentFrame();
	const giro = (f * 9) % 360;
	const pared = `rgb(${Math.round(120 + 30 * rojo)},${Math.round(80 - 50 * rojo)},${Math.round(40 - 10 * rojo)})`;
	return (
		<AbsoluteFill>
			<Lienzo>
				<rect x={0} y={0} width={1080} height={1920} fill={pared} />
				<rect x={0} y={0} width={1080} height={1920} fill="#000" opacity={0.35} />
				{[0, 1, 2, 3].map((i) => (
					<rect key={i} x={60 + i * 260} y={180} width={180} height={30} rx={10} fill={rojo > 0.5 ? '#ff6b6b' : '#ffd08a'} opacity={0.8} />
				))}
				<rect x={0} y={1420} width={1080} height={500} fill="#2a1a14" />
				{/* luz giratoria de alarma */}
				{rojo > 0.3 && (
					<g opacity={rojo}>
						{[110, 970].map((lx, k) => {
							const g = giro + k * 180;
							return (
								<g key={lx}>
									<path d={`M ${lx} 130 L ${lx + Math.cos((g * Math.PI) / 180) * 1400} ${130 + Math.sin((g * Math.PI) / 180) * 900 + 600} L ${lx + Math.cos(((g + 25) * Math.PI) / 180) * 1400} ${130 + Math.sin(((g + 25) * Math.PI) / 180) * 900 + 600} Z`} fill="#ff2a2a" opacity={0.16} />
									<circle cx={lx} cy={130} r={40} fill="#ff2a2a" stroke={TINTA} strokeWidth={8} />
								</g>
							);
						})}
					</g>
				)}
			</Lienzo>
		</AbsoluteFill>
	);
};

/** Pasillo de hospital: blanco frío y negro, sobrio. */
export const EscHospital: React.FC = () => (
	<AbsoluteFill>
		<Lienzo>
			<rect x={0} y={0} width={1080} height={1920} fill="#e9ecf1" />
			<path d="M 0 1500 L 1080 1500 L 1080 1920 L 0 1920 Z" fill="#c9ced6" />
			{[0, 1, 2].map((i) => (
				<rect key={i} x={140 + i * 300} y={160} width={200} height={26} rx={8} fill="#ffffff" stroke="#9aa0aa" strokeWidth={4} />
			))}
			<line x1={0} y1={1500} x2={1080} y2={1500} stroke={TINTA} strokeWidth={8} />
		</Lienzo>
	</AbsoluteFill>
);

/** Puerta pesada que se cierra (cierre 0..1): una hoja que gira hacia el marco. */
export const PuertaPesada: React.FC<{x: number; y: number; ancho: number; alto: number; cierre: number}> = ({x, y, ancho, alto, cierre}) => {
	const abierta = 1 - cierre;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto, width: ancho, height: alto}}>
			<div style={{position: 'absolute', inset: -24, border: `24px solid #2a2c34`, borderBottom: 'none'}} />
			<div style={{position: 'absolute', inset: 0, background: '#14151a'}} />
			<div style={{position: 'absolute', inset: 0, transformOrigin: '0% 50%', transform: `perspective(1600px) rotateY(${-abierta * 80}deg)`, background: '#f4f5f8', border: `10px solid ${TINTA}`, boxSizing: 'border-box'}}>
				<div style={{position: 'absolute', left: '30%', top: '14%', width: '40%', height: '20%', background: '#cfd6e0', border: `8px solid ${TINTA}`}} />
				<div style={{position: 'absolute', right: '10%', top: '52%', width: '14%', height: '4%', background: '#9aa0aa', border: `6px solid ${TINTA}`, borderRadius: 8}} />
			</div>
		</div>
	);
};

/* =============================== EL TÚNEL DIGITAL (E3) =============================== */

type Cosa = {z: number; x: number; y: number; ancho: number; tipo: 'chat' | 'carpeta' | 'boveda' | 'carga' | 'cartel'; texto?: string; lado?: number};

/** Un mundo en profundidad: la cámara avanza en z (`cz`). Se proyecta con perspectiva sobre la pantalla. */
export const Tunel: React.FC<{cz: number; cosas: Cosa[]; abreBoveda: number; carga: number; children?: React.ReactNode}> = ({cz, cosas, abreBoveda, carga, children}) => {
	const F = 620;
	const cx = 540;
	const cy = 860;
	const lineas = [];
	for (let k = 0; k < 26; k++) {
		const z = Math.floor(cz / 150) * 150 + k * 150;
		const dz = z - cz;
		if (dz < 20) continue;
		const s = F / dz;
		lineas.push({y: cy + 520 * s, techo: cy - 520 * s, o: Math.min(1, 6 / (dz / 150))});
	}
	const visibles = cosas.filter((c) => c.z - cz > 40).sort((a, b) => b.z - a.z);
	return (
		<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, #2a0f4a 0%, #0b0418 70%)', overflow: 'hidden'}}>
			<svg viewBox="0 0 1080 1920" width="100%" height="100%" style={{position: 'absolute', inset: 0}}>
				{lineas.map((l, i) => (
					<g key={i} opacity={Math.min(1, l.o)}>
						<line x1={0} y1={l.y} x2={1080} y2={l.y} stroke={NEON_R} strokeWidth={3} opacity={0.6} />
						<line x1={0} y1={l.techo} x2={1080} y2={l.techo} stroke={NEON_M} strokeWidth={3} opacity={0.45} />
					</g>
				))}
				{Array.from({length: 13}).map((_, i) => {
					const x = -1800 + i * 300;
					return (
						<g key={i}>
							<line x1={cx + x * (F / 3000)} y1={cy + 520 * (F / 3000)} x2={cx + x * 2.4} y2={1920 + 600} stroke={NEON_R} strokeWidth={3} opacity={0.5} />
							<line x1={cx + x * (F / 3000)} y1={cy - 520 * (F / 3000)} x2={cx + x * 2.4} y2={-600} stroke={NEON_M} strokeWidth={3} opacity={0.35} />
						</g>
					);
				})}
			</svg>
			{visibles.map((c, i) => {
				const dz = c.z - cz;
				const s = F / dz;
				const op = Math.min(1, (dz - 40) / 120) * Math.min(1, 3200 / dz / 1.4);
				const w = c.ancho * s;
				const left = cx + c.x * s - w / 2;
				const top = cy + c.y * s;
				return (
					<div key={i} style={{position: 'absolute', left, top, width: w, transform: 'translateY(-50%)', opacity: op}}>
						<CosaDigital c={c} w={w} abre={abreBoveda} carga={carga} />
					</div>
				);
			})}
			{children}
		</AbsoluteFill>
	);
};

const CosaDigital: React.FC<{c: Cosa; w: number; abre: number; carga: number}> = ({c, w, abre, carga}) => {
	if (c.tipo === 'chat')
		return (
			<div style={{display: 'flex', gap: w * 0.04, alignItems: 'flex-start', flexDirection: c.lado && c.lado < 0 ? 'row' : 'row-reverse'}}>
				<div style={{width: w * 0.16, height: w * 0.16, borderRadius: '50%', background: c.lado && c.lado < 0 ? NEON_C : NEON_R, border: `${w * 0.012}px solid #fff`, flexShrink: 0}} />
				<div style={{flex: 1, padding: w * 0.04, borderRadius: w * 0.05, background: 'rgba(30,10,60,0.9)', border: `${w * 0.01}px solid ${NEON_M}`, boxShadow: `0 0 ${w * 0.08}px ${NEON_M}`}}>
					{[0.9, 0.6, 0.75].map((k, i) => (
						<div key={i} style={{height: w * 0.035, width: `${k * 100}%`, background: 'rgba(255,255,255,0.55)', borderRadius: 6, marginTop: i ? w * 0.025 : 0}} />
					))}
				</div>
			</div>
		);
	if (c.tipo === 'cartel')
		return <div style={{textAlign: 'center', fontFamily: CONDENSADA, fontSize: w * 0.16, color: '#fff', textShadow: `0 0 ${w * 0.04}px ${NEON_R}, 0 0 ${w * 0.1}px ${NEON_R}`, whiteSpace: 'nowrap'}}>{c.texto}</div>;
	if (c.tipo === 'carpeta')
		return (
			<div style={{position: 'relative', height: w * 0.72}}>
				<div style={{position: 'absolute', left: 0, top: 0, width: '40%', height: '18%', background: '#ffcf5a', border: `${w * 0.02}px solid ${TINTA}`, borderRadius: `${w * 0.04}px ${w * 0.04}px 0 0`}} />
				<div style={{position: 'absolute', left: 0, right: 0, top: '14%', bottom: 0, background: '#ffd86a', border: `${w * 0.02}px solid ${TINTA}`, borderRadius: w * 0.03, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
					<div style={{fontFamily: CONDENSADA, fontSize: w * 0.13, color: '#c4262e', transform: 'rotate(-8deg)', border: `${w * 0.015}px solid #c4262e`, padding: `0 ${w * 0.03}px`}}>{c.texto}</div>
				</div>
			</div>
		);
	if (c.tipo === 'boveda')
		return (
			<div style={{position: 'relative', height: w}}>
				<div style={{position: 'absolute', inset: 0, borderRadius: '50%', background: '#1a1030', border: `${w * 0.04}px solid ${NEON_M}`, boxShadow: `0 0 ${w * 0.1}px ${NEON_M}`}} />
				<div style={{position: 'absolute', inset: w * 0.06, borderRadius: '50%', background: 'radial-gradient(circle, #ffd86a, #ff4fa3 60%, #2a0f4a)', opacity: abre}} />
				<div style={{position: 'absolute', inset: w * 0.06, borderRadius: '50%', transformOrigin: '0% 50%', transform: `perspective(${w * 3}px) rotateY(${-abre * 100}deg)`, background: 'radial-gradient(circle at 40% 40%, #6a6f86, #2e3144)', border: `${w * 0.03}px solid #9aa0c0`}}>
					<div style={{position: 'absolute', left: '35%', top: '35%', width: '30%', height: '30%', borderRadius: '50%', border: `${w * 0.03}px solid #c9cde0`}} />
					{[0, 60, 120].map((a) => (
						<div key={a} style={{position: 'absolute', left: '48%', top: '20%', width: '4%', height: '60%', background: '#c9cde0', transform: `rotate(${a + abre * 180}deg)`}} />
					))}
				</div>
			</div>
		);
	// barra de carga
	return (
		<div style={{padding: w * 0.04, borderRadius: w * 0.04, background: 'rgba(20,6,40,0.9)', border: `${w * 0.012}px solid ${NEON_C}`, boxShadow: `0 0 ${w * 0.08}px ${NEON_C}`}}>
			<div style={{fontFamily: CONDENSADA, fontSize: w * 0.08, color: '#fff', marginBottom: w * 0.03}}>{c.texto}</div>
			<div style={{height: w * 0.07, borderRadius: w * 0.035, background: '#2a1450', overflow: 'hidden'}}>
				<div style={{height: '100%', width: `${carga * 100}%`, background: `linear-gradient(90deg, ${NEON_C}, ${NEON_R})`}} />
			</div>
			<div style={{fontFamily: MONO, fontWeight: 700, fontSize: w * 0.06, color: NEON_C, marginTop: w * 0.02}}>{Math.round(carga * 100)} %</div>
		</div>
	);
};

/** Mosaico de 90 miniaturas (foro) que explota hacia fuera desde el centro. */
export const Miniaturas: React.FC<{desde: number}> = ({desde}) => {
	const f = useCurrentFrame();
	const l = f - desde;
	if (l < 0) return null;
	const cols = 9;
	const filas = 10;
	const w = 104;
	const h = 66;
	const x0 = 540 - (cols * (w + 8)) / 2;
	const y0 = 360;
	return (
		<>
			{Array.from({length: cols * filas}).map((_, i) => {
				const c = i % cols;
				const r = Math.floor(i / cols);
				const tx = x0 + c * (w + 8);
				const ty = y0 + r * (h + 10);
				const retardo = ((i * 7) % 13) * 0.6;
				const p = interpolate(l - retardo, [0, 10], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.4))});
				const x = 540 + (tx - 540) * p;
				const y = 860 + (ty - 860) * p;
				const color = [NEON_M, NEON_R, NEON_C, '#ffd86a'][i % 4];
				return (
					<div key={i} style={{position: 'absolute', left: x, top: y, width: w, height: h, transform: `scale(${p})`, background: '#140a26', border: `4px solid ${color}`, borderRadius: 6, boxShadow: `0 0 10px ${color}88`, overflow: 'hidden'}}>
						<div style={{position: 'absolute', left: '10%', right: '30%', bottom: '18%', height: '22%', background: `${color}55`}} />
						<div style={{position: 'absolute', left: '40%', top: '28%', width: 0, height: 0, borderTop: '11px solid transparent', borderBottom: '11px solid transparent', borderLeft: `18px solid #ffffff`}} />
					</div>
				);
			})}
			<div style={{position: 'absolute', left: 0, right: 0, top: 1150, textAlign: 'center', fontFamily: ROTULADO, fontSize: 150, color: '#ffffff', WebkitTextStroke: `14px ${TINTA}`, paintOrder: 'stroke', opacity: interpolate(l, [6, 12], [0, 1], clamp), textShadow: `0 0 30px ${NEON_R}`}}>90</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 300, textAlign: 'center', fontFamily: TITULAR, fontWeight: 900, fontSize: 40, color: '#ffffff', letterSpacing: 6, opacity: interpolate(l, [0, 8], [0, 1], clamp)}}>FORO · NUEVO TEMA · 90 VIDEOS</div>
		</>
	);
};

/** Fortaleza de servidores en neón (al final de la línea de luz). (x, y) = base. */
export const Fortaleza: React.FC<{x: number; y: number; ancho: number; abre: number}> = ({x, y, ancho, abre}) => {
	const f = useCurrentFrame();
	const alto = ancho * 0.9;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto, width: ancho, height: alto}}>
			{[0, 1, 2, 3, 4].map((i) => {
				const torre = i === 0 || i === 4;
				const h = torre ? alto : alto * 0.72;
				return (
					<div key={i} style={{position: 'absolute', left: (i * ancho) / 5, bottom: 0, width: ancho / 5 - 8, height: h, background: '#120a26', border: `6px solid ${NEON_M}`, boxShadow: `0 0 18px ${NEON_M}`, boxSizing: 'border-box'}}>
						{Array.from({length: Math.floor(h / 40)}).map((_, k) => (
							<div key={k} style={{position: 'absolute', left: '15%', right: '15%', top: 14 + k * 40, height: 18, background: '#241640', borderRadius: 3}}>
								<div style={{position: 'absolute', right: 6, top: 5, width: 8, height: 8, borderRadius: '50%', background: (f + i * 5 + k * 3) % 11 < 6 ? NEON_C : NEON_R}} />
							</div>
						))}
					</div>
				);
			})}
			<Candado x={ancho / 2} y={alto * 0.45} tam={ancho * 0.34} abre={abre} color={NEON_C} />
		</div>
	);
};

/** Celular moderno en la mano (coordenadas de la mano: puño en (0, 36)); la pantalla brilla. */
export const TelefonoMano: React.FC<{rot?: number; brillo?: number}> = ({rot = 0, brillo = 1}) => (
	<g transform={`rotate(${rot} 0 36)`}>
		{brillo > 0 && <ellipse cx={0} cy={70} rx={110} ry={120} fill="#9fb8ff" opacity={0.18 * brillo} />}
		<rect x={-34} y={0} width={68} height={130} rx={14} fill="#111216" stroke={TINTA} strokeWidth={6} />
		<rect x={-27} y={9} width={54} height={112} rx={8} fill={brillo > 0 ? '#3a2a7a' : '#1a1b22'} />
		{brillo > 0 && [24, 44, 64, 84].map((y) => <rect key={y} x={-20} y={y} width={y % 40 ? 30 : 40} height={8} rx={3} fill="#d9c8ff" opacity={0.8} />)}
	</g>
);

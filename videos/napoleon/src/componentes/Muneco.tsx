import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {Accesorios, Boca, CabezaSVG, Cejas, Diseno, Ojos} from './Personaje';

/*
 * Muñeco de cuerpo completo al estilo del video de referencia ("Short 4"):
 * cabeza blanca redonda y expresiva, ropa con volumen, guantes blancos con dedos y botas.
 * Lienzo: 400 x 900. Suela en y = 880, coronilla en y = 10.
 * Los brazos y piernas son articulados (hombro/codo, cadera/rodilla) y las poses se interpolan entre claves,
 * así los personajes HACEN cosas: señalan, levantan, sostienen objetos, saltan, caminan, se agachan.
 */

const TINTA = '#1b1b1f';
export const LIENZO = {ancho: 400, alto: 900};
/** proporción del lienzo que ocupa la persona (coronilla → suela) */
export const FRACCION_ESTATURA = 870 / 900;

export type Mano = 'relajada' | 'abierta' | 'puno' | 'pulgar' | 'senala' | 'agarra' | 'oculta';

export type Pose = {
	/** brazo izquierdo (el de la izquierda de la pantalla): ángulo del hombro y flexión del codo, en grados.
	 *  0 = colgando, 90 = horizontal hacia afuera, 180 = arriba, negativo = cruza por delante del cuerpo */
	bi: number;
	ci: number;
	bd: number;
	cd: number;
	/** giro extra de cada muñeca */
	wi: number;
	wd: number;
	/** apertura de cada pierna (grados) */
	pi: number;
	pd: number;
	/** cuánto levanta cada pie (0..1) */
	li: number;
	ld: number;
	/** inclinación del cuerpo y de la cabeza (grados) */
	cuerpo: number;
	cabeza: number;
	/** sentadilla (0..1): baja la cadera y dobla las rodillas */
	agacha: number;
	/** salto: sube todo el cuerpo (px del lienzo) */
	salto: number;
	mi: Mano;
	md: Mano;
	/** dibujar ese brazo por delante de la cabeza (p. ej. mano en la barbilla) */
	frenteI: number;
	frenteD: number;
};

export const POSE_BASE: Pose = {
	bi: 12, ci: -10, bd: 12, cd: -10, wi: 0, wd: 0,
	pi: 3, pd: 3, li: 0, ld: 0, cuerpo: 0, cabeza: 0, agacha: 0, salto: 0,
	mi: 'relajada', md: 'relajada', frenteI: 0, frenteD: 0,
};

/* ---------------- geometría ---------------- */

const HOMBRO = {i: [124, 318] as const, d: [276, 318] as const};
const L1 = 118;
const L2 = 110;
const CADERA_Y = 585;
const CADERA = {i: 160, d: 240};
const MUSLO = 134;
const PIERNA_TOTAL = 264; // cadera → tobillo estando de pie

const rad = (g: number) => (g * Math.PI) / 180;
const dir = (lado: number, g: number): [number, number] => [lado * Math.sin(rad(g)), Math.cos(rad(g))];

export const brazoFK = (lado: -1 | 1, a: number, c: number) => {
	const s = lado < 0 ? HOMBRO.i : HOMBRO.d;
	const [dx, dy] = dir(lado, a);
	const e: [number, number] = [s[0] + dx * L1, s[1] + dy * L1];
	const [fx, fy] = dir(lado, a + c);
	const m: [number, number] = [e[0] + fx * L2, e[1] + fy * L2];
	return {s, e, m, ang: a + c};
};

/** Cinemática inversa: ángulos para que la muñeca llegue a (x, y) del lienzo. El codo queda hacia afuera. */
export const ik = (lado: -1 | 1, x: number, y: number, codoAdentro = false): {a: number; c: number} => {
	const s = lado < 0 ? HOMBRO.i : HOMBRO.d;
	let dx = x - s[0];
	let dy = y - s[1];
	let d = Math.hypot(dx, dy);
	const max = L1 + L2 - 0.5;
	const min = Math.abs(L1 - L2) + 1;
	if (d > max) {
		dx *= max / d;
		dy *= max / d;
		d = max;
	}
	if (d < min) d = min;
	const tT = (Math.atan2(lado * dx, dy) * 180) / Math.PI;
	const alfa = (Math.acos(Math.min(1, Math.max(-1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)))) * 180) / Math.PI;
	const opciones = [tT + alfa, tT - alfa].map((a) => {
		const [ex] = dir(lado, a);
		const exAbs = s[0] + ex * L1;
		const ox = s[0] + dx;
		const oy = s[1] + dy;
		const e = [exAbs, s[1] + dir(lado, a)[1] * L1];
		const f = (Math.atan2(lado * (ox - e[0]), oy - e[1]) * 180) / Math.PI;
		return {a, c: f - a, fuera: lado * (exAbs - 200)};
	});
	opciones.sort((p, q) => (codoAdentro ? p.fuera - q.fuera : q.fuera - p.fuera));
	return {a: opciones[0].a, c: opciones[0].c};
};

/**
 * Ángulos para que la PUNTA de un objeto largo (puntero, espada) sostenido en esa mano toque (tx, ty) del lienzo.
 * `largo` = distancia de la muñeca a la punta, a lo largo del antebrazo.
 */
export const apuntar = (lado: -1 | 1, tx: number, ty: number, largo: number): {a: number; c: number} => {
	const s = lado < 0 ? HOMBRO.i : HOMBRO.d;
	let mejor = {a: 0, c: 0, err: 1e9};
	for (let g = 0; g < 360; g += 0.5) {
		const [ux, uy] = dir(lado, g);
		const ex = tx - ux * (L2 + largo);
		const ey = ty - uy * (L2 + largo);
		const err = Math.abs(Math.hypot(ex - s[0], ey - s[1]) - L1);
		const a = (Math.atan2(lado * (ex - s[0]), ey - s[1]) * 180) / Math.PI;
		const fuera = lado * (ex - 200);
		const puntaje = err - fuera * 0.02;
		if (puntaje < mejor.err) mejor = {a, c: g - a, err: puntaje};
	}
	return {a: mejor.a, c: mejor.c};
};

/** Brazo casi estirado apuntando hacia (tx, ty) del lienzo: el dedo índice sigue la línea del antebrazo. */
export const senalar = (lado: -1 | 1, tx: number, ty: number, alcance = 0.93): {a: number; c: number} => {
	const s = lado < 0 ? HOMBRO.i : HOMBRO.d;
	const dx = tx - s[0];
	const dy = ty - s[1];
	const d = Math.hypot(dx, dy) || 1;
	const r = (L1 + L2) * alcance;
	return ik(lado, s[0] + (dx / d) * r, s[1] + (dy / d) * r);
};

/** Pose con las manos en puntos concretos del lienzo. */
export const manosEn = (izq?: [number, number], der?: [number, number], extra: Partial<Pose> = {}, codoAdentro = false): Partial<Pose> => {
	const p: Partial<Pose> = {...extra};
	if (izq) {
		const r = ik(-1, izq[0], izq[1], codoAdentro);
		p.bi = r.a;
		p.ci = r.c;
	}
	if (der) {
		const r = ik(1, der[0], der[1], codoAdentro);
		p.bd = r.a;
		p.cd = r.c;
	}
	return p;
};

/* ---------------- poses con nombre ---------------- */

export const POSES = {
	base: {} as Partial<Pose>,
	firme: {bi: 4, ci: 0, bd: 4, cd: 0, pi: 1, pd: 1},
	jarras: {...manosEn([150, 548], [250, 548]), mi: 'puno', md: 'puno'} as Partial<Pose>,
	brazosArriba: {bi: 160, ci: 10, bd: 160, cd: 10, mi: 'abierta', md: 'abierta'} as Partial<Pose>,
	victoria: {bi: 150, ci: 20, bd: 150, cd: 20, mi: 'puno', md: 'puno'} as Partial<Pose>,
	encogeHombros: {...manosEn([34, 438], [366, 438], {}, true), mi: 'abierta', md: 'abierta', wi: 18, wd: 18, cabeza: -6} as Partial<Pose>,
	cruzados: {...manosEn([256, 446], [146, 432]), mi: 'oculta', md: 'puno'} as Partial<Pose>,
	pulgarArriba: {...manosEn(undefined, [236, 392]), md: 'pulgar'} as Partial<Pose>,
	manoEnChaleco: {...manosEn(undefined, [212, 420], {}, true), md: 'oculta'} as Partial<Pose>,
};

/* ---------------- animación de poses ---------------- */

type Clave = [number, Partial<Pose>];
const NUMERICAS: (keyof Pose)[] = ['bi', 'ci', 'bd', 'cd', 'wi', 'wd', 'pi', 'pd', 'li', 'ld', 'cuerpo', 'cabeza', 'agacha', 'salto', 'frenteI', 'frenteD'];

/**
 * Interpola poses entre claves [cuadro, pose]. Cada clave hereda lo que no define de la anterior.
 * Las transiciones duran `transicion` cuadros (con anticipación suave) y terminan en el cuadro de la clave.
 */
export const animarPose = (f: number, claves: Clave[], transicion = 9): Partial<Pose> => {
	if (claves.length === 0) return {};
	const completas: [number, Pose][] = [];
	let acumulada: Pose = {...POSE_BASE};
	for (const [c, p] of claves) {
		acumulada = {...acumulada, ...p};
		completas.push([c, acumulada]);
	}
	let i = completas.length - 1;
	while (i > 0 && f < completas[i][0]) i--;
	const [c1, p1] = completas[i];
	const sig = completas[i + 1];
	if (i === 0 && f < c1) return completas[0][1];
	if (!sig) return p1;
	const [c2, p2] = sig;
	const inicio = Math.max(c1, c2 - transicion);
	const t = interpolate(f, [inicio, c2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
	const r: Pose = {...p1};
	for (const k of NUMERICAS) (r[k] as number) = (p1[k] as number) + ((p2[k] as number) - (p1[k] as number)) * t;
	r.mi = t > 0.5 ? p2.mi : p1.mi;
	r.md = t > 0.5 ? p2.md : p1.md;
	return r;
};

/* ---------------- ropa ---------------- */

export type Ropa = {
	cabeza: Diseno;
	casaca: string;
	casacaSombra: string;
	/** chaleco visible por la casaca abierta */
	chaleco?: string;
	solapas?: string;
	cuello?: string;
	botones?: string;
	faldones?: boolean;
	punos?: string;
	pantalon: string;
	pantalonSombra?: string;
	/** botas altas hasta la rodilla */
	botas?: string;
	/** medias + zapatos (siglo XVIII) */
	medias?: string;
	zapatos?: string;
	hebilla?: boolean;
	charreteras?: string;
	banda?: string;
	fajin?: string;
	correajes?: boolean;
	corbata?: string;
	rayas?: string;
	guantes?: string;
	/** cinturón con hebilla */
	cinturon?: string;
};

/* ---------------- manos ---------------- */

type Forma = {c: [number, number, number][]; k: [number, number, number, number, number][]; lineas?: string[]};

const FORMAS: Record<Exclude<Mano, 'oculta'>, Forma> = {
	relajada: {
		c: [[0, 34, 27]],
		k: [[-13, 42, -15, 70, 15], [-4, 46, -5, 78, 15], [5, 46, 5, 78, 15], [13, 42, 14, 70, 15], [20, 26, 32, 50, 15]],
	},
	abierta: {
		c: [[0, 34, 27]],
		k: [[-8, 46, -32, 86, 15], [-3, 48, -11, 96, 15], [3, 48, 11, 96, 15], [8, 46, 30, 86, 15], [20, 28, 50, 46, 15]],
	},
	puno: {
		c: [[0, 36, 30]],
		k: [[-19, 56, 19, 56, 24], [22, 24, 4, 44, 15]],
		lineas: ['M -8 46 L -8 66', 'M 4 46 L 4 67', 'M 14 44 L 15 63'],
	},
	pulgar: {
		c: [[0, 36, 30]],
		k: [[-19, 56, 19, 56, 24], [18, 30, 58, 24, 18]],
		lineas: ['M -8 46 L -8 66', 'M 4 46 L 4 67'],
	},
	senala: {
		c: [[0, 36, 30]],
		k: [[-17, 56, 12, 56, 22], [-6, 50, -6, 108, 16], [22, 24, 4, 44, 15]],
		lineas: ['M 4 48 L 4 66'],
	},
	agarra: {
		c: [[0, 36, 30]],
		k: [[-19, 56, 19, 56, 24], [22, 26, -2, 30, 16]],
		lineas: ['M -8 46 L -8 66', 'M 4 46 L 4 67', 'M 14 44 L 15 63'],
	},
};

const ManoSVG: React.FC<{tipo: Mano; color: string}> = ({tipo, color}) => {
	if (tipo === 'oculta') return null;
	const fz = FORMAS[tipo];
	const capa = (borde: boolean) => (
		<g>
			{fz.c.map(([cx, cy, r], i) => (
				<circle key={`c${i}`} cx={cx} cy={cy} r={r + (borde ? 6 : 0)} fill={borde ? TINTA : color} />
			))}
			{fz.k.map(([x1, y1, x2, y2, w], i) => (
				<line key={`k${i}`} x1={x1} y1={y1} x2={x2} y2={y2} stroke={borde ? TINTA : color} strokeWidth={w + (borde ? 12 : 0)} strokeLinecap="round" />
			))}
		</g>
	);
	return (
		<g>
			{capa(true)}
			{capa(false)}
			{fz.lineas?.map((d, i) => <path key={i} d={d} stroke={TINTA} strokeWidth={4} strokeLinecap="round" fill="none" opacity={0.75} />)}
			{/* puño del guante */}
			<path d="M -26 -6 L 26 -6 L 30 12 L -30 12 Z" fill={color} stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
		</g>
	);
};

/* ---------------- componente ---------------- */

export type MunecoProps = {
	ropa: Ropa;
	pose?: Partial<Pose>;
	ojos?: Ojos;
	cejas?: Cejas;
	boca?: Boca;
	hablando?: boolean;
	/** ciclo de caminar (velocidad: 1 = normal) */
	camina?: number;
	/** intensidad del vaivén de risa / enojo (0 = quieto) */
	tiembla?: number;
	respira?: boolean;
	parpadea?: boolean;
	semilla?: number;
	sombra?: boolean;
	acc?: Accesorios;
	/** objetos en la mano (coordenadas de la mano: origen en la muñeca, +y hacia los dedos, puño en (0, 36)) */
	objIzq?: React.ReactNode;
	objDer?: React.ReactNode;
	/** objeto delante del pecho (coordenadas del lienzo), por debajo de los brazos */
	objPecho?: React.ReactNode;
	/** algo por delante de todo (mesa, mostrador) en coordenadas del lienzo */
	delante?: React.ReactNode;
	/** detrás de todo el cuerpo (capa, silla) */
	detras?: React.ReactNode;
	/** cabeza más grande (caricatura) */
	escalaCabeza?: number;
};

export const Muneco: React.FC<MunecoProps> = ({
	ropa,
	pose: poseParcial = {},
	ojos = 'normal',
	cejas = 'neutral',
	boca = 'sonrisa',
	hablando = false,
	camina = 0,
	tiembla = 0,
	respira = true,
	parpadea = true,
	semilla = 0,
	sombra = true,
	acc = {},
	objIzq,
	objDer,
	objPecho,
	delante,
	detras,
	escalaCabeza = 1,
}) => {
	const f0 = useCurrentFrame();
	const f = f0 + semilla * 17;
	const p: Pose = {...POSE_BASE, ...poseParcial};
	const idRayas = `rayas-${React.useId().replace(/:/g, '')}`;

	// --- caminar ---
	if (camina) {
		const fase = (f0 * 0.42 * camina) % (Math.PI * 2);
		p.li += Math.max(0, Math.sin(fase)) * 0.32;
		p.ld += Math.max(0, -Math.sin(fase)) * 0.32;
		p.bi += Math.sin(fase) * 16;
		p.bd -= Math.sin(fase) * 16;
		p.salto += Math.abs(Math.sin(fase)) * 10;
		p.cuerpo += Math.sin(fase) * 2;
	}
	// vaivén suave (risa, enojo, nervios): una oscilación lenta, nunca un temblor
	const vaiven = tiembla ? Math.sin(f0 * 0.5) : 0;
	const temblor = tiembla * 1.1 * vaiven;
	if (tiembla) p.salto += Math.abs(vaiven) * 5 * tiembla;
	const resp = respira ? Math.sin(f / 7) : 0;
	const parpadeo = parpadea && f % 97 > 93;
	let bocaFinal = boca;
	if (hablando) bocaFinal = (['abierta', 'o', 'abierta', 'seria'] as Boca[])[Math.floor(f / 3) % 4];

	const baja = p.agacha * 150;
	const caderaY = CADERA_Y + baja;
	const piel = ropa.guantes ?? '#ffffff';

	// --- piernas ---
	const pierna = (lado: -1 | 1) => {
		const hx = lado < 0 ? CADERA.i : CADERA.d;
		const apertura = lado < 0 ? p.pi : p.pd;
		const levanta = lado < 0 ? p.li : p.ld;
		const [dx, dy] = dir(lado, apertura);
		const ax = hx + dx * PIERNA_TOTAL + lado * levanta * 18;
		const ay = CADERA_Y + dy * PIERNA_TOTAL - levanta * 170;
		const h: [number, number] = [hx, caderaY];
		const d = Math.min(Math.hypot(ax - h[0], ay - h[1]), MUSLO * 2 - 0.5);
		const flexMin = 6;
		const mx = (h[0] + ax) / 2;
		const my = (h[1] + ay) / 2;
		const flex = Math.max(flexMin, Math.sqrt(Math.max(0, MUSLO * MUSLO - (d / 2) * (d / 2))));
		// perpendicular hacia afuera
		let px = -(ay - h[1]);
		let py = ax - h[0];
		const n = Math.hypot(px, py) || 1;
		px /= n;
		py /= n;
		if (px * lado < 0) {
			px = -px;
			py = -py;
		}
		const rodilla: [number, number] = [mx + px * flex, my + py * flex];
		const tobillo: [number, number] = [ax, ay];
		const tramo = `M ${h[0]} ${h[1]} L ${rodilla[0]} ${rodilla[1]} L ${tobillo[0]} ${tobillo[1]}`;
		const bota = ropa.botas;
		const caña: [number, number] = [rodilla[0] + (tobillo[0] - rodilla[0]) * 0.08, rodilla[1] + (tobillo[1] - rodilla[1]) * 0.08];
		return (
			<g key={lado}>
				<path d={tramo} stroke={TINTA} strokeWidth={78} fill="none" strokeLinecap="round" strokeLinejoin="round" />
				<path d={tramo} stroke={ropa.pantalon} strokeWidth={64} fill="none" strokeLinecap="round" strokeLinejoin="round" />
				{ropa.pantalonSombra && <path d={tramo} stroke={ropa.pantalonSombra} strokeWidth={18} fill="none" strokeLinecap="round" strokeLinejoin="round" transform={`translate(${lado * 18} 0)`} opacity={0.6} />}
				{bota && (
					<g>
						<path d={`M ${caña[0]} ${caña[1]} L ${tobillo[0]} ${tobillo[1]}`} stroke={TINTA} strokeWidth={84} strokeLinecap="round" />
						<path d={`M ${caña[0]} ${caña[1]} L ${tobillo[0]} ${tobillo[1]}`} stroke={bota} strokeWidth={70} strokeLinecap="round" />
						<path d={`M ${caña[0] - 40} ${caña[1] + 4} Q ${caña[0]} ${caña[1] - 22} ${caña[0] + 40} ${caña[1] + 4}`} stroke={TINTA} strokeWidth={22} fill="none" strokeLinecap="round" />
						<path d={`M ${caña[0] - 40} ${caña[1] + 4} Q ${caña[0]} ${caña[1] - 22} ${caña[0] + 40} ${caña[1] + 4}`} stroke={bota} strokeWidth={10} fill="none" strokeLinecap="round" />
						<path d={`M ${caña[0] - lado * 14} ${caña[1] + 30} L ${tobillo[0] - lado * 14} ${tobillo[1] - 20}`} stroke="#ffffff" strokeWidth={6} opacity={0.18} strokeLinecap="round" />
					</g>
				)}
				{!bota && ropa.medias && (
					<g>
						<path d={`M ${rodilla[0]} ${rodilla[1] + 6} L ${tobillo[0]} ${tobillo[1]}`} stroke={TINTA} strokeWidth={60} strokeLinecap="round" />
						<path d={`M ${rodilla[0]} ${rodilla[1] + 6} L ${tobillo[0]} ${tobillo[1]}`} stroke={ropa.medias} strokeWidth={48} strokeLinecap="round" />
					</g>
				)}
				{/* pie */}
				<g transform={`translate(${tobillo[0]} ${tobillo[1]}) scale(${lado} 1)`}>
					<path d="M -34 -14 Q -36 -34 -4 -34 Q 20 -34 26 -16 Q 58 -14 64 6 Q 66 26 50 30 L -32 30 Q -42 26 -34 -14 Z" fill={bota ?? ropa.zapatos ?? TINTA} stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
					<path d="M -34 22 L 58 22" stroke={TINTA} strokeWidth={6} opacity={0.5} />
					{ropa.hebilla && <rect x={4} y={-24} width={22} height={16} rx={3} fill="none" stroke="#d6b04a" strokeWidth={5} />}
				</g>
			</g>
		);
	};

	// --- brazos ---
	const brazo = (lado: -1 | 1) => {
		const a = lado < 0 ? p.bi : p.bd;
		const c = lado < 0 ? p.ci : p.cd;
		const w = lado < 0 ? p.wi : p.wd;
		const mano = lado < 0 ? p.mi : p.md;
		const {s, e, m, ang} = brazoFK(lado, a, c);
		// manga curva: sale en la dirección del brazo y llega en la del antebrazo (codo redondeado, sin quiebres)
		const k = 0.58;
		const c1 = [s[0] + (e[0] - s[0]) * k, s[1] + (e[1] - s[1]) * k];
		const c2 = [m[0] + (e[0] - m[0]) * k, m[1] + (e[1] - m[1]) * k];
		const tramo = `M ${s[0]} ${s[1]} C ${c1[0]} ${c1[1]} ${c2[0]} ${c2[1]} ${m[0]} ${m[1]}`;
		const [fx, fy] = dir(lado, ang);
		const giro = -lado * (ang + w);
		const espejo = lado < 0 ? 1 : -1;
		const obj = lado < 0 ? objIzq : objDer;
		return (
			<g key={lado}>
				<path d={tramo} stroke={TINTA} strokeWidth={60} fill="none" strokeLinecap="round" />
				<path d={tramo} stroke={ropa.casaca} strokeWidth={46} fill="none" strokeLinecap="round" />
				{ropa.punos && mano !== 'oculta' && (
					<path d={`M ${m[0] - fx * 26} ${m[1] - fy * 26} L ${m[0] - fx * 4} ${m[1] - fy * 4}`} stroke={TINTA} strokeWidth={62} strokeLinecap="butt" />
				)}
				{ropa.punos && mano !== 'oculta' && (
					<path d={`M ${m[0] - fx * 24} ${m[1] - fy * 24} L ${m[0] - fx * 6} ${m[1] - fy * 6}`} stroke={ropa.punos} strokeWidth={50} strokeLinecap="butt" />
				)}
				<g transform={`translate(${m[0]} ${m[1]}) rotate(${giro}) scale(${espejo} 1)`}>
					{obj}
					<ManoSVG tipo={mano} color={piel} />
				</g>
			</g>
		);
	};

	const torso = 'M 116 300 Q 126 284 166 280 L 234 280 Q 274 284 284 300 Q 300 420 294 552 Q 200 568 106 552 Q 100 420 116 300 Z';
	const botones = ropa.botones ?? '#d9b03a';

	const charreteras = ropa.charreteras && (
		<g>
			{[HOMBRO.i, HOMBRO.d].map(([x, y], i) => (
				<g key={i}>
					<ellipse cx={x + (i ? -4 : 4)} cy={y - 18} rx={44} ry={18} fill={ropa.charreteras} stroke={TINTA} strokeWidth={6} />
					{[-30, -18, -6, 6, 18, 30].map((dx) => (
						<line key={dx} x1={x + dx} y1={y - 4} x2={x + dx * 1.08} y2={y + 22} stroke={ropa.charreteras} strokeWidth={6} strokeLinecap="round" />
					))}
				</g>
			))}
		</g>
	);

	const brazoI = brazo(-1);
	const brazoD = brazo(1);

	return (
		<svg viewBox="0 0 400 900" width="100%" height="100%" style={{overflow: 'visible'}}>
			{sombra && <ellipse cx={200} cy={884} rx={150 * Math.max(0.5, 1 - p.salto / 500)} ry={22} fill="rgba(0,0,0,0.28)" />}
			<g transform={`translate(0 ${-p.salto})`}>
				{detras}
				{/* faldones de la casaca (detrás de las piernas) */}
				{ropa.faldones && (
					<g transform={`translate(0 ${baja}) rotate(${p.cuerpo + temblor} 200 ${CADERA_Y})`}>
						<path d="M 112 520 Q 92 650 100 748 Q 140 758 172 726 L 200 600 L 228 726 Q 260 758 300 748 Q 308 650 288 520 Z" fill={ropa.casaca} stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
						<path d="M 278 540 Q 292 640 288 736" stroke={ropa.casacaSombra} strokeWidth={16} fill="none" opacity={0.6} />
					</g>
				)}
				{/* piernas */}
				{pierna(-1)}
				{pierna(1)}
				{/* cadera */}
				<path d={`M 116 ${caderaY - 70} L 284 ${caderaY - 70} L 290 ${caderaY + 14} Q 200 ${caderaY + 40} 110 ${caderaY + 14} Z`} fill={ropa.pantalon} stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
				{/* tronco, brazos y cabeza */}
				<g transform={`translate(0 ${baja}) rotate(${p.cuerpo + temblor} 200 ${CADERA_Y})`}>
					<g transform={`translate(200 552) scale(${1 + resp * 0.01} ${1 - resp * 0.012}) translate(-200 -552)`}>
						<path d={torso} fill={ropa.casaca} stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
						{ropa.rayas && (
							<g>
								<clipPath id={idRayas}>
									<path d={torso} />
								</clipPath>
								<g clipPath={`url(#${idRayas})`}>
									{[318, 362, 406, 450, 494, 538].map((y) => (
										<path key={y} d={`M 90 ${y} Q 200 ${y + 12} 310 ${y}`} stroke={ropa.rayas} strokeWidth={18} fill="none" />
									))}
								</g>
								<path d={torso} fill="none" stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
							</g>
						)}
						{/* sombra lateral */}
						<path d="M 270 300 Q 292 420 286 548 Q 266 556 248 558 Q 270 430 252 296 Z" fill={ropa.casacaSombra} opacity={0.55} />
						{ropa.chaleco && (
							<g>
								<path d="M 172 282 L 228 282 L 240 552 Q 200 562 160 552 Z" fill={ropa.chaleco} stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
								{[340, 390, 440, 490].map((y) => (
									<circle key={y} cx={200} cy={y} r={6} fill={botones} stroke={TINTA} strokeWidth={3} />
								))}
							</g>
						)}
						{ropa.solapas && (
							<g fill={ropa.solapas} stroke={TINTA} strokeWidth={6} strokeLinejoin="round">
								<path d="M 172 284 L 140 306 L 150 470 L 166 470 L 172 284 Z" />
								<path d="M 228 284 L 260 306 L 250 470 L 234 470 L 228 284 Z" />
							</g>
						)}
						{ropa.solapas &&
							[322, 368, 414, 456].map((y) => (
								<g key={y}>
									<circle cx={152} cy={y} r={6.5} fill={botones} stroke={TINTA} strokeWidth={3} />
									<circle cx={248} cy={y} r={6.5} fill={botones} stroke={TINTA} strokeWidth={3} />
								</g>
							))}
						{!ropa.chaleco && !ropa.rayas && !ropa.solapas && (
							<g>
								<line x1={200} y1={300} x2={200} y2={552} stroke={TINTA} strokeWidth={5} />
								{[350, 410, 470].map((y) => (
									<circle key={y} cx={214} cy={y} r={7} fill={botones} stroke={TINTA} strokeWidth={3} />
								))}
								<path d="M 138 352 L 182 352 L 182 392 L 138 392 Z" fill="none" stroke={TINTA} strokeWidth={4} opacity={0.5} />
							</g>
						)}
						{ropa.correajes && (
							<g stroke={TINTA} strokeWidth={4} strokeLinejoin="round">
								<path d="M 128 300 L 160 292 L 290 540 L 262 552 Z" fill="#f4f4f4" />
								<path d="M 272 300 L 240 292 L 110 540 L 138 552 Z" fill="#f4f4f4" />
								<circle cx={200} cy={420} r={13} fill="#d9b03a" />
							</g>
						)}
						{ropa.banda && <path d="M 128 300 L 162 290 L 292 528 L 272 556 Z" fill={ropa.banda} stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />}
						{ropa.fajin && <path d="M 108 500 Q 200 520 292 500 L 294 540 Q 200 560 106 540 Z" fill={ropa.fajin} stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />}
						{ropa.cinturon && (
							<g>
								<path d="M 108 508 Q 200 526 292 508 L 293 534 Q 200 552 107 534 Z" fill={ropa.cinturon} stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
								<rect x={186} y={510} width={30} height={30} rx={4} fill="#d6b04a" stroke={TINTA} strokeWidth={5} />
							</g>
						)}
						{/* cuello alto */}
						{ropa.cuello && <path d="M 150 270 Q 200 292 250 270 L 254 300 Q 200 318 146 300 Z" fill={ropa.cuello} stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />}
						{ropa.corbata && (
							<g>
								<path d="M 176 278 Q 200 296 224 278 L 230 320 Q 200 336 170 320 Z" fill={ropa.corbata} stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
								<path d="M 186 318 L 200 360 L 214 318" fill={ropa.corbata} stroke={TINTA} strokeWidth={5} strokeLinejoin="round" />
							</g>
						)}
						{objPecho}
					</g>
					{p.frenteI < 0.5 && brazoI}
					{p.frenteD < 0.5 && brazoD}
					{charreteras}
					{/* cabeza (lienzo de 400 con radio 150 → radio 125 centrada en (200, 138)) */}
					<g transform={`translate(0 ${resp * 2}) rotate(${p.cabeza + temblor * 0.6} 200 280) translate(200 280) scale(${escalaCabeza}) translate(-200 -280)`}>
						<rect x={178} y={240} width={44} height={50} fill={piel} stroke={TINTA} strokeWidth={7} />
						<g transform="translate(33.33 -28.67) scale(0.8333)">
							<CabezaSVG d={ropa.cabeza} ojos={ojos} cejas={cejas} boca={bocaFinal} acc={acc} parpadeo={parpadeo} f={f} />
						</g>
					</g>
					{p.frenteI >= 0.5 && brazoI}
					{p.frenteD >= 0.5 && brazoD}
					{delante}
				</g>
			</g>
		</svg>
	);
};

/** Coloca un muñeco en el mundo (1080x1920) anclado por la suela. `alto` = alto del lienzo en px. */
export const Actor: React.FC<{
	x: number;
	y: number;
	alto: number;
	voltear?: boolean;
	rot?: number;
	escala?: number;
	opacidad?: number;
	children: React.ReactNode;
}> = ({x, y, alto, voltear, rot = 0, escala = 1, opacidad = 1, children}) => {
	const ancho = (alto * LIENZO.ancho) / LIENZO.alto;
	const suela = (alto * 880) / 900;
	return (
		<div
			style={{
				position: 'absolute',
				left: x - ancho / 2,
				top: y - suela,
				width: ancho,
				height: alto,
				transform: `rotate(${rot}deg) scale(${voltear ? -escala : escala}, ${escala})`,
				transformOrigin: `50% ${(880 / 900) * 100}%`,
				opacity: opacidad,
			}}
		>
			{children}
		</div>
	);
};

/** alto del lienzo para que la persona mida `cm` con `pxPorCm` */
export const altoLienzoParaCm = (cm: number, pxPorCm: number) => (cm * pxPorCm) / FRACCION_ESTATURA;

/* ---------------- vestuario del short de Napoleón ---------------- */

export const ROPA_NAPOLEON: Ropa = {
	cabeza: {piel: '#ffffff', pelo: 'mechon', colorPelo: '#2a1c12', gorra: 'bicornio', chaqueta: '', chaquetaSombra: '', botones: ''},
	casaca: '#1f3a7a',
	casacaSombra: '#132552',
	chaleco: '#f4f0e2',
	solapas: '#f4f0e2',
	cuello: '#c4262e',
	botones: '#e0b23a',
	faldones: true,
	punos: '#c4262e',
	pantalon: '#f1ece0',
	pantalonSombra: '#d9d1bd',
	botas: '#17171b',
	charreteras: '#e0b23a',
	corbata: '#ffffff',
};

/** James Gillray, el caricaturista inglés: casaca verde, chaleco mostaza, peluca empolvada */
export const ROPA_GILLRAY: Ropa = {
	cabeza: {piel: '#ffffff', pelo: 'rizado', colorPelo: '#d9d3c7', lentes: true, chaqueta: '', chaquetaSombra: '', botones: ''},
	casaca: '#3f6a3e',
	casacaSombra: '#284a29',
	chaleco: '#e0b44a',
	botones: '#b8862a',
	faldones: true,
	punos: '#f4f1e8',
	pantalon: '#d8c7a2',
	medias: '#f4f1e8',
	zapatos: '#2a1d14',
	hebilla: true,
	corbata: '#ffffff',
};

/** El médico de Santa Helena */
export const ROPA_DOCTOR: Ropa = {
	cabeza: {piel: '#ffffff', pelo: 'raya', colorPelo: '#3a2a1e', lentes: true, bigote: 'manubrio', colorBigote: '#3a2a1e', chaqueta: '', chaquetaSombra: '', botones: ''},
	casaca: '#2a2a34',
	casacaSombra: '#17171e',
	chaleco: '#ecebe6',
	botones: '#9a9a9a',
	faldones: true,
	punos: '#ffffff',
	pantalon: '#3a3a44',
	botas: '#17171b',
	corbata: '#ffffff',
};

/** Caballero inglés que lee el periódico */
export const ROPA_INGLES: Ropa = {
	cabeza: {piel: '#ffffff', gorra: 'chistera', bigote: 'manubrio', colorBigote: '#a8743a', monoculo: true, chaqueta: '', chaquetaSombra: '', botones: ''},
	casaca: '#8a2f3a',
	casacaSombra: '#5f1f28',
	chaleco: '#e9c46a',
	botones: '#c9a43a',
	faldones: true,
	punos: '#ffffff',
	pantalon: '#e6dcc2',
	botas: '#5a3a1e',
	corbata: '#ffffff',
};

/** Granadero de la Guardia Imperial */
export const ROPA_GRANADERO: Ropa = {
	cabeza: {piel: '#ffffff', gorra: 'oso', bigote: 'manubrio', colorBigote: '#3a2414', chaqueta: '', chaquetaSombra: '', botones: ''},
	casaca: '#1f3a7a',
	casacaSombra: '#132552',
	solapas: '#f4f0e2',
	cuello: '#1f3a7a',
	botones: '#e0b23a',
	faldones: true,
	punos: '#c4262e',
	pantalon: '#f1ece0',
	pantalonSombra: '#d9d1bd',
	botas: '#17171b',
	charreteras: '#c4262e',
	correajes: true,
};

/** El "francés promedio" de la época, en versión caricatura */
export const ROPA_FRANCES: Ropa = {
	cabeza: {piel: '#ffffff', gorra: 'boina', bigote: 'manubrio', colorBigote: '#3a2414', panuelo: '#e3262e', chaqueta: '', chaquetaSombra: '', botones: ''},
	casaca: '#f6f4ee',
	casacaSombra: '#d9d6cc',
	rayas: '#1f3a7a',
	pantalon: '#6b4a32',
	pantalonSombra: '#4a3222',
	medias: '#f6f4ee',
	zapatos: '#2a1d14',
	fajin: '#e3262e',
	corbata: '#e3262e',
};

import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {Destello, Etiqueta} from '../componentes/Efectos';
import {AutoLado} from '../componentes/Gamer';
import {BolsaEvidencia, Billetes, Cama, CelularChat, Colgante, EscEdificio, EscEvidencias, EscFachadaHotel, EscHospital, EscHotel, EscOficinaAlarma, FACHADA_VENTANA, Fortaleza, Laptop, Miniaturas, NEON_C, NEON_M, NEON_R, NOCHE, PantallaAlarma, PantallaHackeo, PuertaPesada, Reloj, Stick, Tele, TelefonoMano, Tunel, VENTANAS_EDIFICIO, mezclaColor} from '../componentes/Hacker';
import {Actor, Muneco, POSES, Pose, Ropa, alcanzar, animarPose, manosFrente} from '../componentes/Muneco';
import {Toma, Transicion} from '../componentes/Toma';
import {Sello} from '../componentes/Utileria';
import {ROPA_CHICO, ROPA_EMPLEADA_2, ROPA_EMPLEADO_1, ROPA_EMPLEADO_3, VECINOS} from '../componentes/Vestuario';
import {CONDENSADA, MONO, TITULAR} from '../fuentes';
import {finFrase, palabra} from '../tiempos';

/*
 * «Hackeó GTA 6 desde la tele de un hotel». Sin nombre ni parecido con el chico (era menor de edad),
 * sin logos ni imágenes reales del juego, sin burlas de su salud; la ironía con la policía va en el cartel.
 * Nunca hay cortes secos: barridos o la cámara se mete en una pantalla.
 */

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const antes = (n: number) => n - 3;
const TINTA = '#14141a';
const suave = Easing.inOut(Easing.cubic);

const W = {
	hackeo: palabra(0, 'hackeó'),
	gta0: palabra(0, 'GTA 6'),
	tele0: palabra(0, 'tele'),
	hotel0: palabra(0, 'hotel'),
	mira: palabra(1, 'Mira'),
	policia1: palabra(1, 'policía'),
	atrapado: palabra(1, 'atrapado'),
	empresas: palabra(1, 'empresas'),
	quitaron: palabra(2, 'quitaron'),
	computadora2: palabra(2, 'computadora'),
	y2: palabra(2, 'y'),
	hotel2: palabra(2, 'hotel'),
	protegerlo2: palabra(2, 'protegerlo'),
	sin3: palabra(3, 'Sin'),
	que3: palabra(3, 'qué'),
	primero: palabra(4, 'Primero'),
	chat4: palabra(4, 'chat'),
	despues: palabra(5, 'Después'),
	archivos: palabra(5, 'archivos'),
	domingo: palabra(6, 'DOMINGO'),
	sube: palabra(6, 'SUBE'),
	gta6: palabra(6, 'GTA 6'),
	foro: palabra(6, 'FORO'),
	y7: palabra(7, 'Y'),
	rien: palabra(7, 'ríen'),
	falso: palabra(8, 'falso'),
	es8: palabra(8, 'Es'),
	eso9: palabra(9, 'Eso'),
	hasta: palabra(10, 'Hasta'),
	escribe: palabra(10, 'escribe'),
	empleados: palabra(10, 'empleados'),
	si11: palabra(11, 'Si'),
	horas: palabra(11, 'horas'),
	juego11: palabra(11, 'juego'),
	y12: palabra(12, 'Y'),
	confirma: palabra(12, 'confirma'),
	los13: palabra(13, 'LOS'),
	reales: palabra(13, 'REALES'),
	y14: palabra(14, 'Y'),
	computadora14: palabra(14, 'computadora'),
	con: palabra(15, 'Con'),
	stick: palabra(15, 'Stick'),
	series: palabra(15, 'series'),
	enchufa: palabra(16, 'enchufa'),
	usa: palabra(16, 'usa'),
	entra: palabra(16, 'entra'),
	la17: palabra(17, 'La'),
	escondido: palabra(17, 'escondido'),
	cuarto: palabra(18, 'CUARTO'),
	hackear18: palabra(18, 'HACKEAR'),
	a19: palabra(19, 'A'),
	costo: palabra(19, 'costó'),
	millones: palabra(19, '5 MILLONES'),
	a20: palabra(20, 'A'),
	hospital: palabra(20, 'hospital'),
	sin20: palabra(20, 'sin'),
	salida: palabra(20, 'salida'),
	todo: palabra(21, 'TODO'),
	cuarenta: palabra(21, '40'),
	enchufado: palabra(21, 'ENCHUFADO'),
	hotel21: palabra(21, 'HOTEL'),
};

/** fin de la voz + 1,2 s: el sello de REAL ocupa el último segundo */
export const FIN_VIDEO = finFrase(21) + 40;
export const SELLO_REAL = FIN_VIDEO - 30;
/** el silencio total del giro (sin música ni efectos) */
export const GIRO: [number, number] = [finFrase(12), W.los13];

type P = {d: number; h: number; e: Transicion; s: Transicion};
const brazo = (lado: -1 | 1, r: {a: number; c: number; k?: number}): Partial<Pose> => (lado < 0 ? {bi: r.a, ci: r.c, ai: r.k ?? 1} : {bd: r.a, cd: r.c, ad: r.k ?? 1});
/** posición en pantalla de un punto del mundo, con la cámara de la Toma (escala s y desplazamiento x, y) */
const enPantalla = (wx: number, wy: number, s: number, x = 0, y = 0): [number, number] => [540 + (wx - 540) * s + x, 960 + (wy - 960) * s + y];
const tramo = (f: number, a: number, b: number, curva = suave) => interpolate(f, [a, b], [0, 1], {...clamp, easing: curva});

/* ---------- el cuarto del hotel (E1 y el final) ---------- */

const TELE = {x: 280, y: 980, ancho: 440};
const STICK = {x: TELE.x + TELE.ancho / 2 + 46, y: TELE.y + 40};

const Comoda: React.FC<{frio?: number}> = ({frio = 0}) => (
	<div style={{position: 'absolute', left: 70, top: 1150, width: 440, height: 350, background: mezclaColor('#2a2140', '#9aa0aa', frio), border: `10px solid ${TINTA}`, borderRadius: 8}}>
		{[0, 1].map((i) => (
			<div key={i} style={{position: 'absolute', left: 30, right: 30, top: 40 + i * 150, height: 110, border: `6px solid ${TINTA}`, borderRadius: 6, opacity: 0.6}}>
				<div style={{position: 'absolute', left: '45%', top: '40%', width: '10%', height: 14, background: '#c9a43a', borderRadius: 6}} />
			</div>
		))}
	</div>
);

const CuartoHotel: React.FC<{abre: number; chico?: boolean; frio?: number; encendida?: number; etiqueta?: number}> = ({abre, chico = true, frio = 0, encendida = 1, etiqueta}) => {
	const f = useCurrentFrame();
	const pantalla = {w: TELE.ancho * 0.956, h: TELE.ancho * 0.6 * 0.926};
	return (
		<>
			<Cama capa="atras" frio={frio} />
			{chico && (
				<Actor x={720} y={1560} alto={880}>
					<Muneco ropa={ROPA_CHICO} pose={{...manosFrente([150, 470]), ...brazo(1, alcanzar(1, 250, 420 + Math.sin(f / 9) * 4)), md: 'agarra', cabeza: -6}} objDer={<TelefonoMano rot={170} />} ojos="mirandoLado" cejas="arrogante" boca="picara" />
				</Actor>
			)}
			<Cama capa="delante" frio={frio} vacia={!chico} />
			<Comoda frio={frio} />
			<Tele x={TELE.x} y={TELE.y} ancho={TELE.ancho} brilloStick={encendida > 0 ? 1 : 0.4} encendida={encendida}>
				<PantallaHackeo abre={abre} w={pantalla.w} h={pantalla.h} />
			</Tele>
			<Stick x={STICK.x} y={STICK.y} largo={110} rot={0} led={encendida > 0 ? 1 : 0.5} etiqueta={etiqueta !== undefined ? '40 USD' : undefined} etiquetaDesde={etiqueta ?? 0} tamEtiqueta={1.8} />
			<Colgante x={985} y={1040} texto={'NO\nMOLESTAR'} tam={0.8} />
		</>
	);
};

/* =============================== E1 =============================== */

const E1: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscHotel />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.12], y: [0, -30], curva: 'lineal'}} golpes={[[W.gta0, 0.04]]}>
			<CuartoHotel abre={tramo(f, W.hackeo, W.gta0 + 4)} />
		</Toma>
	);
};

/* =============================== E2 =============================== */

const E2a: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const baja = tramo(f, W.quitaron - 10, W.quitaron + 6, Easing.out(Easing.cubic));
	const sello = tramo(f, W.computadora2 - 2, W.computadora2 + 12);
	const iconos = ['#ff4fa3', '#3ee8ff', '#ffd86a', '#b44dff'];
	return (
		<Toma escena={<EscEvidencias />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.14], y: [-20, -40]}} golpes={[[W.atrapado, 0.04], [W.computadora2, 0.05]]}>
			<Laptop x={540} y={1330} ancho={620}>
				<AbsoluteFill style={{background: '#0a0a18'}}>
					{iconos.map((c, i) => {
						const x = 40 + (i % 2) * 280;
						const y = 30 + Math.floor(i / 2) * 150;
						const hack = f >= W.policia1 + i * 6;
						return (
							<div key={i} style={{position: 'absolute', left: x, top: y, width: 200, height: 120, border: `5px solid ${c}`, borderRadius: 10, background: '#141428'}}>
								<div style={{position: 'absolute', left: 16, top: 16, width: 60, height: 60, borderRadius: 10, background: c, opacity: 0.8}} />
								<div style={{position: 'absolute', left: 90, top: 22, width: 90, height: 12, background: '#ffffff55'}} />
								<div style={{position: 'absolute', left: 90, top: 46, width: 70, height: 12, background: '#ffffff33'}} />
								{hack && <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(255,40,80,0.55)', fontFamily: MONO, fontWeight: 700, fontSize: 26, color: '#fff'}}>HACKEADO</div>}
							</div>
						);
					})}
				</AbsoluteFill>
			</Laptop>
			<BolsaEvidencia x={540} y={1110} ancho={760} alto={560} baja={baja} sello={sello} />
		</Toma>
	);
};

/** E2b: la fachada del hotel con la patrulla afuera; la cámara sube como una grúa y entra por la ventana. */
const camFachada = (d: number, h: number) => (g: number) => {
	const t = tramo(g, d, h - 4, Easing.inOut(Easing.quad));
	return {s: 1 + 0.15 * t, x: -184 * t, y: 2346 * t};
};
const E2b: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscFachadaHotel />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={camFachada(d, h)} focoSalida={[540, 960]}>
		<AutoLado x={300} y={1720} ancho={560} policia texto="POLICÍA" ritmoSirena={14} />
	</Toma>
);

const E2c: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const encoge = f >= W.que3 - 4;
	const [tx, ty] = enPantalla(TELE.x, TELE.y, 1.06);
	return (
		<Toma escena={<EscHotel />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}} focoEntrada={[540, 960]} focoSalida={[tx, ty]}>
			<Cama capa="atras" />
			<Actor x={700} y={1640} alto={1050}>
				<Muneco ropa={ROPA_CHICO} pose={animarPose(f, [[d, {...manosFrente([186, 480], [214, 480])}], [W.que3, POSES.encogeHombros]])} ojos={encoge ? 'normal' : 'mirandoLado'} cejas={encoge ? 'arrogante' : 'neutral'} boca={encoge ? 'picara' : 'seria'} />
			</Actor>
			<Comoda />
			<Tele x={TELE.x} y={TELE.y} ancho={TELE.ancho} brilloStick={1}>
				<PantallaHackeo abre={0} w={TELE.ancho * 0.956} h={TELE.ancho * 0.6 * 0.926} />
			</Tele>
			<Stick x={STICK.x} y={STICK.y} largo={110} />
		</Toma>
	);
};

/* =============================== E3: dentro de la tele =============================== */

const COSAS = [
	{z: 760, x: 0, y: -360, ancho: 760, tipo: 'cartel' as const, texto: '#CHAT-INTERNO'},
	...Array.from({length: 7}).map((_, i) => ({z: 520 + i * 120, x: i % 2 ? 330 : -330, y: -120 + (i % 3) * 120, ancho: 380, tipo: 'chat' as const, lado: i % 2 ? 1 : -1})),
	{z: 1500, x: 0, y: 0, ancho: 760, tipo: 'boveda' as const},
	{z: 1620, x: -320, y: -230, ancho: 280, tipo: 'carpeta' as const, texto: 'SECRETO'},
	{z: 1720, x: 320, y: 160, ancho: 280, tipo: 'carpeta' as const, texto: 'CONFIDENCIAL'},
	{z: 1830, x: -300, y: 220, ancho: 280, tipo: 'carpeta' as const, texto: 'NO ABRIR'},
	{z: 1940, x: 310, y: -260, ancho: 280, tipo: 'carpeta' as const, texto: 'GTA 6'},
	{z: 2600, x: 0, y: 0, ancho: 820, tipo: 'carga' as const, texto: 'SUBIENDO 90 VIDEOS AL FORO…'},
];

const E3: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	// avance continuo que acelera en cada nivel y frena frente a la barra de carga
	const claves: [number, number][] = [[d, 0], [W.despues, 860], [W.domingo, 1640], [W.sube + 6, 2020], [W.gta6 - 2, 2080]];
	let cz = 0;
	for (let i = 0; i < claves.length - 1; i++) {
		const [a, za] = claves[i];
		const [b, zb] = claves[i + 1];
		if (f >= a) cz = za + (zb - za) * interpolate(f, [a, b], [0, 1], clamp);
	}
	const abre = tramo(f, W.despues + 2, W.archivos + 4, Easing.out(Easing.cubic));
	const carga = tramo(f, W.sube, W.gta6 - 2, (u) => u);
	const explota = f >= W.gta6;
	return (
		<Toma escena={<AbsoluteFill style={{background: '#0b0418'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1.03]}} golpes={[[W.despues + 4, 0.04], [W.gta6, 0.08]]} focoEntrada={[540, 960]}>
			<Tunel cz={cz} cosas={explota ? COSAS.filter((c) => c.tipo !== 'carga') : COSAS} abreBoveda={abre} carga={carga}>
				<Miniaturas desde={W.gta6} />
			</Tunel>
			<Destello desde={W.gta6} color={NEON_R} fuerza={0.5} duracion={10} />
		</Toma>
	);
};

/* =============================== E4 / E6: la gente de internet =============================== */

const Vecino: React.FC<{ropa: Ropa; x: number; y: number; i: number; congelado?: boolean}> = ({ropa, x, y, i, congelado}) => {
	const f = useCurrentFrame();
	const bob = congelado ? 0 : Math.abs(Math.sin(f / 4 + i)) * -10;
	return (
		<div style={{position: 'absolute', left: x - 120, top: y - 130, width: 240, height: 260, overflow: 'hidden'}}>
			<div style={{position: 'absolute', left: -36, top: 20 + bob, width: 312, height: 702}}>
				<Muneco ropa={ropa} pose={congelado ? {} : {cabeza: Math.sin(f / 5 + i) * 6}} ojos={congelado ? 'grandes' : 'feliz'} cejas={congelado ? 'sorprendido' : 'neutral'} boca={congelado ? 'o' : 'sonrisaGrande'} parpadea={!congelado} respira={!congelado} sombra={false} />
			</div>
			{congelado && <div style={{position: 'absolute', inset: 0, background: 'rgba(160,190,230,0.35)'}} />}
		</div>
	);
};

const Burbuja: React.FC<{x: number; y: number; texto: string; desde: number; color?: string; tam?: number; cola?: 'izq' | 'der'}> = ({x, y, texto, desde, color = '#ffffff', tam = 64, cola = 'izq'}) => {
	const f = useCurrentFrame();
	const p = interpolate(f, [desde, desde + 6], [0, 1], {...clamp, easing: Easing.out(Easing.back(2))});
	if (p <= 0) return null;
	return (
		<div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, -100%) scale(${p})`, transformOrigin: cola === 'izq' ? '15% 100%' : '85% 100%'}}>
			<div style={{padding: `${tam * 0.25}px ${tam * 0.45}px`, background: color, border: `8px solid ${TINTA}`, borderRadius: tam * 0.5, fontFamily: CONDENSADA, fontSize: tam, lineHeight: 1.05, color: TINTA, whiteSpace: 'pre', textAlign: 'center', boxShadow: '0 10px 0 rgba(0,0,0,0.35)'}}>{texto}</div>
			<svg width={60} height={44} style={{position: 'absolute', [cola === 'izq' ? 'left' : 'right']: tam * 0.6, bottom: -36}}>
				<path d="M 4 0 L 28 40 L 52 0 Z" fill={color} stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
				<rect x={0} y={0} width={60} height={8} fill={color} />
			</svg>
		</div>
	);
};

const QUIENES = [0, 2, 3, 5, 7, 8, 10, 12, 13, 15, 16, 18, 20, 21, 23];
const Gente: React.FC<{congelado?: boolean}> = ({congelado}) => (
	<>
		{QUIENES.map((k, i) => {
			const [x, y] = VENTANAS_EDIFICIO[k];
			return <Vecino key={k} ropa={VECINOS[i % VECINOS.length]} x={x} y={y} i={i} congelado={congelado} />;
		})}
	</>
);

const E4: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscEdificio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.0], x: [360, -360], curva: 'lineal'}} golpes={[[W.falso, 0.04], [W.eso9, 0.04]]}>
		<Gente />
		<Burbuja x={-80} y={360} texto="JAJAJA" desde={W.rien - 4} tam={52} color="#ffe0f2" />
		<Burbuja x={420} y={380} texto="¡ES FALSO!" desde={W.es8 - 2} tam={86} />
		<Burbuja x={820} y={1080} texto={'¡ESO PARECE\nDE PLAYSTATION 2!'} desde={W.eso9 - 2} tam={70} cola="der" color="#e0f7ff" />
		<Burbuja x={1220} y={420} texto="JAJA" desde={W.eso9 + 10} tam={52} color="#ffe0f2" />
	</Toma>
);

/* =============================== E5: la amenaza =============================== */

const MENSAJE = 'Si no me contactan en 24 horas... publico el código del juego.';

const E5a: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const [px, py] = enPantalla(540, 640, 1.06);
	return (
		<Toma escena={<EscHotel />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}} focoSalida={[px, py]}>
			<Actor x={540} y={2240} alto={1300}>
				<Muneco ropa={ROPA_CHICO} pose={{...manosFrente([160, 300 + Math.sin(f / 2.5) * 4], [240, 300 + Math.cos(f / 2.3) * 4]), mi: 'agarra', md: 'agarra', cabeza: 6}} ojos="entrecerrados" cejas="arrogante" boca="seria" />
			</Actor>
			<CelularChat x={540} y={640} ancho={400} mensaje={MENSAJE} desde={W.escribe} hasta={W.si11 - 6} />
		</Toma>
	);
};

const Empleado: React.FC<{ropa: Ropa; x: number; alarma: boolean; i: number}> = ({ropa, x, alarma, i}) => (
	<Actor x={x} y={1960} alto={1000}>
		<Muneco ropa={ropa} pose={alarma ? (i === 1 ? {...manosFrente([110, 140], [290, 140]), mi: 'abierta', md: 'abierta'} : {...manosFrente([150, 300], [250, 300]), mi: 'abierta', md: 'abierta'}) : {...manosFrente([150, 520], [250, 520]), mi: 'agarra', md: 'agarra'}} ojos={alarma ? 'grandes' : 'normal'} cejas={alarma ? 'preocupado' : 'neutral'} boca={alarma ? 'o' : 'sonrisa'} hablando={!alarma} semilla={i} />
	</Actor>
);

const E5b: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const rojo = tramo(f, W.si11 - 2, W.si11 + 10);
	const alarma = f >= W.si11 + 2;
	// sale de la pantalla del monitor grande: empieza metida en él y se abre hacia atrás
	const camFn = (g: number) => {
		const t = tramo(g, d, d + 26, Easing.out(Easing.cubic));
		return {s: 2.4 - 1.4 * t, x: 0, y: (960 - 600) * (2.4 - 1.4 * t) - (960 - 600)};
	};
	return (
		<Toma escena={<EscOficinaAlarma rojo={rojo} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={camFn} focoEntrada={[540, 960]}>
			<Tele x={540} y={600} ancho={900} pie={false}>
				<PantallaAlarma mensaje={MENSAJE} parpadeo={alarma} tam={50} />
			</Tele>
			<Reloj x={540} y={190} tam={92} desde={W.si11} />
			<Empleado ropa={ROPA_EMPLEADO_1} x={200} alarma={alarma} i={0} />
			<Empleado ropa={ROPA_EMPLEADA_2} x={540} alarma={alarma} i={1} />
			<Empleado ropa={ROPA_EMPLEADO_3} x={880} alarma={alarma} i={2} />
			<div style={{position: 'absolute', left: -40, right: -40, top: 1480, height: 60, background: '#5a3a24', border: `8px solid ${TINTA}`}} />
		</Toma>
	);
};

/* =============================== E6: el giro =============================== */

const E6a: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cae = interpolate(f, [W.los13 - 8, W.los13], [-900, 0], {...clamp, easing: Easing.in(Easing.quad)});
	const rebote = f >= W.los13 ? Math.sin((f - W.los13) / 2) * Math.exp(-(f - W.los13) / 6) * 20 : 0;
	const congelado = f >= W.los13;
	return (
		<Toma escena={<EscEdificio congelado={congelado} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], x: [-120, -120]}} golpes={[[W.los13, 0.08]]}>
			<Gente congelado={congelado} />
			{f >= W.los13 - 8 && (
				<div style={{position: 'absolute', left: 540 + 120 - 380, top: 640 + cae + rebote, width: 760, transform: `rotate(${-3 + rebote * 0.1}deg)`, background: '#fbfbf7', border: `10px solid ${TINTA}`, borderRadius: 14, boxShadow: '0 24px 0 rgba(0,0,0,0.45)', padding: '30px 40px 40px'}}>
					<div style={{fontFamily: TITULAR, fontWeight: 900, fontSize: 40, letterSpacing: 8, color: '#5a5f6a', borderBottom: `6px solid ${TINTA}`, paddingBottom: 10}}>COMUNICADO OFICIAL</div>
					<div style={{fontFamily: CONDENSADA, fontSize: 112, lineHeight: 1, color: TINTA, marginTop: 24}}>LOS VIDEOS SON</div>
					<div style={{fontFamily: CONDENSADA, fontSize: 170, lineHeight: 1, color: '#d6262e'}}>REALES</div>
				</div>
			)}
		</Toma>
	);
};

/** E6b: de vuelta a la fachada (arriba, donde está la ventana) y acercamiento veloz hasta entrar en ella. */
const E6b: React.FC<P> = ({d, h, e, s}) => {
	const camFn = (g: number) => {
		const t = tramo(g, d, h, Easing.in(Easing.cubic));
		const sc = 1.15 + 0.9 * t;
		const [wx, wy] = [FACHADA_VENTANA.x, FACHADA_VENTANA.y];
		return {s: sc, x: -(wx - 540) * sc, y: (960 - wy) * sc - (960 - 960)};
	};
	return <Toma escena={<EscFachadaHotel />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={camFn} focoSalida={[540, 960]} />;
};

/* =============================== E7: el mecanismo =============================== */

const TV7 = {x: 540, y: 800, ancho: 760};
const E7a: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const giro = interpolate(f, [d + 2, W.stick - 2, W.usa + 4, W.entra - 2], [0, 180, 180, 360], {...clamp, easing: suave});
	const enchufe = interpolate(f, [d, W.enchufa - 4, W.enchufa + 6], [0.35, 0.35, 1], {...clamp, easing: Easing.out(Easing.back(2))});
	const fono = interpolate(f, [W.usa - 4, W.usa + 6], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.6))});
	const luz = tramo(f, W.entra - 2, W.entra + 18, Easing.in(Easing.quad));
	const camFn = (g: number) => {
		const t = tramo(g, W.entra, W.entra + 24, Easing.inOut(Easing.quad));
		return {s: 1.0 - 0.06 * t, x: -1000 * t, y: 0};
	};
	const [sx, sy] = [TV7.x + TV7.ancho / 2 + 50, TV7.y + 40];
	return (
		<Toma escena={<AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 40%, #1d2a66, ${NOCHE} 70%)`}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={camFn} golpes={[[W.stick, 0.04], [W.enchufa + 4, 0.05], [W.entra, 0.06]]} focoEntrada={[540, 960]}>
			<Tele x={TV7.x} y={TV7.y} ancho={TV7.ancho} giro={giro} enchufe={enchufe} brilloStick={giro > 270 || giro < 90 ? 1 : 0}>
				<PantallaHackeo abre={1} w={TV7.ancho * 0.956} h={TV7.ancho * 0.6 * 0.926} />
			</Tele>
			{(giro < 90 || giro > 270) && <Stick x={sx} y={sy} largo={170} />}
			{giro > 150 && giro < 210 && <Etiqueta x={TV7.x + 120} y={TV7.y - 150} texto="FIRE STICK" desde={W.stick} color="#e9dcff" tam={52} />}
			{f >= W.series - 2 && f < W.usa && <Etiqueta x={TV7.x - 200} y={TV7.y + 330} texto="▶ SERIES" desde={W.series - 2} color="#ffffff" tam={46} />}
			{/* el celular y el wifi */}
			{fono > 0 && (
				<div style={{position: 'absolute', left: 180 - 90, top: 1380 - 180, width: 180, height: 360, transform: `scale(${fono})`}}>
					<div style={{position: 'absolute', inset: 0, background: '#111216', border: `8px solid ${TINTA}`, borderRadius: 30, boxShadow: `0 0 40px ${NEON_M}88`}}>
						<div style={{position: 'absolute', inset: 12, borderRadius: 20, background: 'linear-gradient(180deg,#3a2a7a,#140a30)'}} />
					</div>
				</div>
			)}
			{fono > 0.5 && (
				<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
					{[0, 1, 2].map((k) => {
						const u = ((f - W.usa) / 14 + k / 3) % 1;
						const r = 60 + u * 260;
						return <path key={k} d={`M ${180 + r * 0.55} ${1200 - r * 0.85} A ${r} ${r} 0 0 1 ${180 + r * 0.95} ${1200 - r * 0.3}`} stroke={NEON_C} strokeWidth={10} fill="none" strokeLinecap="round" opacity={1 - u} />;
					})}
				</svg>
			)}
			{/* la línea de luz hasta la fortaleza de servidores */}
			{luz > 0 && (
				<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
					<path d={`M ${sx} ${sy} C ${sx + 300} ${sy - 200}, ${sx + 600} ${sy + 300}, ${sx + 650 * luz + 300 * luz} ${sy + 160 * luz}`} stroke={NEON_C} strokeWidth={14} fill="none" strokeLinecap="round" style={{filter: `drop-shadow(0 0 16px ${NEON_C})`}} />
				</svg>
			)}
			<Fortaleza x={1540} y={1240} ancho={620} abre={tramo(f, W.entra + 18, W.entra + 26, Easing.out(Easing.back(2)))} />
		</Toma>
	);
};

const E7b: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const estrellas = interpolate(f, [W.cuarto - 2, W.cuarto + 6], [0, 1], {...clamp, easing: Easing.out(Easing.back(2.2))});
	return (
		<Toma escena={<AbsoluteFill style={{background: '#16224a'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.1], y: [0, -20]}} golpes={[[W.escondido, 0.04], [W.cuarto, 0.06]]}>
			{/* puerta del cuarto, de frente */}
			<div style={{position: 'absolute', left: 200, top: 260, width: 680, height: 1460, background: '#1f2a55', border: `14px solid ${TINTA}`}}>
				<div style={{position: 'absolute', left: 60, right: 60, top: 60, height: 520, border: `8px solid ${TINTA}`, opacity: 0.4}} />
				<div style={{position: 'absolute', left: 60, right: 60, top: 760, height: 560, border: `8px solid ${TINTA}`, opacity: 0.4}} />
				<div style={{position: 'absolute', left: 46, top: 690, width: 50, height: 50, borderRadius: '50%', background: '#c9a43a', border: `8px solid ${TINTA}`}} />
			</div>
			<Colgante x={71 + 200} y={700} texto={'NO\nMOLESTAR'} tam={1.2} />
			{/* el cartel de la policía, pegado con cinta */}
			<div style={{position: 'absolute', left: 300, top: 360, width: 480, transform: 'rotate(-3deg)', background: '#fff8e1', border: `10px solid ${TINTA}`, borderRadius: 10, padding: '30px 30px', textAlign: 'center', boxShadow: '0 16px 0 rgba(0,0,0,0.4)'}}>
				<div style={{position: 'absolute', left: 170, top: -26, width: 140, height: 44, background: 'rgba(255,255,255,0.7)', transform: 'rotate(4deg)'}} />
				<div style={{fontFamily: TITULAR, fontWeight: 900, fontSize: 34, letterSpacing: 6, color: '#1f3a7a'}}>POLICÍA</div>
				<div style={{fontFamily: CONDENSADA, fontSize: 96, lineHeight: 1, color: TINTA, marginTop: 10}}>PROTECCIÓN POLICIAL</div>
				<div style={{fontFamily: TITULAR, fontWeight: 700, fontSize: 30, color: '#3a3f4a', marginTop: 14}}>Testigo bajo resguardo · No molestar</div>
			</div>
			{estrellas > 0 && (
				<div style={{position: 'absolute', left: 540, top: 1500, transform: `translate(-50%, -50%) rotate(-6deg) scale(${estrellas})`, background: '#ffd23f', border: `10px solid ${TINTA}`, borderRadius: 24, padding: '20px 36px', textAlign: 'center', boxShadow: '0 14px 0 rgba(0,0,0,0.4)', whiteSpace: 'nowrap'}}>
					<div style={{fontFamily: CONDENSADA, fontSize: 72, color: TINTA, letterSpacing: 6}}>★★★★★</div>
					<div style={{fontFamily: CONDENSADA, fontSize: 56, color: TINTA}}>IDEAL PARA HACKEAR</div>
				</div>
			)}
		</Toma>
	);
};

/* =============================== E8: el remate =============================== */

const E8a: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const n = interpolate(f, [d + 4, W.millones + 6], [0, 5000000], {...clamp, easing: Easing.out(Easing.quad)});
	const txt = `−${Math.round(n).toLocaleString('es-CO').replace(/,/g, '.')} USD`;
	return (
		<Toma escena={<AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, #ffffff, #d9dde4)'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}} golpes={[[W.millones, 0.07]]}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 640, textAlign: 'center', fontFamily: TITULAR, fontWeight: 900, fontSize: 40, letterSpacing: 8, color: '#5a5f6a'}}>LO QUE LE COSTÓ AL ESTUDIO</div>
			<Billetes desde={d + 4} n={30} x={540} y={900} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 820, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 150, color: '#d6262e', WebkitTextStroke: `12px ${TINTA}`, paintOrder: 'stroke', letterSpacing: 2}}>{txt}</div>
		</Toma>
	);
};

const E8b: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cierre = interpolate(f, [d, W.sin20 - 4, W.salida + 6], [0.1, 0.25, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
	return (
		<Toma escena={<EscHospital />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.0], curva: 'lineal'}}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 360, textAlign: 'center', fontFamily: TITULAR, fontWeight: 800, fontSize: 40, letterSpacing: 10, color: '#3a3f4a'}}>HOSPITAL DE SEGURIDAD</div>
			<PuertaPesada x={540} y={1500} ancho={520} alto={940} cierre={cierre} />
		</Toma>
	);
};

/** Final: empieza pegada al aparatito (etiqueta de 40 USD) y se aleja despacio hasta el encuadre del principio; la tele se apaga. */
const E8c: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const camFn = (g: number) => {
		const t = tramo(g, d, W.hotel21 - 2, Easing.inOut(Easing.sin));
		const sc = 3.0 - 2.0 * t;
		// el aparatito arriba de los subtítulos (y ≈ 700 en pantalla) mientras se aleja
		return {s: sc, x: -(STICK.x - 540) * sc * (1 - t), y: (700 - 960 - (STICK.y - 960) * sc) * (1 - t)};
	};
	const encendida = interpolate(f, [W.hotel21 + 2, W.hotel21 + 10], [1, 0], clamp);
	const frio = tramo(f, d, W.cuarenta);
	return (
		<Toma escena={<EscHotel frio={frio} luzTele={encendida} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={camFn} encima={<>{f >= W.hotel21 + 10 && <AbsoluteFill style={{background: '#000', opacity: interpolate(f, [W.hotel21 + 10, W.hotel21 + 22], [0, 0.55], clamp)}} />}<Sello x={540} y={1150} texto="REAL" icono="✔" color="#1f9d48" desde={SELLO_REAL} tam={170} rot={-8} solido /></>}>
			<CuartoHotel abre={1} chico={false} frio={frio} encendida={encendida} etiqueta={W.cuarenta} />
		</Toma>
	);
};

/* =============================== Montaje =============================== */

type Plano = {desde: number; Comp: React.FC<P>; entrada: Transicion};

const PLANOS: Plano[] = [
	{desde: 0, Comp: E1, entrada: 'corte'},
	{desde: antes(W.mira), Comp: E2a, entrada: 'latigoDer'},
	{desde: antes(W.y2), Comp: E2b, entrada: 'latigoArriba'},
	{desde: antes(W.sin3), Comp: E2c, entrada: 'pantalla'},
	{desde: antes(W.primero), Comp: E3, entrada: 'pantalla'},
	{desde: antes(W.y7), Comp: E4, entrada: 'latigoIzq'},
	{desde: antes(W.hasta), Comp: E5a, entrada: 'latigoDer'},
	{desde: antes(W.si11), Comp: E5b, entrada: 'pantalla'},
	{desde: antes(W.y12), Comp: E6a, entrada: 'latigoIzq'},
	{desde: antes(W.y14), Comp: E6b, entrada: 'latigoDer'},
	{desde: antes(W.con), Comp: E7a, entrada: 'pantalla'},
	{desde: antes(W.escondido), Comp: E7b, entrada: 'latigoIzq'},
	{desde: antes(W.a19), Comp: E8a, entrada: 'latigoArriba'},
	{desde: antes(W.a20), Comp: E8b, entrada: 'latigoIzq'},
	{desde: antes(W.todo), Comp: E8c, entrada: 'latigoDer'},
];

export const Historia: React.FC = () => (
	<>
		{PLANOS.map((p, i) => {
			const sig = PLANOS[i + 1];
			return <p.Comp key={i} d={p.desde} h={sig ? sig.desde : FIN_VIDEO} e={p.entrada} s={sig ? sig.entrada : 'corte'} />;
		})}
	</>
);

/** Efectos (pasan por la mezcla: siempre por debajo de la voz). [archivo, cuadro, volumen] */
const transiciones: [string, number, number][] = PLANOS.slice(1).map((p) => [p.entrada === 'pantalla' ? 'glitch' : 'whoosh', p.desde - 10, p.entrada === 'pantalla' ? 0.3 : 0.32]);
const SONIDOS_TODOS: [string, number, number][] = [
	...transiciones,
	// E1: zumbido de la tele y tecleo
	['zumbido', 0, 0.35],
	['teclas', 6, 0.25],
	['notif', W.gta0 - 2, 0.3],
	// E2
	['cierre', W.computadora2 - 2, 0.45],
	['puertaauto', antes(W.y2) + 6, 0.4],
	['neon', antes(W.y2) + 10, 0.16],
	// E3
	['notif', W.chat4 - 2, 0.4],
	['boveda', W.despues + 2, 0.45],
	['whoosh', W.sube, 0.35],
	['pop', W.gta6, 0.4],
	['pop', W.gta6 + 4, 0.35],
	['pop', W.gta6 + 8, 0.35],
	['pop', W.gta6 + 12, 0.3],
	// E5
	['teclas', W.escribe, 0.3],
	['murmullo', antes(W.si11) - 30, 0.3],
	['tictac', W.si11, 0.35],
	['tictac', W.si11 + 110, 0.35],
	// E6
	['sello', W.los13 - 1, 0.45],
	// E7
	['chispas', W.enchufa + 2, 0.4],
	['notif', W.usa, 0.25],
	['chispas', W.entra, 0.4],
	['servidores', W.entra + 10, 0.16],
	['sello', W.cuarto, 0.35],
	// E8
	['caja', W.millones - 4, 0.45],
	['puerta', W.salida, 0.45],
	['nota', W.todo, 0.35],
	['clic', W.hotel21 + 2, 0.5],
	['sello', SELLO_REAL - 3, 0.5],
];
/** silencio total en el giro: ningún efecto suena entre el fin de «confirma» y «los videos son reales» */
export const SONIDOS: [string, number, number][] = SONIDOS_TODOS.filter(([, c]) => c < GIRO[0] - 60 || c >= GIRO[1] - 1);

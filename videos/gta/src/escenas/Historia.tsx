import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {Etiqueta} from '../componentes/Efectos';
import {Atril, AutoA, AutoLado, Barrido, Bicho, BotonRojo, CajaJuego, ChoqueSVG, Control, Hud, Insecticida, Ladrillo, MapaJuego, MaquinaEscribir, Marcador, Monitor, NombreJuego, PantallaCodigo, Pizarra, pantallaDe, ruta} from '../componentes/Gamer';
import {Actor, Muneco, POSES, Pose, Ropa, alcanzar, animarPose, manosEn, manosFrente} from '../componentes/Muneco';
import {Lapiz, Revista} from '../componentes/Objetos';
import {Rotulo, TituloArriba} from '../componentes/Rotulos';
import {Toma, Transicion} from '../componentes/Toma';
import {Bocadillo, Brillos, Confeti, Fundido, Icono, Sello} from '../componentes/Utileria';
import {ROPA_DISTRIBUIDOR, ROPA_JEFE, ROPA_LADRON, ROPA_POLICIA, ROPA_POLITICO, ROPA_PROBADOR, ROPA_PROBADORA, ROPA_PROGRAMADOR, ROPA_PROGRAMADOR_2, ROPA_PUBLICISTA} from '../componentes/Vestuario';
import {EscAlfombra, EscCalleNoche, EscMundo, EscOficina90, EscParlamento, EscTV} from '../escenarios/Escenarios';
import {CONDENSADA, ROTULADO} from '../fuentes';
import {finFrase, palabra} from '../tiempos';

/*
 * «GTA existe por un bug» — chisme gamer con humor.
 * El nombre del juego va en rotulación propia: no se usa el logo ni el arte oficial.
 * Cuadros GLOBALES: cada acción cae sobre la palabra exacta de la narración.
 */

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const antes = (n: number) => n - 3;
const TINTA = '#1b1b1f';
const ROJO = '#d6262e';
const VERDE = '#1f9d48';

const W = {
	bug0: palabra(0, 'BUG'),
	un1: palabra(1, 'Un'),
	error1: palabra(1, 'error'),
	loca: palabra(1, 'loca'),
	y2: palabra(2, 'y'),
	ni2: palabra(2, 'ni'),
	loco2: palabra(2, 'loco'),
	al3: palabra(3, 'Al'),
	principio: palabra(3, 'principio'),
	criminales: palabra(3, 'criminales'),
	era3: palabra(3, 'era', 2),
	carreras: palabra(3, 'carreras'),
	policias3: palabra(3, 'policías'),
	ladrones: palabra(3, 'ladrones'),
	y4: palabra(4, 'Y'),
	era4: palabra(4, 'ERA'),
	aburridisimo: palabra(4, 'ABURRIDÍSIMO'),
	tan: palabra(5, 'Tan'),
	punto: palabra(5, 'punto'),
	cancelarse: palabra(5, 'cancelarse'),
	hasta: palabra(6, 'Hasta'),
	error6: palabra(6, 'error'),
	codigo: palabra(6, 'código'),
	vuelve: palabra(6, 'vuelve'),
	locos6: palabra(6, 'locos'),
	ya7: palabra(7, 'ya'),
	persiguen: palabra(7, 'persiguen'),
	embisten: palabra(8, 'EMBISTEN'),
	encierran: palabra(8, 'ENCIERRAN'),
	sacan: palabra(8, 'SACAN'),
	calle: palabra(8, 'CALLE'),
	y9: palabra(9, 'Y'),
	prueban: palabra(9, 'prueban'),
	quieren: palabra(9, 'quieren'),
	soltarlo: palabra(9, 'soltarlo'),
	lo10: palabra(10, 'Lo'),
	divertido: palabra(10, 'divertido'),
	escaparse: palabra(11, 'ESCAPARSE'),
	locos11: palabra(11, 'LOCOS'),
	y12: palabra(12, 'Y'),
	bug12: palabra(12, 'bug'),
	al13: palabra(13, 'AL'),
	contrario: palabra(13, 'CONTRARIO'),
	lo14: palabra(14, 'Lo'),
	convirtieron: palabra(14, 'convirtieron'),
	juego14: palabra(14, 'juego'),
	y15: palabra(15, 'Y'),
	grand: palabra(15, 'GRAND'),
	theft: palabra(15, 'THEFT'),
	auto: palabra(15, 'AUTO'),
	robo: palabra(15, 'ROBO'),
	autos: palabra(15, 'AUTOS'),
	pero16: palabra(16, 'Pero'),
	loco16: palabra(16, 'loco'),
	despues: palabra(16, 'después'),
	cuando: palabra(17, 'Cuando'),
	inglaterra: palabra(17, 'Inglaterra'),
	prohibirlo: palabra(17, 'prohibirlo'),
	violento: palabra(17, 'violento'),
	esa: palabra(18, 'ESA'),
	polemica: palabra(18, 'POLÉMICA'),
	inventado: palabra(18, 'INVENTADO'),
	propia: palabra(18, 'PROPIA'),
	distribuidora: palabra(18, 'DISTRIBUIDORA'),
	contrataron: palabra(19, 'Contrataron'),
	experto: palabra(19, 'experto'),
	escandalos: palabra(19, 'escándalos'),
	todo: palabra(19, 'todo'),
	mundo: palabra(19, 'mundo'),
	hablara: palabra(19, 'hablara'),
	y20: palabra(20, 'Y'),
	vaya: palabra(20, 'vaya'),
	hablaron: palabra(20, 'hablaron'),
	veredicto: palabra(21, 'VEREDICTO'),
	real: palabra(21, 'REAL'),
	genios: palabra(22, 'Genios'),
	marketing: palabra(22, 'marketing'),
	suerte: palabra(22, 'suerte'),
};

export const FIN_VIDEO = finFrase(22) + 30;

/* La coreografía de las persecuciones se escribió en cuadros; se ancla a su palabra para seguirla si cambia la voz. */
const tPer = (n: number) => n - 706 + W.embisten;
const tEsc = (n: number) => n - 899 + W.escaparse;

type P = {d: number; h: number; e: Transicion; s: Transicion};
type Lugar = {x: number; y: number; alto: number};

const aLienzo = (a: Lugar, wx: number, wy: number): [number, number] => {
	const k = a.alto / 900;
	return [(wx - (a.x - 200 * k)) / k, (wy - (a.y - 880 * k)) / k];
};
const brazo = (lado: -1 | 1, r: {a: number; c: number; k?: number}): Partial<Pose> => (lado < 0 ? {bi: r.a, ci: r.c, ai: r.k ?? 1} : {bd: r.a, cd: r.c, ad: r.k ?? 1});
const REPOSO = manosFrente([186, 480], [214, 480]);
const TECLEA = (f: number): Partial<Pose> => ({...manosFrente([150, 500 + Math.sin(f / 2.2) * 8], [250, 500 + Math.cos(f / 2.4) * 8]), mi: 'agarra', md: 'agarra'});
const CON_CONTROL: Partial<Pose> = {...manosFrente([150, 470], [250, 470]), mi: 'agarra', md: 'agarra'};
/** aparece con un pequeño rebote */
const pop = (f: number, desde: number) => ({opacidad: interpolate(f, [desde - 2, desde + 2], [0, 1], clamp), escala: interpolate(f, [desde - 2, desde + 4, desde + 8], [0.6, 1.06, 1], clamp)});

const ROPA_PRESENTADORA: Ropa = {...ROPA_JEFE, cabeza: {...ROPA_JEFE.cabeza, pelo: 'melena', colorPelo: '#e8c25a', lentes: false, pestanas: true}, casaca: '#c4262e', casacaSombra: '#8e1a22', corbata: undefined};

/** Escritorio de madera (por delante de los personajes) */
const Escritorio: React.FC<{y: number}> = ({y}) => (
	<>
		<div style={{position: 'absolute', left: -40, right: -40, top: y, height: 54, background: '#9a6a3a', border: `8px solid ${TINTA}`, borderRadius: 10}} />
		<div style={{position: 'absolute', left: 30, right: 30, top: y + 54, height: 1920 - y, background: '#7a4a24', borderLeft: `8px solid ${TINTA}`, borderRight: `8px solid ${TINTA}`}} />
	</>
);

/* ---------- el juego dentro del monitor: dos carros dando vueltas a una manzana ---------- */

const ESQUINAS = [[0, 0], [640, 0], [640, 640], [0, 640]];
const circuito = (s: number, carril = 40): AutoA => {
	const u = ((s % 4) + 4) % 4;
	const k = Math.floor(u);
	const t = u - k;
	const [x1, y1] = ESQUINAS[k];
	const [x2, y2] = ESQUINAS[(k + 1) % 4];
	const off = [[0, -carril], [carril, 0], [0, carril], [-carril, 0]][k];
	return {x: x1 + (x2 - x1) * t + off[0], y: y1 + (y2 - y1) * t + off[1], rot: [90, 180, 270, 0][k]};
};
const Carreras: React.FC<{ancho: number; velocidad: number; titulo?: boolean}> = ({ancho, velocidad, titulo}) => {
	const f = useCurrentFrame();
	const {w, h} = pantallaDe(ancho);
	const s = f * velocidad;
	return (
		<>
			<MapaJuego cx={320} cy={320} zoom={w / 1080} ancho={w} alto={h} autos={[{...circuito(s), color: '#e3262e', jugador: true}, {...circuito(s - 0.35), policia: true}]} />
			{titulo && (
				<div style={{position: 'absolute', left: 0, right: 0, top: h * 0.04, textAlign: 'center', fontFamily: ROTULADO, fontSize: w * 0.085, color: '#ffd23f', WebkitTextStroke: `${w * 0.012}px ${TINTA}`, paintOrder: 'stroke'}}>RACE&apos;N&apos;CHASE</div>
			)}
		</>
	);
};

/* =============================== GANCHO =============================== */

const Gancho: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const ancho = 860;
	const {w, h: hp} = pantallaDe(ancho);
	const bx = interpolate(f, [W.bug0 - 4, W.bug0 + 20], [200, 470], {...clamp, easing: Easing.out(Easing.quad)});
	const ve = f >= W.bug0 - 2;
	return (
		<Toma escena={<EscOficina90 />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [0, -20]}} golpes={[[W.bug0, 0.07]]}>
			<Monitor x={540} y={930} ancho={ancho}>
				<MapaJuego cx={0} cy={1500 - f * 6} zoom={0.5} ancho={w} alto={hp} autos={[{x: 40, y: 1450 - f * 7, rot: 0, color: '#e3262e', jugador: true}, {x: -10 + Math.sin(f / 6) * 50, y: 1720 - f * 6, rot: f * 14, policia: true}]} />
			</Monitor>
			<Escritorio y={1340} />
			{ve && <Bicho x={bx} y={900} tam={300} rot={70} camina={f < W.bug0 + 20} cara="picaro" />}
			<Actor x={900} y={1990} alto={1150}>
				<Muneco ropa={ROPA_PROGRAMADOR} pose={ve ? {...manosFrente([150, 300], [250, 300]), mi: 'abierta', md: 'abierta'} : TECLEA(f)} ojos={ve ? 'grandes' : 'normal'} cejas={ve ? 'sorprendido' : 'neutral'} boca={ve ? 'o' : 'sonrisa'} />
			</Actor>
		</Toma>
	);
};

const Loca: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const l = f - d;
	return (
		<Toma escena={<EscCalleNoche desplaza={f * 16} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}} golpes={[[W.loca, 0.06]]} encima={<><TituloArriba texto={'¡VOLVÍA *LOCA*\nA LA POLICÍA!'} desde={W.loca} tam={112} /></>}>
			<AutoLado x={540 + Math.sin(l / 7) * 120} y={1700} ancho={720} policia rueda={f * 30} rot={Math.sin(l / 5) * 7} salta={Math.abs(Math.sin(l / 3.5)) * 26} />
			<Icono tipo="interrogacion" x={330} y={1060} desde={W.loca} tam={140} rot={-12} />
			<Icono tipo="exclamacion" x={760} y={1030} desde={W.loca + 4} tam={140} rot={12} />
		</Toma>
	);
};

const MasLoco: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const p = interpolate(f, [W.ni2 - 6, W.ni2 + 14], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	return (
		<Toma escena={<EscParlamento />} desde={d} hasta={h} entrada={e} salida={s} tinte="rgba(20,20,60,0.6)" cam={{s: [1.02, 1.08]}} golpes={[[W.loco2, 0.06]]} encima={<><TituloArriba texto="Y NO ES LO MÁS *LOCO*..." desde={W.loco2} tam={108} /></>}>
			<div style={{position: 'absolute', inset: 0, background: 'rgba(10,10,30,0.45)'}} />
			<div style={{position: 'absolute', inset: 0, transform: `rotate(${(1 - p) * 720}deg) scale(${0.15 + 0.85 * p})`, opacity: p}}>
				<Revista x={540} y={1000} ancho={560} nombre="EL ESCÁNDALO" titular="¡PROHÍBANLO!" rot={-5}>
					<div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(45deg,#ffe0e0,#ffe0e0 20px,#fff4f4 20px,#fff4f4 40px)'}} />
					<div style={{position: 'absolute', left: 40, right: 40, top: 80}}>
						<CajaJuego x={240} y={210} ancho={240} rot={-8} />
					</div>
				</Revista>
			</div>
			<Icono tipo="interrogacion" x={880} y={760} desde={W.loco2} tam={160} rot={14} />
		</Toma>
	);
};

/* =============================== ORIGEN =============================== */

const Principio: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const {opacidad, escala} = pop(f, W.criminales);
	return (
		<Toma escena={<EscOficina90 />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], x: [-10, 10]}} golpes={[[W.criminales, 0.05]]} encima={<><Rotulo texto="1995 · DMA DESIGN · DUNDEE, ESCOCIA" desde={W.principio} /><TituloArriba texto="AL *PRINCIPIO*..." desde={W.al3} tam={130} /></>}>
			<Actor x={250} y={1880} alto={1100}>
				<Muneco ropa={ROPA_PROGRAMADOR} pose={TECLEA(f)} ojos="entrecerrados" cejas="neutral" boca="sonrisa" semilla={1} />
			</Actor>
			<Actor x={850} y={1880} alto={1100}>
				<Muneco ropa={ROPA_PROGRAMADOR_2} pose={TECLEA(f + 9)} ojos="normal" cejas="neutral" boca="sonrisa" semilla={2} />
			</Actor>
			<Monitor x={420} y={1300} ancho={300} />
			<Monitor x={680} y={1300} ancho={300} />
			<Escritorio y={1420} />
			<Actor x={540} y={2020} alto={1100} opacidad={opacidad} escala={escala}>
				<Muneco ropa={ROPA_LADRON} acc={{antifaz: true}} pose={POSES.cruzados} ojos="normal" cejas="arrogante" boca="picara" />
			</Actor>
			<Sello x={540} y={1560} texto="NO" icono="✘" color={ROJO} desde={W.criminales + 4} tam={130} rot={-8} solido />
		</Toma>
	);
};

const RaceChase: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const poli = pop(f, W.policias3);
	const ladron = pop(f, W.ladrones);
	return (
		<Toma escena={<EscOficina90 tono="#5c7484" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.07]}} golpes={[[W.carreras, 0.05], [W.ladrones, 0.05]]} encima={<><Rotulo texto="SE LLAMABA «RACE'N'CHASE»" desde={W.carreras} /><TituloArriba texto="UN JUEGO DE *CARRERAS*" desde={W.era3} hasta={W.policias3} tam={116} /><TituloArriba texto="POLICÍAS *VS* LADRONES" desde={W.policias3} tam={116} /></>}>
			<Monitor x={540} y={900} ancho={820}>
				<Carreras ancho={820} velocidad={0.035} titulo />
			</Monitor>
			<Actor x={200} y={2030} alto={1120} opacidad={poli.opacidad} escala={poli.escala}>
				<Muneco ropa={ROPA_POLICIA} pose={{...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 330, 300)), md: 'puno'}} ojos="entrecerrados" cejas="enojado" boca="mueca" />
			</Actor>
			<Actor x={880} y={2030} alto={1120} opacidad={ladron.opacidad} escala={ladron.escala}>
				<Muneco ropa={ROPA_LADRON} acc={{antifaz: true}} pose={{...manosFrente(undefined, [214, 480]), ...brazo(-1, alcanzar(-1, 70, 300)), mi: 'puno'}} ojos="normal" cejas="arrogante" boca="picara" />
			</Actor>
			{f >= W.ladrones && <div style={{position: 'absolute', left: 0, right: 0, top: 1440, textAlign: 'center', fontFamily: ROTULADO, fontSize: 150, color: '#ffd23f', WebkitTextStroke: `20px ${TINTA}`, paintOrder: 'stroke', transform: `scale(${pop(f, W.ladrones + 2).escala})`}}>VS</div>}
		</Toma>
	);
};

const Aburrido: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const duerme = f >= W.aburridisimo - 2;
	const bosteza = f >= W.era4 - 4 && !duerme;
	const pose = animarPose(f, [
		[d, CON_CONTROL],
		[W.era4, {bi: 160, ci: 20, bd: 160, cd: 20, mi: 'puno', md: 'puno'}],
		[W.aburridisimo, {...CON_CONTROL, cabeza: 24, cuerpo: 6}],
	]);
	return (
		<Toma escena={<EscOficina90 />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [-10, -30]}} golpes={[[W.aburridisimo, 0.06]]} encima={<><TituloArriba texto="¡*ABURRIDÍSIMO*!" desde={W.aburridisimo} tam={140} /></>}>
			<Monitor x={700} y={1140} ancho={520}>
				<Carreras ancho={520} velocidad={0.012} />
			</Monitor>
			<Escritorio y={1440} />
			<Actor x={300} y={1980} alto={1140}>
				<Muneco ropa={ROPA_PROBADOR} pose={pose} objPecho={<Control />} ojos={duerme || bosteza ? 'cerrados' : 'entrecerrados'} cejas="neutral" boca={bosteza ? 'o' : 'seria'} respira={!duerme} />
			</Actor>
			{duerme &&
				[0, 1, 2].map((i) => {
					const t = ((f - W.aburridisimo + i * 10) % 30) / 30;
					return (
						<div key={i} style={{position: 'absolute', left: 430 + t * 120 + i * 20, top: 880 - t * 220, fontFamily: CONDENSADA, fontSize: 70 + i * 16, color: '#ffffff', WebkitTextStroke: `8px ${TINTA}`, paintOrder: 'stroke', opacity: 1 - t}}>
							Z
						</div>
					);
				})}
			<Sello x={540} y={1620} texto="ABURRIDO" color={ROJO} desde={W.aburridisimo + 2} tam={100} rot={-6} solido />
		</Toma>
	);
};

const Cancelar: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const jefe = {x: 380, y: 1880, alto: 1080};
	const baja = interpolate(f, [W.punto - 8, W.cancelarse + 4], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
	const [hx, hy] = aLienzo(jefe, 600, 1150 + baja * 120);
	return (
		<Toma escena={<EscOficina90 tono="#6a6a7a" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.12], y: [0, -30]}} golpes={[[W.cancelarse, 0.06]]} encima={<><TituloArriba texto={'¡A PUNTO DE\n*CANCELARSE*!'} desde={W.punto} tam={118} /></>}>
			<BotonRojo x={650} y={1830} tam={1.25} />
			<Actor {...jefe}>
				<Muneco ropa={ROPA_JEFE} pose={{...manosFrente([186, 480]), ...brazo(1, alcanzar(1, hx, hy)), md: 'abierta', wd: 60}} ojos="entrecerrados" cejas="enojado" boca="seria" />
			</Actor>
			<Actor x={900} y={1960} alto={1060}>
				<Muneco ropa={ROPA_PROGRAMADOR} pose={{...manosFrente([180, 360], [220, 360]), mi: 'abierta', md: 'abierta'}} ojos="grandes" cejas="preocupado" boca="o" />
			</Actor>
		</Toma>
	);
};

/* =============================== EL BUG =============================== */

const ErrorCodigo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const ancho = 900;
	const {w, h: hp} = pantallaDe(ancho);
	const sale = f >= W.error6 - 2;
	const bx = interpolate(f, [W.error6, W.error6 + 30], [760, 560], {...clamp, easing: Easing.out(Easing.quad)});
	return (
		<Toma escena={<EscOficina90 tono="#3a4a56" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08]}} golpes={[[W.error6, 0.06], [W.locos6, 0.06]]} sacudida={(g) => (g >= W.vuelve && g < W.vuelve + 12 ? Math.sin(g * 3.1) * 10 : 0)} encima={<><TituloArriba texto="UN *ERROR* EN EL CÓDIGO" desde={W.error6} tam={110} /></>}>
			<Monitor x={540} y={900} ancho={ancho}>
				<PantallaCodigo w={w} h={hp} desde={d} error={W.error6} glitch={W.vuelve} />
			</Monitor>
			<Escritorio y={1320} />
			{sale && <Bicho x={bx} y={960} tam={220} rot={-80} camina={f < W.error6 + 30} cara="picaro" />}
			<Actor x={870} y={2000} alto={1150}>
				<Muneco ropa={ROPA_PROGRAMADOR_2} pose={sale ? {...manosFrente([150, 300], [250, 300]), mi: 'abierta', md: 'abierta'} : TECLEA(f)} ojos={sale ? 'grandes' : 'entrecerrados'} cejas={sale ? 'sorprendido' : 'neutral'} boca={sale ? 'o' : 'seria'} />
			</Actor>
		</Toma>
	);
};

/** Persecución dentro del juego, a pantalla completa. */
const Persecucion: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const jug = ruta(f, [[d, 40, 2600, 0], [tPer(716), 40, 1676, 0], [tPer(722), 70, 1630, 22], [tPer(736), 60, 1580, 18], [tPer(748), 60, 1576, 18], [tPer(766), 190, 1560, 70], [tPer(790), 196, 1558, 72]]);
	const p1 = ruta(f, [[d, 40, 2950, 0], [tPer(690), 40, 2288, 0], [tPer(706), 40, 1930, 0], [tPer(716), 40, 1820, 0], [tPer(736), 40, 1720, 0], [tPer(790), 40, 1716, 0]]);
	const p2 = ruta(f, [[d, -40, 700, 180], [tPer(712), -40, 1120, 180], [tPer(730), 20, 1440, 200], [tPer(790), 20, 1440, 200]]);
	const p3 = ruta(f, [[d, -40, 3100, 0], [tPer(712), -40, 1960, 0], [tPer(730), -60, 1600, 10], [tPer(748), -60, 1590, 10], [tPer(766), 70, 1578, 60], [tPer(790), 76, 1576, 62]]);
	const autos: AutoA[] = [
		{...p1, policia: true},
		{...p2, policia: true},
		{...p3, policia: true},
		{...jug, color: '#e3262e', jugador: true},
	];
	const estrellas = f < W.embisten ? 1 : f < W.encierran ? 3 : 5;
	return (
		<Toma
			escena={<AbsoluteFill style={{background: '#5d6470'}} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.0, 1.04]}}
			golpes={[[W.embisten, 0.08], [W.encierran, 0.06], [W.calle, 0.08]]}
			sacudida={(g) => [W.embisten, W.encierran, W.calle].reduce((m, k) => (g >= k && g < k + 10 ? Math.sin(g * 2.7) * (k + 10 - g) * 2.2 : m), 0)}
			encima={
				<>
					<Barrido fuerza={0.6} />
					<Hud estrellas={estrellas} dinero={1500 + (f - d) * 35} />
					<TituloArriba texto="YA NO TE *PERSIGUEN*..." desde={W.ya7} hasta={W.embisten - 4} tam={110} />
					<TituloArriba texto="¡TE *EMBISTEN*!" desde={W.embisten - 4} hasta={W.encierran - 2} tam={140} />
					<TituloArriba texto="¡TE *ENCIERRAN*!" desde={W.encierran - 2} hasta={W.sacan - 2} tam={140} />
					<TituloArriba texto={'¡TE SACAN\nDE LA *CALLE*!'} desde={W.sacan - 2} tam={130} />
				</>
			}
		>
			<MapaJuego cx={jug.x * 0.4} cy={jug.y + 70} zoom={1.5} ancho={1080} alto={1920} autos={autos}>
				<ChoqueSVG x={40} y={1862} desde={W.embisten} tam={1.3} />
				<ChoqueSVG x={20} y={1510} desde={W.encierran} tam={1.1} />
				<ChoqueSVG x={250} y={1560} desde={W.calle} tam={1.4} />
			</MapaJuego>
		</Toma>
	);
};

const Probadores: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const jala = f >= W.soltarlo - 4;
	const jefe = {x: 930, y: 1960, alto: 1100};
	const [hx, hy] = aLienzo(jefe, jala ? 720 : 760, 1290);
	return (
		<Toma escena={<EscOficina90 />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08]}} golpes={[[W.soltarlo, 0.05]]} encima={<><TituloArriba texto="¡NO QUIEREN *SOLTARLO*!" desde={W.quieren} tam={112} /></>}>
			<Monitor x={540} y={1060} ancho={560}>
				<Carreras ancho={560} velocidad={0.06} />
			</Monitor>
			<Escritorio y={1360} />
			<Actor x={260} y={1980} alto={1100}>
				<Muneco ropa={ROPA_PROBADOR} pose={{...CON_CONTROL, cuerpo: Math.sin(f / 5) * 3}} objPecho={<Control />} ojos="grandes" cejas="arrogante" boca="sonrisaGrande" semilla={1} />
			</Actor>
			<Actor x={590} y={1980} alto={1100}>
				<Muneco ropa={ROPA_PROBADORA} pose={{...CON_CONTROL, cuerpo: jala ? -10 : Math.sin(f / 6) * 3}} objPecho={<Control />} ojos="grandes" cejas={jala ? 'enojado' : 'arrogante'} boca={jala ? 'dientes' : 'sonrisaGrande'} semilla={2} />
			</Actor>
			<Actor {...jefe}>
				<Muneco ropa={ROPA_JEFE} pose={f >= W.prueban ? {...manosFrente(undefined, [214, 480]), ...brazo(-1, alcanzar(-1, hx, hy)), mi: 'agarra'} : POSES.cruzados} ojos="entrecerrados" cejas="enojado" boca="mueca" />
			</Actor>
			<Bocadillo x={460} y={760} texto="¡UNA MÁS!" desde={W.soltarlo} cola="der" ancho={360} tam={62} />
		</Toma>
	);
};

const Escape: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const jug = ruta(f, [[d, 40, 3300, 0], [tEsc(895), 40, 2650, 0], [tEsc(903), 90, 2602, 60], [tEsc(909), 170, 2600, 90], [tEsc(960), 900, 2600, 90]]);
	const pol: AutoA[] = [
		{...ruta(f, [[d, 40, 3520, 0], [tEsc(899), 40, 2860, 0], [tEsc(911), 40, 2650, 0], [tEsc(918), 60, 2570, 30]]), policia: true},
		{...ruta(f, [[d, 40, 3740, 0], [tEsc(905), 40, 2900, 0], [tEsc(917), 40, 2720, 0], [tEsc(922), 30, 2680, -20]]), policia: true},
		{...ruta(f, [[d, -40, 3960, 0], [tEsc(911), -40, 3000, 0], [tEsc(924), -30, 2780, -10], [tEsc(930), -80, 2720, -60]]), policia: true},
		{...ruta(f, [[d, 40, 4180, 0], [tEsc(917), 40, 3100, 0], [tEsc(930), 40, 2880, 0], [tEsc(936), 110, 2810, 40]]), policia: true},
	];
	const cx = interpolate(f, [d, tEsc(905), tEsc(960)], [20, 150, 400], clamp);
	const cy = f < tEsc(895) ? jug.y + 110 : interpolate(f, [tEsc(895), tEsc(912)], [2760, 2720], clamp);
	return (
		<Toma
			escena={<AbsoluteFill style={{background: '#5d6470'}} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.0, 1.03]}}
			golpes={[[W.escaparse, 0.06], [tEsc(918), 0.04], [tEsc(930), 0.04]]}
			encima={
				<>
					<Barrido fuerza={0.6} />
					<Hud estrellas={5} dinero={9000 + (f - d) * 140} />
					<TituloArriba texto="¿LO MÁS *DIVERTIDO*?" desde={W.lo10} hasta={W.escaparse - 2} tam={116} />
					<TituloArriba texto="¡*ESCAPARSE*!" desde={W.escaparse - 2} tam={150} />
				</>
			}
		>
			<MapaJuego cx={cx} cy={cy} zoom={1.0} ancho={1080} alto={1920} autos={[...pol, {...jug, color: '#e3262e', jugador: true}]}>
				<ChoqueSVG x={60} y={2600} desde={tEsc(918)} />
				<ChoqueSVG x={40} y={2700} desde={tEsc(922)} />
				<ChoqueSVG x={-60} y={2740} desde={tEsc(930)} />
				<ChoqueSVG x={90} y={2840} desde={tEsc(936)} />
			</MapaJuego>
		</Toma>
	);
};

const Spray: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const ancho = 760;
	const {w, h: hp} = pantallaDe(ancho);
	const contrario = f >= W.al13 - 2;
	const prog = {x: 240, y: 1960, alto: 1150};
	const pose: Partial<Pose> = contrario ? {...POSES.encogeHombros, md: 'agarra'} : {...manosEn([170, 490], [470, 296 + Math.sin(f / 4) * 6]), mi: 'puno', md: 'agarra'};
	return (
		<Toma escena={<EscOficina90 />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08]}} golpes={[[W.bug12, 0.05], [W.contrario, 0.07]]} encima={<><TituloArriba texto="¿ARREGLARON EL *BUG*?" desde={W.y12} hasta={W.al13 - 2} tam={112} /></>}>
			<Monitor x={620} y={900} ancho={ancho}>
				<MapaJuego cx={320} cy={320} zoom={0.6} ancho={w} alto={hp} autos={[{...circuito(0.3), color: '#e3262e'}, {...circuito(0.1), policia: true}]} />
			</Monitor>
			<Escritorio y={1300} />
			<Bicho x={640} y={880} tam={280} corona={f >= W.contrario - 2} camina={false} cara={contrario ? 'feliz' : 'susto'} />
			{f >= W.contrario - 2 && <Brillos x={640} y={800} desde={W.contrario - 2} radio={220} n={10} />}
			<Actor {...prog}>
				<Muneco ropa={ROPA_PROGRAMADOR} pose={pose} objDer={<Insecticida rot={contrario ? 180 : 0} rocia={!contrario && f >= W.bug12 - 4 ? interpolate(f, [W.bug12 - 4, W.bug12 + 6], [0, 0.7], clamp) : 0} />} ojos={contrario ? 'feliz' : 'entrecerrados'} cejas={contrario ? 'neutral' : 'enojado'} boca={contrario ? 'sonrisaGrande' : 'mueca'} />
			</Actor>
			<Sello x={540} y={1580} texto="¡AL CONTRARIO!" color={VERDE} desde={W.contrario} tam={92} rot={-6} solido />
		</Toma>
	);
};

const PizarraJuego: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscOficina90 />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.06]}} golpes={[[W.juego14, 0.05]]} encima={<><TituloArriba texto={'LO CONVIRTIERON\nEN *EL JUEGO*'} desde={W.lo14} tam={112} /></>}>
			<Pizarra x={500} y={900} ancho={820} alto={600}>
				<div style={{position: 'absolute', left: 40, top: 60}}>
					<Marcador texto="POLICÍAS VS LADRONES" desde={d - 60} tam={74} tachado={W.convirtieron} />
				</div>
				<div style={{position: 'absolute', left: 40, top: 230}}>
					<Marcador texto="¡TÚ ERES EL LADRÓN!" desde={W.convirtieron + 6} color="#d6262e" tam={92} />
				</div>
				<div style={{position: 'absolute', left: 60, top: 400, fontFamily: CONDENSADA, fontSize: 56, color: '#1f3a7a', opacity: f >= W.juego14 ? 1 : 0}}>+ POLICÍAS LOCOS = ★★★★★</div>
			</Pizarra>
			<Actor x={900} y={1960} alto={1080}>
				<Muneco ropa={ROPA_PROGRAMADOR_2} pose={{...manosFrente([186, 480]), ...brazo(-1, alcanzar(-1, 20, 300)), mi: 'agarra'}} objIzq={<Lapiz rot={200} />} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
			</Actor>
		</Toma>
	);
};

/* =============================== EL NOMBRE =============================== */

const Nombre: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const lx = interpolate(f, [d, W.robo - 2], [140, 430], clamp);
	const puerta = interpolate(f, [W.robo - 2, W.robo + 4, W.autos + 4, W.autos + 10], [0, 1, 1, 0], clamp);
	const dentro = f >= W.autos + 2;
	const cx = interpolate(f, [W.autos + 8, h], [660, 1500], {...clamp, easing: Easing.in(Easing.quad)});
	return (
		<Toma escena={<EscCalleNoche desplaza={f * 3} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05]}} golpes={[[W.grand, 0.05], [W.theft, 0.05], [W.auto, 0.08]]} encima={<><Rotulo texto="1997 · DMA DESIGN / BMG INTERACTIVE" desde={W.grand} y={250} /><NombreJuego y={360} desdes={[W.grand, W.theft, W.auto]} tam={140} /></>}>
			<AutoLado x={cx} y={1720} ancho={680} color="#2f7fd1" puerta={puerta} rueda={f >= W.autos + 8 ? (f - W.autos) * 40 : 0} />
			{!dentro && (
				<Actor x={lx} y={1720} alto={820}>
					<Muneco ropa={ROPA_LADRON} acc={{antifaz: true}} pose={f >= W.robo - 2 ? {...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 360, 470)), md: 'agarra'} : {}} camina={f < W.robo - 2 ? 1 : 0} ojos="mirandoLado" cejas="arrogante" boca="picara" />
				</Actor>
			)}
			<Sello x={540} y={1000} texto="= ROBO DE AUTOS" color={VERDE} desde={W.robo} tam={66} rot={-4} solido />
		</Toma>
	);
};

/* =============================== GOLPE EXTRA =============================== */

const Despues: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscTV />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.1]}} golpes={[[W.loco16, 0.06]]} encima={<><TituloArriba texto={'LO MÁS *LOCO*\nVINO DESPUÉS'} desde={W.loco16} tam={118} /></>}>
			<Actor x={540} y={1900} alto={1060}>
				<Muneco ropa={ROPA_PRESENTADORA} pose={f >= W.loco16 ? {...manosFrente([150, 300], [250, 300]), mi: 'abierta', md: 'abierta'} : REPOSO} hablando={f < W.loco16} ojos={f >= W.loco16 ? 'grandes' : 'normal'} cejas="sorprendido" boca={f >= W.loco16 ? 'o' : 'sonrisa'} />
			</Actor>
			<div style={{position: 'absolute', left: 0, right: 0, top: 1480, height: 130, background: ROJO, borderTop: `8px solid ${TINTA}`, borderBottom: `8px solid ${TINTA}`, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 24, opacity: f >= W.despues - 6 ? 1 : 0}}>
				<div style={{fontFamily: CONDENSADA, fontSize: 58, color: '#ffd23f'}}>ÚLTIMA HORA</div>
				<div style={{fontFamily: CONDENSADA, fontSize: 48, color: '#ffffff'}}>¿PROHIBIR UN VIDEOJUEGO?</div>
			</div>
		</Toma>
	);
};

const Inglaterra: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const grita = f >= W.prohibirlo - 2;
	const ban = interpolate(f, [W.prohibirlo, W.prohibirlo + 6], [0, 1], clamp);
	return (
		<Toma escena={<EscParlamento />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], y: [0, -20]}} golpes={[[W.prohibirlo, 0.07], [W.violento, 0.05]]} encima={<><Rotulo texto="REINO UNIDO · 1997" desde={W.inglaterra} /><TituloArriba texto="¡QUE LO *PROHÍBAN*!" desde={W.prohibirlo} tam={124} /></>}>
			<CajaJuego x={850} y={1080} ancho={300} rot={8} prohibido={ban} />
			<Revista x={210} y={900} ancho={260} nombre="EL ESCÁNDALO" titular="¡VIOLENTO!" desde={W.violento - 2} rot={-10}>
				<div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(45deg,#ffe0e0,#ffe0e0 20px,#fff4f4 20px,#fff4f4 40px)'}} />
			</Revista>
			<Actor x={480} y={1890} alto={1080}>
				<Muneco ropa={ROPA_POLITICO} pose={grita ? {...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 300, 130)), md: 'puno'} : {...manosFrente([150, 520], [250, 520]), mi: 'agarra', md: 'agarra'}} hablando={!grita} ojos={grita ? 'grandes' : 'entrecerrados'} cejas="enojado" boca={grita ? 'grito' : 'seria'} />
			</Actor>
			<Atril x={480} y={1890} />
		</Toma>
	);
};

const Inventada: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const rie = f >= W.inventado - 2;
	const hoja = interpolate(f, [W.esa, W.polemica + 20], [0.15, 1], {...clamp, easing: Easing.out(Easing.quad)});
	const teclea: Partial<Pose> = {...manosFrente([40, 400 + Math.sin(f / 2) * 10], [120, 410 + Math.cos(f / 2.3) * 10]), mi: 'agarra', md: 'agarra'};
	return (
		<Toma escena={<EscOficina90 tono="#4a3a5a" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08]}} golpes={[[W.inventado, 0.07]]} encima={<><Rotulo texto="LA DISTRIBUIDORA: BMG INTERACTIVE" desde={W.propia} /><TituloArriba texto={'LA POLÉMICA\nERA *INVENTADA*'} desde={W.inventado} tam={118} /></>}>
			<Actor x={820} y={1960} alto={1100}>
				<Muneco ropa={ROPA_DISTRIBUIDOR} pose={rie ? {...teclea, ...brazo(1, alcanzar(1, 236, 392)), md: 'pulgar'} : teclea} ojos={rie ? 'feliz' : 'entrecerrados'} cejas="arrogante" boca={rie ? 'sonrisaGrande' : 'picara'} />
			</Actor>
			<Escritorio y={1440} />
			<MaquinaEscribir x={460} y={1450} ancho={620} hoja={hoja} titular="¡PROHÍBAN GTA!" desde={W.polemica} />
			<Sello x={540} y={1640} texto="¡INVENTADA!" color={ROJO} desde={W.inventado} tam={96} rot={-6} solido />
		</Toma>
	);
};

const Experto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const titulares: [string, string, number, number, number, number][] = [
		['EL ESCÁNDALO', '¡ESCÁNDALO!', 190, 760, W.escandalos, -10],
		['DIARIO X', '¿PROHIBIDO?', 890, 800, W.escandalos + 8, 9],
		['LA BOMBA', '¡VIOLENTO!', 180, 1200, W.mundo, -6],
		['EL CHISME', '¡GTA!', 900, 1240, W.hablara, 7],
	];
	return (
		<Toma escena={<EscAlfombra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08]}} golpes={[[W.escandalos, 0.06], [W.mundo, 0.04]]} encima={<><Rotulo texto="UN PUBLICISTA EXPERTO EN ESCÁNDALOS" desde={W.experto} /><TituloArriba texto={'EXPERTO EN\n*ESCÁNDALOS*'} desde={W.escandalos} tam={118} /></>}>
			{titulares.map(([nombre, titular, x, y, desde, rot], i) => (
				<Revista key={i} x={x} y={y} ancho={250} nombre={nombre} titular={titular} desde={desde} rot={rot} color={['#e3262e', '#1f6fd1', '#ff8a1e', '#7b3fe4'][i]}>
					<div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(45deg,#fff0e0,#fff0e0 20px,#fffaf4 20px,#fffaf4 40px)'}} />
				</Revista>
			))}
			<Actor x={540} y={1960} alto={1150}>
				<Muneco ropa={ROPA_PUBLICISTA} acc={{gafas: true}} pose={{...brazo(1, alcanzar(1, 338, 168)), md: 'agarra', ...(f >= W.escandalos ? {...brazo(-1, alcanzar(-1, 140, 380)), mi: 'pulgar'} : manosFrente([186, 480]))}} objDer={<Ladrillo rot={160} />} hablando ojos="normal" cejas="arrogante" boca="picara" />
			</Actor>
		</Toma>
	);
};

const Hablaron: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const titulares = ['¡GTA!', '¡PROHÍBANLO!', '¡ESCÁNDALO!', '¡VIOLENTO!'];
	const colores = ['#e3262e', '#1f6fd1', '#ff8a1e', '#7b3fe4'];
	return (
		<Toma escena={<EscMundo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}} golpes={[[W.hablaron, 0.06]]} encima={<><TituloArriba texto="¡Y VAYA QUE *HABLARON*!" desde={W.vaya} tam={112} /></>}>
			{titulares.map((t, i) => {
				const a = (f - d) / 14 + (i * Math.PI) / 2;
				return <Revista key={i} x={540 + Math.cos(a) * 400} y={1020 + Math.sin(a) * 300} ancho={210} nombre="EXTRA" titular={t} color={colores[i]} rot={Math.cos(a) * 12} desde={d + 2 + i * 4} />;
			})}
			<CajaJuego x={540} y={1020} ancho={300} rot={-4} />
			<Brillos x={540} y={1000} desde={W.hablaron} radio={260} n={12} />
		</Toma>
	);
};

/* =============================== CIERRE =============================== */

const Veredicto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const real = f >= W.real;
	const salto = real ? Math.abs(Math.sin((f - W.real) / 4)) * 40 : 0;
	return (
		<Toma escena={<EscOficina90 />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], y: [0, -10]}} golpes={[[W.real, 0.08]]} encima={<><TituloArriba texto="*VEREDICTO*" desde={W.veredicto} tam={150} /><Confeti desde={W.real} n={50} /></>}>
			<Actor x={230} y={1960} alto={1080}>
				<Muneco ropa={ROPA_PROGRAMADOR} pose={real ? {...POSES.victoria, salto: salto * 0.5} : REPOSO} ojos={real ? 'feliz' : 'normal'} cejas="neutral" boca={real ? 'sonrisaGrande' : 'sonrisa'} semilla={1} />
			</Actor>
			<Actor x={850} y={1960} alto={1080}>
				<Muneco ropa={ROPA_PROGRAMADOR_2} pose={real ? {...POSES.victoria, salto: salto * 0.4} : REPOSO} ojos={real ? 'feliz' : 'normal'} cejas="neutral" boca={real ? 'sonrisaGrande' : 'sonrisa'} semilla={2} />
			</Actor>
			<Bicho x={540} y={1150 - salto} tam={340} corona camina={false} cara="feliz" />
			<Sello x={540} y={1600} texto="REAL" icono="✔" color={VERDE} desde={W.real} tam={150} rot={-8} solido />
		</Toma>
	);
};

const Pregunta: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma
			escena={
				<AbsoluteFill>
					<div style={{position: 'absolute', inset: 0, background: '#4a2a8a'}} />
					<div style={{position: 'absolute', inset: 0, background: '#1f7a3e', clipPath: 'polygon(58% 0, 100% 0, 100% 100%, 42% 100%)'}} />
					<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 50%, rgba(255,255,255,0.12), rgba(0,0,0,0) 60%)'}} />
				</AbsoluteFill>
			}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.0, 1.05]}}
			golpes={[[W.marketing, 0.05], [W.suerte, 0.06]]}
			encima={
				<>
					<TituloArriba texto={'¿GENIOS DEL *MARKETING*...\nO PURA *SUERTE*?'} desde={W.genios} tam={100} />
					<Fundido desde={h - 12} duracion={12} />
				</>
			}
		>
			<Actor x={280} y={1960} alto={1120}>
				<Muneco ropa={ROPA_PUBLICISTA} acc={{gafas: true}} pose={{...brazo(1, alcanzar(1, 338, 168)), md: 'agarra', ...brazo(-1, alcanzar(-1, 140, 380)), mi: 'pulgar'}} objDer={<Ladrillo rot={160} />} ojos="normal" cejas="arrogante" boca="picara" />
			</Actor>
			<Bicho x={800} y={1200} tam={380} trebol camina={false} cara={f >= W.suerte ? 'feliz' : 'picaro'} />
			<Etiqueta x={300} y={900} texto="MARKETING" desde={W.marketing} color="#e9dcff" tam={60} />
			<Etiqueta x={800} y={960} texto="SUERTE" desde={W.suerte} color="#c9f5d4" tam={60} />
		</Toma>
	);
};

/* =============================== Montaje =============================== */

type Plano = {desde: number; Comp: React.FC<P>; entrada: Transicion};

const PLANOS: Plano[] = [
	{desde: 0, Comp: Gancho, entrada: 'corte'},
	{desde: antes(W.un1), Comp: Loca, entrada: 'latigoDer'},
	{desde: antes(W.y2), Comp: MasLoco, entrada: 'zoom'},
	{desde: antes(W.al3), Comp: Principio, entrada: 'latigoIzq'},
	{desde: antes(W.era3), Comp: RaceChase, entrada: 'latigoDer'},
	{desde: antes(W.y4), Comp: Aburrido, entrada: 'corte'},
	{desde: antes(W.tan), Comp: Cancelar, entrada: 'latigoArriba'},
	{desde: antes(W.hasta), Comp: ErrorCodigo, entrada: 'zoom'},
	{desde: antes(W.ya7), Comp: Persecucion, entrada: 'zoom'},
	{desde: antes(W.y9), Comp: Probadores, entrada: 'latigoIzq'},
	{desde: antes(W.lo10), Comp: Escape, entrada: 'zoom'},
	{desde: antes(W.y12), Comp: Spray, entrada: 'latigoDer'},
	{desde: antes(W.lo14), Comp: PizarraJuego, entrada: 'latigoIzq'},
	{desde: antes(W.y15), Comp: Nombre, entrada: 'zoom'},
	{desde: antes(W.pero16), Comp: Despues, entrada: 'latigoArriba'},
	{desde: antes(W.cuando), Comp: Inglaterra, entrada: 'latigoDer'},
	{desde: antes(W.esa), Comp: Inventada, entrada: 'zoom'},
	{desde: antes(W.contrataron), Comp: Experto, entrada: 'latigoIzq'},
	{desde: antes(W.y20), Comp: Hablaron, entrada: 'latigoArriba'},
	{desde: antes(W.veredicto), Comp: Veredicto, entrada: 'latigoDer'},
	{desde: antes(W.genios), Comp: Pregunta, entrada: 'zoom'},
];

export const Historia: React.FC = () => (
	<>
		{PLANOS.map((p, i) => {
			const sig = PLANOS[i + 1];
			return <p.Comp key={i} d={p.desde} h={sig ? sig.desde : FIN_VIDEO} e={p.entrada} s={sig ? sig.entrada : 'corte'} />;
		})}
		<TituloArriba texto={'GTA EXISTE\nPOR UN *BUG*'} desde={0} hasta={antes(W.un1)} tam={130} />
	</>
);

/** Efectos (pasan por la mezcla: siempre por debajo de la voz). [archivo, cuadro, volumen] */
export const SONIDOS: [string, number, number][] = [
	...PLANOS.filter((p) => p.entrada !== 'corte').map((p) => ['whoosh', p.desde - 10, 0.36] as [string, number, number]),
	['boing', W.bug0 - 6, 0.35],
	['sirena', W.un1, 0.3],
	['derrape', W.loca - 4, 0.3],
	['dundun', W.loco2 - 6, 0.35],
	['teclas', W.al3, 0.3],
	['sello', W.criminales, 0.4],
	['motor', W.carreras - 6, 0.3],
	['pop', W.policias3 - 4, 0.3],
	['pop', W.ladrones - 4, 0.3],
	['sello', W.aburridisimo - 2, 0.4],
	['dundun', W.cancelarse - 6, 0.35],
	['beep', W.error6 - 2, 0.35],
	['beep', W.error6 + 6, 0.35],
	['temblor', W.vuelve - 2, 0.3],
	['sirena', W.ya7 - 6, 0.25],
	['choque', W.embisten - 2, 0.5],
	['derrape', W.encierran - 6, 0.35],
	['choque', W.encierran - 2, 0.4],
	['choque', W.calle - 2, 0.5],
	['pop', W.soltarlo - 4, 0.3],
	['sirena', W.lo10 - 4, 0.3],
	['derrape', W.escaparse - 8, 0.4],
	['choque', tEsc(918), 0.4],
	['choque', tEsc(930), 0.4],
	['burbujas', W.bug12 - 4, 0.3],
	['objeto', W.contrario - 4, 0.4],
	['garabato', W.convirtieron + 6, 0.3],
	['pop', W.grand - 3, 0.4],
	['pop', W.theft - 3, 0.4],
	['boom', W.auto - 3, 0.45],
	['motor', W.autos + 4, 0.4],
	['dundun', W.loco16 - 6, 0.35],
	['sello', W.prohibirlo - 3, 0.4],
	['hoja', W.violento - 4, 0.3],
	['teclas', W.polemica - 2, 0.35],
	['sello', W.inventado - 4, 0.45],
	['beep', W.contrataron, 0.25],
	['hoja', W.escandalos - 4, 0.3],
	['hoja', W.mundo - 4, 0.3],
	['hoja', W.hablara - 4, 0.3],
	['aplausos', W.hablaron - 4, 0.3],
	['sello', W.real - 4, 0.5],
	['pop', W.marketing - 4, 0.35],
	['ding', W.suerte - 4, 0.35],
];

import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {Destello} from '../componentes/Efectos';
import {Actor, Muneco, POSES, Pose, ROPA_DOCTOR, ROPA_FRANCES, ROPA_GILLRAY, ROPA_GRANADERO, ROPA_INGLES, ROPA_NAPOLEON, animarPose, apuntar, manosEn} from '../componentes/Muneco';
import {Corazones, MarcaAltura, PeriodicosVolando, Pulgadas} from '../componentes/Napoleon';
import {Atril, CajaCinta, Caricatura, CintaEntre, DardoMano, DardoVolando, Espada, Mosquete, Nota, Papel, Pedestal, PeriodicoPecho, Pluma, Puntero, Retrato, Tiza as TizaMano} from '../componentes/Objetos';
import {Rotulo, TituloArriba} from '../componentes/Rotulos';
import {Toma, Transicion} from '../componentes/Toma';
import {Bocadillo, Brillos, Confeti, Fundido, Icono, Puf, Rayos, Sello, Tiza} from '../componentes/Utileria';
import {EscCelular, EscDesfile, EscEscenario, EscEstudio, EscMapa, EscMedidas, EscPalacio, EscPizarra, EscSantaHelena, MEME, PISO, altoParaCm, yDeCm} from '../escenarios/Escenarios';
import {CONDENSADA} from '../fuentes';
import {finFrase, palabra} from '../tiempos';

/*
 * "¿Napoleón era bajito?" — versión con personajes que actúan (estilo del video de referencia "Short 4").
 * Todo en cuadros GLOBALES: las acciones caen sobre la palabra exacta de la narración.
 */

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const antes = (n: number) => n - 3;
const TINTA = '#1b1b1f';

const W = {
	alto: palabra(0, 'alto'),
	promedio: palabra(0, 'promedio'),
	y1: palabra(1, 'Y'),
	enano: palabra(1, 'enano'),
	dibujante: palabra(1, 'dibujante'),
	en2: palabra(2, 'En'),
	anio1802: palabra(2, '1802'),
	napoleon2: palabra(2, 'Napoleón'),
	poderoso: palabra(2, 'poderoso'),
	pero3: palabra(3, 'Pero'),
	londres: palabra(3, 'Londres'),
	caricaturista: palabra(3, 'caricaturista'),
	odia: palabra(3, 'odia'),
	lo4: palabra(4, 'Lo'),
	diminuto: palabra(4, 'diminuto'),
	berrinches: palabra(4, 'berrinches'),
	apodo: palabra(4, 'apodo'),
	little: palabra(5, 'LITTLE'),
	boney: palabra(5, 'BONEY'),
	los6: palabra(6, 'Los'),
	copian: palabra(6, 'copian'),
	europa: palabra(6, 'Europa'),
	cuando: palabra(7, 'Cuando'),
	anio1821: palabra(7, '1821'),
	autopsia: palabra(7, 'autopsia'),
	cinco: palabra(7, 'cinco'),
	en8: palabra(8, 'En'),
	es8: palabra(8, 'es'),
	m157: palabra(9, '1,57'),
	pero10: palabra(10, 'Pero'),
	francesas: palabra(10, 'francesas'),
	largas: palabra(10, 'largas'),
	cuanto: palabra(11, '¿Cuánto'),
	m169: palabra(12, '1,69'),
	y13: palabra(13, '¿Y'),
	promedio13: palabra(13, 'promedio'),
	m165: palabra(14, '1,65'),
	para: palabra(15, 'Para'),
	guardia: palabra(15, 'guardia'),
	altos: palabra(15, 'altos'),
	y16: palabra(16, 'Y'),
	cabo: palabra(16, 'cabo'),
	carinoso: palabra(16, 'cariñoso'),
	veredicto: palabra(17, 'VEREDICTO'),
	mito: palabra(17, 'MITO'),
	emperador: palabra(18, '¿Emperador'),
	meme: palabra(18, 'meme'),
};

export const FIN_VIDEO = finFrase(18) + 30;

type P = {d: number; h: number; e: Transicion; s: Transicion};

/** valor escalonado: el de la última clave que ya pasó */
function segun<T>(f: number, claves: [number, T][]): T {
	let v = claves[0][1];
	for (const [c, x] of claves) if (f >= c) v = x;
	return v;
}

type Lugar = {x: number; y: number; alto: number};
/** punto del mundo → lienzo (400x900) de un actor */
const aLienzo = (a: Lugar, wx: number, wy: number): [number, number] => {
	const k = a.alto / 900;
	return [(wx - (a.x - 200 * k)) / k, (wy - (a.y - 880 * k)) / k];
};
/** punto del lienzo de un actor → mundo */
const aMundo = (a: Lugar, cx: number, cy: number): [number, number] => {
	const k = a.alto / 900;
	return [a.x - 200 * k + cx * k, a.y - 880 * k + cy * k];
};

/** Personaje parado sobre la tabla de estaturas con una estatura exacta. */
const EnTabla: React.FC<{x: number; cm: number; children: React.ReactNode; voltear?: boolean}> = ({x, cm, children, voltear}) => (
	<Actor x={x} y={PISO} alto={altoParaCm(cm)} voltear={voltear}>
		{children}
	</Actor>
);

/** Cabezal del tallímetro que baja hasta la coronilla. */
const Medidor: React.FC<{cm: number; x1: number; x2: number; color?: string}> = ({cm, x1, x2, color = '#ffd84a'}) => {
	const y = yDeCm(cm);
	return (
		<>
			<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
				<rect x={x2 - 14} y={y - 30} width={28} height={PISO - y + 30} fill="#c9ced6" stroke={TINTA} strokeWidth={6} />
				<rect x={x1} y={y - 18} width={x2 - x1} height={30} rx={8} fill={color} stroke={TINTA} strokeWidth={7} />
			</svg>
			<div style={{position: 'absolute', left: x2 + 20, top: y - 50, fontFamily: CONDENSADA, fontSize: 70, color: '#fff', WebkitTextStroke: `10px ${TINTA}`, paintOrder: 'stroke'}}>{`${(cm / 100).toFixed(2).replace('.', ',')}`}</div>
		</>
	);
};

const CAM_TABLA = {s: [1.0, 1.05] as [number, number], y: [10, 0] as [number, number]};

/* =============================== GANCHO =============================== */

const Gancho: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const xNap = interpolate(f, [0, 20], [-220, 320], {...clamp, easing: Easing.out(Easing.quad)});
	const napo = animarPose(f, [
		[0, {}],
		[24, {...POSES.jarras, cuerpo: -3, cabeza: -5}],
		[W.promedio - 2, {...POSES.jarras, cuerpo: -3, cabeza: 4}],
		[W.promedio + 6, {...manosEn([150, 548], [372, 412]), mi: 'puno', md: 'senala', wd: -20, cabeza: 8, cuerpo: 3}],
	]);
	const frances = animarPose(f, [
		[0, {}],
		[W.promedio + 2, {}],
		[W.promedio + 9, {...POSES.cruzados, cabeza: -6}],
	]);
	return (
		<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={CAM_TABLA} golpes={[[W.alto, 0.05], [W.promedio, 0.04]]}>
			<EnTabla x={xNap} cm={169}>
				<Muneco ropa={ROPA_NAPOLEON} pose={napo} camina={f < 20 ? 1.3 : 0} ojos={segun(f, [[0, 'normal'], [24, 'entrecerrados']])} cejas="arrogante" boca={segun(f, [[0, 'sonrisa'], [24, 'picara'], [W.promedio + 4, 'sonrisaGrande']])} />
			</EnTabla>
			<EnTabla x={770} cm={165} voltear>
				<Muneco ropa={ROPA_FRANCES} pose={frances} semilla={3} ojos={segun(f, [[0, 'normal'], [W.promedio, 'mirandoLado'], [W.promedio + 10, 'entrecerrados']])} cejas={segun(f, [[0, 'neutral'], [W.promedio + 8, 'enojado']])} boca={segun(f, [[0, 'sonrisa'], [W.promedio + 8, 'mueca']])} />
			</EnTabla>
			<MarcaAltura cm={169} desde={W.alto} color="#22a84f" lado="izq" x1={130} x2={560} />
			<MarcaAltura cm={165} desde={W.promedio} color="#1f6fd1" lado="der" x1={560} x2={950} />
		</Toma>
	);
};

const Enano: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const encoge = W.enano;
	const cm = interpolate(f, [encoge - 1, encoge + 6], [169, 104], {...clamp, easing: Easing.out(Easing.back(1.8))});
	const chico = f >= encoge;
	const napo: Partial<Pose> = chico
		? {...POSES.brazosArriba, bi: 150 + Math.sin(f * 0.9) * 18, bd: 150 + Math.cos(f * 0.9) * 18, salto: Math.abs(Math.sin(f * 0.5)) * 40, li: Math.max(0, Math.sin(f * 0.5)) * 0.4, ld: Math.max(0, -Math.sin(f * 0.5)) * 0.4}
		: {...POSES.jarras, cuerpo: -3};
	const frances = animarPose(f, [
		[d, {...POSES.cruzados}],
		[encoge + 4, {...POSES.cruzados}],
		[encoge + 11, {...manosEn([236, 470], [330, 610], {}, true), mi: 'abierta', md: 'senala', wd: 25, cuerpo: -8, cabeza: -10}],
	]);
	return (
		<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.16], y: [-60, -80], x: [60, 40]}} golpes={[[encoge, 0.08]]}>
			<EnTabla x={320} cm={cm}>
				<Muneco ropa={ROPA_NAPOLEON} pose={napo} ojos={chico ? 'grandes' : 'entrecerrados'} cejas={chico ? 'preocupado' : 'arrogante'} boca={chico ? 'grito' : 'picara'} tiembla={chico ? 1.5 : 0} />
			</EnTabla>
			<EnTabla x={770} cm={165} voltear>
				<Muneco ropa={ROPA_FRANCES} pose={frances} semilla={3} ojos={f >= encoge + 6 ? 'feliz' : 'entrecerrados'} cejas="arrogante" boca={f >= encoge + 6 ? 'sonrisaGrande' : 'mueca'} tiembla={f >= encoge + 8 ? 1.4 : 0} />
			</EnTabla>
			<Puf x={320} y={1300} desde={encoge - 1} tam={620} />
			<Icono tipo="exclamacion" x={330} y={1020} desde={encoge + 6} tam={150} />
		</Toma>
	);
};

const Dibujante: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const pose = animarPose(f, [
		[d, {...manosEn([150, 548], [306, 380]), mi: 'puno', md: 'agarra', cuerpo: 4, cabeza: 6}],
		[d + 12, {...manosEn([150, 548], [300, 330]), mi: 'puno', md: 'agarra', cuerpo: -2, cabeza: -6}],
	]);
	return (
		<Toma escena={<EscEstudio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.14], y: [-40, -60]}} encima={<><Rotulo texto="JAMES GILLRAY · CARICATURISTA" desde={d + 2} /></>}>
			<Actor x={540} y={1900} alto={1340}>
				<Muneco ropa={ROPA_GILLRAY} pose={{...pose, wd: Math.sin(f / 2.5) * 25}} objDer={<Pluma rot={-20} />} ojos="entrecerrados" cejas="arrogante" boca="picara" />
			</Actor>
		</Toma>
	);
};

/* =============================== DESARROLLO =============================== */

const Poderoso: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const desenvaina = W.poderoso - 12;
	const napo = animarPose(f, [
		[d, {...POSES.manoEnChaleco, ...manosEn([150, 540]), mi: 'relajada', cabeza: -4}],
		[desenvaina, {...POSES.manoEnChaleco, ...manosEn([150, 540]), mi: 'agarra', cabeza: -4}],
		[W.poderoso, {...POSES.manoEnChaleco, ...manosEn([40, 96]), mi: 'agarra', cabeza: -8, cuerpo: -3}],
	]);
	const saludo = animarPose(f, [
		[d, {...manosEn([118, 548]), mi: 'agarra'}],
		[W.napoleon2, {...manosEn([118, 548]), mi: 'agarra'}],
		[W.napoleon2 + 6, {...manosEn([118, 548], [262, 142]), mi: 'agarra', md: 'abierta', wd: 160}],
	]);
	const conEspada = f >= desenvaina;
	const vitorea = f >= W.poderoso;
	return (
		<Toma escena={<EscPalacio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.1], y: [0, -20]}} golpes={[[W.poderoso, 0.06]]} encima={<><TituloArriba texto="*1802*" desde={W.anio1802} tam={150} /><Rotulo texto="PARÍS · FRANCIA" desde={d + 2} /></>}>
			<Rayos x={540} y={900} color="#ffe9a0" opacidad={vitorea ? 0.32 : 0.12} />
			<Pedestal x={540} y={1490} ancho={440} alto={150} />
			<Actor x={540} y={1490} alto={900}>
				<Muneco ropa={ROPA_NAPOLEON} pose={napo} objIzq={conEspada ? <Espada rot={f < W.poderoso - 4 ? 160 : 0} brillo={vitorea ? 1 : 0} /> : undefined} ojos="entrecerrados" cejas="arrogante" boca={vitorea ? 'sonrisaGrande' : 'picara'} />
			</Actor>
			<Actor x={115} y={1960} alto={1020}>
				<Muneco ropa={ROPA_GRANADERO} pose={saludo} objIzq={<Mosquete />} ojos={vitorea ? 'feliz' : 'entrecerrados'} cejas="arrogante" boca={vitorea ? 'sonrisaGrande' : 'seria'} semilla={1} />
			</Actor>
			<Actor x={965} y={1960} alto={1020} voltear>
				<Muneco ropa={ROPA_GRANADERO} pose={saludo} objIzq={<Mosquete />} ojos={vitorea ? 'feliz' : 'entrecerrados'} cejas="arrogante" boca={vitorea ? 'sonrisaGrande' : 'seria'} semilla={4} />
			</Actor>
			<Brillos x={420} y={700} desde={W.poderoso} radio={300} n={9} />
		</Toma>
	);
};

const LoOdia: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const actor = {x: 330, y: 1900, alto: 1300};
	const lanza = W.odia - 7;
	const pose = animarPose(
		f,
		[
			[d, {...POSES.cruzados, cabeza: 4}],
			[W.caricaturista - 2, {...POSES.cruzados, cabeza: 4}],
			[W.caricaturista + 6, {...manosEn([150, 548]), mi: 'puno', md: 'agarra', bd: 60, cd: 70}],
			[lanza - 2, {...manosEn([150, 548]), mi: 'puno', md: 'agarra', bd: 150, cd: 40, cuerpo: -6, cabeza: -6}],
			[lanza + 2, {...manosEn([150, 548], [392, 300]), mi: 'puno', md: 'abierta', cuerpo: 8, cabeza: 4}],
		],
		5,
	);
	const [mx, my] = aMundo(actor, 392, 300);
	const enojo = f >= W.caricaturista;
	return (
		<Toma escena={<EscEstudio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [-20, -30]}} golpes={[[W.odia, 0.07]]} encima={<><TituloArriba texto="*LONDRES*" desde={W.londres} tam={140} /><Rotulo texto="INGLATERRA · 1803" desde={W.londres + 2} /></>}>
			<Retrato x={810} y={760} ancho={330} golpe={W.odia} />
			<DardoVolando x1={mx} y1={my} x2={790} y2={700} desde={lanza} llega={W.odia} />
			<Actor {...actor}>
				<Muneco ropa={ROPA_GILLRAY} pose={pose} objDer={f >= W.caricaturista + 2 && f < lanza ? <DardoMano rot={180} /> : undefined} ojos={enojo ? 'entrecerrados' : 'normal'} cejas="enojado" boca={f >= W.odia ? 'dientes' : enojo ? 'mueca' : 'seria'} />
			</Actor>
			<Icono tipo="enojo" x={250} y={720} desde={W.odia} tam={150} />
		</Toma>
	);
};

const ATRIL = {x: 700, y: 880, ancho: 520, alto: 660};

const Diminuto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const actor = {x: 250, y: 1920, alto: 1300};
	const dibujando = f < W.berrinches + 4 || f >= W.apodo - 4;
	const [px, py] = aLienzo(actor, ATRIL.x - 150 + Math.sin(f / 1.8) * 60, ATRIL.y + 40 + Math.cos(f / 2.6) * 50);
	const [tx, ty] = aLienzo(actor, ATRIL.x - 120 + (f - (W.apodo - 4)) * 6, ATRIL.y - 250);
	const pose = animarPose(f, [
		[d, {...manosEn([150, 548], [px, py]), mi: 'puno', md: 'agarra', cuerpo: 6, cabeza: 6}],
		[W.berrinches + 4, {...manosEn([150, 548], [px, py]), mi: 'puno', md: 'agarra', cuerpo: 6, cabeza: 6}],
		[W.berrinches + 10, {...manosEn([226, 486], [330, 300], {}, true), mi: 'abierta', md: 'agarra', cuerpo: -8, cabeza: -10}],
		[W.apodo - 6, {...manosEn([226, 486], [330, 300], {}, true), mi: 'abierta', md: 'agarra', cuerpo: -8, cabeza: -10}],
		[W.apodo, {...manosEn([150, 548], [tx, ty]), mi: 'puno', md: 'agarra', cuerpo: 8, cabeza: 4}],
	]);
	const poseFinal = f < W.berrinches + 4 ? {...pose, ...manosEn(undefined, [px, py])} : f >= W.apodo ? {...pose, ...manosEn(undefined, [tx, ty])} : pose;
	const riendo = !dibujando;
	return (
		<Toma escena={<EscEstudio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.12], y: [-30, -50], x: [-20, -40]}} golpes={[[W.diminuto, 0.05], [W.berrinches, 0.05]]} encima={<><TituloArriba texto="LO DIBUJA *DIMINUTO*" desde={W.diminuto} tam={118} /></>}>
			<Atril {...ATRIL}>
				<Caricatura ancho={ATRIL.ancho - 52} alto={ATRIL.alto - 52} desde={W.diminuto - 2} berrinche={W.berrinches} titulo={1e9} />
			</Atril>
			<Actor {...actor}>
				<Muneco ropa={ROPA_GILLRAY} pose={poseFinal} objDer={<Pluma rot={-30} />} ojos={riendo ? 'feliz' : 'entrecerrados'} cejas="arrogante" boca={riendo ? 'sonrisaGrande' : 'picara'} tiembla={riendo ? 1.3 : 0} />
			</Actor>
		</Toma>
	);
};

const LittleBoney: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const letras = interpolate(f, [W.little, W.little + 10], [0, 1], clamp);
	const ancho = 780;
	const alto = 990;
	const px = 540 - 300 + letras * 600;
	const py = 1000 - alto / 2 + 80 + Math.sin(f * 1.3) * 16;
	return (
		<Toma escena={<EscEstudio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}} golpes={[[W.boney, 0.08]]}>
			<Papel x={540} y={1000} ancho={ancho} alto={alto} rot={-2}>
				<Caricatura ancho={ancho - 52} alto={alto - 52} berrinche={W.diminuto} titulo={W.little} trazo={false} />
			</Papel>
			{f < W.little + 14 && (
				<div style={{position: 'absolute', left: px, top: py - 230, width: 200, height: 300}}>
					<svg viewBox="-60 -200 200 300" width="100%" height="100%" style={{overflow: 'visible'}}>
						<g transform="rotate(25)">
							<Pluma />
						</g>
					</svg>
				</div>
			)}
		</Toma>
	);
};

const Periodicos: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const risa = f >= W.copian;
	const pose = animarPose(f, [
		[d, {...manosEn([62, 420], [338, 420]), mi: 'agarra', md: 'agarra'}],
		[W.copian, {...manosEn([62, 420], [338, 420]), mi: 'agarra', md: 'agarra', cabeza: 0}],
		[W.copian + 6, {...manosEn([62, 420], [338, 420]), mi: 'agarra', md: 'agarra', cabeza: -12, cuerpo: -5}],
	]);
	return (
		<Toma escena={<EscMapa />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [0, -10]}} golpes={[[W.europa, 0.05]]} encima={<><TituloArriba texto="EN TODA *EUROPA*" desde={W.copian} tam={120} /></>}>
			<PeriodicosVolando desde={W.los6 - 2} />
			<Actor x={540} y={2010} alto={1120}>
				<Muneco ropa={ROPA_INGLES} pose={pose} objPecho={<PeriodicoPecho x={200} y={440} ancho={300} alto={290} />} ojos={risa ? 'cerrados' : 'grandes'} cejas={risa ? 'arrogante' : 'sorprendido'} boca={risa ? 'sonrisaGrande' : 'o'} tiembla={risa ? 1.6 : 0} semilla={2} />
			</Actor>
		</Toma>
	);
};

/* =============================== CONFLICTO =============================== */

const Autopsia: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const actor = {x: 840, y: 1610, alto: 1080};
	const tira = W.autopsia - 4;
	const extremo = interpolate(f, [tira, tira + 22], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const xFin = 800 - extremo * 630;
	const [cx, cy] = aLienzo(actor, 800, 1135);
	const pose = animarPose(f, [
		[d, {...manosEn([170, 520], [230, 520], {}, true), mi: 'relajada', md: 'relajada', cabeza: 8}],
		[tira - 4, {...manosEn([170, 520], [230, 520], {}, true), mi: 'relajada', md: 'relajada', cabeza: 8}],
		[tira, {...manosEn([cx, cy]), mi: 'agarra', md: 'relajada', cabeza: 4}],
		[W.cinco - 2, {...manosEn([cx, cy]), mi: 'agarra', md: 'relajada', cabeza: -4}],
		[W.cinco + 6, {...manosEn([cx, cy], [300, 250]), mi: 'agarra', md: 'senala', wd: 160, cabeza: -6}],
	]);
	return (
		<Toma escena={<EscSantaHelena />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.03, 1.09], y: [-20, -40]}} golpes={[[W.cinco, 0.05]]} encima={<><TituloArriba texto="*1821*" desde={W.anio1821} tam={150} /><Rotulo texto="ISLA DE SANTA HELENA" desde={d + 3} /></>}>
			{f >= tira && <CintaEntre x1={xFin} y1={1128} x2={800} y2={1128} />}
			<Actor {...actor}>
				<Muneco ropa={ROPA_DOCTOR} pose={pose} objIzq={f >= tira ? <CajaCinta /> : undefined} ojos={segun(f, [[d, 'cerrados'], [tira - 6, 'normal'], [W.cinco - 2, 'grandes']])} cejas={segun(f, [[d, 'preocupado'], [W.cinco - 2, 'sorprendido']])} boca={segun(f, [[d, 'seria'], [W.cinco - 2, 'o']])} semilla={5} />
			</Actor>
			<Nota x={470} y={860} texto="5 pies y 2 pulgadas" desde={W.cinco} tam={60} />
		</Toma>
	);
};

const Inglaterra: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const actor = {x: 890, y: 1960, alto: 1200};
	const avance = interpolate(f, [d + 2, W.es8], [0, 1], clamp);
	const [ex, ey] = aLienzo(actor, 260 + avance * 340, 790 + Math.sin(f * 1.2) * 14);
	const pose = animarPose(f, [
		[d, {...manosEn([ex, ey], [250, 548]), mi: 'agarra', md: 'puno', cuerpo: -6, cabeza: -6}],
		[W.es8 - 2, {...manosEn([ex, ey], [250, 548]), mi: 'agarra', md: 'puno', cuerpo: -6, cabeza: -6}],
		[W.es8 + 6, {...manosEn([150, 548], [318, 130]), mi: 'puno', md: 'abierta', frenteD: 1, wd: 170, cabeza: 8, cuerpo: 0}],
	]);
	const poseF = f < W.es8 - 2 ? {...pose, ...manosEn([ex, ey])} : pose;
	return (
		<Toma escena={<EscPizarra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08]}} encima={<><TituloArriba texto="EN *INGLATERRA*..." desde={d + 2} tam={124} /></>}>
			<Tiza x={120} y={600} texto="5 pies 2 pulg." desde={d + 2} tam={80} duracion={18} rot={-2} />
			<Tiza x={140} y={760} texto="= ¿? cm" desde={d + 22} tam={96} duracion={10} rot={-2} />
			<Actor {...actor}>
				<Muneco ropa={ROPA_INGLES} pose={poseF} objIzq={f < W.es8 + 2 ? <TizaMano /> : undefined} ojos={f >= W.es8 ? 'mirandoLado' : 'entrecerrados'} cejas={f >= W.es8 ? 'preocupado' : 'neutral'} boca={f >= W.es8 ? 'mueca' : 'seria'} semilla={2} />
			</Actor>
		</Toma>
	);
};

const Mide157: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cm = interpolate(f, [W.m157 - 1, W.m157 + 6], [169, 157], {...clamp, easing: Easing.out(Easing.back(2))});
	const risa = f >= W.m157 + 4;
	const ingles = animarPose(f, [
		[d, {...POSES.jarras}],
		[W.m157 + 2, {...POSES.jarras}],
		[W.m157 + 9, {...manosEn([118, 640], [224, 470], {}, true), mi: 'senala', md: 'abierta', wi: -10, cuerpo: 6, cabeza: -8}],
	]);
	const napo = animarPose(f, [
		[d, {...POSES.firme}],
		[W.m157 + 4, {...POSES.firme}],
		[W.m157 + 10, {...POSES.jarras, cabeza: 6}],
	]);
	return (
		<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={CAM_TABLA} golpes={[[W.m157, 0.07]]} encima={<><TituloArriba texto="*1,57 M|#ff5a4f*" desde={W.m157} tam={160} /></>}>
			<EnTabla x={320} cm={cm}>
				<Muneco ropa={ROPA_NAPOLEON} pose={napo} ojos={f >= W.m157 ? 'grandes' : 'normal'} cejas={f >= W.m157 + 10 ? 'enojado' : 'sorprendido'} boca={f >= W.m157 + 10 ? 'mueca' : 'o'} tiembla={f >= W.m157 + 10 ? 0.8 : 0} />
			</EnTabla>
			<EnTabla x={770} cm={178} voltear>
				<Muneco ropa={ROPA_INGLES} pose={ingles} semilla={2} ojos={risa ? 'feliz' : 'entrecerrados'} cejas="arrogante" boca={risa ? 'sonrisaGrande' : 'picara'} tiembla={risa ? 1.4 : 0} />
			</EnTabla>
			<MarcaAltura cm={157} desde={W.m157} color="#e3262e" lado="izq" x1={130} x2={560} />
		</Toma>
	);
};

const PulgadasFrancesas: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const actor = {x: 330, y: 1880, alto: 900};
	const LARGO = 400;
	// la punta del puntero: primero en alto (como maestro), luego golpecitos al final de la barra francesa
	const toque = f >= W.francesas && f < W.largas ? Math.abs(Math.sin((f - W.francesas) / 2.2)) * 22 : 0;
	const [bx, by] = aLienzo(actor, 784 - toque, 969 + toque * 0.5);
	const arriba = apuntar(1, 330, -250, LARGO);
	const barra = apuntar(1, bx, by, LARGO);
	const pose = animarPose(f, [
		[d, {bd: arriba.a, cd: arriba.c, ...manosEn([150, 548]), mi: 'puno', md: 'agarra', cabeza: 4}],
		[W.francesas - 4, {bd: arriba.a, cd: arriba.c, ...manosEn([150, 548]), mi: 'puno', md: 'agarra', cabeza: 4}],
		[W.francesas + 2, {bd: barra.a, cd: barra.c, ...manosEn([150, 548]), mi: 'puno', md: 'agarra', cabeza: 8, cuerpo: 3}],
		[W.largas, {bd: barra.a, cd: barra.c, ...manosEn([150, 548]), mi: 'puno', md: 'agarra', cabeza: 8, cuerpo: 3}],
		[W.largas + 6, {bd: barra.a, cd: barra.c, md: 'agarra', mi: 'puno', bi: 150, ci: 20, cabeza: 0, salto: 34}],
		[W.largas + 12, {bd: barra.a, cd: barra.c, md: 'agarra', mi: 'puno', bi: 150, ci: 20, cabeza: 0, salto: 0}],
	]);
	const tocando = f >= W.francesas + 2;
	const poseF = tocando ? {...pose, bd: barra.a, cd: barra.c} : pose;
	return (
		<Toma escena={<EscPizarra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}} golpes={[[W.largas, 0.05]]} encima={<><TituloArriba texto="PULGADAS *FRANCESAS*" desde={d + 2} tam={112} /></>}>
			<Pulgadas desde={W.pero10 - 2} />
			<Actor {...actor}>
				<Muneco ropa={ROPA_NAPOLEON} pose={poseF} objDer={<Puntero largo={LARGO} />} ojos={f >= W.largas ? 'feliz' : 'entrecerrados'} cejas="arrogante" boca={f >= W.largas ? 'sonrisaGrande' : 'picara'} />
			</Actor>
			<Brillos x={800} y={969} desde={W.largas} radio={240} />
		</Toma>
	);
};

const Cuanto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const llega = W.m169;
	const cmNap = interpolate(f, [llega - 1, llega + 6], [157, 169], {...clamp, easing: Easing.out(Easing.back(2))});
	const cabezal =
		f < llega
			? interpolate(f, [d + 6, llega - 2], [205, 158], {...clamp, easing: Easing.inOut(Easing.quad)})
			: interpolate(f, [llega - 1, llega + 6], [157, 169], {...clamp, easing: Easing.out(Easing.back(2))});
	const feliz = f >= llega + 2;
	const napo: Partial<Pose> = feliz
		? animarPose(f, [
				[llega + 2, {...POSES.firme}],
				[llega + 8, {...POSES.victoria, salto: 60, li: 0.3, ld: 0.3}],
				[llega + 16, {...POSES.victoria, salto: 0}],
				[llega + 22, {...POSES.victoria, bi: 130, bd: 130, salto: 40, li: 0.25, ld: 0.25}],
				[llega + 30, {...POSES.victoria, salto: 0}],
			])
		: {...POSES.firme, cabeza: Math.sin(f / 3) * 2};
	return (
		<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [-10, -30]}} golpes={[[llega, 0.08]]} encima={<><TituloArriba texto="¿CUÁNTO *MEDÍA*?" desde={d + 2} hasta={llega} tam={130} /><TituloArriba texto="¡CASI *1,69 M|#3fe07a*!" desde={llega} tam={150} /></>}>
			<Medidor cm={cabezal} x1={330} x2={760} />
			<EnTabla x={540} cm={cmNap}>
				<Muneco ropa={ROPA_NAPOLEON} pose={napo} ojos={feliz ? 'feliz' : f >= d + 6 ? 'grandes' : 'normal'} cejas={feliz ? 'arrogante' : 'preocupado'} boca={feliz ? 'sonrisaGrande' : 'o'} tiembla={!feliz && f > d + 10 ? 0.5 : 0} />
			</EnTabla>
			{feliz && <MarcaAltura cm={169} desde={llega + 2} color="#22a84f" lado="izq" x1={130} x2={430} />}
			<Confeti desde={llega + 2} n={50} />
		</Toma>
	);
};

const ElFrances: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const x = interpolate(f, [d, W.promedio13 + 4], [1300, 770], {...clamp, easing: Easing.out(Easing.quad)});
	const caminando = f < W.promedio13 + 2;
	const frances = animarPose(f, [
		[d, {}],
		[W.promedio13 + 4, {}],
		[W.m165 + 6, {...POSES.cruzados, cabeza: -5}],
		[W.m165 + 22, {...POSES.encogeHombros}],
	]);
	const napo = animarPose(f, [
		[d, {...POSES.manoEnChaleco, ...manosEn([150, 548]), mi: 'puno'}],
		[W.m165 + 2, {...POSES.manoEnChaleco, ...manosEn([150, 548]), mi: 'puno'}],
		[W.m165 + 9, {...POSES.pulgarArriba, ...manosEn([150, 548]), mi: 'puno', cabeza: 6}],
	]);
	return (
		<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={CAM_TABLA} golpes={[[W.m165, 0.05]]} encima={<><TituloArriba texto="¿Y EL FRANCÉS *PROMEDIO*?" desde={d + 2} hasta={W.m165} tam={104} /><TituloArriba texto="*1,65 M|#5aa8ff*" desde={W.m165} tam={150} /></>}>
			<EnTabla x={320} cm={169}>
				<Muneco ropa={ROPA_NAPOLEON} pose={napo} ojos={f >= W.m165 ? 'entrecerrados' : 'mirandoLado'} cejas="arrogante" boca={f >= W.m165 + 4 ? 'sonrisaGrande' : 'picara'} />
			</EnTabla>
			<MarcaAltura cm={169} desde={d - 40} color="#22a84f" lado="izq" x1={130} x2={560} />
			<EnTabla x={x} cm={165} voltear>
				<Muneco
					ropa={ROPA_FRANCES}
					pose={frances}
					camina={caminando ? 1.2 : 0}
					semilla={3}
					ojos={segun(f, [[d, 'normal'], [W.m165 + 4, 'entrecerrados']])}
					cejas={segun(f, [[d, 'neutral'], [W.m165 + 4, 'enojado'], [W.m165 + 20, 'preocupado']])}
					boca={segun(f, [[d, 'sonrisa'], [W.m165 + 4, 'mueca'], [W.m165 + 20, 'seria']])}
				/>
			</EnTabla>
			<MarcaAltura cm={165} desde={W.m165} color="#1f6fd1" lado="der" x1={560} x2={950} />
		</Toma>
	);
};

/* =============================== LA GUARDIA =============================== */

const Guardia: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const salta = W.altos - 4;
	const napo: Partial<Pose> =
		f < salta
			? {}
			: animarPose(f, [
					[salta, {}],
					[salta + 6, {...POSES.brazosArriba, salto: 110, li: 0.4, ld: 0.4, bi: 165}],
					[salta + 12, {...POSES.brazosArriba, salto: 0}],
					[salta + 18, {...POSES.brazosArriba, salto: 100, li: 0.4, ld: 0.4}],
					[salta + 24, {...POSES.brazosArriba, salto: 0}],
				]);
	const mira = f >= W.altos;
	const guardia = (semilla: number) => (
		<Muneco
			ropa={ROPA_GRANADERO}
			pose={{...manosEn([108, 300]), mi: 'agarra', cabeza: mira ? -10 : 0}}
			objIzq={<Mosquete rot={8} />}
			camina={f < salta ? 1 : 0}
			ojos={mira ? 'mirandoLado' : 'entrecerrados'}
			cejas="arrogante"
			boca="seria"
			semilla={semilla}
		/>
	);
	return (
		<Toma escena={<EscDesfile />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [30, 0]}} golpes={[[W.altos, 0.06]]} encima={<><TituloArriba texto="LA *GUARDIA IMPERIAL*" desde={W.guardia} tam={116} /><Rotulo texto="TODOS DE MÁS DE 1,80 M" desde={W.altos} y={485} tam={46} /></>}>
			<Actor x={180} y={1990} alto={1400}>
				{guardia(1)}
			</Actor>
			<Actor x={900} y={1990} alto={1400} voltear>
				{guardia(4)}
			</Actor>
			<Actor x={540} y={1930} alto={960}>
				<Muneco ropa={ROPA_NAPOLEON} pose={napo} camina={f < salta ? 1 : 0} ojos={f >= salta ? 'grandes' : 'normal'} cejas={f >= salta ? 'preocupado' : 'neutral'} boca={f >= salta ? 'abierta' : 'sonrisa'} />
			</Actor>
		</Toma>
	);
};

const PequenoCabo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sube = interpolate(f, [d + 2, d + 16], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.4))});
	const izq = {x: 250, y: 1990, alto: 1300};
	const der = {x: 830, y: 1990, alto: 1300};
	const pieY = 1930 - sube * 560;
	const [lx, ly] = aLienzo(izq, 470, pieY - 10);
	const [rx, ry] = aLienzo(der, 610, pieY - 10);
	const alza = (manoX: number, manoY: number): Partial<Pose> => ({...manosEn([120, 540], [manoX, manoY]), mi: 'puno', md: 'abierta', wd: 150});
	const saludo = Math.sin(f / 2.2) * 25;
	return (
		<Toma escena={<EscDesfile />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [0, -10]}} golpes={[[W.cabo, 0.06]]} encima={<><TituloArriba texto="«EL PEQUEÑO *CABO*»" desde={W.cabo} tam={104} /></>}>
			<Actor {...izq}>
				<Muneco ropa={ROPA_GRANADERO} pose={alza(lx, ly)} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" semilla={1} />
			</Actor>
			<Actor {...der} voltear>
				<Muneco ropa={ROPA_GRANADERO} pose={alza(400 - rx, ry)} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" semilla={4} />
			</Actor>
			<Actor x={540} y={pieY} alto={900}>
				<Muneco ropa={{...ROPA_NAPOLEON, cabeza: {...ROPA_NAPOLEON.cabeza, mejillas: true}}} pose={{...manosEn([150, 548]), mi: 'puno', bd: 150, cd: 20, md: 'abierta', wd: saludo, pi: 8, pd: 8}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
			</Actor>
			<Bocadillo x={290} y={650} texto="¡PETIT CAPORAL!" desde={W.cabo - 2} cola="izq" ancho={510} tam={42} />
			<Corazones x={540} y={1000} desde={W.carinoso - 4} n={12} />
		</Toma>
	);
};

/* =============================== VEREDICTO Y PREGUNTA =============================== */

const Veredicto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const mito = f >= W.mito;
	const pose = animarPose(f, [
		[d, {...POSES.manoEnChaleco, ...manosEn([150, 548]), mi: 'puno'}],
		[W.mito - 2, {...POSES.manoEnChaleco, ...manosEn([150, 548]), mi: 'puno'}],
		[W.mito + 4, {...manosEn([150, 548]), mi: 'puno', bd: 160, cd: 10, md: 'puno', salto: 50, cabeza: -6}],
		[W.mito + 10, {...manosEn([150, 548]), mi: 'puno', bd: 160, cd: 10, md: 'puno', salto: 0, cabeza: -6}],
	]);
	return (
		<Toma escena={<EscEscenario />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], y: [0, -10]}} golpes={[[W.mito, 0.08]]} encima={<><Destello desde={W.mito} color="#ff8a7a" fuerza={0.45} duracion={12} /><TituloArriba texto="*VEREDICTO*" desde={W.veredicto} tam={150} /></>}>
			<Pedestal x={540} y={1530} ancho={420} alto={160} />
			<Actor x={540} y={1530} alto={940}>
				<Muneco ropa={ROPA_NAPOLEON} pose={pose} ojos={mito ? 'feliz' : 'entrecerrados'} cejas="arrogante" boca={mito ? 'sonrisaGrande' : 'picara'} />
			</Actor>
			<Sello x={540} y={1090} texto="MITO" icono="✘" color="#d6262e" desde={W.mito} tam={140} rot={-8} />
			<Confeti desde={W.mito} n={60} />
		</Toma>
	);
};

const PrimerMeme: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const reacciones = interpolate(f, [d, W.meme + 6], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
	const asoma = interpolate(f, [d + 6, d + 18], [600, 0], {...clamp, easing: Easing.out(Easing.back(1.4))});
	const pose = animarPose(f, [
		[d, {...POSES.jarras}],
		[W.meme - 6, {...POSES.jarras}],
		[W.meme, {...POSES.encogeHombros}],
	]);
	return (
		<Toma escena={<EscCelular reacciones={reacciones} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [40, 40]}} golpes={[[W.meme, 0.06]]} encima={<><TituloArriba texto={'¿EMPERADOR *BAJITO*...\nO *PRIMER MEME|#ff5a4f*?'} desde={W.emperador} tam={96} y={160} /></>}>
			<div style={{position: 'absolute', left: MEME.x, top: MEME.y, width: MEME.w, height: MEME.h, overflow: 'hidden', filter: 'sepia(0.55) saturate(0.8) contrast(1.15)'}}>
				<Caricatura ancho={MEME.w} alto={MEME.h} berrinche={d - 200} titulo={d - 100} trazo={false} />
			</div>
			<Actor x={760 + asoma} y={2110} alto={1260}>
				<Muneco ropa={ROPA_NAPOLEON} pose={pose} ojos={f >= W.meme ? 'entrecerrados' : 'mirandoLado'} cejas={f >= W.meme ? 'arrogante' : 'enojado'} boca={f >= W.meme ? 'picara' : 'mueca'} />
			</Actor>
			<Confeti desde={W.meme} n={40} />
			<Fundido desde={h - 12} duracion={12} />
		</Toma>
	);
};

/* =============================== Montaje =============================== */

type Plano = {desde: number; Comp: React.FC<P>; entrada: Transicion};

const PLANOS: Plano[] = [
	{desde: 0, Comp: Gancho, entrada: 'corte'},
	{desde: antes(W.y1), Comp: Enano, entrada: 'corte'},
	{desde: antes(W.dibujante), Comp: Dibujante, entrada: 'latigoDer'},
	{desde: antes(W.en2), Comp: Poderoso, entrada: 'latigoIzq'},
	{desde: antes(W.pero3), Comp: LoOdia, entrada: 'latigoDer'},
	{desde: antes(W.lo4), Comp: Diminuto, entrada: 'corte'},
	{desde: antes(W.little), Comp: LittleBoney, entrada: 'zoom'},
	{desde: antes(W.los6), Comp: Periodicos, entrada: 'latigoArriba'},
	{desde: antes(W.cuando), Comp: Autopsia, entrada: 'latigoIzq'},
	{desde: antes(W.en8), Comp: Inglaterra, entrada: 'latigoDer'},
	{desde: antes(W.m157), Comp: Mide157, entrada: 'corte'},
	{desde: antes(W.pero10), Comp: PulgadasFrancesas, entrada: 'latigoArriba'},
	{desde: antes(W.cuanto), Comp: Cuanto, entrada: 'latigoIzq'},
	{desde: antes(W.y13), Comp: ElFrances, entrada: 'corte'},
	{desde: antes(W.para), Comp: Guardia, entrada: 'latigoArriba'},
	{desde: antes(W.y16), Comp: PequenoCabo, entrada: 'corte'},
	{desde: antes(W.veredicto), Comp: Veredicto, entrada: 'zoom'},
	{desde: antes(W.emperador), Comp: PrimerMeme, entrada: 'latigoDer'},
];

export const Historia: React.FC = () => (
	<>
		{PLANOS.map((p, i) => {
			const sig = PLANOS[i + 1];
			return <p.Comp key={i} d={p.desde} h={sig ? sig.desde : FIN_VIDEO} e={p.entrada} s={sig ? sig.entrada : 'corte'} />;
		})}
		{/* el título del gancho se mantiene entre las dos primeras tomas */}
		<TituloArriba texto="¿NAPOLEÓN *BAJITO*?" desde={0} hasta={antes(W.dibujante)} tam={132} />
	</>
);

/** Efectos (pasan por la mezcla: siempre por debajo de la voz). [archivo, cuadro, volumen] */
export const SONIDOS: [string, number, number][] = [
	...PLANOS.filter((p) => p.entrada !== 'corte').map((p) => ['whoosh', p.desde - 7, 0.36] as [string, number, number]),
	['tic', 4, 0.3],
	['tic', 12, 0.3],
	['pop', W.alto, 0.45],
	['pop', W.promedio, 0.45],
	['boing', W.enano - 2, 0.6],
	['pop', W.enano, 0.4],
	['garabato', antes(W.dibujante) + 2, 0.35],
	['pop', W.anio1802, 0.4],
	['ding', W.poderoso, 0.4],
	['aplausos', W.poderoso + 2, 0.3],
	['pop', W.londres, 0.4],
	['whoosh', W.odia - 7, 0.35],
	['objeto', W.odia, 0.55],
	['garabato', antes(W.lo4) + 2, 0.4],
	['garabato', W.diminuto, 0.4],
	['boing', W.berrinches, 0.4],
	['garabato', W.apodo, 0.35],
	['garabato', W.little, 0.4],
	['sello', W.boney, 0.5],
	['hoja', W.los6, 0.4],
	['hoja', W.los6 + 8, 0.4],
	['hoja', W.los6 + 16, 0.4],
	['pop', W.anio1821, 0.4],
	['hoja', W.autopsia - 4, 0.35],
	['pop', W.cinco, 0.4],
	['garabato', antes(W.en8) + 4, 0.35],
	['boing', W.m157 - 1, 0.6],
	['pop', W.m157, 0.4],
	['pop', W.pero10, 0.35],
	['pop', W.pero10 + 12, 0.35],
	['ding', W.largas, 0.35],
	['tic', W.cuanto + 6, 0.35],
	['tic', W.cuanto + 14, 0.35],
	['tic', W.cuanto + 22, 0.35],
	['tic', W.cuanto + 30, 0.35],
	['boing', W.m169 - 1, 0.55],
	['ding', W.m169 + 2, 0.4],
	['aplausos', W.m169 + 4, 0.3],
	['pop', W.m165, 0.45],
	['tic', W.para, 0.3],
	['tic', W.para + 10, 0.3],
	['tic', W.para + 20, 0.3],
	['tic', W.para + 30, 0.3],
	['tic', W.para + 40, 0.3],
	['boing', W.altos - 2, 0.45],
	['boing', W.y16 + 2, 0.4],
	['aplausos', W.cabo, 0.4],
	['ding', W.carinoso, 0.3],
	['sello', W.mito, 0.7],
	['aplausos', W.mito + 2, 0.35],
	['pop', W.meme, 0.45],
];

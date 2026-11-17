import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {Destello} from '../componentes/Efectos';
import {Actor, Muneco, POSES, Pose, alcanzar, animarPose, manosEn, manosFrente, senalar} from '../componentes/Muneco';
import {Abanico, Antorcha, Bandera, Brioche, Canasta, Carta, Carruaje, Cofre, LibroAbierto, Muneca, Pedestal, PlatoPastel, Pluma, PastelMesa} from '../componentes/Objetos';
import {Rotulo, TituloArriba} from '../componentes/Rotulos';
import {Toma, Transicion} from '../componentes/Toma';
import {Bocadillo, Fundido, Icono, Puf, Sello} from '../componentes/Utileria';
import {ROPA_DAMA_1, ROPA_DAMA_2, ROPA_LUIS, ROPA_MARIA, ROPA_MARIA_BLANCO, ROPA_MARIA_JOVEN, ROPA_MARIA_NINA, ROPA_PUEBLO_1, ROPA_PUEBLO_2, ROPA_PUEBLO_3, ROPA_ROUSSEAU} from '../componentes/Vestuario';
import {BALCON_Y, CIUDADES, EscBalcon, EscCadalso, EscCalle, EscEscenario, EscFilosofo, EscMapa, EscVersalles, EscViena} from '../escenarios/Escenarios';
import {CONDENSADA} from '../fuentes';
import {finFrase, palabra} from '../tiempos';

/*
 * «¿María Antonieta dijo "que coman pasteles"?» — los personajes actúan cada frase.
 * Cuadros GLOBALES: cada acción cae sobre la palabra exacta de la narración.
 */

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const antes = (n: number) => n - 3;
const TINTA = '#1b1b1f';

const W = {
	nunca: palabra(0, 'nunca'),
	que0: palabra(0, 'que'),
	pasteles0: palabra(0, 'pasteles'),
	y1: palabra(1, 'y'),
	escribio1: palabra(1, 'escribió'),
	nina1: palabra(1, 'niña'),
	en2: palabra(2, 'En'),
	anio1770: palabra(2, '1770'),
	princesa: palabra(2, 'princesa'),
	catorce: palabra(2, '14'),
	versalles: palabra(2, 'Versalles'),
	casarse: palabra(2, 'casarse'),
	rey: palabra(2, 'rey'),
	pero3: palabra(3, 'Pero'),
	quieren: palabra(3, 'quieren'),
	la4: palabra(4, 'La'),
	austriaca: palabra(4, 'Austríaca'),
	esconde: palabra(5, 'esconde'),
	perra: palabra(5, 'perra'),
	cuando6: palabra(6, 'Cuando'),
	arruina: palabra(6, 'arruina'),
	madame: palabra(6, 'Madame'),
	llega7: palabra(7, 'Llega'),
	revolucion: palabra(7, 'Revolución'),
	pan7: palabra(7, 'pan'),
	persigue: palabra(7, 'persigue'),
	que8: palabra(8, 'QUE'),
	la9: palabra(9, 'La'),
	nadie9: palabra(9, 'nadie'),
	pero10: palabra(10, 'Pero'),
	quien: palabra(10, 'quién'),
	nadie11: palabra(11, 'NADIE'),
	la12: palabra(12, 'La'),
	libro: palabra(12, 'libro'),
	filosofo: palabra(12, 'filósofo'),
	una12: palabra(12, 'una'),
	sin12: palabra(12, 'sin'),
	y13: palabra(13, 'Y'),
	pasteles13: palabra(13, 'pasteles'),
	brioche: palabra(13, 'brioche'),
	y14: palabra(14, 'Y'),
	escribio14: palabra(14, 'escribió'),
	en15: palabra(15, 'EN'),
	nina15: palabra(15, 'NIÑA'),
	lo16: palabra(16, 'Lo'),
	anio1775: palabra(16, '1775'),
	revueltas: palabra(16, 'revueltas'),
	le16: palabra(16, 'le'),
	trabajar: palabra(16, 'trabajar'),
	dieciocho: palabra(17, '18'),
	guillotinan: palabra(17, 'guillotinan'),
	veredicto: palabra(18, 'VEREDICTO'),
	falso: palabra(18, 'FALSO'),
	reina: palabra(19, 'Reina'),
	fake: palabra(19, 'fake'),
};

export const FIN_VIDEO = finFrase(19) + 30;

type P = {d: number; h: number; e: Transicion; s: Transicion};

function segun<T>(f: number, claves: [number, T][]): T {
	let v = claves[0][1];
	for (const [c, x] of claves) if (f >= c) v = x;
	return v;
}

type Lugar = {x: number; y: number; alto: number};
const aLienzo = (a: Lugar, wx: number, wy: number): [number, number] => {
	const k = a.alto / 900;
	return [(wx - (a.x - 200 * k)) / k, (wy - (a.y - 880 * k)) / k];
};
const brazo = (lado: -1 | 1, r: {a: number; c: number; k?: number}): Partial<Pose> => (lado < 0 ? {bi: r.a, ci: r.c, ai: r.k ?? 1} : {bd: r.a, cd: r.c, ad: r.k ?? 1});

/** sostener la falda con las dos manos (reverencia) */
const FALDA: Partial<Pose> = {...manosFrente([118, 560], [282, 560]), mi: 'agarra', md: 'agarra'};
/** abanico frente a la boca (chisme) */
const CHISME = (lado: -1 | 1): Partial<Pose> => ({...brazo(lado, alcanzar(lado, lado < 0 ? 180 : 220, 236)), ...(lado < 0 ? {mi: 'agarra'} : {md: 'agarra'})});

/* =============================== GANCHO =============================== */

const Gancho: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const niega = f >= W.nunca - 2;
	const pose = animarPose(f, [
		[0, {...manosFrente([170, 470], [230, 470]), mi: 'relajada', md: 'relajada'}],
		[W.nunca - 4, {...manosFrente([170, 470], [230, 470])}],
		[W.nunca + 4, {...manosFrente([70, 330], [330, 330]), mi: 'abierta', md: 'abierta', wi: 20, wd: 20}],
	]);
	const vaiven = niega ? Math.sin((f - W.nunca) / 4) : 0;
	return (
		<Toma escena={<EscVersalles />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [0, -20]}} golpes={[[W.nunca, 0.05], [W.pasteles0, 0.05]]} encima={<><Sello x={540} y={1560} texto="NUNCA LO DIJO" icono="✘" color="#d6262e" desde={W.pasteles0 + 4} tam={74} rot={-6} /></>}>
			<PastelMesa x={850} y={1780} ancho={360} />
			<Actor x={460} y={1900} alto={1080}>
				<Muneco ropa={ROPA_MARIA} pose={{...pose, cabeza: vaiven * 9, wi: (pose.wi ?? 0) + vaiven * 12, wd: (pose.wd ?? 0) - vaiven * 12}} ojos={niega ? 'cerrados' : 'normal'} cejas={niega ? 'preocupado' : 'neutral'} boca={niega ? 'mueca' : 'sonrisa'} />
			</Actor>
		</Toma>
	);
};

const Nina: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cambio = W.nina1 - 2;
	const nina = f >= cambio;
	const reina = animarPose(f, [
		[d, {...manosFrente([70, 330], [330, 330]), mi: 'abierta', md: 'abierta'}],
		[d + 8, POSES.encogeHombros],
	]);
	const salto = nina ? Math.abs(Math.sin((f - cambio) / 5)) * 40 : 0;
	return (
		<Toma escena={<EscVersalles />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.14], y: [-30, -40]}} golpes={[[W.nina1, 0.08]]}>
			{!nina && (
				<Actor x={500} y={1900} alto={1080}>
					<Muneco ropa={ROPA_MARIA} pose={reina} ojos="entrecerrados" cejas="sorprendido" boca="o" />
				</Actor>
			)}
			{nina && (
				<Actor x={500} y={1880} alto={780}>
					<Muneco ropa={ROPA_MARIA_NINA} pose={{...manosFrente([170, 450]), mi: 'agarra', ...brazo(1, alcanzar(1, 340, 160)), md: 'abierta', salto}} objIzq={<Muneca />} ojos="feliz" cejas="neutral" boca="sonrisaGrande" />
				</Actor>
			)}
			<Puf x={500} y={1300} desde={cambio - 1} tam={700} />
		</Toma>
	);
};

/* =============================== ORIGEN =============================== */

const Mapa: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const [vx, vy] = CIUDADES.VIENA;
	const [px, py] = CIUDADES.PARÍS;
	const t = interpolate(f, [W.princesa - 6, W.versalles - 2], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
	const x = vx + (px - vx) * t;
	const y = vy + (py - vy) * t - Math.sin(Math.PI * t) * 70;
	const etiqueta = f >= W.catorce;
	return (
		<Toma escena={<EscMapa ciudades={['VIENA', 'PARÍS', 'LONDRES', 'MADRID', 'ROMA', 'BERLÍN']} resaltar={['VIENA', 'PARÍS']} nombres={{PARÍS: 'VERSALLES'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.25, 1.35], x: [-120, -40], y: [40, 60]}} encima={<><Rotulo texto="DE VIENA A VERSALLES" desde={W.princesa} /></>}>
			<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
				<path d={`M ${vx} ${vy} Q ${(vx + px) / 2} ${vy - 140} ${px} ${py}`} stroke="#e3262e" strokeWidth={8} strokeDasharray="22 16" fill="none" opacity={f >= W.princesa - 6 ? 1 : 0} />
			</svg>
			<Carruaje x={x} y={y} tam={150} voltear />
			{/* retrato de la princesa sobre el carruaje */}
			<div style={{position: 'absolute', left: x - 70, top: y + 70, width: 140, height: 140, borderRadius: '50%', overflow: 'hidden', border: `8px solid ${TINTA}`, background: '#ffd9e6', opacity: f >= W.princesa ? 1 : 0}}>
				<div style={{position: 'absolute', left: -38, top: -6, width: 216, height: 486}}>
					<Muneco ropa={ROPA_MARIA_JOVEN} pose={{}} ojos="normal" boca="sonrisa" sombra={false} />
				</div>
			</div>
			{etiqueta && (
				<div style={{position: 'absolute', left: x + 70, top: y + 100, transform: `scale(${interpolate(f, [W.catorce, W.catorce + 6], [0.3, 1], {...clamp, easing: Easing.out(Easing.back(2))})})`, background: '#ff8fb8', border: `6px solid ${TINTA}`, borderRadius: 14, padding: '2px 14px 6px', fontFamily: CONDENSADA, fontSize: 46, color: '#fff', whiteSpace: 'nowrap'}}>14 AÑOS</div>
			)}
		</Toma>
	);
};

const Llegada: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const x = interpolate(f, [d, d + 18], [-120, 350], {...clamp, easing: Easing.out(Easing.quad)});
	const princesa = animarPose(f, [
		[d, {}],
		[d + 18, {}],
		[W.casarse - 4, {...FALDA, agacha: 0.22, cabeza: 8}],
		[W.casarse + 14, {...FALDA, agacha: 0, cabeza: 0}],
	]);
	const luis = animarPose(f, [
		[d, {...manosFrente(undefined, [214, 400]), md: 'abierta'}],
		[W.casarse, {...manosFrente(undefined, [214, 400]), md: 'abierta'}],
		[W.casarse + 8, {...manosFrente(undefined, [214, 400]), md: 'abierta', cuerpo: 12, cabeza: 12}],
		[W.rey + 6, {...manosFrente(undefined, [214, 400]), md: 'abierta', cuerpo: 0, cabeza: 4}],
	]);
	return (
		<Toma escena={<EscVersalles />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [0, -10]}} encima={<><Rotulo texto="VERSALLES · FRANCIA" desde={d + 2} /></>}>
			<Actor x={x} y={1880} alto={980}>
				<Muneco ropa={ROPA_MARIA_JOVEN} pose={princesa} camina={f < d + 18 ? 1.1 : 0} ojos={f >= W.casarse ? 'cerrados' : 'normal'} cejas="neutral" boca="sonrisa" />
			</Actor>
			<Actor x={790} y={1880} alto={1060} voltear>
				<Muneco ropa={ROPA_LUIS} pose={luis} ojos={f >= W.casarse ? 'mirandoLado' : 'normal'} cejas="preocupado" boca={f >= W.casarse ? 'sonrisa' : 'seria'} semilla={2} />
			</Actor>
		</Toma>
	);
};

const NoLaQuieren: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const desprecio = f >= W.quieren - 2;
	const dama = (lado: -1 | 1) =>
		animarPose(f, [
			[d, {...CHISME(lado === 1 ? -1 : 1)}],
			[W.quieren - 4, {...CHISME(lado === 1 ? -1 : 1)}],
			[W.quieren + 4, {...CHISME(lado === 1 ? -1 : 1), cabeza: -14, cuerpo: -4}],
		]);
	return (
		<Toma escena={<EscVersalles />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.1], y: [-10, -20]}} golpes={[[W.quieren, 0.04]]}>
			<Actor x={540} y={1700} alto={760}>
				<Muneco ropa={ROPA_MARIA_JOVEN} pose={{...manosFrente([186, 470], [214, 470]), mi: 'relajada', md: 'relajada', cabeza: 6}} ojos={desprecio ? 'cerrados' : 'mirandoLado'} cejas="preocupado" boca="mueca" />
			</Actor>
			<Actor x={190} y={1960} alto={1160}>
				<Muneco ropa={ROPA_DAMA_1} pose={dama(1)} objDer={<Abanico color="#bfe6c4" rot={150} />} ojos={desprecio ? 'cerrados' : 'mirandoLado'} cejas="arrogante" boca="seria" semilla={1} />
			</Actor>
			<Actor x={890} y={1960} alto={1160} voltear>
				<Muneco ropa={ROPA_DAMA_2} pose={dama(-1)} objDer={<Abanico color="#e6d6f7" rot={150} />} ojos={desprecio ? 'cerrados' : 'mirandoLado'} cejas="arrogante" boca="seria" semilla={3} />
			</Actor>
		</Toma>
	);
};

/* =============================== PRIMER ESCALÓN =============================== */

const Juego: React.FC<{d: number}> = ({d}) => {
	const f = useCurrentFrame();
	if (f < W.austriaca) return null;
	const aparece = interpolate(f, [W.austriaca, W.austriaca + 8], [0.4, 1], {...clamp, easing: Easing.out(Easing.back(2))});
	const parte = interpolate(f, [W.esconde, W.esconde + 12], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
	const perra = interpolate(f, [W.perra - 2, W.perra + 6], [0, 1], {...clamp, easing: Easing.out(Easing.back(2.4))});
	const base: React.CSSProperties = {fontFamily: CONDENSADA, fontSize: 132, lineHeight: 1, WebkitTextStroke: `16px ${TINTA}`, paintOrder: 'stroke fill', letterSpacing: 2};
	return (
		<div style={{position: 'absolute', left: 0, right: 0, top: 560, display: 'flex', flexDirection: 'column', alignItems: 'center', transform: `scale(${aparece})`}}>
			<div style={{display: 'flex', filter: 'drop-shadow(0 10px 0 rgba(0,0,0,0.5))'}}>
				<span style={{...base, color: '#ffffff', opacity: 1 - parte * 0.65}}>L'AUTRI</span>
				<span style={{...base, color: parte > 0.5 ? '#ff4d4d' : '#ffffff', transform: `translateY(${parte * 26}px) scale(${1 + parte * 0.25})`, display: 'inline-block', transformOrigin: '0% 50%'}}>CHIENNE</span>
			</div>
			{perra > 0 && (
				<div style={{...base, fontSize: 120, color: '#ffc21a', marginTop: 54, transform: `scale(${perra}) rotate(-4deg)`}}>= «PERRA»</div>
			)}
		</div>
	);
};

const Austriaca: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const ofendida = f >= W.perra;
	const dama = (lado: -1 | 1) =>
		animarPose(f, [
			[d, {...CHISME(lado === 1 ? -1 : 1)}],
			[W.austriaca - 4, {...CHISME(lado === 1 ? -1 : 1)}],
			[W.austriaca + 4, {...CHISME(lado === 1 ? -1 : 1), ...brazo(lado === 1 ? 1 : -1, senalar(lado === 1 ? 1 : -1, lado === 1 ? 640 : 640, 420, 0.8)), ...(lado === 1 ? {md: 'senala'} : {mi: 'senala'})}],
		]);
	return (
		<Toma escena={<EscVersalles />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], y: [0, -10]}} golpes={[[W.esconde, 0.04], [W.perra, 0.07]]} encima={<><Juego d={d} /></>}>
			<Actor x={540} y={2020} alto={1060}>
				<Muneco ropa={ROPA_MARIA_JOVEN} pose={ofendida ? {...manosFrente([96, 214], [304, 214]), mi: 'abierta', md: 'abierta'} : {...manosFrente([186, 470], [214, 470]), cabeza: 4}} ojos={ofendida ? 'grandes' : 'mirandoLado'} cejas={ofendida ? 'sorprendido' : 'preocupado'} boca={ofendida ? 'o' : 'mueca'} />
			</Actor>
			<Actor x={130} y={2000} alto={1180}>
				<Muneco ropa={ROPA_DAMA_1} pose={dama(1)} objIzq={<Abanico color="#bfe6c4" rot={150} />} ojos="entrecerrados" cejas="arrogante" boca="picara" semilla={1} />
			</Actor>
			<Actor x={950} y={2000} alto={1180} voltear>
				<Muneco ropa={ROPA_DAMA_2} pose={dama(-1)} objIzq={<Abanico color="#e6d6f7" rot={150} />} ojos="entrecerrados" cejas="arrogante" boca="picara" semilla={3} />
			</Actor>
		</Toma>
	);
};

const Deficit: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const susto = f >= W.madame - 2;
	const pose = animarPose(f, [
		[d, {...manosFrente([170, 470]), mi: 'relajada', ...brazo(1, alcanzar(1, 250, 236)), md: 'agarra'}],
		[W.arruina + 4, {...manosFrente([170, 470]), mi: 'relajada', ...brazo(1, alcanzar(1, 250, 236)), md: 'agarra'}],
		[W.arruina + 12, {...manosFrente([96, 300]), mi: 'abierta', ...brazo(1, alcanzar(1, 250, 236)), md: 'agarra', cabeza: -8}],
		[W.madame, {...manosFrente([96, 214], [304, 214]), mi: 'abierta', md: 'abierta'}],
	]);
	return (
		<Toma escena={<EscVersalles />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [0, -20]}} golpes={[[W.madame, 0.07]]} encima={<><TituloArriba texto="«MADAME *DÉFICIT*»" desde={W.madame} tam={124} /></>}>
			<Cofre x={260} y={1640} ancho={340} desde={W.arruina - 6} />
			<Actor x={700} y={1900} alto={1080}>
				<Muneco ropa={ROPA_MARIA} pose={pose} objDer={susto ? undefined : <Abanico color="#ffd3e2" rot={150} />} ojos={susto ? 'grandes' : f >= W.arruina + 8 ? 'mirandoLado' : 'entrecerrados'} cejas={susto ? 'sorprendido' : 'arrogante'} boca={susto ? 'grito' : 'picara'} />
			</Actor>
			<Rotulo texto="FRANCIA EN QUIEBRA" desde={W.arruina} y={520} tam={46} />
		</Toma>
	);
};

/* =============================== SEGUNDO ESCALÓN =============================== */

const PUEBLO: {ropa: typeof ROPA_PUEBLO_1; x: number; alto: number; semilla: number}[] = [
	{ropa: ROPA_PUEBLO_2, x: 190, alto: 1100, semilla: 1},
	{ropa: ROPA_PUEBLO_1, x: 540, alto: 1200, semilla: 2},
	{ropa: ROPA_PUEBLO_3, x: 890, alto: 1080, semilla: 3},
];

const Revolucion: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const marcha = f < W.pan7 - 6;
	const avance = interpolate(f, [d, W.pan7 - 6], [120, 0], {...clamp, easing: Easing.out(Easing.quad)});
	const mira = f >= W.persigue - 2;
	const poses: Partial<Pose>[] = [
		{...manosEn([110, 300]), mi: 'agarra'},
		{...brazo(1, alcanzar(1, 330, 60)), md: 'agarra', ...manosFrente([150, 520]), mi: 'puno'},
		f >= W.pan7 - 4 ? {...brazo(-1, alcanzar(-1, 70, 250)), mi: 'agarra', ...manosFrente(undefined, [250, 520]), md: 'puno'} : {...manosEn([100, 500]), mi: 'agarra'},
	];
	return (
		<Toma escena={<EscCalle />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [0, -10]}} golpes={[[W.revolucion, 0.06], [W.pan7, 0.04]]} encima={<><TituloArriba texto="¡*REVOLUCIÓN*!" desde={W.revolucion} tam={150} /><Rotulo texto="PARÍS · 1789" desde={W.revolucion + 2} /></>}>
			{PUEBLO.map((p, i) => (
				<Actor key={i} x={p.x} y={1960 + avance * (i === 1 ? 1 : 0.6)} alto={p.alto} voltear={i === 2}>
					<Muneco
						ropa={p.ropa}
						pose={poses[i]}
						camina={marcha ? 0.9 : 0}
						objIzq={i === 0 ? <Bandera rot={180} /> : i === 2 ? <Canasta /> : undefined}
						objDer={i === 1 ? <Antorcha /> : undefined}
						ojos={mira ? 'entrecerrados' : 'normal'}
						cejas={f >= W.pan7 ? 'enojado' : 'neutral'}
						boca={f >= W.pan7 ? 'mueca' : 'seria'}
						semilla={p.semilla}
					/>
				</Actor>
			))}
		</Toma>
	);
};

const Balcon: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const reina = animarPose(f, [
		[d, {...brazo(-1, alcanzar(-1, 150, 420)), mi: 'agarra', ...manosFrente(undefined, [300, 300]), md: 'abierta'}],
		[W.que8 + 6, {...brazo(-1, alcanzar(-1, 150, 420)), mi: 'agarra', ...brazo(1, alcanzar(1, 360, 200)), md: 'abierta', cabeza: -10}],
	]);
	return (
		<Toma escena={<EscBalcon />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}} golpes={[[W.que8, 0.06]]}>
			<Actor x={650} y={BALCON_Y} alto={620}>
				<Muneco ropa={ROPA_MARIA} pose={reina} objIzq={<PlatoPastel rot={180} />} ojos="entrecerrados" cejas="arrogante" boca="picara" />
			</Actor>
			<Bocadillo x={300} y={590} texto="¡QUE COMAN PASTELES!" desde={W.que8 - 2} cola="der" ancho={500} tam={56} />
			{PUEBLO.map((p, i) => (
				<Actor key={i} x={p.x} y={2160} alto={p.alto * 0.95} voltear={i === 2}>
					<Muneco ropa={p.ropa} pose={{cabeza: i === 0 ? 10 : i === 2 ? 10 : -4, ...manosFrente([170, 470], [230, 470])}} objDer={i === 1 ? <Antorcha rot={140} /> : undefined} ojos="grandes" cejas="sorprendido" boca="o" semilla={p.semilla} />
				</Actor>
			))}
		</Toma>
	);
};

const Furia: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const puno = (i: number): Partial<Pose> => ({...POSES.jarras, ...brazo(1, alcanzar(1, 330, 40 + Math.sin(f / 6 + i) * 30)), md: 'puno'});
	return (
		<Toma escena={<EscBalcon />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.18, 1.24], y: [-260, -280]}} golpes={[[W.nadie9, 0.06]]} encima={<><TituloArriba texto="«NO LE IMPORTABA *NADIE*»" desde={W.la9 + 2} tam={104} /></>}>
			<Actor x={650} y={BALCON_Y} alto={620}>
				<Muneco ropa={ROPA_MARIA} pose={{...brazo(-1, alcanzar(-1, 150, 420)), mi: 'agarra'}} objIzq={<PlatoPastel rot={180} />} ojos="cerrados" cejas="arrogante" boca="picara" />
			</Actor>
			{PUEBLO.map((p, i) => (
				<Actor key={i} x={p.x} y={2080} alto={p.alto} voltear={i === 2}>
					<Muneco ropa={p.ropa} pose={puno(i)} objIzq={i === 2 ? <Canasta /> : undefined} ojos="entrecerrados" cejas="enojado" boca="dientes" tiembla={0.6} semilla={p.semilla} />
				</Actor>
			))}
		</Toma>
	);
};

/* =============================== CLÍMAX =============================== */

const QuienLaOyo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const nadie = f >= W.nadie11;
	return (
		<Toma escena={<EscCalle />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.12], y: [-10, -30]}} golpes={[[W.nadie11, 0.08]]} encima={<><TituloArriba texto="¿QUIÉN LA *OYÓ*?" desde={W.quien} hasta={W.nadie11} tam={140} /><TituloArriba texto="¡*NADIE*!" desde={W.nadie11} tam={190} /></>}>
			{PUEBLO.map((p, i) => (
				<Actor key={i} x={p.x} y={1990} alto={p.alto} voltear={i === 2}>
					<Muneco
						ropa={p.ropa}
						pose={animarPose(f, [
							[d, {cabeza: i === 1 ? 0 : i === 0 ? 12 : 12}],
							[W.quien + 4, {cabeza: i === 0 ? 14 : i === 2 ? 14 : -10}],
							[W.nadie11 - 2, POSES.encogeHombros],
						])}
						ojos={nadie ? 'cerrados' : 'mirandoLado'}
						cejas={nadie ? 'preocupado' : 'sorprendido'}
						boca={nadie ? 'mueca' : 'o'}
						semilla={p.semilla}
					/>
				</Actor>
			))}
			{[0, 1, 2].map((i) => (
				<Icono key={i} tipo="interrogacion" x={PUEBLO[i].x} y={760 + (i % 2) * 40} desde={W.quien + 4 + i * 4} hasta={W.nadie11} tam={120} />
			))}
		</Toma>
	);
};

const Filosofo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const actor = {x: 280, y: 1980, alto: 1150};
	const [px, py] = aLienzo(actor, 430 + Math.sin(f / 5) * 26, 1330 + Math.cos(f / 6.5) * 10);
	const levanta = f >= W.sin12 - 2;
	const pose: Partial<Pose> = levanta
		? {...manosFrente([170, 470]), mi: 'relajada', ...brazo(1, senalar(1, 320, -160, 0.85)), md: 'senala', cabeza: -6}
		: {...manosFrente([170, 470], [px, py]), mi: 'relajada', md: 'agarra', cuerpo: 5, cabeza: 8};
	return (
		<Toma escena={<EscFilosofo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.06]}} encima={<><Rotulo texto="JEAN-JACQUES ROUSSEAU · FILÓSOFO" desde={W.filosofo} /></>}>
			<LibroAbierto
				x={640}
				y={780}
				ancho={760}
				titulo="Las Confesiones"
				lineas={[
					{texto: '«...una gran princesa,', desde: W.una12, resaltar: true},
					{texto: 'al oír que los', desde: W.una12 + 10},
					{texto: 'campesinos no tenían', desde: W.una12 + 18},
					{texto: 'pan, dijo:', desde: W.una12 + 26},
				]}
			/>
			{f >= W.sin12 && (
				<div style={{position: 'absolute', left: 820, top: 980, width: 170, height: 170, borderRadius: '50%', background: '#2a2a32', border: `8px solid ${TINTA}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: CONDENSADA, fontSize: 120, color: '#ffc21a', transform: `scale(${interpolate(f, [W.sin12, W.sin12 + 6], [0.3, 1], {...clamp, easing: Easing.out(Easing.back(2))})})`}}>?</div>
			)}
			<Actor {...actor}>
				<Muneco ropa={ROPA_ROUSSEAU} pose={pose} objDer={levanta ? undefined : <Pluma rot={-30} />} ojos={levanta ? 'entrecerrados' : 'normal'} cejas={levanta ? 'arrogante' : 'neutral'} boca={levanta ? 'picara' : 'seria'} />
			</Actor>
			{/* borde del escritorio por delante */}
			<div style={{position: 'absolute', left: 0, right: 0, top: 1360, height: 560, background: 'linear-gradient(180deg,#946036,#6a4122)', borderTop: `8px solid ${TINTA}`}} />
		</Toma>
	);
};

const BriocheToma: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const tacha = f >= W.pasteles13;
	return (
		<Toma escena={<EscFilosofo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}} golpes={[[W.brioche, 0.07]]} encima={<><TituloArriba texto="NO DICE *PASTELES*:" desde={W.pasteles13} hasta={W.brioche} tam={116} /><TituloArriba texto="DICE *BRIOCHE*" desde={W.brioche} tam={150} /></>}>
			<LibroAbierto x={540} y={1020} ancho={920} lineas={[{texto: 'pan, dijo:', desde: -1e9}, {texto: '«Que coman', desde: -1e9}, {texto: 'brioche»', desde: -1e9, resaltar: f >= W.brioche}]} titulo="Las Confesiones" rot={-2} />
			{tacha && f < W.brioche && (
				<div style={{position: 'absolute', left: 280, top: 560, width: 520, height: 420}}>
					<PastelMesa x={260} y={380} ancho={300} />
					<svg viewBox="0 0 520 420" style={{position: 'absolute', inset: 0}}>
						<path d="M 120 60 L 400 380 M 400 60 L 120 380" stroke={TINTA} strokeWidth={46} strokeLinecap="round" />
						<path d="M 120 60 L 400 380 M 400 60 L 120 380" stroke="#e3262e" strokeWidth={30} strokeLinecap="round" />
					</svg>
				</div>
			)}
			<Brioche x={540} y={700} tam={380} desde={W.brioche} rot={-6} />
		</Toma>
	);
};

const Donde: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const [px, py] = CIUDADES.PARÍS;
	return (
		<Toma escena={<EscMapa ciudades={['VIENA', 'PARÍS', 'LONDRES', 'MADRID', 'ROMA', 'BERLÍN']} resaltar={['VIENA', 'PARÍS']} nombres={{PARÍS: 'VERSALLES'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.3, 1.36], x: [-120, -140], y: [40, 40]}} encima={<><TituloArriba texto="¿DÓNDE *ESTABA*?" desde={d + 2} tam={140} /><Rotulo texto="EL LIBRO SE ESCRIBIÓ HACIA 1765" desde={W.escribio14} y={520} tam={44} /></>}>
			<Icono tipo="interrogacion" x={px} y={py - 150} desde={W.y14 + 4} tam={170} />
		</Toma>
	);
};

const Viena: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const l = f - d;
	const pose: Partial<Pose> = {
		...brazo(-1, alcanzar(-1, 80 + Math.sin(l / 6) * 20, 300)),
		mi: 'agarra',
		...brazo(1, alcanzar(1, 330, 200 + Math.sin(l / 4) * 30)),
		md: 'abierta',
		salto: Math.abs(Math.sin(l / 5)) * 50,
		li: Math.max(0, Math.sin(l / 5)) * 0.3,
		ld: Math.max(0, -Math.sin(l / 5)) * 0.3,
	};
	return (
		<Toma escena={<EscViena />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [0, -10]}} golpes={[[W.en15, 0.07], [W.nina15, 0.05]]} encima={<><TituloArriba texto="¡EN *VIENA*!" desde={W.en15} hasta={W.nina15} tam={160} /><TituloArriba texto="SIENDO UNA *NIÑA*" desde={W.nina15} tam={130} /><Rotulo texto="PALACIO DE SCHÖNBRUNN · AUSTRIA" desde={W.en15 + 2} /></>}>
			<Actor x={540} y={1880} alto={900}>
				<Muneco ropa={ROPA_MARIA_NINA} pose={pose} objIzq={<Muneca />} ojos="feliz" cejas="neutral" boca="sonrisaGrande" />
			</Actor>
		</Toma>
	);
};

/* =============================== GOLPE FINAL =============================== */

const Escribe: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const actor = {x: 420, y: 1960, alto: 1120};
	const [px, py] = aLienzo(actor, 620 + Math.sin(f / 4) * 40, 1330 + Math.cos(f / 5.5) * 8);
	return (
		<Toma escena={<EscVersalles tono="noche" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.08], y: [0, -10]}} encima={<><TituloArriba texto="*1775*" desde={W.anio1775} tam={160} /><Rotulo texto="TRAS LA «GUERRA DE LAS HARINAS»" desde={W.revueltas} y={520} tam={44} /></>}>
			<Actor {...actor}>
				<Muneco ropa={ROPA_MARIA} pose={{...manosFrente([200, 470], [px, py]), mi: 'relajada', md: 'agarra', cuerpo: 5, cabeza: 8}} objDer={<Pluma rot={-30} />} ojos="entrecerrados" cejas="preocupado" boca="seria" />
			</Actor>
			<div style={{position: 'absolute', left: 0, right: 0, top: 1360, height: 560, background: 'linear-gradient(180deg,#8a5a32,#5a3a1e)', borderTop: `8px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 520, top: 1290, width: 300, height: 90, background: '#fbf3dc', border: `6px solid ${TINTA}`, transform: 'rotate(-4deg)'}} />
			<div style={{position: 'absolute', left: 880, top: 1170, width: 60, height: 120, background: '#f6eedd', border: `5px solid ${TINTA}`, borderRadius: 6}} />
			<div style={{position: 'absolute', left: 880, top: 1100, width: 60, height: 70, background: 'radial-gradient(circle at 50% 70%, #fff3a0, #ffb02e 60%, transparent 62%)'}} />
		</Toma>
	);
};

const CartaToma: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscVersalles tono="noche" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}} encima={<><Rotulo texto="CARTA A SU MADRE, MARÍA TERESA DE AUSTRIA" desde={d + 2} tam={38} /></>}>
		<Carta x={540} y={560} ancho={880} encabezado="Querida madre:" texto="...debemos trabajar por la felicidad del pueblo." resaltar="trabajar por la felicidad del pueblo" desde={W.le16} duracion={W.trabajar + 30 - W.le16} rot={-2} />
	</Toma>
);

const Cadalso: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscCadalso />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [0, -30], curva: 'lineal'}} encima={<><TituloArriba texto="*1793*" desde={W.dieciocho} tam={170} /><Rotulo texto="18 AÑOS DESPUÉS" desde={W.dieciocho + 4} /><Fundido desde={W.guillotinan - 2} duracion={6} /></>}>
		<Actor x={300} y={1180} alto={620}>
			<Muneco ropa={ROPA_MARIA_BLANCO} pose={{...manosFrente([186, 480], [214, 480]), cabeza: -4}} ojos="cerrados" cejas="neutral" boca="seria" respira={false} />
		</Actor>
	</Toma>
);

/* =============================== VEREDICTO Y PREGUNTA =============================== */

const Veredicto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const falso = f >= W.falso;
	return (
		<Toma escena={<EscEscenario />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], y: [0, -10]}} golpes={[[W.falso, 0.08]]} encima={<><Destello desde={W.falso} color="#ff8a7a" fuerza={0.45} duracion={12} /><TituloArriba texto="*VEREDICTO*" desde={W.veredicto} tam={150} /></>}>
			<Pedestal x={540} y={1540} ancho={420} alto={160} />
			<Actor x={540} y={1540} alto={820}>
				<Muneco ropa={ROPA_MARIA} pose={falso ? {...manosFrente([60, 330], [340, 330]), mi: 'abierta', md: 'abierta', wi: 20, wd: 20} : {...manosFrente([186, 480], [214, 480])}} ojos={falso ? 'feliz' : 'normal'} cejas="neutral" boca={falso ? 'sonrisaGrande' : 'seria'} />
			</Actor>
			<Sello x={540} y={1240} texto="FALSO" icono="✘" color="#d6262e" desde={W.falso} tam={150} rot={-8} />
		</Toma>
	);
};

const Pregunta: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma
			escena={
				<div style={{position: 'absolute', inset: 0}}>
					<div style={{position: 'absolute', left: 0, top: 0, width: 540, height: 1920, background: 'linear-gradient(180deg,#3a0f18,#140409)'}} />
					<div style={{position: 'absolute', left: 540, top: 0, width: 540, height: 1920, background: 'linear-gradient(180deg,#ffd3e2,#9ec9ea)'}} />
					<div style={{position: 'absolute', left: 528, top: 0, width: 24, height: 1920, background: TINTA}} />
				</div>
			}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.0, 1.04]}}
			golpes={[[W.fake, 0.05]]}
			encima={<><TituloArriba texto={'¿REINA *SIN CORAZÓN|#ff6b6b*...\nO VÍCTIMA DE LA *FAKE NEWS*?'} desde={W.reina} tam={88} y={290} /><Fundido desde={h - 12} duracion={12} /></>}
		>
			<Actor x={540} y={1940} alto={1150}>
				<Muneco ropa={ROPA_MARIA} pose={animarPose(f, [[d, {...manosFrente([186, 480], [214, 480])}], [W.fake - 6, POSES.encogeHombros]])} ojos={f >= W.fake ? 'entrecerrados' : 'mirandoLado'} cejas="arrogante" boca={f >= W.fake ? 'picara' : 'seria'} />
			</Actor>
		</Toma>
	);
};

/* =============================== Montaje =============================== */

type Plano = {desde: number; Comp: React.FC<P>; entrada: Transicion};

const PLANOS: Plano[] = [
	{desde: 0, Comp: Gancho, entrada: 'corte'},
	{desde: antes(W.y1), Comp: Nina, entrada: 'corte'},
	{desde: antes(W.en2), Comp: Mapa, entrada: 'latigoDer'},
	{desde: antes(W.versalles), Comp: Llegada, entrada: 'zoom'},
	{desde: antes(W.pero3), Comp: NoLaQuieren, entrada: 'corte'},
	{desde: antes(W.la4), Comp: Austriaca, entrada: 'latigoIzq'},
	{desde: antes(W.cuando6), Comp: Deficit, entrada: 'latigoDer'},
	{desde: antes(W.llega7), Comp: Revolucion, entrada: 'latigoArriba'},
	{desde: antes(W.que8), Comp: Balcon, entrada: 'zoom'},
	{desde: antes(W.la9), Comp: Furia, entrada: 'corte'},
	{desde: antes(W.pero10), Comp: QuienLaOyo, entrada: 'latigoIzq'},
	{desde: antes(W.la12), Comp: Filosofo, entrada: 'latigoDer'},
	{desde: antes(W.y13), Comp: BriocheToma, entrada: 'corte'},
	{desde: antes(W.y14), Comp: Donde, entrada: 'latigoArriba'},
	{desde: antes(W.en15), Comp: Viena, entrada: 'zoom'},
	{desde: antes(W.lo16), Comp: Escribe, entrada: 'latigoIzq'},
	{desde: antes(W.le16), Comp: CartaToma, entrada: 'corte'},
	{desde: antes(W.dieciocho), Comp: Cadalso, entrada: 'corte'},
	{desde: antes(W.veredicto), Comp: Veredicto, entrada: 'zoom'},
	{desde: antes(W.reina), Comp: Pregunta, entrada: 'latigoDer'},
];

export const Historia: React.FC = () => (
	<>
		{PLANOS.map((p, i) => {
			const sig = PLANOS[i + 1];
			return <p.Comp key={i} d={p.desde} h={sig ? sig.desde : FIN_VIDEO} e={p.entrada} s={sig ? sig.entrada : 'corte'} />;
		})}
		{/* títulos que se mantienen entre tomas */}
		<TituloArriba texto="¿«QUE COMAN *PASTELES*»?" desde={0} hasta={antes(W.en2)} tam={92} />
		<TituloArriba texto="*1770*" desde={W.anio1770} hasta={antes(W.pero3)} tam={160} />
	</>
);

/** Efectos (pasan por la mezcla: siempre por debajo de la voz). [archivo, cuadro, volumen] */
export const SONIDOS: [string, number, number][] = [
	...PLANOS.filter((p) => p.entrada !== 'corte').map((p) => ['whoosh', p.desde - 7, 0.36] as [string, number, number]),
	['pop', W.nunca, 0.35],
	['sello', W.pasteles0 + 4, 0.45],
	['boing', W.nina1 - 2, 0.5],
	['pop', W.anio1770, 0.4],
	['tic', W.princesa, 0.3],
	['tic', W.princesa + 10, 0.3],
	['tic', W.princesa + 20, 0.3],
	['pop', W.catorce, 0.4],
	['ding', W.casarse, 0.35],
	['dundun', W.quieren - 4, 0.35],
	['pop', W.austriaca, 0.4],
	['boing', W.esconde + 4, 0.35],
	['sello', W.perra, 0.5],
	['objeto', W.arruina, 0.35],
	['sello', W.madame, 0.5],
	['dundun', W.revolucion - 2, 0.4],
	['tic', W.llega7 + 6, 0.25],
	['tic', W.llega7 + 18, 0.25],
	['tic', W.llega7 + 30, 0.25],
	['pop', W.que8, 0.45],
	['aplausos', W.la9, 0.25],
	['pop', W.quien + 4, 0.3],
	['sello', W.nadie11, 0.55],
	['hoja', W.libro, 0.4],
	['garabato', W.una12, 0.35],
	['pop', W.sin12 - 5, 0.3],
	['sello', W.pasteles13, 0.45],
	['ding', W.brioche, 0.4],
	['pop', W.y14 + 4, 0.4],
	['boing', W.en15, 0.4],
	['pop', W.anio1775, 0.4],
	['garabato', W.le16, 0.35],
	['garabato', W.trabajar, 0.35],
	['dundun', W.dieciocho, 0.45],
	['tic', W.dieciocho + 20, 0.3],
	['tic', W.dieciocho + 32, 0.3],
	['sello', W.falso - 5, 0.5],
	['pop', W.fake, 0.4],
];

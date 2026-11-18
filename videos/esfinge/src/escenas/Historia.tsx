import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {BalaCanon, Canon, Cuaderno, Esfinge, Esquirlas, LineaTiempo, Martillo, Ofrenda, Pala, PiedraRosetta, Placa, Vitrina, bocaCanon, narizEn} from '../componentes/Egipto';
import {Destello, Etiqueta, Explosion, Flecha} from '../componentes/Efectos';
import {Actor, Muneco, POSES, Pose, ROPA_GRANADERO, ROPA_INGLES, ROPA_NAPOLEON, alcanzar, animarPose, manosEn, manosFrente, senalar} from '../componentes/Muneco';
import {MarcaAltura} from '../componentes/Napoleon';
import {Antorcha, CintaEntre, Lapiz, Papel} from '../componentes/Objetos';
import {Rotulo, TituloArriba} from '../componentes/Rotulos';
import {Toma, Transicion} from '../componentes/Toma';
import {Bocadillo, Brillos, Documento, Fundido, Icono, Lupa, Puf, Sello} from '../componentes/Utileria';
import {ROPA_ALDEANA, ROPA_ALDEANO, ROPA_FANATICO, ROPA_GUIA, ROPA_NORDEN, ROPA_TURISTA, ROPA_TURISTA_2} from '../componentes/Vestuario';
import {EscDesierto, EscMedidas, EscMuseo, EscPergamino, PISO, altoParaCm} from '../escenarios/Escenarios';
import {SERIF} from '../fuentes';
import {finFrase, palabra} from '../tiempos';

/*
 * «¿Napoleón le voló la nariz a la Esfinge?» — tono de chisme histórico, con humor.
 * Cuadros GLOBALES: cada acción cae sobre la palabra exacta de la narración.
 */

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const antes = (n: number) => n - 3;
const TINTA = '#1b1b1f';
const VERDE = '#bff2c6';
const ROJO = '#d6262e';

const W = {
	no0: palabra(0, 'no'),
	nariz0: palabra(0, 'nariz'),
	esfinge0: palabra(0, 'Esfinge'),
	la1: palabra(1, 'La'),
	pobre1: palabra(1, 'pobre'),
	chata1: palabra(1, 'chata'),
	antes1: palabra(1, 'antes'),
	naciera: palabra(1, 'naciera'),
	en2: palabra(2, 'En'),
	a1798: palabra(2, '1798'),
	napoleon2: palabra(2, 'Napoleón'),
	llega2: palabra(2, 'llega'),
	canones2: palabra(2, 'cañones'),
	piramides: palabra(2, 'pirámides'),
	y3: palabra(3, 'Y'),
	frances: palabra(3, 'francés'),
	canones3: palabra(3, 'cañones'),
	sin3: palabra(3, 'sin'),
	quien: palabra(4, 'quién'),
	ser4: palabra(4, 'ser'),
	y5: palabra(5, 'Y'),
	leyenda: palabra(5, 'leyenda'),
	soldados: palabra(5, 'soldados'),
	aburridos: palabra(5, 'aburridos'),
	nariz5: palabra(5, 'nariz'),
	tiro: palabra(5, 'tiro'),
	blanco: palabra(5, 'blanco'),
	una6: palabra(6, 'Una'),
	metro: palabra(6, 'metro'),
	imposible: palabra(6, 'imposible'),
	fallar: palabra(6, 'fallar'),
	y7: palabra(7, 'Y'),
	historia: palabra(7, 'historia'),
	guia1: palabra(7, 'guía', 1),
	guia2: palabra(7, 'guía', 2),
	el8: palabra(8, 'El'),
	clarisimo: palabra(8, 'clarísimo'),
	llega8: palabra(8, 'llega'),
	y8: palabra(8, 'y'),
	desaparece: palabra(8, 'desaparece'),
	total: palabra(9, 'Total'),
	bajito9: palabra(9, 'bajito'),
	que10: palabra(10, 'qué'),
	vandalo10: palabra(10, 'vándalo'),
	pero11: palabra(11, 'Pero'),
	a1737: palabra(11, '1737'),
	explorador: palabra(11, 'explorador'),
	dibuja: palabra(11, 'dibuja'),
	y12: palabra(12, 'Y'),
	chata12: palabra(12, 'CHATA'),
	cuantos: palabra(13, 'Cuántos'),
	napoleon13: palabra(13, 'Napoleón'),
	ni: palabra(14, 'NI'),
	nacido: palabra(14, 'NACIDO'),
	y15: palabra(15, 'Y'),
	culpable: palabra(15, 'culpable'),
	un16: palabra(16, 'Un'),
	fanatico: palabra(16, 'fanático'),
	a1378: palabra(16, '1378'),
	harto: palabra(16, 'harto'),
	que16: palabra(16, 'que'),
	ofrendas: palabra(16, 'ofrendas'),
	para17: palabra(17, 'Para'),
	vandalo17: palabra(17, 'vándalo'),
	ahorcaron: palabra(17, 'ahorcaron'),
	y18: palabra(18, 'Y'),
	expedicion: palabra(18, 'expedición'),
	encontro: palabra(18, 'encontró'),
	piedra: palabra(18, 'piedra'),
	rosetta: palabra(18, 'Rosetta'),
	que19: palabra(19, 'que'),
	londres: palabra(19, 'Londres'),
	los20: palabra(20, 'Los'),
	ingleses: palabra(20, 'ingleses'),
	otra: palabra(20, 'otra'),
	veredicto: palabra(21, 'VEREDICTO'),
	mito: palabra(21, 'MITO'),
	primero: palabra(22, 'Primero'),
	bajito22: palabra(22, 'bajito'),
	ahora: palabra(22, 'ahora'),
	vandalo22: palabra(22, 'vándalo'),
	que23: palabra(23, 'qué'),
	inventar: palabra(23, 'inventar'),
	pobre23: palabra(23, 'pobre'),
};

export const FIN_VIDEO = finFrase(23) + 30;

type P = {d: number; h: number; e: Transicion; s: Transicion};

type Lugar = {x: number; y: number; alto: number; voltear?: boolean};
/** punto del mundo -> coordenadas del lienzo del muñeco (400 x 900) */
const aLienzo = (a: Lugar, wx: number, wy: number): [number, number] => {
	const k = a.alto / 900;
	const cx = (wx - (a.x - 200 * k)) / k;
	return [a.voltear ? 400 - cx : cx, (wy - (a.y - 880 * k)) / k];
};
const brazo = (lado: -1 | 1, r: {a: number; c: number; k?: number}): Partial<Pose> => (lado < 0 ? {bi: r.a, ci: r.c, ai: r.k ?? 1} : {bd: r.a, cd: r.c, ad: r.k ?? 1});
const REPOSO = manosFrente([186, 480], [214, 480]);
const ESCONDE = {...manosEn([168, 560], [232, 560]), mi: 'oculta', md: 'oculta'} as Partial<Pose>;
/** mano en la cara (el clásico "¡no puede ser!") */
const PALMA_CARA: Partial<Pose> = {...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 214, 150)), md: 'abierta', frenteD: 1};

/** viñeta y tono sepia de "la leyenda" */
const Vineta: React.FC = () => <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(60,35,10,0.55) 100%)'}} />;
const TINTE_LEYENDA = 'rgba(200,140,60,0.65)';

/* =============================== GANCHO =============================== */

const ESF_G = {x: 560, y: 1330, ancho: 880};

const Gancho: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const actor = {x: 290, y: 1900, alto: 1080};
	const [nx, ny] = narizEn(ESF_G.x, ESF_G.y, ESF_G.ancho);
	const [tx, ty] = aLienzo(actor, nx + 60, ny + 260);
	const pose = animarPose(f, [
		[0, REPOSO],
		[W.no0 - 2, {...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 312, 236)), md: 'abierta'}],
		[W.nariz0 + 6, {...manosFrente([186, 480]), ...brazo(1, senalar(1, tx, ty, 0.9)), md: 'abierta', wd: -30}],
	]);
	const vaiven = f >= W.no0 && f < W.nariz0 + 2 ? Math.sin((f - W.no0) / 3.6) : 0;
	return (
		<Toma escena={<EscDesierto />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [0, -20]}} golpes={[[W.no0, 0.05], [W.esfinge0, 0.04]]}>
			<Esfinge {...ESF_G} nariz={0} cara={f >= W.esfinge0 ? 'triste' : 'normal'} mira={-0.7} />
			<Actor {...actor}>
				<Muneco ropa={ROPA_NAPOLEON} pose={{...pose, wd: (pose.wd ?? 0) + vaiven * 18, cabeza: vaiven * 5}} ojos={f >= W.no0 ? 'entrecerrados' : 'normal'} cejas="arrogante" boca={f >= W.no0 ? 'picara' : 'sonrisa'} />
			</Actor>
		</Toma>
	);
};

/** primer plano de la cara: ancho 2000 con la nariz en (540, 1050) */
const CARA = {x: 540, y: 1990, ancho: 2000};

const Chata: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const traza = interpolate(f, [W.chata1 - 2, W.chata1 + 10], [0, 1], clamp);
	return (
		<Toma escena={<EscDesierto piramides={false} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [0, 20]}} golpes={[[W.chata1, 0.05]]} encima={<><TituloArriba texto="YA ESTABA *CHATA*" desde={W.chata1} tam={130} /></>}>
			<Esfinge {...CARA} nariz={0} cara={f >= W.pobre1 ? 'triste' : 'normal'} mira={f >= W.antes1 ? 0.6 : 0} />
			{f >= W.chata1 - 2 && (
				<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
					<path d="M 540 954 L 480 1118 Q 540 1146 600 1118 Z" fill="none" stroke={ROJO} strokeWidth={10} strokeDasharray="26 16" strokeLinejoin="round" opacity={traza} />
				</svg>
			)}
			<Icono tipo="interrogacion" x={850} y={1070} desde={W.chata1 + 4} tam={150} rot={12} />
			<Sello x={540} y={1560} texto="ANTES DE 1769" color={ROJO} desde={W.naciera - 2} tam={78} rot={-6} />
		</Toma>
	);
};

/* =============================== ORIGEN =============================== */

const Llegada: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const nx = interpolate(f, [d, W.llega2 + 8], [-180, 720], {...clamp, easing: Easing.out(Easing.quad)});
	const camina = f < W.llega2 + 6 ? 1.2 : 0;
	const cx = interpolate(f, [W.canones2 - 26, W.canones2 + 6], [-380, 330], {...clamp, easing: Easing.out(Easing.quad)});
	const empuja = f < W.canones2 + 4;
	const actor = {x: 720, y: 1870, alto: 1000};
	const [tx, ty] = aLienzo(actor, 300, 1040);
	const pose = animarPose(f, [
		[d, {}],
		[W.llega2 + 8, REPOSO],
		[W.piramides, {...manosFrente(undefined, [214, 480]), ...brazo(-1, senalar(-1, tx, ty, 0.9)), mi: 'abierta', wi: -30}],
	]);
	return (
		<Toma escena={<EscDesierto />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], x: [20, -20]}} golpes={[[W.a1798, 0.05], [W.piramides, 0.05]]} encima={<><Rotulo texto="EXPEDICIÓN A EGIPTO" desde={W.a1798 + 6} /><TituloArriba texto="*1798*" desde={W.a1798} tam={170} /></>}>
			<Canon x={cx} y={1700} tam={0.85} elev={10} />
			<Actor x={cx - 260} y={1830} alto={940}>
				<Muneco ropa={ROPA_GRANADERO} pose={{...manosFrente([300, 470], [340, 450]), mi: 'agarra', md: 'agarra', cuerpo: empuja ? 8 : 0}} camina={empuja ? 1 : 0} ojos="entrecerrados" cejas="preocupado" boca="mueca" semilla={3} />
			</Actor>
			<Actor x={nx} y={actor.y} alto={actor.alto}>
				<Muneco ropa={ROPA_NAPOLEON} pose={pose} camina={camina} ojos="normal" cejas="arrogante" boca={f >= W.piramides ? 'sonrisaGrande' : 'sonrisa'} />
			</Actor>
		</Toma>
	);
};

const ESF_S = {x: 540, y: 1240, ancho: 760};

const Sospechoso: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const silba = Math.sin(f / 11) * 4;
	return (
		<Toma escena={<EscDesierto />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [-10, -30]}} golpes={[[W.frances, 0.04], [W.canones3, 0.04], [W.sin3, 0.05]]}>
			<Esfinge {...ESF_S} nariz={0} cara="enojo" mira={-0.8} />
			<Canon x={810} y={1790} tam={0.8} elev={24} voltear />
			<Actor x={310} y={1880} alto={1000}>
				<Muneco ropa={ROPA_NAPOLEON} pose={{...ESCONDE, cabeza: silba, cuerpo: silba * 0.4}} ojos="mirandoLado" cejas="neutral" boca="o" />
			</Actor>
			<Etiqueta x={300} y={900} texto="FRANCÉS ✔" desde={W.frances} color={VERDE} tam={50} />
			<Etiqueta x={800} y={1630} texto="CAÑONES ✔" desde={W.canones3} color={VERDE} tam={50} />
			<Etiqueta x={720} y={830} texto="SIN NARIZ ✔" desde={W.sin3} color={VERDE} tam={50} />
		</Toma>
	);
};

const Quien: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscDesierto piramides={false} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}} golpes={[[W.ser4, 0.07]]} encima={<><TituloArriba texto="¿QUIÉN MÁS IBA A *SER*?" desde={W.quien} tam={104} /></>}>
		<Actor x={540} y={2150} alto={1500}>
			<Muneco ropa={ROPA_NAPOLEON} pose={{...manosFrente([150, 420], [250, 420]), mi: 'abierta', md: 'abierta'}} ojos="grandes" cejas="preocupado" boca="o" />
		</Actor>
		<Flecha d="M 40 640 Q 160 760 270 860" desde={W.quien} duracion={8} />
		<Flecha d="M 1040 660 Q 920 760 810 860" desde={W.quien + 3} duracion={8} />
		<Flecha d="M 60 1500 Q 160 1340 280 1220" desde={W.quien + 6} duracion={8} />
		<Flecha d="M 1020 1500 Q 920 1340 800 1220" desde={W.quien + 9} duracion={8} />
		<Sello x={540} y={1580} texto="SOSPECHOSO" color={ROJO} desde={W.ser4} tam={92} rot={-6} />
	</Toma>
);

/* =============================== PRIMER ESCALÓN: LA LEYENDA =============================== */

const ESF_L = {x: 760, y: 1230, ancho: 660};
const CANON_L = {x: 330, y: 1700, tam: 0.9, elev: 30};

const Leyenda: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const [nx, ny] = narizEn(ESF_L.x, ESF_L.y, ESF_L.ancho);
	const [bx, by] = bocaCanon(CANON_L.x, CANON_L.y, CANON_L.tam, CANON_L.elev);
	const s1 = {x: 190, y: 1840, alto: 900};
	const s2 = {x: 400, y: 1890, alto: 920};
	const bostezo = f >= W.aburridos - 2 && f < W.nariz5 - 4;
	const pose1 = animarPose(f, [
		[d, REPOSO],
		[W.aburridos, {...POSES.brazosArriba, mi: 'puno', md: 'puno'}],
		[W.nariz5 - 2, REPOSO],
		[W.tiro, {...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 330, 470)), md: 'agarra'}],
	]);
	const pose2 = animarPose(f, [
		[d, POSES.cruzados],
		[W.nariz5, {...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 232, 92)), md: 'abierta', wd: 70, cabeza: -8}],
	]);
	return (
		<Toma escena={<EscDesierto tono="leyenda" />} desde={d} hasta={h} entrada={e} salida={s} tinte={TINTE_LEYENDA} cam={{s: [1.0, 1.06]}} golpes={[[W.nariz5, 0.04], [W.blanco, 0.07]]} sacudida={(g) => (g >= W.blanco && g < W.blanco + 10 ? Math.sin(g * 2.3) * (W.blanco + 10 - g) * 2 : 0)} encima={<><Vineta /><TituloArriba texto="LA *LEYENDA*" desde={W.leyenda} tam={140} /></>}>
			<Esfinge {...ESF_L} nariz={1} diana={f >= W.nariz5} cara={f >= W.tiro ? 'sorpresa' : 'normal'} mira={-0.8} />
			<Puf x={nx} y={ny} desde={W.nariz5} tam={260} />
			<Canon {...CANON_L} dispara={W.blanco} />
			<BalaCanon x1={bx} y1={by} x2={nx} y2={ny} desde={W.blanco + 1} llega={W.blanco + 40} arco={120} />
			<Actor {...s1}>
				<Muneco ropa={ROPA_GRANADERO} pose={pose1} objDer={f >= W.nariz5 ? <Antorcha rot={-30} /> : undefined} ojos={bostezo ? 'cerrados' : 'entrecerrados'} cejas="neutral" boca={bostezo ? 'o' : 'picara'} semilla={3} />
			</Actor>
			<Actor {...s2}>
				<Muneco ropa={ROPA_GRANADERO} pose={pose2} ojos={bostezo ? 'cerrados' : 'normal'} cejas="arrogante" boca={bostezo ? 'o' : 'sonrisaGrande'} semilla={5} />
			</Actor>
		</Toma>
	);
};

const Metro: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const impacto = W.fallar - 2;
	const roto = f >= impacto;
	const cinta = interpolate(f, [W.metro - 6, W.metro + 4], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	return (
		<Toma escena={<EscDesierto tono="leyenda" piramides={false} />} desde={d} hasta={h} entrada={e} salida={s} tinte={TINTE_LEYENDA} cam={{s: [1.0, 1.05], y: [0, 10]}} golpes={[[W.metro, 0.04], [impacto, 0.1]]} sacudida={(g) => (g >= impacto && g < impacto + 14 ? Math.sin(g * 2.1) * (impacto + 14 - g) * 2.4 : 0)} encima={<><Vineta /><Destello desde={impacto} fuerza={0.5} /><TituloArriba texto="¡IMPOSIBLE *FALLAR*!" desde={W.imposible} tam={120} /></>}>
			<Esfinge {...CARA} nariz={roto ? 0 : 1} diana={!roto} cara={roto ? 'triste' : f >= W.imposible ? 'sorpresa' : 'normal'} mira={f >= W.imposible && !roto ? -0.9 : 0} />
			{cinta > 0 && !roto && <CintaEntre x1={660} y1={954} x2={660} y2={954 + 192 * cinta} />}
			{!roto && <Etiqueta x={840} y={1080} texto="1 METRO" desde={W.metro} color="#ffd84a" tam={62} />}
			<BalaCanon x1={-80} y1={1800} x2={540} y2={1060} desde={W.imposible - 6} llega={impacto} arco={60} tam={90} />
			<Explosion x={540} y={1060} desde={impacto} tam={700} />
			<Esquirlas x={540} y={1060} desde={impacto} n={9} tam={2} />
		</Toma>
	);
};

const Guias: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const g1 = {x: 150, y: 1840, alto: 880};
	const [tx, ty] = aLienzo(g1, 540, 1000);
	const voltea = f >= W.guia1;
	return (
		<Toma escena={<EscDesierto />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05], x: [-20, 20]}} encima={<><TituloArriba texto="DE *GUÍA* EN *GUÍA*" desde={W.guia1} tam={120} /></>}>
			<Esfinge x={540} y={1200} ancho={600} nariz={0} cara="triste" />
			<Actor {...g1}>
				<Muneco ropa={ROPA_GUIA} pose={{...manosFrente([186, 480]), ...brazo(1, senalar(1, tx, ty, 0.9)), md: 'senala'}} hablando={f < W.guia1} ojos="normal" cejas="arrogante" boca="abierta" semilla={1} />
			</Actor>
			<Actor x={390} y={1860} alto={820}>
				<Muneco ropa={ROPA_TURISTA} pose={REPOSO} ojos="grandes" cejas="sorprendido" boca="o" semilla={2} />
			</Actor>
			<Actor x={680} y={1850} alto={880} voltear={!voltea}>
				<Muneco ropa={ROPA_GUIA} pose={voltea ? {...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 330, 240)), md: 'abierta'} : REPOSO} hablando={voltea} ojos="normal" cejas="arrogante" boca={voltea ? 'abierta' : 'sonrisa'} semilla={4} />
			</Actor>
			<Actor x={930} y={1870} alto={800}>
				<Muneco ropa={ROPA_TURISTA_2} pose={REPOSO} ojos={f >= W.guia2 ? 'grandes' : 'normal'} cejas="sorprendido" boca={f >= W.guia2 ? 'o' : 'sonrisa'} semilla={6} />
			</Actor>
			<Bocadillo x={250} y={780} texto="¡FUE NAPOLEÓN!" desde={W.historia} cola="izq" ancho={400} tam={52} />
			<Bocadillo x={780} y={820} texto="¡FUE NAPOLEÓN!" desde={W.guia1 + 2} cola="izq" ancho={400} tam={52} />
		</Toma>
	);
};

/* =============================== SEGUNDO ESCALÓN =============================== */

const ESF_C = {x: 520, y: 1290, ancho: 820};

const Clarisimo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const [nx, ny] = narizEn(ESF_C.x, ESF_C.y, ESF_C.ancho);
	const llega = W.llega8;
	const x = interpolate(f, [llega - 10, llega + 10], [1300, 820], {...clamp, easing: Easing.out(Easing.quad)});
	const sinNariz = f >= W.desaparece;
	return (
		<Toma escena={<EscDesierto />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [0, -20]}} golpes={[[llega, 0.04], [W.desaparece, 0.07]]} encima={<><TituloArriba texto={'EL CASO PARECE\n*CLARÍSIMO*'} desde={W.clarisimo} tam={112} /></>}>
			<Esfinge {...ESF_C} nariz={sinNariz ? 0 : 1} cara={sinNariz ? 'sorpresa' : 'normal'} mira={f >= llega ? 0.8 : 0} />
			<Puf x={nx} y={ny} desde={W.desaparece} tam={300} />
			<Actor x={x} y={1880} alto={1000}>
				<Muneco ropa={ROPA_NAPOLEON} pose={sinNariz ? ESCONDE : REPOSO} camina={f < llega + 8 ? 1.2 : 0} ojos={sinNariz ? 'mirandoLado' : 'normal'} cejas={sinNariz ? 'neutral' : 'arrogante'} boca={sinNariz ? 'o' : 'sonrisa'} />
			</Actor>
		</Toma>
	);
};

const Bajito: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const furia = f >= W.vandalo10 - 2;
	const pose = animarPose(f, [
		[d, POSES.cruzados],
		[W.vandalo10, {bi: 150, ci: 25, bd: 150, cd: 25, mi: 'puno', md: 'puno', salto: 14}],
	]);
	return (
		<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [-20, -40]}} golpes={[[W.bajito9, 0.05], [W.vandalo10, 0.08]]} encima={<><TituloArriba texto="YA ERA «EL *BAJITO*»" desde={W.total} hasta={W.que10} tam={118} /><TituloArriba texto="¿Y *VÁNDALO|#ff6b6b* TAMBIÉN?" desde={W.que10} tam={118} /></>}>
			<MarcaAltura cm={169} desde={W.bajito9 + 6} color="#22a84f" lado="izq" x1={130} x2={470} texto="1,69 M" />
			<Actor x={600} y={PISO} alto={altoParaCm(169)}>
				<Muneco ropa={ROPA_NAPOLEON} pose={pose} ojos={furia ? 'grandes' : 'entrecerrados'} cejas="enojado" boca={furia ? 'grito' : 'mueca'} />
			</Actor>
			<Rotulo texto="(OTRO MITO: MEDÍA 1,69 M)" desde={W.bajito9 + 8} y={590} tam={38} />
			<Sello x={790} y={720} texto="BAJITO" color="#1f6fd1" desde={W.bajito9} tam={70} rot={8} solido />
			<Sello x={560} y={1570} texto="VÁNDALO" color={ROJO} desde={W.vandalo10} tam={110} rot={-6} solido />
		</Toma>
	);
};

/* =============================== CLÍMAX =============================== */

const Norden: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const dibuja = f >= W.dibuja - 2;
	const lapiz: [number, number] = dibuja ? [238 + Math.sin(f / 2.6) * 22, 430 + Math.cos(f / 3.4) * 14] : [250, 440];
	return (
		<Toma escena={<EscDesierto />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], x: [0, -20]}} golpes={[[W.a1737, 0.05], [W.dibuja, 0.03]]} encima={<><Rotulo texto="FREDERIK NORDEN · EXPLORADOR DANÉS" desde={W.explorador} /><TituloArriba texto="*1737*" desde={W.a1737} tam={170} /></>}>
			<Esfinge x={770} y={1230} ancho={620} nariz={0} cara="normal" mira={-0.6} />
			<Actor x={330} y={1880} alto={1060}>
				<Muneco
					ropa={ROPA_NORDEN}
					pose={{...manosFrente([96, 440], lapiz), mi: 'agarra', md: 'agarra', cabeza: dibuja ? 6 : -4}}
					objPecho={
						<g transform="translate(200 340) scale(0.82)">
							<Cuaderno dibujo={interpolate(f, [W.dibuja, W.dibuja + 30], [0, 1], clamp)} />
						</g>
					}
					objDer={<Lapiz rot={150} />}
					ojos={dibuja ? 'entrecerrados' : 'mirandoLado'}
					cejas="arrogante"
					boca="sonrisa"
				/>
			</Actor>
		</Toma>
	);
};

const Dibujo: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscDesierto piramides={false} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08]}} golpes={[[W.chata12, 0.08]]} encima={<><TituloArriba texto="¡YA ESTÁ *CHATA*!" desde={W.y12} tam={130} /></>}>
		<Papel x={540} y={980} ancho={860} alto={900} rot={-2}>
			<Esfinge x={404} y={700} ancho={760} nariz={0} cara="normal" />
			<div style={{position: 'absolute', left: 0, right: 0, bottom: 20, textAlign: 'center', fontFamily: SERIF, fontWeight: 700, fontStyle: 'italic', fontSize: 40, color: '#4a3018'}}>F. L. Norden · 1737</div>
		</Papel>
		<Lupa x={570} y={960} tam={380} desde={d + 2} radio={8} />
		<Sello x={540} y={1580} texto="SIN NARIZ" icono="✘" color={ROJO} desde={W.chata12} tam={96} rot={-6} />
	</Toma>
);

const Linea: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscPergamino />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}} golpes={[[W.ni, 0.06]]} encima={<><TituloArriba texto="¿CUÁNTOS AÑOS *TENÍA*?" desde={W.cuantos} hasta={W.ni} tam={110} /><TituloArriba texto="¡NI HABÍA *NACIDO*!" desde={W.ni} tam={124} /></>}>
		<LineaTiempo
			x={230}
			y1={640}
			y2={1500}
			desde={d}
			rango={[1725, 1805]}
			hitos={[
				{anio: 1737, texto: 'NORDEN: YA ESTÁ CHATA', desde: d + 4, color: ROJO},
				{anio: 1769, texto: 'NACE NAPOLEÓN', desde: W.napoleon13, color: '#1f6fd1'},
				{anio: 1798, texto: 'NAPOLEÓN EN EGIPTO', desde: W.napoleon13 + 8, color: '#1f9d48'},
			]}
		/>
		<Sello x={620} y={950} texto="32 AÑOS ANTES" color={ROJO} desde={W.nacido - 2} tam={66} rot={-6} />
	</Toma>
);

const Culpable: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const luz = interpolate(f, [d, d + 10], [0, 1], clamp);
	return (
		<Toma escena={<EscDesierto tono="noche" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.1]}} golpes={[[W.culpable, 0.06]]} encima={<><TituloArriba texto="¿EL VERDADERO *CULPABLE*?" desde={W.y15} tam={104} /></>}>
			<Esfinge x={540} y={1300} ancho={820} nariz={0} cara="enojo" mira={0} opacidad={0.75} />
			<div style={{position: 'absolute', left: 240, top: 820, width: 600, height: 1100, background: 'radial-gradient(ellipse at 50% 70%, rgba(255,240,190,0.55), rgba(255,240,190,0) 70%)', opacity: luz}} />
			<div style={{position: 'absolute', inset: 0, filter: 'brightness(0)'}}>
				<Actor x={540} y={1880} alto={1000}>
					<Muneco ropa={ROPA_FANATICO} pose={POSES.cruzados} ojos="normal" boca="seria" />
				</Actor>
			</div>
			<Icono tipo="interrogacion" x={540} y={1020} desde={W.culpable} tam={200} />
		</Toma>
	);
};

const ESF_F = {x: 540, y: 1260, ancho: 700};

const Ofrendas: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const harto = f >= W.harto - 2;
	const sube = (k: number): Partial<Pose> => ({...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 312, 250 + Math.sin(f / 10 + k) * 10)), md: 'agarra'});
	const poseF = animarPose(f, [
		[d, POSES.cruzados],
		[W.harto, {bi: 150, ci: 25, bd: 150, cd: 25, mi: 'puno', md: 'puno'}],
	]);
	const entra = interpolate(f, [W.fanatico - 8, W.fanatico + 4], [0, 1], clamp);
	return (
		<Toma escena={<EscDesierto />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [0, -20]}} golpes={[[W.a1378, 0.05], [W.harto, 0.07]]} encima={<><Rotulo texto="UN FANÁTICO, HARTO DE LAS OFRENDAS" desde={W.fanatico} /><TituloArriba texto="*1378*" desde={W.a1378} tam={170} /></>}>
			<Esfinge {...ESF_F} nariz={1} cara={harto ? 'sorpresa' : 'normal'} mira={0} />
			{/* ofrendas al pie de la Esfinge */}
			<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
				{[[400, 1300], [520, 1320], [650, 1300]].map(([x, y], i) => (
					<g key={i} transform={`translate(${x} ${y - 200 * 0.8}) scale(0.8)`}>
						<Ofrenda />
					</g>
				))}
			</svg>
			<Actor x={180} y={1820} alto={860}>
				<Muneco ropa={ROPA_ALDEANO} pose={sube(0)} objDer={<Ofrenda rot={180} />} ojos="cerrados" cejas="neutral" boca="sonrisa" semilla={1} />
			</Actor>
			<Actor x={900} y={1830} alto={820} voltear>
				<Muneco ropa={ROPA_ALDEANA} pose={sube(2)} objDer={<Ofrenda rot={180} />} ojos="cerrados" cejas="neutral" boca="sonrisa" semilla={2} />
			</Actor>
			<Actor x={540} y={1920} alto={1040} opacidad={entra} escala={0.9 + 0.1 * entra}>
				<Muneco ropa={ROPA_FANATICO} pose={poseF} ojos={harto ? 'grandes' : 'entrecerrados'} cejas="enojado" boca={harto ? 'grito' : 'mueca'} />
			</Actor>
		</Toma>
	);
};

/** Golpes del martillo sobre la nariz (cuadros globales) */
const GOLPES = [0, 9, 18, 27].map((k) => W.que16 + 4 + k);

const Cincel: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const esf = {x: 540, y: 2000, ancho: 1700};
	const [nx, ny] = narizEn(esf.x, esf.y, esf.ancho);
	const actor = {x: 790, y: 1960, alto: 1000};
	const [tx, ty] = aLienzo(actor, nx + 40, ny + 10);
	const hechos = GOLPES.filter((g) => f >= g).length;
	const ultimo = GOLPES[GOLPES.length - 1];
	// el brazo baja de golpe en cada impacto y vuelve a subir
	const fase = GOLPES.reduce((m, g) => (f >= g - 6 && f < g + 4 ? (f < g ? (f - (g - 6)) / 6 : 1 - (f - g) / 4) : m), 0);
	const arriba: [number, number] = [70, 70];
	const mano: [number, number] = [arriba[0] + (tx - arriba[0]) * fase, arriba[1] + (ty - arriba[1]) * fase];
	return (
		<Toma escena={<EscDesierto piramides={false} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}} golpes={GOLPES.map((g) => [g, 0.03] as [number, number])} sacudida={(g) => GOLPES.reduce((m, k) => (g >= k && g < k + 5 ? Math.sin(g * 2.4) * (k + 5 - g) * 2 : m), 0)} encima={<><TituloArriba texto="¡A *MARTILLAZOS*!" desde={d + 2} tam={130} /></>}>
			<Esfinge {...esf} nariz={f >= ultimo ? 0 : 1} cincel={Math.min(1, hechos / 3)} cara={f >= GOLPES[0] ? 'cerrados' : 'normal'} />
			{GOLPES.map((g, i) => (
				<Esquirlas key={g} x={nx} y={ny} desde={g} n={i === GOLPES.length - 1 ? 9 : 5} tam={i === GOLPES.length - 1 ? 1.8 : 1.1} />
			))}
			{/* escalera */}
			<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
				{[690, 890].map((x) => (
					<g key={x}>
						<line x1={x} y1={1340} x2={x + 20} y2={1960} stroke={TINTA} strokeWidth={30} strokeLinecap="round" />
						<line x1={x} y1={1340} x2={x + 20} y2={1960} stroke="#9a6a3a" strokeWidth={18} strokeLinecap="round" />
					</g>
				))}
				{[1420, 1560, 1700, 1840].map((y) => (
					<line key={y} x1={696} y1={y} x2={904} y2={y} stroke="#9a6a3a" strokeWidth={16} />
				))}
			</svg>
			<Actor {...actor}>
				<Muneco ropa={ROPA_FANATICO} pose={{...manosFrente(mano, [316, 470]), mi: 'agarra', md: 'agarra', cuerpo: -6 * fase}} objIzq={<Martillo rot={-90} />} ojos="entrecerrados" cejas="enojado" boca="dientes" />
			</Actor>
		</Toma>
	);
};

/* =============================== GOLPE EXTRA =============================== */

const Sentencia: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscPergamino />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05]}} golpes={[[W.vandalo17, 0.06]]} encima={<><TituloArriba texto="PARA *COLMO*..." desde={W.para17} tam={130} /></>}>
		<Documento x={460} y={930} ancho={500} desde={W.para17 + 2} titulo="SENTENCIA" rot={-3} />
		<Sello x={460} y={1020} texto="CULPABLE" color={ROJO} desde={W.vandalo17} tam={92} rot={-12} />
		<Actor x={880} y={1880} alto={860}>
			<Muneco ropa={ROPA_FANATICO} pose={{...manosEn([168, 560], [232, 560]), mi: 'oculta', md: 'oculta'}} ojos="cerrados" cejas="preocupado" boca="seria" />
		</Actor>
	</Toma>
);

const Rosetta: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sale = interpolate(f, [W.encontro - 6, W.encontro + 12], [1, 0.25], {...clamp, easing: Easing.out(Easing.back(1.4))});
	const cava = f < W.encontro + 4;
	const pala: [number, number] = cava ? [120 + Math.sin(f / 3.2) * 30, 470 + Math.cos(f / 3.2) * 40] : [150, 380];
	const poseN = animarPose(f, [
		[d, POSES.jarras],
		[W.piedra, {...POSES.victoria, salto: 16}],
	]);
	return (
		<Toma escena={<EscDesierto />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [0, -20]}} golpes={[[W.encontro, 0.05], [W.rosetta, 0.06]]} encima={<><Rotulo texto="1799 · LA HALLA LA EXPEDICIÓN FRANCESA" desde={W.expedicion} /><TituloArriba texto={'LA PIEDRA\nDE *ROSETTA*'} desde={W.piedra} tam={120} /></>}>
			<PiedraRosetta x={480} y={1560 + sale * 120} ancho={300} brillo={f >= W.piedra ? 1 : 0} enterrada={sale} />
			<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
				<ellipse cx={480} cy={1770} rx={240} ry={44} fill="#d9a95a" stroke={TINTA} strokeWidth={6} opacity={0.9} />
			</svg>
			<Brillos x={480} y={1460} desde={W.piedra} radio={260} n={10} />
			<Actor x={170} y={1880} alto={980}>
				<Muneco ropa={ROPA_NAPOLEON} pose={poseN} ojos={f >= W.piedra ? 'feliz' : 'normal'} cejas="arrogante" boca={f >= W.piedra ? 'sonrisaGrande' : 'sonrisa'} />
			</Actor>
			<Actor x={830} y={1880} alto={980}>
				<Muneco ropa={ROPA_GRANADERO} pose={{...manosFrente([60 + (pala[0] - 120) * 0.6, pala[1] - 70], pala), mi: 'agarra', md: 'agarra', cuerpo: cava ? -8 + Math.sin(f / 3.2) * 4 : 0}} objDer={<Pala rot={200} />} ojos={cava ? 'entrecerrados' : 'grandes'} cejas={cava ? 'preocupado' : 'sorprendido'} boca={cava ? 'mueca' : 'o'} semilla={3} />
			</Actor>
		</Toma>
	);
};

const Museo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const nx = interpolate(f, [W.los20 - 8, W.los20 + 8], [-260, 210], {...clamp, easing: Easing.out(Easing.quad)});
	const ingles = f >= W.ingleses - 2;
	const poseN = animarPose(f, [
		[d, REPOSO],
		[W.otra, PALMA_CARA],
	]);
	return (
		<Toma escena={<EscMuseo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], x: [10, -10]}} golpes={[[W.londres, 0.05], [W.otra, 0.05]]} encima={<><Rotulo texto="MUSEO BRITÁNICO · LONDRES" desde={W.londres - 4} /><TituloArriba texto="HOY ESTÁ EN *LONDRES*" desde={W.que19} hasta={W.los20} tam={118} /><TituloArriba texto={'LOS *INGLESES*...\nOTRA VEZ'} desde={W.los20} tam={118} /></>}>
			<Vitrina x={600} y={1560} ancho={480} alto={920}>
				<PiedraRosetta x={600} y={1010} ancho={300} />
			</Vitrina>
			<Placa x={600} y={1300} texto="PIEDRA DE ROSETTA" ancho={360} />
			<Actor x={910} y={1890} alto={1000} voltear>
				<Muneco ropa={ROPA_INGLES} pose={ingles ? {...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 236, 392)), md: 'pulgar'} : POSES.manoEnChaleco} ojos="entrecerrados" cejas="arrogante" boca="picara" />
			</Actor>
			<Actor x={nx} y={1890} alto={1000}>
				<Muneco ropa={ROPA_NAPOLEON} pose={poseN} camina={f < W.los20 + 6 ? 1.2 : 0} ojos={f >= W.otra ? 'cerrados' : 'grandes'} cejas="preocupado" boca={f >= W.otra ? 'mueca' : 'o'} />
			</Actor>
		</Toma>
	);
};

/* =============================== CIERRE =============================== */

const Veredicto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const mito = f >= W.mito;
	return (
		<Toma escena={<EscDesierto />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], y: [0, -10]}} golpes={[[W.mito, 0.08]]} encima={<><Destello desde={W.mito} color="#ff8a7a" fuerza={0.45} duracion={12} /><TituloArriba texto="*VEREDICTO*" desde={W.veredicto} tam={150} /></>}>
			<Esfinge x={540} y={1280} ancho={800} nariz={0} cara={mito ? 'normal' : 'sorpresa'} />
			<Actor x={540} y={1900} alto={1000}>
				<Muneco ropa={ROPA_NAPOLEON} pose={mito ? {...manosFrente([60, 330], [340, 330]), mi: 'abierta', md: 'abierta', wi: 20, wd: 20} : REPOSO} ojos={mito ? 'feliz' : 'normal'} cejas="neutral" boca={mito ? 'sonrisaGrande' : 'seria'} />
			</Actor>
			<Sello x={540} y={1590} texto="MITO" icono="✘" color={ROJO} desde={W.mito} tam={150} rot={-8} />
		</Toma>
	);
};

const Etiquetas: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const pose = animarPose(f, [
		[d, REPOSO],
		[W.bajito22, POSES.jarras],
	]);
	return (
		<Toma escena={<EscDesierto />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [-20, -40]}} golpes={[[W.bajito22, 0.05], [W.vandalo22, 0.05]]} encima={<><TituloArriba texto="PRIMERO *BAJITO*..." desde={W.primero} hasta={W.ahora} tam={124} /><TituloArriba texto="...AHORA *VÁNDALO|#ff6b6b*" desde={W.ahora} tam={124} /></>}>
			<Esfinge x={540} y={1240} ancho={760} nariz={0} cara="normal" mira={0.4} />
			<Actor x={540} y={1950} alto={1120}>
				<Muneco ropa={ROPA_NAPOLEON} pose={pose} ojos="entrecerrados" cejas="enojado" boca="mueca" />
			</Actor>
			<Sello x={340} y={780} texto="BAJITO" color="#1f6fd1" desde={W.bajito22} tam={64} rot={-12} solido />
			<Sello x={750} y={830} texto="VÁNDALO" color={ROJO} desde={W.vandalo22} tam={64} rot={9} solido />
		</Toma>
	);
};

const Pregunta: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscDesierto />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05]}} golpes={[[W.inventar, 0.05]]} encima={<><TituloArriba texto={'¿QUÉ MÁS LE VAN\nA *INVENTAR*?'} desde={W.que23} tam={118} /><Fundido desde={h - 12} duracion={12} /></>}>
			<Esfinge x={540} y={1240} ancho={760} nariz={0} cara={f >= W.pobre23 ? 'triste' : 'normal'} mira={0} />
			<Actor x={540} y={1950} alto={1120}>
				<Muneco ropa={ROPA_NAPOLEON} pose={animarPose(f, [[d, {...REPOSO, cabeza: 6}], [W.inventar, POSES.encogeHombros]])} ojos={f >= W.pobre23 ? 'normal' : 'cerrados'} cejas="preocupado" boca="seria" />
			</Actor>
		</Toma>
	);
};

/* =============================== Montaje =============================== */

type Plano = {desde: number; Comp: React.FC<P>; entrada: Transicion};

const PLANOS: Plano[] = [
	{desde: 0, Comp: Gancho, entrada: 'corte'},
	{desde: antes(W.la1), Comp: Chata, entrada: 'zoom'},
	{desde: antes(W.en2), Comp: Llegada, entrada: 'latigoDer'},
	{desde: antes(W.y3), Comp: Sospechoso, entrada: 'corte'},
	{desde: antes(W.quien), Comp: Quien, entrada: 'zoom'},
	{desde: antes(W.y5), Comp: Leyenda, entrada: 'latigoIzq'},
	{desde: antes(W.una6), Comp: Metro, entrada: 'zoom'},
	{desde: antes(W.y7), Comp: Guias, entrada: 'latigoDer'},
	{desde: antes(W.el8), Comp: Clarisimo, entrada: 'latigoArriba'},
	{desde: antes(W.total), Comp: Bajito, entrada: 'latigoIzq'},
	{desde: antes(W.pero11), Comp: Norden, entrada: 'zoom'},
	{desde: antes(W.y12), Comp: Dibujo, entrada: 'zoom'},
	{desde: antes(W.cuantos), Comp: Linea, entrada: 'latigoDer'},
	{desde: antes(W.y15), Comp: Culpable, entrada: 'corte'},
	{desde: antes(W.un16), Comp: Ofrendas, entrada: 'zoom'},
	{desde: antes(W.que16), Comp: Cincel, entrada: 'corte'},
	{desde: antes(W.para17), Comp: Sentencia, entrada: 'latigoIzq'},
	{desde: antes(W.y18), Comp: Rosetta, entrada: 'latigoDer'},
	{desde: antes(W.que19), Comp: Museo, entrada: 'latigoArriba'},
	{desde: antes(W.veredicto), Comp: Veredicto, entrada: 'latigoIzq'},
	{desde: antes(W.primero), Comp: Etiquetas, entrada: 'corte'},
	{desde: antes(W.que23), Comp: Pregunta, entrada: 'zoom'},
];

export const Historia: React.FC = () => (
	<>
		{PLANOS.map((p, i) => {
			const sig = PLANOS[i + 1];
			return <p.Comp key={i} d={p.desde} h={sig ? sig.desde : FIN_VIDEO} e={p.entrada} s={sig ? sig.entrada : 'corte'} />;
		})}
		<TituloArriba texto={'¿NAPOLEÓN LE VOLÓ\nLA *NARIZ*?'} desde={0} hasta={antes(W.la1)} tam={112} />
	</>
);

/** Efectos (pasan por la mezcla: siempre por debajo de la voz). [archivo, cuadro, volumen] */
export const SONIDOS: [string, number, number][] = [
	...PLANOS.filter((p) => p.entrada !== 'corte').map((p) => ['whoosh', p.desde - 7, 0.36] as [string, number, number]),
	['pop', W.no0 - 4, 0.3],
	['dundun', W.chata1 - 6, 0.3],
	['sello', W.naciera - 5, 0.4],
	['pop', W.a1798 - 4, 0.4],
	['objeto', W.canones2 - 20, 0.3],
	['ding', W.piramides - 4, 0.3],
	['pop', W.frances - 4, 0.3],
	['pop', W.canones3 - 4, 0.3],
	['pop', W.sin3 - 4, 0.3],
	['sello', W.ser4 - 5, 0.45],
	['arpa', W.leyenda - 8, 0.3],
	['pop', W.nariz5 - 4, 0.3],
	['boom', W.blanco - 2, 0.5],
	['garabato', W.metro - 8, 0.25],
	['boom', W.fallar - 8, 0.55],
	['hoja', W.historia - 6, 0.3],
	['hoja', W.guia1 - 4, 0.3],
	['pop', W.llega8 - 6, 0.3],
	['boing', W.desaparece - 6, 0.35],
	['sello', W.bajito9 - 5, 0.4],
	['sello', W.vandalo10 - 5, 0.45],
	['pop', W.a1737 - 4, 0.4],
	['garabato', W.dibuja - 2, 0.3],
	['sello', W.chata12 - 5, 0.45],
	['tic', W.napoleon13 - 2, 0.3],
	['tic', W.napoleon13 + 6, 0.3],
	['sello', W.nacido - 6, 0.4],
	['dundun', W.culpable - 6, 0.4],
	['pop', W.a1378 - 4, 0.4],
	['boing', W.harto - 4, 0.3],
	...GOLPES.map((g) => ['tic', g - 1, 0.5] as [string, number, number]),
	['objeto', GOLPES[GOLPES.length - 1] - 2, 0.35],
	['sello', W.vandalo17 - 5, 0.45],
	['burbujas', W.encontro - 4, 0.3],
	['ding', W.piedra - 4, 0.35],
	['pop', W.londres - 6, 0.3],
	['boing', W.otra - 6, 0.3],
	['sello', W.mito - 5, 0.5],
	['sello', W.bajito22 - 5, 0.35],
	['sello', W.vandalo22 - 5, 0.35],
	['pop', W.inventar - 4, 0.35],
];

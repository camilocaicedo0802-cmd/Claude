import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {Destello} from '../componentes/Efectos';
import {Actor, Muneco, POSES, Pose, Ropa, alcanzar, animarPose, manosFrente, senalar} from '../componentes/Muneco';
import {Borla, CamaraFoto, Informe, Microfono, Palomitas, Pedestal, Polaroid, Revista, TarroCrema} from '../componentes/Objetos';
import {Rotulo, TituloArriba} from '../componentes/Rotulos';
import {Toma, Transicion} from '../componentes/Toma';
import {Bocadillo, Brillos, Confeti, Fundido, Sello} from '../componentes/Utileria';
import {ROPA_ESPECTADOR_1, ROPA_ESPECTADORA_2, ROPA_FORENSE, ROPA_MJ_1978, ROPA_MJ_1982, ROPA_MJ_1991, ROPA_MJ_1993, ROPA_PAPARAZZI_1, ROPA_PAPARAZZI_2, ROPA_PRESENTADOR} from '../componentes/Vestuario';
import {EscAlfombra, EscBlancoNegro, EscCamerino, EscCiencia, EscConcierto, EscCorcho, EscEscenario, EscMundo, EscSala, EscTV} from '../escenarios/Escenarios';
import {CONDENSADA} from '../fuentes';
import {finFrase, palabra} from '../tiempos';

/*
 * «¿Michael Jackson se quiso volver blanco?» — tono respetuoso: el vitiligo es una enfermedad, no un chiste.
 * Cuadros GLOBALES: cada acción cae sobre la palabra exacta de la narración.
 */

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const antes = (n: number) => n - 3;
const TINTA = '#1b1b1f';

const W = {
	no0: palabra(0, 'no'),
	gusto: palabra(0, 'gusto'),
	y1: palabra(1, 'y'),
	secreto: palabra(1, 'secreto'),
	guardo: palabra(1, 'guardó'),
	en2: palabra(2, 'En'),
	anio1982: palabra(2, '1982'),
	thriller: palabra(2, 'Thriller'),
	grande: palabra(2, 'grande'),
	planeta: palabra(2, 'planeta'),
	pero3: palabra(3, 'Pero'),
	manchas3: palabra(3, 'manchas'),
	piel3: palabra(3, 'piel'),
	el4: palabra(4, 'Él'),
	maquillaje: palabra(4, 'maquillaje'),
	calla: palabra(4, 'calla'),
	los5: palabra(5, 'Los'),
	wacko: palabra(5, 'Wacko'),
	blanquea: palabra(5, 'blanquea'),
	las6: palabra(6, 'Las'),
	mundo: palabra(6, 'mundo'),
	y7: palabra(7, 'Y'),
	fotos: palabra(7, 'fotos'),
	veinte: palabra(8, '20'),
	treinta: palabra(9, '33'),
	blanca: palabra(9, 'BLANCA'),
	y10: palabra(10, 'Y'),
	opera: palabra(10, 'opera'),
	pero11: palabra(11, 'Pero'),
	vitiligo: palabra(11, 'vitiligo'),
	borra: palabra(11, 'borra'),
	piel11: palabra(11, 'piel'),
	quien: palabra(12, 'Quién'),
	autopsia: palabra(13, 'AUTOPSIA'),
	anio2009: palabra(13, '2009'),
	y14: palabra(14, 'Y'),
	cremas: palabra(14, 'cremas'),
	igualar: palabra(15, 'igualar'),
	no15: palabra(15, 'no'),
	para16: palabra(16, 'Para'),
	television: palabra(16, 'televisión'),
	muchos: palabra(16, 'muchos'),
	creyeron: palabra(16, 'creyeron'),
	y17: palabra(17, 'Y'),
	cantado: palabra(17, 'cantado'),
	noImporta: palabra(17, 'No'),
	veredicto: palabra(18, 'VEREDICTO'),
	mito: palabra(18, 'MITO'),
	quiso: palabra(19, 'Quiso'),
	chisme: palabra(19, 'chisme'),
};

export const FIN_VIDEO = finFrase(19) + 30;

type P = {d: number; h: number; e: Transicion; s: Transicion};

type Lugar = {x: number; y: number; alto: number};
const aLienzo = (a: Lugar, wx: number, wy: number): [number, number] => {
	const k = a.alto / 900;
	return [(wx - (a.x - 200 * k)) / k, (wy - (a.y - 880 * k)) / k];
};
const brazo = (lado: -1 | 1, r: {a: number; c: number; k?: number}): Partial<Pose> => (lado < 0 ? {bi: r.a, ci: r.c, ai: r.k ?? 1} : {bd: r.a, cd: r.c, ad: r.k ?? 1});
/** Michael con manchas de vitiligo (cara y manos) */
const conManchas = (ropa: Ropa, m: number): Ropa => ({...ropa, manchasManos: m, cabeza: {...ropa.cabeza, manchas: m}});

/** retrato (solo la cabeza) de un muñeco, para fotos y revistas */
const Retrato: React.FC<{ropa: Ropa; ancho: number; ojos?: 'normal' | 'feliz'}> = ({ropa, ancho, ojos = 'normal'}) => (
	<div style={{position: 'absolute', left: ancho * -0.32, top: ancho * 0.02, width: ancho * 1.64, height: ancho * 3.7}}>
		<Muneco ropa={ropa} pose={{}} ojos={ojos} boca="sonrisa" sombra={false} parpadea={false} respira={false} />
	</div>
);

/* =============================== GANCHO =============================== */

const Gancho: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const niega = f >= W.no0 - 2;
	const pose = animarPose(f, [
		[0, {...manosFrente([186, 480], [214, 480])}],
		[W.no0 - 4, {...manosFrente([186, 480], [214, 480])}],
		[W.no0 + 4, {...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 352, 236)), md: 'senala'}],
		[W.gusto + 4, POSES.cruzados],
	]);
	const vaiven = niega && f < W.gusto ? Math.sin((f - W.no0) / 4) : 0;
	return (
		<Toma escena={<EscConcierto color="#1c1236" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], y: [0, -20]}} golpes={[[W.no0, 0.05]]}>
			<Actor x={540} y={1960} alto={1180}>
				<Muneco ropa={ROPA_MJ_1991} pose={{...pose, cabeza: vaiven * 8, wd: (pose.wd ?? 0) + vaiven * 16}} ojos={niega ? 'entrecerrados' : 'normal'} cejas={niega ? 'preocupado' : 'neutral'} boca={niega ? 'seria' : 'sonrisa'} />
			</Actor>
		</Toma>
	);
};

const Secreto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const shh = f >= W.secreto - 4;
	const pose = shh ? {...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 214, 262)), md: 'senala' as const} : {...manosFrente([186, 480], [214, 480])};
	return (
		<Toma escena={<EscCamerino />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.08, 1.14], y: [-40, -60]}} golpes={[[W.secreto, 0.05]]}>
			<Actor x={540} y={2080} alto={1300}>
				<Muneco ropa={ROPA_MJ_1991} pose={pose} ojos={shh ? 'mirandoLado' : 'normal'} cejas="preocupado" boca="seria" />
			</Actor>
			<Sello x={540} y={1560} texto="UN SECRETO" color="#1b1b22" desde={W.guardo - 4} tam={74} rot={-6} />
		</Toma>
	);
};

/* =============================== ORIGEN =============================== */

const PASOS: Partial<Pose>[] = [
	{bi: 150, ci: 20, bd: 150, cd: 20, mi: 'abierta', md: 'abierta', salto: 20},
	{...POSES.jarras, ...brazo(1, alcanzar(1, 330, -60)), md: 'senala', cabeza: -8},
	{bi: 60, ci: 40, bd: 100, cd: -30, mi: 'puno', md: 'abierta', ld: 0.5, cuerpo: -6},
	{bi: 20, ci: -60, bd: 20, cd: -60, mi: 'puno', md: 'puno', salto: 40, li: 0.15, ld: 0.15, cabeza: 6},
	{...POSES.jarras, li: 0.45, cuerpo: 6, cabeza: -6},
];

const Thriller: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const claves: [number, Partial<Pose>][] = [];
	for (let k = 0; d + 6 + k * 14 < h; k++) claves.push([d + 6 + k * 14, PASOS[k % PASOS.length]]);
	const estrella = f >= W.grande;
	return (
		<Toma escena={<EscConcierto />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [10, -10]}} golpes={[[W.thriller, 0.05], [W.planeta, 0.06]]} encima={<><TituloArriba texto="*1982*" desde={W.anio1982} tam={160} /><Rotulo texto="«THRILLER» · EL DISCO MÁS VENDIDO DE LA HISTORIA" desde={W.thriller} tam={36} /></>}>
			<Actor x={540} y={1470} alto={1000}>
				<Muneco ropa={ROPA_MJ_1982} pose={animarPose(f, claves, 6)} ojos={estrella ? 'feliz' : 'entrecerrados'} cejas="arrogante" boca={estrella ? 'sonrisaGrande' : 'picara'} />
			</Actor>
			<Brillos x={540} y={800} desde={W.planeta} radio={420} n={12} />
			<Confeti desde={W.grande} n={40} />
		</Toma>
	);
};

const Manchas: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const m = interpolate(f, [W.manchas3 - 4, W.piel3 + 6], [0, 0.6], {...clamp, easing: Easing.inOut(Easing.quad)});
	const mira = f >= W.manchas3 - 10;
	return (
		<Toma escena={<EscCamerino />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.16], y: [-50, -70]}} encima={<><TituloArriba texto="MANCHAS *BLANCAS*" desde={W.manchas3} tam={130} /></>}>
			<Actor x={540} y={2080} alto={1300}>
				<Muneco ropa={conManchas(ROPA_MJ_1982, m)} pose={mira ? {...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 318, 330)), md: 'abierta', wd: -20, cabeza: 10} : {...manosFrente([186, 480], [214, 480])}} ojos={mira ? 'grandes' : 'normal'} cejas={mira ? 'preocupado' : 'neutral'} boca={mira ? 'o' : 'seria'} />
			</Actor>
		</Toma>
	);
};

/* =============================== PRIMER ESCALÓN =============================== */

const Maquillaje: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const m = interpolate(f, [d + 4, W.calla - 6], [0.6, 0], {...clamp, easing: Easing.inOut(Easing.quad)});
	const calla = f >= W.calla - 4;
	const pose: Partial<Pose> = calla
		? {...brazo(-1, alcanzar(-1, 186, 262)), mi: 'senala', ...manosFrente(undefined, [250, 470]), md: 'agarra'}
		: {...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 262 + Math.sin(f / 3) * 16, 196 + Math.cos(f / 4) * 12)), md: 'agarra'};
	return (
		<Toma escena={<EscCamerino />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.12, 1.16], y: [-60, -70]}} encima={<><TituloArriba texto="LAS TAPA... Y *CALLA*" desde={W.maquillaje} tam={120} /></>}>
			<Actor x={540} y={2080} alto={1300}>
				<Muneco ropa={conManchas(ROPA_MJ_1982, m)} pose={pose} objDer={<Borla />} ojos={calla ? 'mirandoLado' : 'entrecerrados'} cejas="preocupado" boca="seria" />
			</Actor>
		</Toma>
	);
};

const Tabloides: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const destello = (k: number) => {
		const t = (f + k * 9) % 18;
		return t < 3 ? 1 - t / 3 : 0;
	};
	const fotografo = (k: number): Partial<Pose> => ({...manosFrente([150, 250], [250, 250]), mi: 'agarra', md: 'agarra', cuerpo: k ? -4 : 4});
	return (
		<Toma escena={<EscAlfombra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.06]}} golpes={[[W.wacko, 0.07], [W.blanquea, 0.05]]}>
			<Actor x={540} y={2060} alto={1060}>
				<Muneco ropa={ROPA_MJ_1982} pose={{...brazo(-1, alcanzar(-1, 150, 230)), mi: 'abierta', ...manosFrente(undefined, [250, 480]), cabeza: 10}} ojos="cerrados" cejas="preocupado" boca="mueca" />
			</Actor>
			<Actor x={120} y={2000} alto={1150}>
				<Muneco ropa={ROPA_PAPARAZZI_1} pose={fotografo(0)} objDer={<CamaraFoto rot={180} flash={destello(0)} />} ojos="entrecerrados" cejas="arrogante" boca="picara" semilla={1} />
			</Actor>
			<Actor x={960} y={2000} alto={1150} voltear>
				<Muneco ropa={ROPA_PAPARAZZI_2} pose={fotografo(1)} objDer={<CamaraFoto rot={180} flash={destello(1)} />} ojos="entrecerrados" cejas="arrogante" boca="picara" semilla={2} />
			</Actor>
			<Revista x={540} y={700} ancho={420} nombre="EL CHISME" titular="¡WACKO JACKO!" desde={W.wacko - 2} rot={-5}>
				<div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(45deg,#ffe0e0,#ffe0e0 20px,#fff4f4 20px,#fff4f4 40px)'}} />
				<div style={{position: 'absolute', left: 30, right: 30, top: 40, fontFamily: CONDENSADA, fontSize: 64, lineHeight: 1, color: TINTA, textAlign: 'center'}}>¿SE BLANQUEA A PROPÓSITO?</div>
			</Revista>
			<Sello x={540} y={1560} texto="RUMOR" color="#d6262e" desde={W.blanquea} tam={92} rot={-8} />
		</Toma>
	);
};

const Mundo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const titulares = ['¡WACKO JACKO!', '¿SE BLANQUEA?', '¡ESCÁNDALO!', '¿QUÉ LE PASA?'];
	const colores = ['#e3262e', '#1f6fd1', '#ff8a1e', '#7b3fe4'];
	return (
		<Toma escena={<EscMundo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}} encima={<><TituloArriba texto="EN TODO EL *MUNDO*" desde={W.las6} tam={130} /></>}>
			{titulares.map((t, i) => {
				const a = (f - d) / 16 + (i * Math.PI) / 2;
				return <Revista key={i} x={540 + Math.cos(a) * 420} y={1000 + Math.sin(a) * 300} ancho={210} nombre="REVISTA" titular={t} color={colores[i]} rot={Math.cos(a) * 12} desde={d + 2 + i * 5} />;
			})}
		</Toma>
	);
};

/* =============================== SEGUNDO ESCALÓN =============================== */

const FotosCorcho: React.FC<{conRojo: boolean}> = ({conRojo}) => {
	const f = useCurrentFrame();
	return (
		<>
			{f >= W.treinta && (
				<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
					<path d="M 300 560 Q 540 700 780 760" stroke="#c4262e" strokeWidth={8} fill="none" strokeDasharray={conRojo ? undefined : '0'} />
				</svg>
			)}
			<Polaroid x={300} y={810} ancho={400} leyenda="1978 · 20 AÑOS" desde={W.fotos} revela={W.veinte - 2} rot={-6}>
				<Retrato ropa={ROPA_MJ_1978} ancho={376} />
			</Polaroid>
			<Polaroid x={780} y={1010} ancho={400} leyenda="1991 · 33 AÑOS" desde={W.fotos + 6} revela={W.treinta - 2} rot={5}>
				<Retrato ropa={{...ROPA_MJ_1991, cabeza: {...ROPA_MJ_1991.cabeza, gorra: undefined}}} ancho={376} />
			</Polaroid>
		</>
	);
};

const Fotos: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscCorcho />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05]}} golpes={[[W.blanca, 0.07]]} encima={<><TituloArriba texto="LAS *FOTOS*" desde={W.fotos} tam={140} /></>}>
		<FotosCorcho conRojo />
		<Sello x={540} y={1470} texto="¡CASI BLANCA!" color="#d6262e" desde={W.blanca} tam={96} rot={-6} />
	</Toma>
);

const Nariz: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscCorcho />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.08]}} golpes={[[W.opera, 0.06]]}>
		<FotosCorcho conRojo />
		<Revista x={540} y={1180} ancho={460} nombre="EL CHISME" titular="¡SE OPERA LA NARIZ!" color="#1f6fd1" desde={W.opera - 2} rot={-3}>
			<div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(-45deg,#e3eefc,#e3eefc 20px,#f6f9ff 20px,#f6f9ff 40px)'}} />
			<div style={{position: 'absolute', left: 30, right: 30, top: 60, fontFamily: CONDENSADA, fontSize: 70, lineHeight: 1, color: TINTA, textAlign: 'center'}}>Y ENCIMA...</div>
		</Revista>
	</Toma>
);

/* =============================== CLÍMAX =============================== */

const Vitiligo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const m = interpolate(f, [W.vitiligo, W.piel11 + 6], [0.35, 1.1], {...clamp, easing: Easing.inOut(Easing.quad)});
	const borra = interpolate(f, [W.borra - 6, W.piel11 + 10], [1, 0], clamp);
	return (
		<Toma escena={<EscCiencia />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}} golpes={[[W.vitiligo, 0.07]]} encima={<><TituloArriba texto="*VITILIGO*" desde={W.vitiligo} tam={170} /><Rotulo texto="ENFERMEDAD QUE BORRA EL COLOR DE LA PIEL" desde={W.borra - 4} y={540} tam={40} /></>}>
			<Actor x={300} y={1960} alto={1120}>
				<Muneco ropa={conManchas(ROPA_MJ_1982, m)} pose={{...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 268, 290)), md: 'abierta', cabeza: 6}} ojos="normal" cejas="preocupado" boca="seria" />
			</Actor>
			{/* lupa: las células del color (melanocitos) desaparecen */}
			<div style={{position: 'absolute', left: 560, top: 720, width: 440, height: 440, borderRadius: '50%', border: `16px solid ${TINTA}`, overflow: 'hidden', background: '#f2dccb', boxShadow: '0 16px 0 rgba(0,0,0,0.25)'}}>
				<div style={{position: 'absolute', inset: 0, background: '#8a5a3c', opacity: borra}} />
				{Array.from({length: 16}).map((_, i) => {
					const x = 40 + ((i * 97) % 340);
					const y = 40 + ((i * 61) % 340);
					const vive = borra > i / 16;
					return <div key={i} style={{position: 'absolute', left: x, top: y, width: 46, height: 46, borderRadius: '50%', background: '#4a2a18', border: `4px solid ${TINTA}`, opacity: vive ? 1 : 0, transform: `scale(${vive ? 1 : 0.2})`}} />;
				})}
			</div>
			<div style={{position: 'absolute', left: 940, top: 1110, width: 40, height: 220, background: TINTA, borderRadius: 20, transform: 'rotate(-40deg)', transformOrigin: '50% 0%'}} />
			<div style={{position: 'absolute', left: 560, top: 1180, width: 440, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 46, color: TINTA}}>CÉLULAS DEL COLOR</div>
		</Toma>
	);
};

const Autopsia: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const actor = {x: 860, y: 1980, alto: 1120};
	const [tx, ty] = aLienzo(actor, 540, 820);
	return (
		<Toma escena={<EscCiencia color="#eef2f5" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}} golpes={[[W.autopsia, 0.06], [W.anio2009, 0.05]]} encima={<><TituloArriba texto="¿QUIÉN LO *CONFIRMÓ*?" desde={W.quien} hasta={W.autopsia} tam={130} /><TituloArriba texto="¡SU *AUTOPSIA*!" desde={W.autopsia} tam={150} /></>}>
			<Informe
				x={430}
				y={600}
				ancho={640}
				titulo="INFORME DE AUTOPSIA"
				lineas={[
					{texto: 'Año: 2009', desde: W.anio2009},
					{texto: 'Diagnóstico: VITILIGO', desde: W.anio2009 + 6, marca: true},
					{texto: 'Enfermedad confirmada', desde: W.anio2009 + 12, marca: true},
				]}
			/>
			<Actor {...actor}>
				<Muneco ropa={ROPA_FORENSE} pose={f >= W.autopsia ? {...brazo(-1, senalar(-1, tx, ty, 0.85)), mi: 'senala', ...manosFrente(undefined, [250, 480])} : {...manosFrente([186, 480], [214, 480])}} ojos="normal" cejas="neutral" boca="seria" />
			</Actor>
			<Sello x={420} y={1240} texto="CONFIRMADO" icono="✔" color="#1f9d48" desde={W.anio2009 + 14} tam={86} rot={-6} />
		</Toma>
	);
};

const Cremas: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const m = interpolate(f, [d, W.igualar + 10], [0.9, 2.4], {...clamp, easing: Easing.inOut(Easing.quad)});
	const parejo = interpolate(f, [W.igualar + 8, W.igualar + 22], [0, 1], clamp);
	const pose: Partial<Pose> = {...brazo(-1, alcanzar(-1, 150, 430)), mi: 'agarra', ...brazo(1, alcanzar(1, 262 + Math.sin(f / 3.5) * 14, 214 + Math.cos(f / 4) * 10)), md: 'abierta'};
	return (
		<Toma escena={<EscCamerino />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.14], y: [-50, -60]}} encima={<><TituloArriba texto="PARA *IGUALAR*" desde={W.igualar} hasta={W.no15} tam={150} /><TituloArriba texto="*NO|#ff6b6b* PARA BLANQUEARSE" desde={W.no15} tam={118} /><Rotulo texto="EL VITILIGO YA CUBRÍA CASI TODA SU PIEL" desde={W.cremas} y={530} tam={40} /></>}>
			<Actor x={540} y={2080} alto={1300} opacidad={1 - parejo}>
				<Muneco ropa={conManchas(ROPA_MJ_1982, m)} pose={pose} objIzq={<TarroCrema />} ojos="entrecerrados" cejas="neutral" boca="seria" />
			</Actor>
			<Actor x={540} y={2080} alto={1300} opacidad={parejo}>
				<Muneco ropa={{...ROPA_MJ_1993, casaca: '#c8102e', guanteDer: undefined, brillosGuante: false, cabeza: {...ROPA_MJ_1982.cabeza, piel: '#f1dccb'}, guantes: '#f1dccb', cheurones: '#1b1b22', pantalon: '#c8102e'}} pose={pose} objIzq={<TarroCrema />} ojos="entrecerrados" cejas="neutral" boca="sonrisa" />
			</Actor>
		</Toma>
	);
};

/* =============================== GOLPE EXTRA =============================== */

const TV: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscTV />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], y: [0, -10]}} encima={<><Rotulo texto="ENTREVISTA EN TELEVISIÓN · 1993" desde={d + 2} /><TituloArriba texto="LO CONTÓ EN *TV*" desde={W.television} tam={140} /></>}>
			<Actor x={360} y={1880} alto={1080}>
				<Muneco ropa={ROPA_MJ_1993} pose={{...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 214, 380)), md: 'abierta', cabeza: Math.sin(f / 12) * 3}} hablando ojos="normal" cejas="preocupado" boca="seria" />
			</Actor>
			<Actor x={810} y={1880} alto={1060} voltear>
				<Muneco ropa={ROPA_PRESENTADOR} pose={{...brazo(-1, alcanzar(-1, 110, 300)), mi: 'agarra', ...manosFrente(undefined, [214, 480]), cabeza: -4}} objIzq={<Microfono rot={150} />} ojos="normal" cejas="sorprendido" boca="o" semilla={2} />
			</Actor>
		</Toma>
	);
};

const Incredulos: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscSala />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.08], y: [-20, -30]}} golpes={[[W.creyeron, 0.05]]} encima={<><TituloArriba texto="NO LE *CREYERON*" desde={W.creyeron} tam={140} /></>}>
			<Actor x={330} y={1760} alto={1000}>
				<Muneco ropa={ROPA_ESPECTADOR_1} pose={POSES.cruzados} ojos="entrecerrados" cejas="arrogante" boca="mueca" semilla={1} />
			</Actor>
			<Actor x={750} y={1760} alto={960} voltear>
				<Muneco ropa={ROPA_ESPECTADORA_2} pose={{...brazo(-1, alcanzar(-1, 150, 440)), mi: 'agarra', ...brazo(1, alcanzar(1, 230, 250 + Math.max(0, Math.sin(f / 5)) * 20)), md: 'agarra'}} objIzq={<Palomitas />} ojos="entrecerrados" cejas="arrogante" boca="seria" semilla={2} />
			</Actor>
			{/* respaldo del sofá por delante: están sentados */}
			<div style={{position: 'absolute', left: 30, right: 30, top: 1360, height: 300, borderRadius: 70, background: '#4a5c76', border: `8px solid ${TINTA}`}} />
			<Bocadillo x={300} y={660} texto="¡SÍ, CLARO!" desde={W.muchos} cola="der" ancho={420} tam={60} />
		</Toma>
	);
};

const BlackOrWhite: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const balanceo = Math.sin(f / 10);
	return (
		<Toma escena={<EscBlancoNegro />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], y: [0, -10]}} golpes={[[W.noImporta, 0.05]]} encima={<><Rotulo texto="«BLACK OR WHITE» · 1991" desde={W.cantado - 4} /><TituloArriba texto={'«NO IMPORTA SI ERES\n*NEGRO* O *BLANCO*»'} desde={W.noImporta} tam={104} /></>}>
			<Actor x={540} y={1560} alto={1060}>
				<Muneco ropa={ROPA_MJ_1991} pose={{...brazo(-1, alcanzar(-1, 0, 330 + balanceo * 30)), mi: 'abierta', ...brazo(1, alcanzar(1, 228, 268)), md: 'agarra', cuerpo: balanceo * 3}} objDer={<Microfono rot={160} />} ojos="cerrados" cejas="neutral" boca={f >= W.noImporta ? 'abierta' : 'sonrisa'} />
			</Actor>
		</Toma>
	);
};

/* =============================== CIERRE =============================== */

const Veredicto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const mito = f >= W.mito;
	return (
		<Toma escena={<EscEscenario />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], y: [0, -10]}} golpes={[[W.mito, 0.08]]} encima={<><Destello desde={W.mito} color="#ff8a7a" fuerza={0.45} duracion={12} /><TituloArriba texto="*VEREDICTO*" desde={W.veredicto} tam={150} /></>}>
			<Pedestal x={540} y={1540} ancho={420} alto={160} />
			<Actor x={540} y={1540} alto={900}>
				<Muneco ropa={ROPA_MJ_1991} pose={mito ? {...manosFrente([60, 330], [340, 330]), mi: 'abierta', md: 'abierta', wi: 20, wd: 20} : {...manosFrente([186, 480], [214, 480])}} ojos={mito ? 'feliz' : 'normal'} cejas="neutral" boca={mito ? 'sonrisa' : 'seria'} />
			</Actor>
			<Sello x={540} y={1240} texto="MITO" icono="✘" color="#d6262e" desde={W.mito} tam={150} rot={-8} />
		</Toma>
	);
};

const Pregunta: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscConcierto color="#1c1236" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05]}} golpes={[[W.chisme, 0.05]]} encima={<><TituloArriba texto={'¿QUISO SER *BLANCO*...\nO VÍCTIMA DEL *CHISME|#ff6b6b*?'} desde={W.quiso} tam={104} /><Fundido desde={h - 12} duracion={12} /></>}>
			<Actor x={540} y={1960} alto={1180}>
				<Muneco ropa={ROPA_MJ_1991} pose={animarPose(f, [[d, {...manosFrente([186, 480], [214, 480]), cabeza: 8}], [W.chisme - 6, POSES.encogeHombros]])} ojos={f >= W.chisme ? 'normal' : 'cerrados'} cejas="preocupado" boca="seria" />
			</Actor>
		</Toma>
	);
};

/* =============================== Montaje =============================== */

type Plano = {desde: number; Comp: React.FC<P>; entrada: Transicion};

const PLANOS: Plano[] = [
	{desde: 0, Comp: Gancho, entrada: 'corte'},
	{desde: antes(W.y1), Comp: Secreto, entrada: 'zoom'},
	{desde: antes(W.en2), Comp: Thriller, entrada: 'latigoDer'},
	{desde: antes(W.pero3), Comp: Manchas, entrada: 'zoom'},
	{desde: antes(W.el4), Comp: Maquillaje, entrada: 'corte'},
	{desde: antes(W.los5), Comp: Tabloides, entrada: 'latigoIzq'},
	{desde: antes(W.las6), Comp: Mundo, entrada: 'latigoArriba'},
	{desde: antes(W.y7), Comp: Fotos, entrada: 'latigoDer'},
	{desde: antes(W.y10), Comp: Nariz, entrada: 'corte'},
	{desde: antes(W.pero11), Comp: Vitiligo, entrada: 'zoom'},
	{desde: antes(W.quien), Comp: Autopsia, entrada: 'latigoIzq'},
	{desde: antes(W.y14), Comp: Cremas, entrada: 'latigoDer'},
	{desde: antes(W.para16), Comp: TV, entrada: 'latigoArriba'},
	{desde: antes(W.muchos), Comp: Incredulos, entrada: 'corte'},
	{desde: antes(W.y17), Comp: BlackOrWhite, entrada: 'zoom'},
	{desde: antes(W.veredicto), Comp: Veredicto, entrada: 'latigoIzq'},
	{desde: antes(W.quiso), Comp: Pregunta, entrada: 'zoom'},
];

export const Historia: React.FC = () => (
	<>
		{PLANOS.map((p, i) => {
			const sig = PLANOS[i + 1];
			return <p.Comp key={i} d={p.desde} h={sig ? sig.desde : FIN_VIDEO} e={p.entrada} s={sig ? sig.entrada : 'corte'} />;
		})}
		<TituloArriba texto="¿SE QUISO VOLVER *BLANCO*?" desde={0} hasta={antes(W.en2)} tam={104} />
	</>
);

/** Efectos (pasan por la mezcla: siempre por debajo de la voz). [archivo, cuadro, volumen] */
export const SONIDOS: [string, number, number][] = [
	...PLANOS.filter((p) => p.entrada !== 'corte').map((p) => ['whoosh', p.desde - 7, 0.36] as [string, number, number]),
	['pop', W.no0 - 4, 0.3],
	['dundun', W.secreto - 6, 0.35],
	['pop', W.anio1982 - 4, 0.4],
	['aplausos', W.thriller, 0.35],
	['ding', W.planeta - 4, 0.35],
	['burbujas', W.manchas3 - 6, 0.3],
	['tic', W.los5, 0.3],
	['tic', W.los5 + 9, 0.3],
	['tic', W.los5 + 18, 0.3],
	['tic', W.los5 + 27, 0.3],
	['sello', W.wacko - 6, 0.45],
	['sello', W.blanquea - 4, 0.4],
	['hoja', W.las6, 0.35],
	['hoja', W.las6 + 10, 0.35],
	['pop', W.veinte - 4, 0.4],
	['pop', W.treinta - 4, 0.4],
	['sello', W.blanca - 5, 0.45],
	['hoja', W.opera - 9, 0.22],
	['dundun', W.vitiligo - 6, 0.4],
	['garabato', W.anio2009, 0.3],
	['sello', W.anio2009 + 10, 0.45],
	['burbujas', W.igualar - 4, 0.3],
	['pop', W.no15 - 4, 0.35],
	['beep', W.para16 + 4, 0.25],
	['pop', W.muchos - 4, 0.35],
	['arpa', W.cantado - 6, 0.3],
	['sello', W.mito - 5, 0.5],
	['pop', W.chisme - 4, 0.35],
];

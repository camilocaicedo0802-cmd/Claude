import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {Bombilla, Calendario, Destello, Etiqueta, Explosion, Flecha, Moscas} from '../componentes/Efectos';
import {CHOLMONDELEY, ESPIA_MUERTO, HITLER, MONTAGU, Personaje, SOLDADO} from '../componentes/Personaje';
import {EnMundo, Toma, Transicion} from '../componentes/Toma';
import {finFrase, inicioFrase, palabra} from '../tiempos';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/* Momentos clave, sacados de los tiempos reales de la voz */
export const M = {
	hitler: palabra(0, 'Hitler'),
	durante: palabra(0, 'durante'),
	pues: palabra(1, 'Pues'),
	britanicos: palabra(1, 'británicos'),
	idea: palabra(1, 'idea'),
	peculiar: palabra(1, 'peculiar'),
	enviarle: palabra(2, 'enviarle'),
	muerto: palabra(2, 'muerto'),
	era: palabra(3, 'Era'),
	n1943: palabra(3, '1943'),
	aliados: palabra(3, 'aliados'),
	sicilia: palabra(3, 'Sicilia'),
	finMuestra: Math.min(finFrase(3) + 3, inicioFrase(4) - 1),
};

/* Cortes de cámara: un poquito antes de la palabra, para que la imagen "llegue" con la voz */
export const CORTES = {
	bunker: 0,
	batalla: M.durante,
	londres: M.pues - 3,
	oficina: M.idea - 4,
	morgue: M.enviarle - 3,
	calendario: M.era - 4,
	mapa: palabra(3, 'y') - 2,
	fin: M.finMuestra,
};

const sacudidaExplosiones = (golpes: number[], fuerza = 16) => (f: number) =>
	golpes.reduce((acc, g) => acc + (f >= g ? fuerza * Math.exp(-(f - g) / 5) : 0), 0);

/** 1. "¿Cómo engañas a Hitler..." — Hitler en su búnker frente al mapa. */
const TomaBunker: React.FC = () => {
	const f = useCurrentFrame();
	const mira = f >= M.hitler - 3;
	return (
		<Toma fondo="bunker.jpg" desde={CORTES.bunker} hasta={CORTES.batalla} salida="latigoDer" cam={{s: [1.0, 1.2], y: [0, -50], r: [-1.5, 0.5], curva: 'salida'}} golpes={[[M.hitler, 0.06]]}>
			<EnMundo x={560} y={1900} alto={1180}>
				<Personaje
					diseno={HITLER}
					ojos={mira ? 'normal' : 'mirandoLado'}
					cejas={mira ? 'enojado' : 'neutral'}
					boca={mira ? 'mueca' : 'seria'}
					cabeza={mira ? 5 : -7}
					brazoIzq={40}
					codoIzq={-95}
					brazoDer={40}
					codoDer={-95}
				/>
			</EnMundo>
		</Toma>
	);
};

/** 2. "...durante una guerra?" — campo de batalla con explosiones y un soldado huyendo. */
const TomaBatalla: React.FC = () => {
	const f = useCurrentFrame();
	const boom = [CORTES.batalla + 3, CORTES.batalla + 17, CORTES.batalla + 29];
	const xSoldado = interpolate(f, [CORTES.batalla - 4, CORTES.londres + 4], [-200, 1250], clamp);
	return (
		<Toma
			fondo="batalla.jpg"
			desde={CORTES.batalla}
			hasta={CORTES.londres}
			entrada="latigoDer"
			salida="latigoIzq"
			cam={{s: [1.12, 1.42], y: [30, -70], r: [-1, 1.5]}}
			sacudida={sacudidaExplosiones(boom)}
			encima={boom.map((b) => <Destello key={b} desde={b} />)}
		>
			<Explosion x={870} y={690} desde={boom[0]} tam={520} />
			<Explosion x={260} y={770} desde={boom[1]} tam={420} />
			<Explosion x={640} y={860} desde={boom[2]} tam={460} />
			<EnMundo x={xSoldado} y={2090} alto={720}>
				<Personaje diseno={SOLDADO} caminando ojos="grandes" cejas="preocupado" boca="abierta" brazoIzq={150} brazoDer={150} codoIzq={-20} codoDer={-20} />
			</EnMundo>
		</Toma>
	);
};

/** 3. "Pues los británicos tuvieron..." — los dos oficiales británicos llegan por la calle de Londres. */
const TomaLondres: React.FC = () => {
	const f = useCurrentFrame();
	const llegada = M.britanicos + 12;
	const avance = interpolate(f, [CORTES.londres - 4, llegada], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const caminando = f < llegada - 2;
	return (
		<Toma fondo="londres.jpg" desde={CORTES.londres} hasta={CORTES.oficina} entrada="latigoIzq" salida="zoom" cam={{s: [1.1, 1.2], x: [60, -20], y: [-70, -110]}}>
			<EnMundo x={interpolate(avance, [0, 1], [-560, 300])} y={1900} alto={1120}>
				<Personaje diseno={CHOLMONDELEY} semilla={2} caminando={caminando} ojos={caminando ? 'normal' : 'feliz'} cejas="arrogante" boca={caminando ? 'sonrisa' : 'picara'} />
			</EnMundo>
			<EnMundo x={interpolate(avance, [0, 1], [-230, 780])} y={1930} alto={1060}>
				<Personaje diseno={MONTAGU} caminando={caminando} cejas={caminando ? 'neutral' : 'arrogante'} boca="sonrisa" ojos={caminando ? 'normal' : 'mirandoLado'} />
			</EnMundo>
		</Toma>
	);
};

/** 4. "...una idea bastante peculiar:" — primer plano, se le prende el bombillo. */
const TomaOficina: React.FC = () => {
	const f = useCurrentFrame();
	const sorpresa = f >= M.idea + 2;
	const picaro = f >= M.peculiar;
	return (
		<Toma fondo="oficina.jpg" desde={CORTES.oficina} hasta={CORTES.morgue} entrada="zoom" salida="latigoDer" cam={{s: [1.12, 1.3], y: [0, 30]}} golpes={[[M.idea + 2, 0.07]]}>
			<EnMundo x={540} y={2180} alto={1700}>
				<Personaje
					diseno={CHOLMONDELEY}
					semilla={2}
					ojos={picaro ? 'entrecerrados' : sorpresa ? 'grandes' : 'normal'}
					cejas={picaro ? 'arrogante' : sorpresa ? 'sorprendido' : 'preocupado'}
					boca={picaro ? 'picara' : sorpresa ? 'o' : 'seria'}
					cabeza={picaro ? 7 : sorpresa ? -3 : 0}
				/>
			</EnMundo>
			<Bombilla x={560} y={390} tam={240} desde={M.idea + 2} />
		</Toma>
	);
};

/** 5. "¡enviarle un espía muerto!" — presentan al espía... que está bien muerto. */
const TomaMorgue: React.FC = () => {
	const f = useCurrentFrame();
	const cae = interpolate(f, [M.muerto + 14, CORTES.calendario + 2], [0, -24], {...clamp, easing: Easing.in(Easing.quad)});
	const asombro = f >= M.muerto + 16;
	return (
		<Toma
			fondo="morgue.jpg"
			desde={CORTES.morgue}
			hasta={CORTES.calendario}
			entrada="latigoDer"
			salida="latigoArriba"
			cam={{s: [1.05, 1.12]}}
			golpes={[[M.muerto - 2, 0.3]]}
			tinte="rgba(60,200,190,0.35)"
		>
			<EnMundo x={185} y={1640} alto={760}>
				<Personaje diseno={MONTAGU} ojos={asombro ? 'grandes' : 'feliz'} cejas={asombro ? 'sorprendido' : 'arrogante'} boca={asombro ? 'o' : 'sonrisaGrande'} brazoDer={105} codoDer={-10} brazoIzq={150} codoIzq={10} />
			</EnMundo>
			<EnMundo x={895} y={1640} alto={800}>
				<Personaje diseno={CHOLMONDELEY} semilla={2} ojos={asombro ? 'grandes' : 'feliz'} cejas={asombro ? 'sorprendido' : 'arrogante'} boca={asombro ? 'o' : 'sonrisaGrande'} brazoIzq={105} codoIzq={-10} brazoDer={150} codoDer={10} />
			</EnMundo>
			<EnMundo x={540} y={1660} alto={900} rot={cae}>
				<Personaje diseno={ESPIA_MUERTO} ojos="x" cejas="ninguna" boca="lengua" cabeza={-14} inclinacion={-3} respira={false} parpadea={false} brazoIzq={6} brazoDer={8} />
			</EnMundo>
			<Moscas x={540} y={930} radio={210} n={4} />
		</Toma>
	);
};

/** 6. "Era 1943," — el calendario pasa los años de la guerra hasta 1943. */
const TomaCalendario: React.FC = () => {
	const c = CORTES.calendario;
	return (
		<Toma fondo="pared.jpg" desde={c} hasta={CORTES.mapa} entrada="latigoArriba" salida="latigoIzq" cam={{s: [1.02, 1.16], y: [0, 20]}} golpes={[[M.n1943 + 3, 0.05]]}>
			<Calendario x={540} y={410} ancho={830} anios={[1939, 1940, 1941, 1942, 1943]} cambios={[c + 4, M.n1943 - 4, M.n1943 - 1, M.n1943 + 2]} />
		</Toma>
	);
};

/** 7. "...y los aliados querían invadir Sicilia." — vista aérea, flechas de invasión hacia la isla. */
const TomaMapa: React.FC<{hasta: number; salida: Transicion}> = ({hasta, salida}) => (
	<Toma fondo="mediterraneo.jpg" desde={CORTES.mapa} hasta={hasta} entrada="latigoIzq" salida={salida} cam={{s: [1.04, 1.28], y: [10, 60], r: [0, 2.5]}}>
		<Flecha d="M 90 1880 Q 160 1450 430 1170" desde={M.aliados - 4} />
		<Flecha d="M 1000 1900 Q 980 1480 760 1190" desde={M.aliados + 2} />
		<Flecha d="M 560 1960 Q 540 1600 600 1260" desde={M.aliados + 8} />
		<Etiqueta x={560} y={500} texto="SICILIA" desde={M.sicilia - 2} />
	</Toma>
);

/** En la muestra el mapa cierra el video; en el completo sale con un latigazo hacia el desarrollo. */
export const Gancho: React.FC<{finMapa?: number; salidaMapa?: Transicion}> = ({finMapa = CORTES.fin + 1, salidaMapa = 'corte'}) => (
	<>
		<TomaBunker />
		<TomaBatalla />
		<TomaLondres />
		<TomaOficina />
		<TomaMorgue />
		<TomaCalendario />
		<TomaMapa hasta={finMapa} salida={salidaMapa} />
	</>
);

/** Efectos de sonido de la muestra: [archivo, cuadro, volumen] */
export const SONIDOS_GANCHO: [string, number, number][] = [
	['whoosh', CORTES.batalla - 5, 0.55],
	['boom', CORTES.batalla + 3, 0.38],
	['boom', CORTES.batalla + 17, 0.28],
	['boom', CORTES.batalla + 29, 0.24],
	['whoosh', CORTES.londres - 5, 0.55],
	['whoosh', CORTES.oficina - 5, 0.45],
	['ding', M.idea + 2, 0.4],
	['whoosh', CORTES.morgue - 5, 0.55],
	['moscas', CORTES.morgue, 0.18],
	['dundun', M.muerto - 2, 0.6],
	['whoosh', CORTES.calendario - 5, 0.55],
	['hoja', CORTES.calendario + 4, 0.5],
	['hoja', M.n1943 - 4, 0.5],
	['hoja', M.n1943 - 1, 0.5],
	['sello', M.n1943 + 2, 0.7],
	['whoosh', CORTES.mapa - 5, 0.55],
	['pop', M.sicilia - 2, 0.5],
];

import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {Destello, Etiqueta, Explosion, Flecha, Moscas} from '../componentes/Efectos';
import {
	CHOLMONDELEY,
	ESPIA_MUERTO,
	HITLER,
	MONTAGU,
	OFICIAL_ALEMAN,
	OFICIAL_ALEMAN_2,
	Personaje,
	SOLDADO,
	SOLDADO_ALEMAN,
} from '../componentes/Personaje';
import {EnMundo, Toma, Transicion} from '../componentes/Toma';
import {
	Bocadillo,
	Brillos,
	Carne,
	Confeti,
	Documento,
	Fundido,
	Icono,
	Letrero,
	Lupa,
	Maletin,
	Olas,
	Puf,
	Rayos,
	Retrato,
	Sello,
	Tiza,
} from '../componentes/Utileria';
import {finFrase, inicioFrase, palabra} from '../tiempos';

/*
 * Del "El problema era que..." hasta el final.
 * Cada toma usa cuadros GLOBALES; los cortes caen 3 cuadros antes de la palabra que los motiva.
 */

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const antes = (n: number) => n - 3;

/* Palabras clave */
const W = {
	sospechaban: palabra(4, 'sospechaban'),
	plan: palabra(4, 'plan'),
	distraerlos: palabra(5, 'distraerlos'),
	mucho: palabra(6, 'mucho'),
	conseguir: palabra(7, 'conseguir'),
	cadaver: palabra(7, 'cadáver'),
	uniforme: palabra(7, 'uniforme'),
	militar: palabra(7, 'militar'),
	identidad: palabra(7, 'identidad'),
	documentos: palabra(7, 'documentos'),
	falsos: palabra(7, 'falsos'),
	crearon: palabra(8, 'crearon'),
	espia: palabra(8, 'espía'),
	hablar: palabra(8, 'hablar'),
	traicionar: palabra(8, 'traicionar'),
	nadie: palabra(8, 'nadie'),
	mision: palabra(9, 'misión'),
	importante: palabra(9, 'importante'),
	william: palabra(10, 'William'),
	espana: palabra(10, 'España'),
	maletin: palabra(10, 'maletín'),
	falsa: palabra(10, 'falsa'),
	encontraron: palabra(11, 'encontraron'),
	documentos2: palabra(11, 'documentos'),
	tragaron: palabra(12, 'tragaron'),
	cuento: palabra(12, 'cuento'),
	reforzo: palabra(13, 'reforzó'),
	grecia: palabra(13, 'Grecia'),
	cerdena: palabra(13, 'Cerdeña'),
	aliados: palabra(13, 'aliados'),
	sicilia: palabra(13, 'Sicilia'),
	si: palabra(14, 'Sí'),
	muerto: palabra(14, 'muerto'),
	enganar: palabra(14, 'engañar'),
	mundo: palabra(14, 'mundo'),
	verdad: palabra(15, 'verdad'),
	cumplio: palabra(16, 'cumplió'),
	decir: palabra(16, 'decir'),
	palabra: palabra(16, 'palabra'),
};

export const FIN_VIDEO = finFrase(16) + 30;

type P = {d: number; h: number; e: Transicion; s: Transicion};

/* ---------------- CONTEXTO ---------------- */

const Costa: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const gira = f > d + 16;
	return (
		<Toma fondo="costa.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.24], x: [40, -40]}}>
			<EnMundo x={640} y={1820} alto={1000} voltear={gira}>
				<Personaje diseno={SOLDADO_ALEMAN} ojos={gira ? 'entrecerrados' : 'mirandoLado'} cejas="enojado" boca="mueca" cabeza={gira ? 4 : -6} />
			</EnMundo>
			<Icono tipo="interrogacion" x={880} y={640} desde={d + 14} tam={220} />
		</Toma>
	);
};

const Cuartel: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sospecha = f >= W.sospechaban;
	const pulso = 1 + 0.12 * Math.sin((f - W.plan) / 2.5);
	return (
		<Toma fondo="cuartel.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.18], y: [40, 70]}} golpes={[[W.plan, 0.05]]}>
			{f >= W.plan && (
				<div style={{position: 'absolute', left: 270 - 70, top: 540 - 60, width: 140, height: 120, border: '12px solid #e3262e', borderRadius: '50%', transform: `scale(${pulso})`}} />
			)}
			<Lupa x={330} y={560} tam={260} desde={W.sospechaban - 2} radio={45} />
			<Etiqueta x={320} y={450} texto="¿SICILIA?" desde={W.plan} tam={68} />
			<EnMundo x={300} y={1870} alto={1050}>
				<Personaje diseno={OFICIAL_ALEMAN} ojos={sospecha ? 'entrecerrados' : 'normal'} cejas={sospecha ? 'enojado' : 'neutral'} boca={sospecha ? 'mueca' : 'seria'} cabeza={sospecha ? 6 : 0} />
			</EnMundo>
			<EnMundo x={790} y={1880} alto={1080}>
				<Personaje diseno={OFICIAL_ALEMAN_2} semilla={3} ojos={sospecha ? 'entrecerrados' : 'mirandoLado'} cejas={sospecha ? 'enojado' : 'neutral'} boca="seria" cabeza={sospecha ? -6 : 0} brazoIzq={sospecha ? 40 : 12} codoIzq={sospecha ? -90 : 0} brazoDer={sospecha ? 40 : 12} codoDer={sospecha ? -90 : 0} />
			</EnMundo>
		</Toma>
	);
};

const Pizarra: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma fondo="pizarra.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.08, 1.2], x: [30, -20]}}>
			<Tiza x={80} y={210} texto="PLAN:" desde={d + 3} tam={96} />
			<Tiza x={80} y={360} texto="DISTRAER A" desde={W.distraerlos - 18} tam={84} />
			<Tiza x={80} y={490} texto="LOS ALEMANES" desde={W.distraerlos - 2} tam={84} />
			{f >= W.distraerlos + 8 && <Tiza x={80} y={600} texto="━━━━━━━━━" desde={W.distraerlos + 8} tam={60} duracion={8} rot={-2} />}
			<EnMundo x={290} y={1820} alto={980}>
				<Personaje diseno={CHOLMONDELEY} semilla={2} ojos="feliz" cejas="arrogante" boca="sonrisa" cabeza={Math.sin(f / 4) * 6} />
			</EnMundo>
			<EnMundo x={800} y={1880} alto={1050}>
				<Personaje diseno={MONTAGU} hablando={f < h - 6} cejas="arrogante" ojos="normal" brazoIzq={125} codoIzq={-25} cabeza={-5} />
			</EnMundo>
		</Toma>
	);
};

const MuchoPrimerPlano: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const ya = f >= W.mucho;
	return (
		<Toma fondo="oficina.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.2, 1.3], x: [40, 40]}} golpes={[[W.mucho, 0.14]]}>
			<EnMundo x={540} y={2180} alto={1700}>
				<Personaje diseno={MONTAGU} ojos="entrecerrados" cejas={ya ? 'arrogante' : 'neutral'} boca="seria" cabeza={ya ? -4 : 0} />
			</EnMundo>
		</Toma>
	);
};

/* ---------------- DESARROLLO ---------------- */

const Cadaver: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sabana = interpolate(f, [W.conseguir + 2, W.cadaver - 1], [0, 1000], {...clamp, easing: Easing.in(Easing.quad)});
	const visto = f >= W.cadaver - 2;
	return (
		<Toma fondo="morgue.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.2]}} golpes={[[W.cadaver, 0.1]]} tinte="rgba(60,200,190,0.3)">
			<EnMundo x={850} y={800} alto={700} rot={-90}>
				<Personaje diseno={ESPIA_MUERTO} ojos="x" cejas="ninguna" boca="lengua" respira={false} parpadea={false} sombra={false} />
			</EnMundo>
			{/* sábana que se retira */}
			<div style={{position: 'absolute', left: 110 + sabana, top: 600, width: 800, height: 390, background: '#f4f7f6', border: '10px solid #1b1b1f', borderRadius: '120px 60px 40px 40px', transform: `rotate(${sabana * 0.02}deg)`}} />
			{visto && <Moscas x={330} y={700} radio={150} n={3} />}
			<EnMundo x={170} y={1770} alto={820}>
				<Personaje diseno={MONTAGU} ojos={visto ? 'feliz' : 'grandes'} cejas={visto ? 'arrogante' : 'sorprendido'} boca={visto ? 'sonrisaGrande' : 'o'} />
			</EnMundo>
			<EnMundo x={920} y={1780} alto={850}>
				<Personaje diseno={CHOLMONDELEY} semilla={2} ojos={visto ? 'feliz' : 'normal'} cejas="arrogante" boca={visto ? 'sonrisaGrande' : 'picara'} brazoIzq={visto ? 100 : 60} codoIzq={-10} />
			</EnMundo>
		</Toma>
	);
};

const Uniforme: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const vestido = f >= W.uniforme;
	const fiesta = f >= W.militar;
	return (
		<Toma fondo="sastreria.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.2], y: [0, -20]}} golpes={[[W.uniforme, 0.06]]}>
			<EnMundo x={600} y={1840} alto={1060}>
				<Personaje diseno={ESPIA_MUERTO} chaqueta={vestido ? undefined : '#f2f2f2'} acc={{}} ojos="x" cejas="ninguna" boca="lengua" respira={false} parpadea={false} cabeza={-10} />
			</EnMundo>
			<Puf x={600} y={1300} desde={W.uniforme - 2} tam={760} />
			<Brillos x={600} y={1250} desde={W.uniforme + 2} radio={380} n={9} />
			<EnMundo x={210} y={1800} alto={940}>
				<Personaje diseno={CHOLMONDELEY} semilla={2} ojos={fiesta ? 'feliz' : 'normal'} cejas="arrogante" boca={fiesta ? 'sonrisaGrande' : 'sonrisa'} brazoIzq={fiesta ? 150 : 20} brazoDer={fiesta ? 150 : 20} />
			</EnMundo>
		</Toma>
	);
};

const Identidad: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="escritorio.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.14], r: [-2, 1]}}>
		<Carne x={540} y={760} ancho={840} desde={d + 2} />
		<Sello x={720} y={930} texto="APROBADO" color="#1f9d48" desde={W.identidad} tam={86} rot={-14} />
		<Icono tipo="carta" x={240} y={1600} desde={d + 8} tam={240} rot={-10} />
		<Icono tipo="entrada" x={820} y={1620} desde={d + 13} tam={270} rot={12} />
		<Icono tipo="foto" x={530} y={1700} desde={d + 18} tam={220} rot={4} />
	</Toma>
);

const Documentos: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const guino = f >= W.falsos;
	return (
		<Toma fondo="oficina.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.16], x: [-30, 30]}} golpes={[[W.falsos, 0.06]]}>
			<Documento x={470} y={560} desde={W.documentos - 2} rot={-8} />
			<Documento x={640} y={600} desde={W.documentos + 6} rot={7} />
			<Sello x={560} y={640} texto="FALSOS" desde={W.falsos} tam={120} />
			<EnMundo x={270} y={1880} alto={1040}>
				<Personaje diseno={MONTAGU} ojos={guino ? 'entrecerrados' : 'feliz'} cejas="arrogante" boca={guino ? 'picara' : 'sonrisa'} brazoDer={100} codoDer={-20} />
			</EnMundo>
			<EnMundo x={800} y={1860} alto={1040}>
				<Personaje diseno={ESPIA_MUERTO} ojos="x" cejas="ninguna" boca="lengua" respira={false} parpadea={false} cabeza={-10} />
			</EnMundo>
		</Toma>
	);
};

const EspiaNoir: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const gafas = f >= W.crearon - 2;
	const caida = interpolate(f, [W.crearon - 6, W.crearon - 2], [-260, 0], clamp);
	return (
		<Toma fondo="callejon.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.3, 1.1], y: [80, 0], r: [3, 0], curva: 'salida'}} golpes={[[W.espia, 0.06]]}>
			<EnMundo x={540} y={1880} alto={1200}>
				<Personaje diseno={ESPIA_MUERTO} ojos="x" cejas="ninguna" boca={gafas ? 'picara' : 'lengua'} acc={{gafas}} respira={false} parpadea={false} />
			</EnMundo>
			{!gafas && f >= W.crearon - 6 && (
				<div style={{position: 'absolute', left: 540 - 150, top: 1007 + caida, width: 300, height: 70, background: '#111', borderRadius: 30, border: '8px solid #000'}} />
			)}
			<Moscas x={540} y={900} radio={240} n={2} />
		</Toma>
	);
};

const NoHabla: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma fondo="interrogatorio.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.12]}}>
			<EnMundo x={300} y={1860} alto={1040}>
				<Personaje diseno={OFICIAL_ALEMAN} hablando={f < W.hablar} cejas="enojado" boca="abierta" brazoDer={105} codoDer={-15} />
			</EnMundo>
			<EnMundo x={790} y={1850} alto={1020}>
				<Personaje diseno={ESPIA_MUERTO} ojos="x" cejas="ninguna" boca="lengua" respira={false} parpadea={false} cabeza={-12} />
			</EnMundo>
			<Bocadillo x={320} y={700} texto="¡HABLE!" desde={d + 3} cola="izq" ancho={430} />
			<Bocadillo x={790} y={700} texto="..." desde={W.hablar} cola="der" ancho={260} />
			<Moscas x={790} y={1040} radio={180} n={2} />
		</Toma>
	);
};

const NoTraiciona: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const harto = f >= W.nadie;
	return (
		<Toma fondo="interrogatorio.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.28, 1.36], x: [-30, -60], y: [-20, -30]}} golpes={[[W.nadie, 0.07]]}>
			<EnMundo x={300} y={1860} alto={1040}>
				<Personaje diseno={OFICIAL_ALEMAN} ojos={harto ? 'normal' : 'feliz'} cejas={harto ? 'enojado' : 'arrogante'} boca={harto ? 'dientes' : 'sonrisaGrande'} brazoDer={95} codoDer={-10} />
			</EnMundo>
			<EnMundo x={790} y={1850} alto={1020}>
				<Personaje diseno={ESPIA_MUERTO} ojos="x" cejas="ninguna" boca="lengua" respira={false} parpadea={false} cabeza={-12} />
			</EnMundo>
			<Icono tipo="dinero" x={540} y={1040} desde={W.traicionar - 12} tam={260} />
			<Icono tipo="enojo" x={210} y={820} desde={W.nadie + 2} tam={150} />
			<Moscas x={790} y={1040} radio={180} n={3} />
		</Toma>
	);
};

const Mision: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const brazo = interpolate(f, [W.mision - 2, W.mision + 6], [8, 160], {...clamp, easing: Easing.out(Easing.back(2))});
	const viva = f >= W.importante;
	return (
		<Toma fondo="muelle.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.16], x: [20, -20], y: [-40, -60]}} golpes={[[W.importante, 0.07]]}>
			<EnMundo x={190} y={1790} alto={860}>
				<Personaje diseno={MONTAGU} ojos={viva ? 'feliz' : 'normal'} cejas="arrogante" boca={viva ? 'sonrisaGrande' : 'sonrisa'} brazoIzq={viva ? 150 : 15} brazoDer={viva ? 150 : 15} />
			</EnMundo>
			<EnMundo x={540} y={1770} alto={880}>
				<Personaje diseno={ESPIA_MUERTO} ojos="x" cejas="ninguna" boca="lengua" respira={false} parpadea={false} cabeza={-10} brazoDer={brazo} codoDer={-10} />
			</EnMundo>
			<EnMundo x={895} y={1790} alto={870}>
				<Personaje diseno={CHOLMONDELEY} semilla={2} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={f >= W.mision - 2 ? 100 : 20} codoIzq={-20} />
			</EnMundo>
			<Brillos x={540} y={1060} desde={W.importante} radio={330} />
		</Toma>
	);
};

/* ---------------- GIRO ---------------- */

const Nombre: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="galeria.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.14], y: [0, 30]}} golpes={[[W.william, 0.05]]}>
		<Retrato x={540} y={240} ancho={600} desde={d + 2} placaDesde={W.william} />
		<Brillos x={540} y={600} desde={W.william + 1} radio={420} n={9} />
	</Toma>
);

const MarNoche: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const deriva = interpolate(f, [d, h], [0, -160], clamp);
	return (
		<Toma fondo="mar_noche.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.18], y: [0, -20]}}>
			<EnMundo x={880 + deriva} y={1590 + Math.sin(f / 8) * 14} alto={700} rot={-90 + Math.sin(f / 11) * 5}>
				<Personaje diseno={ESPIA_MUERTO} ojos="x" cejas="ninguna" boca="lengua" respira={false} parpadea={false} sombra={false} acc={{salvavidas: true}} />
			</EnMundo>
			<Olas y={1600} />
			<Etiqueta x={760} y={520} texto="ESPAÑA" desde={W.espana - 2} tam={62} />
		</Toma>
	);
};

const Playa: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="playa.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.18], y: [0, 40]}} golpes={[[W.falsa, 0.06]]}>
		<Maletin x={560} y={980} ancho={720} abre={W.maletin} />
		<Sello x={560} y={1080} texto="FALSO" desde={W.falsa} tam={140} />
	</Toma>
);

const Encontraron: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const hallazgo = f >= W.encontraron;
	const convencidos = f >= W.documentos2 + 14;
	const cara = convencidos
		? ({ojos: 'feliz', cejas: 'arrogante', boca: 'sonrisaGrande'} as const)
		: hallazgo
			? ({ojos: 'grandes', cejas: 'sorprendido', boca: 'o'} as const)
			: ({ojos: 'normal', cejas: 'neutral', boca: 'seria'} as const);
	return (
		<Toma fondo="oficina_espana.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.18], x: [20, -20]}}>
			<Documento x={560} y={700} ancho={380} desde={W.encontraron - 2} rot={4} />
			<Lupa x={560} y={700} tam={320} desde={W.documentos2 - 2} radio={50} />
			<EnMundo x={290} y={1880} alto={1050}>
				<Personaje diseno={OFICIAL_ALEMAN} {...cara} />
			</EnMundo>
			<EnMundo x={800} y={1880} alto={1060}>
				<Personaje diseno={OFICIAL_ALEMAN_2} semilla={3} {...cara} />
			</EnMundo>
			<Icono tipo="exclamacion" x={290} y={760} desde={W.encontraron + 1} tam={170} hasta={W.documentos2 + 14} />
			<Icono tipo="exclamacion" x={800} y={760} desde={W.encontraron + 4} tam={170} hasta={W.documentos2 + 14} />
		</Toma>
	);
};

const SeLoTraga: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const p = interpolate(f, [W.tragaron - 2, W.cuento - 1], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
	const tragado = f >= W.cuento;
	const boca = 2150 - 1600 + (282 / 760) * 1600;
	return (
		<Toma fondo="bunker.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.12, 1.2], y: [-40, -40]}} golpes={[[W.cuento, 0.06]]}>
			<EnMundo x={540} y={2150} alto={1600}>
				<Personaje diseno={HITLER} ojos={tragado ? 'feliz' : 'grandes'} cejas={tragado ? 'arrogante' : 'sorprendido'} boca={tragado ? 'sonrisa' : f >= W.tragaron - 4 ? 'abierta' : 'sonrisaGrande'} />
			</EnMundo>
			{!tragado && (
				<div style={{position: 'absolute', left: interpolate(p, [0, 1], [130, 540]) - 160, top: interpolate(p, [0, 1], [1500, boca]) - 125, width: 320, height: 250, transform: `scale(${1 - p * 0.85}) rotate(${p * 540}deg)`}}>
					<Icono tipo="libro" x={160} y={125} desde={d} tam={320} />
				</div>
			)}
			<Bocadillo x={820} y={560} texto="¡ÑAM!" desde={W.cuento + 2} cola="izq" ancho={360} />
		</Toma>
	);
};

/* ---------------- DESENLACE ---------------- */

const Diorama: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="diorama.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.16], y: [20, 0]}}>
		<Flecha d="M 600 300 Q 820 470 870 820" desde={W.reforzo - 2} color="#8d9474" duracion={16} grosor={28} />
		<Flecha d="M 560 320 Q 420 560 455 850" desde={W.reforzo + 6} color="#8d9474" duracion={16} grosor={28} />
		<Etiqueta x={790} y={760} texto="GRECIA" desde={W.grecia} tam={58} />
		<Etiqueta x={430} y={800} texto="CERDEÑA" desde={W.cerdena} tam={58} />
		<EnMundo x={200} y={2020} alto={760}>
			<Personaje diseno={HITLER} ojos="feliz" cejas="arrogante" boca="sonrisa" brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
		</EnMundo>
	</Toma>
);

const Desembarco: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const t = f - d;
	const soldados = [
		{x0: 320, v: 9, y: 1480, alto: 460, sem: 7},
		{x0: -200, v: 11, y: 1580, alto: 580, sem: 4},
		{x0: 60, v: 10, y: 1690, alto: 700, sem: 0},
	];
	return (
		<Toma fondo="desembarco.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.2], x: [30, -30]}} sacudida={(g) => (g >= d + 8 ? 6 * Math.exp(-(g - d - 8) / 6) : 0)}>
			<Explosion x={880} y={420} desde={d + 8} tam={360} />
			<Explosion x={300} y={360} desde={d + 40} tam={300} />
			{soldados.map((so, i) => (
				<EnMundo key={i} x={so.x0 + so.v * t} y={so.y} alto={so.alto}>
					<Personaje diseno={SOLDADO} semilla={so.sem} caminando ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={150} brazoDer={150} codoIzq={-15} codoDer={-15} />
				</EnMundo>
			))}
			<Etiqueta x={640} y={430} texto="SICILIA" desde={W.sicilia - 2} tam={62} />
		</Toma>
	);
};

const Medalla: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const medalla = f >= W.si + 4;
	const aplauso = Math.floor(f / 3) % 2 === 0;
	return (
		<Toma fondo="ceremonia.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.08, 1.2], y: [-30, -30]}} golpes={[[W.si + 4, 0.05], [W.muerto, 0.06]]}>
			<EnMundo x={540} y={1800} alto={1060}>
				<Personaje diseno={ESPIA_MUERTO} acc={{medalla}} ojos="x" cejas="ninguna" boca="lengua" respira={false} parpadea={false} cabeza={f >= W.muerto ? -18 : -8} />
			</EnMundo>
			<Brillos x={450} y={1220} desde={W.si + 5} radio={240} />
			<EnMundo x={200} y={1800} alto={920}>
				<Personaje diseno={MONTAGU} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoDer={medalla ? 30 : 75} codoDer={medalla ? 0 : 20} />
			</EnMundo>
			<EnMundo x={880} y={1800} alto={940}>
				<Personaje diseno={CHOLMONDELEY} semilla={2} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={aplauso ? 45 : 75} codoIzq={aplauso ? -80 : -40} brazoDer={aplauso ? 45 : 75} codoDer={aplauso ? -80 : -40} />
			</EnMundo>
			{f >= W.muerto && <Moscas x={540} y={960} radio={200} n={3} />}
			<Confeti desde={W.si + 4} />
		</Toma>
	);
};

const Cruce: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const t = f - d;
	return (
		<Toma fondo="cruce.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.15], x: [0, -30]}}>
			<Letrero x={560} y={420} desde={d + 2} giro={f >= W.enganar ? Math.sin((f - W.enganar) / 2) * 6 : 0} tablas={[{texto: 'GRECIA', dir: 'der'}, {texto: 'SICILIA', dir: 'izq', color: '#f3b3a8'}]} />
			{[0, 1, 2, 3].map((i) => (
				<EnMundo key={i} x={140 - i * 240 + t * 13} y={1500 + i * 60} alto={470 + i * 45}>
					<Personaje diseno={SOLDADO_ALEMAN} semilla={i * 5} caminando ojos="feliz" cejas="arrogante" boca="sonrisa" />
				</EnMundo>
			))}
		</Toma>
	);
};

const HitlerConfundido: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma fondo="bunker.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.18], x: [-20, 20]}} golpes={[[W.mundo, 0.08]]}>
			<EnMundo x={540} y={1960} alto={1300}>
				<Personaje diseno={HITLER} ojos="grandes" cejas="preocupado" boca="mueca" cabeza={Math.sin(f / 5) * 8} brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
			</EnMundo>
			<Icono tipo="interrogacion" x={210} y={560} desde={d + 4} tam={200} rot={-12} />
			<Icono tipo="interrogacion" x={870} y={500} desde={d + 12} tam={230} rot={10} />
			<Icono tipo="interrogacion" x={540} y={340} desde={W.mundo - 2} tam={260} />
		</Toma>
	);
};

const Veredicto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const gana = f >= W.verdad;
	return (
	<Toma
		fondo="tribunal.jpg"
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1.05, 1.16]}}
		golpes={[[W.verdad, 0.08]]}
		encima={<Destello desde={W.verdad} color="#7dff9a" fuerza={0.5} duracion={12} />}
	>
		<Rayos x={540} y={700} opacidad={0.22} />
		<EnMundo x={190} y={1790} alto={860}>
			<Personaje diseno={MONTAGU} ojos={gana ? 'feliz' : 'normal'} cejas="arrogante" boca={gana ? 'sonrisaGrande' : 'seria'} brazoIzq={gana ? 150 : 15} brazoDer={gana ? 150 : 15} />
		</EnMundo>
		<EnMundo x={540} y={1770} alto={880}>
			<Personaje diseno={ESPIA_MUERTO} acc={{medalla: true}} ojos="x" cejas="ninguna" boca={gana ? 'sonrisa' : 'lengua'} respira={false} parpadea={false} cabeza={-8} />
		</EnMundo>
		<EnMundo x={895} y={1790} alto={870}>
			<Personaje diseno={CHOLMONDELEY} semilla={2} ojos={gana ? 'feliz' : 'normal'} cejas="arrogante" boca={gana ? 'sonrisaGrande' : 'seria'} brazoIzq={gana ? 150 : 15} brazoDer={gana ? 150 : 15} />
		</EnMundo>
		<Sello x={540} y={560} texto="VERDAD" icono="✔" color="#1f9d48" desde={W.verdad} tam={118} rot={-8} />
		<Confeti desde={W.verdad + 2} n={50} />
	</Toma>
	);
};

/* ---------------- CIERRE ---------------- */

const Cielo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma fondo="cielo.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.16], y: [0, -20]}}>
			<Rayos x={540} y={500} opacidad={0.18} />
			<EnMundo x={540} y={1640 + Math.sin(f / 10) * 18} alto={1000}>
				<Personaje diseno={ESPIA_MUERTO} acc={{aureola: true, medalla: true}} ojos="x" cejas="ninguna" boca="sonrisa" parpadea={false} brazoDer={120 + Math.sin(f / 3) * 25} codoDer={-10} />
			</EnMundo>
			<Brillos x={540} y={1000} desde={W.cumplio} radio={380} n={9} />
		</Toma>
	);
};

const Final: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const guino = f >= finFrase(16) - 2;
	return (
		<Toma fondo="cielo.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.18, 1.3], y: [-60, -60]}} golpes={[[finFrase(16) - 2, 0.06]]}>
			<EnMundo x={540} y={2160} alto={1700}>
				<Personaje diseno={ESPIA_MUERTO} acc={{aureola: true}} ojos={guino ? 'guinoX' : 'x'} cejas="ninguna" boca={guino ? 'picara' : 'seria'} respira={false} parpadea={false} />
			</EnMundo>
			<Bocadillo x={840} y={430} texto="..." desde={W.decir} hasta={guino ? 0 : 99999} cola="izq" ancho={260} />
			<Brillos x={720} y={980} desde={finFrase(16) - 1} radio={200} n={6} />
			<Fundido desde={h - 14} duracion={14} />
		</Toma>
	);
};

/* ---------------- Montaje ---------------- */

type Plano = {desde: number; Comp: React.FC<P>; entrada: Transicion};

export const INICIO_DESARROLLO = antes(inicioFrase(4));

const PLANOS: Plano[] = [
	{desde: INICIO_DESARROLLO, Comp: Costa, entrada: 'latigoDer'},
	{desde: antes(palabra(4, 'alemanes')), Comp: Cuartel, entrada: 'latigoIzq'},
	{desde: antes(palabra(5, 'Así')), Comp: Pizarra, entrada: 'latigoDer'},
	{desde: antes(palabra(6, 'Y')), Comp: MuchoPrimerPlano, entrada: 'zoom'},
	{desde: antes(palabra(7, 'Su')), Comp: Cadaver, entrada: 'latigoArriba'},
	{desde: antes(palabra(7, 'ponerle')), Comp: Uniforme, entrada: 'latigoDer'},
	{desde: antes(palabra(7, 'inventarle')), Comp: Identidad, entrada: 'zoom'},
	{desde: antes(palabra(7, 'y')), Comp: Documentos, entrada: 'latigoIzq'},
	{desde: antes(palabra(8, 'Básicamente')), Comp: EspiaNoir, entrada: 'latigoDer'},
	{desde: antes(palabra(8, 'que')), Comp: NoHabla, entrada: 'latigoIzq'},
	{desde: antes(palabra(8, 'no', 2)), Comp: NoTraiciona, entrada: 'corte'},
	{desde: antes(palabra(9, 'y')), Comp: Mision, entrada: 'latigoArriba'},
	{desde: antes(palabra(10, 'Lo')), Comp: Nombre, entrada: 'latigoDer'},
	{desde: antes(palabra(10, 'y')), Comp: MarNoche, entrada: 'latigoIzq'},
	{desde: antes(palabra(10, 'con')), Comp: Playa, entrada: 'latigoArriba'},
	{desde: antes(palabra(11, 'Los')), Comp: Encontraron, entrada: 'latigoDer'},
	{desde: antes(palabra(12, 'y')), Comp: SeLoTraga, entrada: 'zoom'},
	{desde: antes(palabra(13, 'Hitler')), Comp: Diorama, entrada: 'latigoIzq'},
	{desde: antes(palabra(13, 'mientras')), Comp: Desembarco, entrada: 'latigoDer'},
	{desde: antes(palabra(14, 'Sí')), Comp: Medalla, entrada: 'latigoArriba'},
	{desde: antes(palabra(14, 'ayudó')), Comp: Cruce, entrada: 'latigoIzq'},
	{desde: antes(palabra(14, 'más')), Comp: HitlerConfundido, entrada: 'zoom'},
	{desde: antes(palabra(15, 'Veredicto')), Comp: Veredicto, entrada: 'latigoDer'},
	{desde: antes(palabra(16, 'Y')), Comp: Cielo, entrada: 'latigoArriba'},
	{desde: antes(palabra(16, 'sin')), Comp: Final, entrada: 'zoom'},
];

export const ENTRADA_DESARROLLO = PLANOS[0].entrada;

export const Desarrollo: React.FC = () => (
	<>
		{PLANOS.map((p, i) => {
			const sig = PLANOS[i + 1];
			return <p.Comp key={i} d={p.desde} h={sig ? sig.desde : FIN_VIDEO} e={p.entrada} s={sig ? sig.entrada : 'corte'} />;
		})}
	</>
);

/** Efectos de sonido: [archivo, cuadro, volumen]. Un "whoosh" en cada latigazo/zoom. */
export const SONIDOS_DESARROLLO: [string, number, number][] = [
	...PLANOS.filter((p) => p.entrada !== 'corte').map((p) => ['whoosh', p.desde - 5, 0.5] as [string, number, number]),
	['pop', PLANOS[0].desde + 14, 0.4],
	['pop', W.plan, 0.45],
	['hoja', W.distraerlos - 18, 0.35],
	['hoja', W.distraerlos - 2, 0.35],
	['pop', W.mucho, 0.5],
	['whoosh', W.conseguir + 2, 0.4],
	['dundun', W.cadaver - 2, 0.4],
	['moscas', W.cadaver, 0.14],
	['pop', W.uniforme - 2, 0.55],
	['ding', W.uniforme + 2, 0.3],
	['pop', PLANOS[6].desde + 8, 0.35],
	['pop', PLANOS[6].desde + 13, 0.35],
	['pop', PLANOS[6].desde + 18, 0.35],
	['sello', W.identidad, 0.6],
	['hoja', W.documentos - 2, 0.45],
	['hoja', W.documentos + 6, 0.45],
	['sello', W.falsos, 0.65],
	['whoosh', W.crearon - 6, 0.35],
	['pop', W.crearon - 2, 0.5],
	['pop', PLANOS[9].desde + 3, 0.4],
	['pop', W.hablar, 0.4],
	['moscas', W.hablar, 0.12],
	['pop', W.traicionar - 12, 0.45],
	['dundun', W.nadie, 0.35],
	['pop', W.mision - 2, 0.45],
	['ding', W.importante, 0.35],
	['pop', W.william, 0.5],
	['ding', W.william + 1, 0.3],
	['pop', W.espana - 2, 0.45],
	['hoja', W.maletin, 0.5],
	['whoosh', W.maletin + 6, 0.35],
	['sello', W.falsa, 0.65],
	['pop', W.encontraron + 1, 0.45],
	['hoja', W.documentos2 - 2, 0.4],
	['whoosh', W.tragaron - 2, 0.4],
	['pop', W.cuento, 0.6],
	['pop', W.grecia, 0.45],
	['pop', W.cerdena, 0.45],
	['boom', PLANOS[18].desde + 8, 0.22],
	['boom', PLANOS[18].desde + 40, 0.18],
	['pop', W.sicilia - 2, 0.45],
	['ding', W.si + 4, 0.45],
	['pop', W.si + 4, 0.4],
	['moscas', W.muerto, 0.12],
	['pop', W.enganar, 0.3],
	['pop', PLANOS[21].desde + 4, 0.4],
	['pop', PLANOS[21].desde + 12, 0.4],
	['pop', W.mundo - 2, 0.45],
	['sello', W.verdad, 0.75],
	['ding', W.verdad + 1, 0.45],
	['ding', W.cumplio, 0.3],
	['pop', W.decir, 0.35],
	['ding', finFrase(16) - 1, 0.4],
];

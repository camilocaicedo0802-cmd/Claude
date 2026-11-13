import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {Destello, Etiqueta} from '../componentes/Efectos';
import {ColumnasCayendo, Desconocido, LluviaMonedas, MarDelante, OlaObediente, Pergamino, TituloDorado, Tridente} from '../componentes/Atlantes';
import {ATLANTE, CIUDADANA, Personaje, PLATON, POSEIDON, REY} from '../componentes/Personaje';
import {EnMundo, Toma, Transicion} from '../componentes/Toma';
import {Brillos, Confeti, Fundido, Icono, Olas, Rayos, Sello} from '../componentes/Utileria';
import {EscAtenas, EscCanales, EscCielo, EscCiudadAerea, EscLibro, EscNoche, EscPalacio, EscPlaza, EscProfundo, EscSubmarino, EscTerraza, EscTesoro, EscTsunami} from '../escenarios/Escenarios';
import {TITULAR} from '../fuentes';
import {finFrase, hablandoEn, palabra} from '../tiempos';

/* La Atlántida contada por uno de sus habitantes. Cuadros GLOBALES. */

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const antes = (n: number) => n - 3;
const TINTA = '#1b1b1f';

const W = {
	oro: palabra(0, 'oro'),
	canales: palabra(0, 'canales'),
	oceano: palabra(0, 'océano'),
	obedecernos: palabra(0, 'obedecernos'),
	paraiso: palabra(2, 'paraíso'),
	gigantescos: palabra(3, 'gigantescos'),
	riquezas: palabra(3, 'riquezas'),
	circulos: palabra(3, 'círculos'),
	tierra: palabra(3, 'tierra'),
	agua: palabra(3, 'agua'),
	poderosos: palabra(4, 'poderosos'),
	detenernos: palabra(4, 'detenernos'),
	error: palabra(5, 'error'),
	admiracion: palabra(6, 'admiración'),
	castigarnos: palabra(7, 'castigarnos'),
	tembló: palabra(8, 'tembló'),
	olas: palabra(9, 'olas'),
	correr: palabra(10, 'correr'),
	noche: palabra(11, 'noche'),
	existir: palabra(11, 'existir'),
	nombre: palabra(12, 'nombre'),
	atlantida: palabra(13, 'Atlántida'),
	escritos: palabra(14, 'escritos'),
	platon: palabra(14, 'Platón'),
	dosmil: palabra(14, '2.000'),
	concluyentes: palabra(15, 'concluyentes'),
	leyenda: palabra(17, 'leyenda'),
	mito: palabra(19, 'MITO'),
};

export const FIN_VIDEO = finFrase(19) + 32;

type P = {d: number; h: number; e: Transicion; s: Transicion};

/** El narrador con la boca sincronizada a la voz. */
const Narrador: React.FC<Omit<React.ComponentProps<typeof Personaje>, 'diseno'>> = (props) => {
	const f = useCurrentFrame();
	return <Personaje diseno={ATLANTE} hablando={hablandoEn(f)} {...props} />;
};

/* ------------------------------ GANCHO ------------------------------ */

const Presentacion: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscCanales />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.12, 1.22], y: [-40, -60]}}>
		<EnMundo x={540} y={2060} alto={1450}>
			<Narrador ojos="normal" cejas="arrogante" boca="sonrisa" brazoDer={70} codoDer={-40} />
		</EnMundo>
	</Toma>
);

const TemplosDeOro: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const brillo = interpolate(f, [W.oro, W.oro + 12], [0, 1], clamp);
	return (
		<Toma escena={<EscCanales templo={brillo} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.7, 1.9], y: [560, 640]}} golpes={[[W.oro, 0.05]]}>
			<Rayos x={540} y={600} color="#ffe9a0" opacidad={0.3 * brillo} />
			<Brillos x={540} y={560} desde={W.oro} radio={260} n={9} />
		</Toma>
	);
};

const Canales: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscCanales />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.25], y: [0, 120]}}>
			<EnMundo x={interpolate(f, [d, h], [170, 230])} y={1700} alto={620}>
				<Narrador caminando ojos="feliz" cejas="arrogante" boca="sonrisa" />
			</EnMundo>
		</Toma>
	);
};

const Oceano: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const manda = f >= W.obedecernos - 6;
	return (
		<Toma escena={<EscTerraza />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.14]}}>
			<OlaObediente x={600} base={1260} desde={W.obedecernos - 4} />
			<EnMundo x={250} y={1840} alto={1000}>
				<Narrador ojos={manda ? 'entrecerrados' : 'normal'} cejas="arrogante" boca="picara" brazoDer={manda ? 120 : 20} codoDer={-20} />
			</EnMundo>
			<Brillos x={600} y={900} desde={W.obedecernos + 20} radio={260} />
		</Toma>
	);
};

const Creeme: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscTerraza />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.35, 1.45], y: [-120, -120]}}>
		<EnMundo x={540} y={2200} alto={1700}>
			<Narrador ojos="entrecerrados" cejas="neutral" boca="sonrisa" cabeza={6} />
		</EnMundo>
	</Toma>
);

const Paraiso: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscTerraza />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], x: [20, -20]}}>
		<EnMundo x={300} y={1830} alto={940} rot={-4}>
			<Narrador ojos="cerrados" cejas="neutral" boca="sonrisa" brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
		</EnMundo>
		<EnMundo x={640} y={1840} alto={880}>
			<Personaje diseno={CIUDADANA} ojos="feliz" cejas="arrogante" boca="sonrisa" semilla={3} />
		</EnMundo>
		<Brillos x={540} y={1000} desde={W.paraiso} radio={420} n={10} />
	</Toma>
);

/* ------------------------------ MARAVILLA ------------------------------ */

const Palacios: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscPalacio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.3, 1.1], y: [-420, 80], curva: 'salida'}} golpes={[[W.gigantescos, 0.04]]}>
		<EnMundo x={540} y={1900} alto={340}>
			<Narrador ojos="grandes" cejas="sorprendido" boca="o" cabeza={-12} />
		</EnMundo>
	</Toma>
);

const Riquezas: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscTesoro />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.18]}}>
			<LluviaMonedas desde={W.riquezas - 4} x={540} y={1550} />
			<EnMundo x={540} y={1620 + Math.abs(Math.sin(f / 5)) * -60} alto={900}>
				<Narrador ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={150} brazoDer={150} />
			</EnMundo>
		</Toma>
	);
};

const Anillos: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const revelar = interpolate(f, [d, W.circulos + 6], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	return (
		<Toma escena={<EscCiudadAerea revelar={revelar} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.16, 1.26], r: [-3, 3]}}>
			<Etiqueta x={360} y={880} texto="TIERRA" desde={W.tierra - 1} tam={60} />
			<Etiqueta x={800} y={880} texto="AGUA" desde={W.agua - 1} tam={60} color="#bff3ff" />
		</Toma>
	);
};

const Poderosos: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscPlaza />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.16], y: [-20, -20]}} golpes={[[W.poderosos, 0.05]]}>
		<EnMundo x={540} y={1840} alto={1060}>
			<Personaje diseno={REY} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={150} brazoDer={150} />
		</EnMundo>
		<EnMundo x={170} y={1880} alto={820}>
			<Narrador ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={140} brazoDer={140} />
		</EnMundo>
		<EnMundo x={910} y={1880} alto={800}>
			<Personaje diseno={CIUDADANA} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={140} brazoDer={140} semilla={3} />
		</EnMundo>
		<Cartel x={540} y={300} texto="¡INVENCIBLES!" desde={W.poderosos} />
	</Toma>
);

const Detenernos: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscPlaza />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.2, 1.3], y: [-80, -80]}}>
		<EnMundo x={540} y={2150} alto={1550}>
			<Narrador ojos="entrecerrados" cejas="arrogante" boca="picara" brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
		</EnMundo>
		<Confeti desde={d} n={50} />
	</Toma>
);

const PrimerError: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscPlaza gris={1} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.25, 1.35], y: [-80, -80]}} golpes={[[W.error, 0.12]]}>
		<EnMundo x={540} y={2150} alto={1550}>
			<Narrador ojos="grandes" cejas="preocupado" boca="mueca" brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
		</EnMundo>
		<Sello x={540} y={560} texto="ERROR #1" desde={W.error} tam={110} />
	</Toma>
);

/* ------------------------------ EFECTO DOMINÓ ------------------------------ */

const Dioses: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const enojo = f >= W.admiracion + 4;
	const sube = interpolate(f, [d, d + 24], [500, 0], {...clamp, easing: Easing.out(Easing.cubic)});
	return (
		<Toma escena={<EscCielo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.12]}}>
			<EnMundo x={540} y={3150 + sube} alto={2700}>
				<Personaje diseno={POSEIDON} ojos={enojo ? 'normal' : 'feliz'} cejas={enojo ? 'enojado' : 'arrogante'} boca={enojo ? 'seria' : 'sonrisa'} sombra={false} />
			</EnMundo>
			<MarDelante y={1500} />
		</Toma>
	);
};

const Castigo: React.FC<P> = ({d, h, e, s}) => {
	const rayos = [d + 8, W.castigarnos - 2, W.castigarnos + 14];
	return (
		<Toma
			escena={<EscCielo tormenta rayos={rayos} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.1, 1.2]}}
			sacudida={(g) => rayos.reduce((a, r) => a + (g >= r ? 14 * Math.exp(-(g - r) / 6) : 0), 0)}
			golpes={[[W.castigarnos, 0.07]]}
		>
			<EnMundo x={540} y={3150} alto={2700}>
				<Personaje diseno={POSEIDON} ojos="normal" cejas="enojado" boca="dientes" sombra={false} brazoDer={0} />
			</EnMundo>
			<Tridente x={930} y={1560} alto={1250} rot={8} brilla />
			<MarDelante y={1500} tormenta />
		</Toma>
	);
};

const Temblor: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscCanales variante="temblor" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.08, 1.16], r: [-2, 2]}} sacudida={(g) => (g >= W.tembló - 2 ? 22 : 6)}>
		<ColumnasCayendo desde={W.tembló} />
		<EnMundo x={540} y={1880} alto={1000}>
			<Narrador ojos="grandes" cejas="preocupado" boca="grito" brazoIzq={150} brazoDer={150} />
		</EnMundo>
	</Toma>
);

const Olas2: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const subida = interpolate(f, [d, h], [0.1, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
	return (
		<Toma escena={<EscTsunami subida={subida} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.12]}} sacudida={(g) => interpolate(g, [d, h], [2, 12])}>
			<EnMundo x={540} y={1900} alto={560}>
				<Narrador ojos="grandes" cejas="sorprendido" boca="grito" cabeza={-10} />
			</EnMundo>
		</Toma>
	);
};

const Correr: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const nivel = interpolate(f, [d, h], [0, 420], clamp);
	const superficie = 1150 - nivel;
	const x = interpolate(f, [d, h], [960, 120]);
	return (
		<Toma escena={<EscCanales variante="inundada" nivelAgua={nivel} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.12]}} sacudida={() => 4}>
			<EnMundo x={x} y={superficie + 420} alto={900} voltear>
				<Narrador caminando ojos="grandes" cejas="preocupado" boca="grito" brazoIzq={140} brazoDer={140} />
			</EnMundo>
			<Olas y={superficie + 200} color="rgba(16,52,96,0.85)" />
		</Toma>
	);
};

const Noche: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const hundir = interpolate(f, [d, W.existir + 10], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
	return <Toma escena={<EscNoche hundir={hundir} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.12], y: [0, 40], curva: 'lineal'}} />;
};

/* ------------------------------ REVELACIÓN ------------------------------ */

const MiNombre: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscSubmarino />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.18]}}>
			<EnMundo x={540} y={1760 + Math.sin(f / 12) * 20} alto={1100} opacidad={0.82} filtro="drop-shadow(0 0 30px rgba(160,240,255,0.8))">
				<Narrador ojos="normal" cejas="preocupado" boca="seria" sombra={false} />
			</EnMundo>
			<Desconocido x={540} y={560} desde={W.nombre} />
		</Toma>
	);
};

const Atlantida: React.FC<P> = ({d, h, e, s}) => (
	<Toma
		escena={<EscSubmarino />}
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1.0, 1.1], y: [0, 30]}}
		golpes={[[W.atlantida, 0.06]]}
		encima={<Destello desde={W.atlantida} color="#ffe39a" fuerza={0.45} duracion={14} />}
	>
		<Rayos x={540} y={700} color="#ffe9a0" opacidad={0.25} />
		<TituloDorado texto="ATLÁNTIDA" y={580} desde={W.atlantida - 2} tam={116} />
		<Brillos x={540} y={650} desde={W.atlantida + 4} radio={460} n={10} />
	</Toma>
);

const Platon: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscAtenas />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.14]}}>
		<EnMundo x={540} y={1770} alto={980}>
			<Personaje diseno={PLATON} ojos="entrecerrados" cejas="arrogante" boca="seria" brazoDer={60} codoDer={-50} />
		</EnMundo>
		<Pergamino x={230} y={1100} titulo="TIMEO" desde={W.escritos - 2} rot={-6} />
		<Pergamino x={850} y={1100} titulo="CRITIAS" desde={W.escritos + 4} rot={6} />
		<Etiqueta x={540} y={760} texto="PLATÓN" desde={W.platon - 1} tam={70} />
	</Toma>
);

const DosMil: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscAtenas />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.3, 1.4], y: [-120, -120]}} golpes={[[W.dosmil, 0.06]]}>
		<EnMundo x={540} y={2150} alto={1550}>
			<Personaje diseno={PLATON} ojos="normal" cejas="arrogante" boca="sonrisa" />
		</EnMundo>
		<Cartel x={540} y={540} texto="HACE +2.000 AÑOS" desde={W.dosmil - 2} tam={66} />
		<Cartel x={540} y={700} texto="≈ 360 a. C." desde={W.dosmil + 10} color="#ffffff" tam={50} />
	</Toma>
);

/* ------------------------------ CIERRE ------------------------------ */

const SinPruebas: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscProfundo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.14]}}>
		<Icono tipo="interrogacion" x={200} y={420} desde={d + 8} tam={180} rot={-12} />
		<Icono tipo="interrogacion" x={880} y={380} desde={d + 16} tam={200} rot={10} />
		<Sello x={540} y={1060} texto="0 PRUEBAS" desde={W.concluyentes} tam={96} />
	</Toma>
);

const Testigo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const op = interpolate(f, [d, h], [0.95, 0.3], clamp);
	return (
		<Toma escena={<EscSubmarino oscuro={0.35} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.15, 1.25]}}>
			<EnMundo x={540} y={2000 + Math.sin(f / 12) * 16} alto={1400} opacidad={op} filtro="drop-shadow(0 0 30px rgba(160,240,255,0.8))">
				<Narrador ojos="normal" cejas="preocupado" boca="seria" sombra={false} />
			</EnMundo>
		</Toma>
	);
};

const Leyenda: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLibro />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.12], x: [0, 60], y: [0, 20]}}>
		<EnMundo x={320} y={1420} alto={820} filtro="sepia(1) saturate(1.4) contrast(1.05)" opacidad={0.9}>
			<Narrador ojos="cerrados" cejas="neutral" boca="sonrisa" sombra={false} />
		</EnMundo>
		<Brillos x={320} y={1000} desde={W.leyenda} radio={300} />
		<Cartel x={540} y={260} texto="LEYENDA" desde={W.leyenda - 1} color="#f3e3bd" />
	</Toma>
);

const Veredicto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const mito = f >= W.mito;
	return (
		<Toma fondo="tribunal.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.14]}} golpes={[[W.mito, 0.08]]} encima={<Destello desde={W.mito} color="#ff8a7a" fuerza={0.45} duracion={12} />}>
			<EnMundo x={300} y={1790} alto={900}>
				<Narrador ojos={mito ? 'feliz' : 'normal'} cejas={mito ? 'preocupado' : 'neutral'} boca={mito ? 'mueca' : 'seria'} brazoIzq={mito ? 70 : 15} codoIzq={-60} brazoDer={mito ? 70 : 15} codoDer={-60} />
			</EnMundo>
			<EnMundo x={790} y={1790} alto={900}>
				<Personaje diseno={PLATON} ojos={mito ? 'entrecerrados' : 'normal'} cejas="arrogante" boca={mito ? 'picara' : 'seria'} />
			</EnMundo>
			<Sello x={540} y={560} texto="MITO" icono="✘" color="#d6262e" desde={W.mito} tam={130} rot={-8} />
			<Fundido desde={h - 14} duracion={14} />
		</Toma>
	);
};

/* ------------------------------ piezas pequeñas ------------------------------ */

const Cartel: React.FC<{x: number; y: number; texto: string; desde: number; color?: string; tam?: number}> = ({x, y, texto, desde, color = '#ffd84a', tam = 76}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	const s = interpolate(f, [desde, desde + 7], [0, 1], {...clamp, easing: Easing.out(Easing.back(2.2))});
	return (
		<div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, 0) scale(${s}) rotate(-3deg)`, background: color, border: `10px solid ${TINTA}`, borderRadius: 26, padding: '12px 36px 18px', fontFamily: TITULAR, fontWeight: 900, fontSize: tam, color: TINTA, whiteSpace: 'nowrap', boxShadow: '0 12px 0 rgba(0,0,0,0.4)'}}>
			{texto}
		</div>
	);
};

/* ------------------------------ Montaje ------------------------------ */

type Plano = {desde: number; Comp: React.FC<P>; entrada: Transicion};

const PLANOS: Plano[] = [
	{desde: 0, Comp: Presentacion, entrada: 'corte'},
	{desde: antes(W.oro), Comp: TemplosDeOro, entrada: 'zoom'},
	{desde: antes(palabra(0, 'los', 2)), Comp: Canales, entrada: 'latigoDer'},
	{desde: antes(palabra(0, 'y')), Comp: Oceano, entrada: 'latigoIzq'},
	{desde: antes(palabra(1, 'Créeme')), Comp: Creeme, entrada: 'zoom'},
	{desde: antes(palabra(2, 'vivíamos')), Comp: Paraiso, entrada: 'latigoDer'},
	{desde: antes(palabra(3, 'Nuestros')), Comp: Palacios, entrada: 'latigoArriba'},
	{desde: antes(palabra(3, 'nuestras')), Comp: Riquezas, entrada: 'latigoIzq'},
	{desde: antes(palabra(3, 'y')), Comp: Anillos, entrada: 'zoom'},
	{desde: antes(palabra(4, 'Éramos')), Comp: Poderosos, entrada: 'latigoDer'},
	{desde: antes(palabra(4, 'creer')), Comp: Detenernos, entrada: 'zoom'},
	{desde: antes(palabra(5, 'Y')), Comp: PrimerError, entrada: 'corte'},
	{desde: antes(palabra(6, 'Los')), Comp: Dioses, entrada: 'latigoArriba'},
	{desde: antes(palabra(7, 'y')), Comp: Castigo, entrada: 'corte'},
	{desde: antes(palabra(8, 'Primero')), Comp: Temblor, entrada: 'latigoIzq'},
	{desde: antes(palabra(9, 'Después')), Comp: Olas2, entrada: 'latigoArriba'},
	{desde: antes(palabra(10, 'Intenté')), Comp: Correr, entrada: 'latigoDer'},
	{desde: antes(palabra(11, 'En')), Comp: Noche, entrada: 'zoom'},
	{desde: antes(palabra(12, 'Quizás')), Comp: MiNombre, entrada: 'latigoArriba'},
	{desde: antes(palabra(13, 'pero')), Comp: Atlantida, entrada: 'zoom'},
	{desde: antes(palabra(14, 'Y')), Comp: Platon, entrada: 'latigoDer'},
	{desde: antes(palabra(14, 'hace')), Comp: DosMil, entrada: 'zoom'},
	{desde: antes(palabra(15, 'Nunca')), Comp: SinPruebas, entrada: 'latigoArriba'},
	{desde: antes(palabra(16, 'Así')), Comp: Testigo, entrada: 'latigoIzq'},
	{desde: antes(palabra(17, 'Tal')), Comp: Leyenda, entrada: 'zoom'},
	{desde: antes(palabra(18, 'VEREDICTO')), Comp: Veredicto, entrada: 'latigoDer'},
];

export const Historia: React.FC = () => (
	<>
		{PLANOS.map((p, i) => {
			const sig = PLANOS[i + 1];
			return <p.Comp key={i} d={p.desde} h={sig ? sig.desde : FIN_VIDEO} e={p.entrada} s={sig ? sig.entrada : 'corte'} />;
		})}
	</>
);

/** Efectos de sonido: [archivo, cuadro, volumen] */
export const SONIDOS: [string, number, number][] = [
	...PLANOS.filter((p) => p.entrada !== 'corte').map((p) => ['whoosh', p.desde - 5, 0.4] as [string, number, number]),
	['arpa', W.oro - 2, 0.4],
	['ola', W.obedecernos - 6, 0.4],
	['pop', W.obedecernos + 24, 0.35],
	['arpa', W.paraiso - 2, 0.35],
	['ding', W.gigantescos, 0.3],
	['ding', W.riquezas, 0.3],
	['aplausos', W.riquezas, 0.25],
	['pop', W.tierra - 1, 0.4],
	['pop', W.agua - 1, 0.4],
	['aplausos', W.poderosos - 2, 0.4],
	['pop', W.poderosos, 0.4],
	['dundun', W.error - 2, 0.55],
	['sello', W.error, 0.5],
	['trueno', W.admiracion + 2, 0.35],
	['trueno', antes(palabra(7, 'y')) + 8, 0.6],
	['trueno', W.castigarnos - 2, 0.55],
	['temblor', antes(palabra(8, 'Primero')), 0.7],
	['temblor', W.tembló, 0.6],
	['ola', antes(palabra(9, 'Después')), 0.6],
	['ola', W.olas, 0.5],
	['ola', W.correr, 0.35],
	['burbujas', W.noche, 0.35],
	['burbujas', W.existir, 0.4],
	['burbujas', antes(palabra(12, 'Quizás')) + 10, 0.3],
	['pop', W.nombre, 0.4],
	['dundun', W.atlantida - 3, 0.5],
	['arpa', W.atlantida, 0.45],
	['hoja', W.escritos - 2, 0.45],
	['hoja', W.escritos + 4, 0.45],
	['pop', W.platon - 1, 0.4],
	['pop', W.dosmil - 2, 0.4],
	['sello', W.concluyentes, 0.6],
	['burbujas', antes(palabra(16, 'Así')) + 20, 0.3],
	['arpa', W.leyenda - 2, 0.35],
	['sello', W.mito, 0.75],
	['dundun', W.mito - 2, 0.4],
];

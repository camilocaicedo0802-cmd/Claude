import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {Destello, Etiqueta} from '../componentes/Efectos';
import {Corazones, CintaMetrica, HojaCaricatura, Lagrimas, MarcaAltura, PeriodicosVolando, Pluma, Pulgadas} from '../componentes/Napoleon';
import {CARICATURISTA, DOCTOR, FRANCES, GRANADERO, INGLES, NAPOLEON, Personaje} from '../componentes/Personaje';
import {EnMundo, Toma, Transicion} from '../componentes/Toma';
import {Bocadillo, Brillos, Confeti, Fundido, Icono, Rayos, Sello} from '../componentes/Utileria';
import {EscCelular, EscDesfile, EscEstudio, EscMapa, EscMedidas, EscPalacio, EscPizarra, EscSantaHelena, MEME, PISO, altoParaCm} from '../escenarios/Escenarios';
import {TITULAR} from '../fuentes';
import {finFrase, palabra} from '../tiempos';

/* "¿Napoleón era bajito?" — chisme histórico. Cuadros GLOBALES. */

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const antes = (n: number) => n - 3;
const TINTA = '#1b1b1f';

const W = {
	alto: palabra(0, 'alto'),
	promedio: palabra(0, 'promedio'),
	enano: palabra(1, 'enano'),
	dibujante: palabra(1, 'dibujante'),
	anio1802: palabra(2, '1802'),
	poderoso: palabra(2, 'poderoso'),
	londres: palabra(3, 'Londres'),
	caricaturista: palabra(3, 'caricaturista'),
	odia: palabra(3, 'odia'),
	diminuto: palabra(4, 'diminuto'),
	berrinches: palabra(4, 'berrinches'),
	boney: palabra(5, 'LITTLE BONEY'),
	periodicos: palabra(6, 'periódicos'),
	europa: palabra(6, 'Europa'),
	anio1821: palabra(7, '1821'),
	autopsia: palabra(7, 'autopsia'),
	cinco: palabra(7, 'cinco'),
	inglaterra: palabra(8, 'Inglaterra'),
	m157: palabra(9, '1,57'),
	pulgadas: palabra(10, 'pulgadas'),
	largas: palabra(10, 'largas'),
	verdad: palabra(11, 'verdad'),
	m169: palabra(12, '1,69'),
	frances: palabra(13, 'francés'),
	m165: palabra(14, '1,65'),
	guardia: palabra(15, 'guardia'),
	altos: palabra(15, 'altos'),
	cabo: palabra(16, 'cabo'),
	carinoso: palabra(16, 'cariñoso'),
	mito: palabra(17, 'MITO'),
	meme: palabra(18, 'meme'),
	historia: palabra(18, 'historia'),
};

export const FIN_VIDEO = finFrase(18) + 30;

type P = {d: number; h: number; e: Transicion; s: Transicion};

/** Cámara de la tabla de estaturas: encuadra las cabezas por encima de los subtítulos. */
const CAM_TABLA = {s: [1.14, 1.2] as [number, number], y: [-30, -50] as [number, number]};

/** Personaje parado sobre la tabla con una estatura exacta en cm. */
const EnTabla: React.FC<{x: number; cm: number; children: React.ReactNode; voltear?: boolean}> = ({x, cm, children, voltear}) => (
	<EnMundo x={x} y={PISO} alto={altoParaCm(cm)} voltear={voltear}>
		{children}
	</EnMundo>
);

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

/* ------------------------------ GANCHO ------------------------------ */

const Gancho: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={CAM_TABLA} golpes={[[W.alto, 0.05]]}>
		<EnTabla x={300} cm={169}>
			<Personaje diseno={NAPOLEON} ojos="entrecerrados" cejas="arrogante" boca="picara" brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
		</EnTabla>
		<EnTabla x={780} cm={165}>
			<Personaje diseno={FRANCES} ojos="grandes" cejas="sorprendido" boca="o" semilla={3} />
		</EnTabla>
		<MarcaAltura cm={169} desde={W.alto} color="#22a84f" lado="izq" x1={160} x2={560} />
		<MarcaAltura cm={165} desde={W.promedio} color="#1f6fd1" lado="der" x1={560} x2={920} />
	</Toma>
);

const Enano: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cm = interpolate(f, [W.enano - 2, W.enano + 6], [169, 112], {...clamp, easing: Easing.out(Easing.back(1.6))});
	const encogido = f >= W.enano;
	return (
		<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={CAM_TABLA} golpes={[[W.enano, 0.06]]}>
			<EnTabla x={300} cm={cm}>
				<Personaje diseno={NAPOLEON} ojos={encogido ? 'grandes' : 'entrecerrados'} cejas={encogido ? 'preocupado' : 'arrogante'} boca={encogido ? 'grito' : 'picara'} brazoIzq={encogido ? 150 : 40} codoIzq={encogido ? 0 : -95} brazoDer={encogido ? 150 : 40} codoDer={encogido ? 0 : -95} />
			</EnTabla>
			<EnTabla x={780} cm={165}>
				<Personaje diseno={FRANCES} ojos={encogido ? 'feliz' : 'normal'} cejas="arrogante" boca={encogido ? 'sonrisaGrande' : 'seria'} semilla={3} />
			</EnTabla>
			<Icono tipo="interrogacion" x={300} y={1150} desde={W.enano + 6} tam={150} />
		</Toma>
	);
};

const Dibujante: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscEstudio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.08, 1.18], y: [-30, -30]}}>
		<EnMundo x={540} y={1780} alto={1060}>
			<Personaje diseno={CARICATURISTA} ojos="entrecerrados" cejas="arrogante" boca="picara" brazoDer={95} codoDer={-30} />
		</EnMundo>
		<Pluma x={740} y={1180} desde={d} tam={260} />
	</Toma>
);

/* ------------------------------ DESARROLLO ------------------------------ */

const Poderoso: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscPalacio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.16], y: [-20, -40]}} golpes={[[W.poderoso, 0.05]]}>
		<Rayos x={540} y={900} color="#ffe9a0" opacidad={0.22} />
		<EnMundo x={540} y={1800} alto={1080}>
			<Personaje diseno={NAPOLEON} ojos="entrecerrados" cejas="arrogante" boca="picara" brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
		</EnMundo>
		<Cartel x={540} y={540} texto="1802" desde={W.anio1802} />
		<Brillos x={540} y={1000} desde={W.poderoso} radio={420} n={10} />
	</Toma>
);

const LoOdia: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const enojo = f >= W.odia - 2;
	return (
		<Toma escena={<EscEstudio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.12, 1.22], y: [-40, -40]}} golpes={[[W.odia, 0.07]]}>
			<EnMundo x={540} y={1800} alto={1100}>
				<Personaje diseno={CARICATURISTA} ojos={enojo ? 'normal' : 'entrecerrados'} cejas="enojado" boca={enojo ? 'dientes' : 'mueca'} brazoIzq={enojo ? 150 : 20} brazoDer={enojo ? 150 : 20} />
			</EnMundo>
			<Etiqueta x={540} y={380} texto="LONDRES" desde={W.londres - 1} tam={64} />
			<Cartel x={540} y={480} texto="James Gillray" desde={W.caricaturista} color="#ffffff" tam={52} />
			<Icono tipo="enojo" x={300} y={800} desde={W.odia} tam={160} />
		</Toma>
	);
};

const Diminuto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const berrinche = f >= W.berrinches - 2;
	return (
		<Toma escena={<EscEstudio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.15, 1.22], y: [-60, -60]}}>
			<HojaCaricatura x={540} y={880} ancho={780} alto={1000}>
				<EnMundo x={360} y={820} alto={560} rot={berrinche ? Math.sin(f * 1.4) * 10 : 0}>
					<Personaje diseno={NAPOLEON} ojos={berrinche ? 'cerrados' : 'grandes'} cejas={berrinche ? 'enojado' : 'sorprendido'} boca={berrinche ? 'grito' : 'o'} brazoIzq={berrinche ? 150 + Math.sin(f) * 20 : 30} brazoDer={berrinche ? 150 + Math.cos(f) * 20 : 30} caminando={berrinche} />
				</EnMundo>
				{berrinche && <Lagrimas x={350} y={360} desde={W.berrinches} />}
			</HojaCaricatura>
			<Pluma x={850} y={1150} desde={d} tam={280} />
		</Toma>
	);
};

const LittleBoney: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscEstudio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.22, 1.28], y: [-60, -60]}} golpes={[[W.boney, 0.08]]}>
			<HojaCaricatura x={540} y={880} ancho={780} alto={1000}>
				<EnMundo x={360} y={820} alto={560} rot={Math.sin(f * 1.4) * 10}>
					<Personaje diseno={NAPOLEON} ojos="cerrados" cejas="enojado" boca="grito" brazoIzq={150 + Math.sin(f) * 20} brazoDer={150 + Math.cos(f) * 20} caminando />
				</EnMundo>
				<Lagrimas x={350} y={360} desde={d} />
			</HojaCaricatura>
			<Sello x={540} y={520} texto="LITTLE BONEY" color="#1b1b1f" desde={W.boney} tam={86} rot={-8} />
		</Toma>
	);
};

const Periodicos: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscMapa />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.14]}} golpes={[[W.europa, 0.04]]}>
		<PeriodicosVolando desde={W.periodicos - 2} />
	</Toma>
);

/* ------------------------------ CONFLICTO ------------------------------ */

const Autopsia: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscSantaHelena />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.15], y: [-20, -20]}}>
		<Etiqueta x={540} y={240} texto="SANTA HELENA" desde={d + 4} tam={52} />
		<Cartel x={540} y={780} texto="1821" desde={W.anio1821} />
		<EnMundo x={880} y={1800} alto={1000}>
			<Personaje diseno={DOCTOR} ojos="entrecerrados" cejas="neutral" boca="seria" brazoIzq={80} codoIzq={-20} />
		</EnMundo>
		<CintaMetrica x={170} y={1090} largo={760} desde={W.autopsia} />
		<Cartel x={460} y={1500} texto="5 pies 2 pulgadas" desde={W.cinco} color="#ffffff" tam={58} />
	</Toma>
);

const Inglaterra: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={CAM_TABLA}>
		<EnTabla x={300} cm={169}>
			<Personaje diseno={NAPOLEON} ojos="grandes" cejas="preocupado" boca="mueca" />
		</EnTabla>
		<EnTabla x={780} cm={178}>
			<Personaje diseno={INGLES} ojos="entrecerrados" cejas="arrogante" boca="picara" semilla={2} brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
		</EnTabla>
		<Icono tipo="interrogacion" x={540} y={760} desde={W.inglaterra} tam={150} />
	</Toma>
);

const Mide157: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cm = interpolate(f, [W.m157 - 2, W.m157 + 5], [169, 157], {...clamp, easing: Easing.out(Easing.back(2))});
	return (
		<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={CAM_TABLA} golpes={[[W.m157, 0.07]]}>
			<EnTabla x={300} cm={cm}>
				<Personaje diseno={NAPOLEON} ojos="grandes" cejas="preocupado" boca="grito" />
			</EnTabla>
			<EnTabla x={780} cm={178}>
				<Personaje diseno={INGLES} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" semilla={2} brazoIzq={45} codoIzq={-80} brazoDer={45} codoDer={-80} />
			</EnTabla>
			<MarcaAltura cm={157} desde={W.m157} color="#e3262e" lado="izq" x1={160} x2={560} />
		</Toma>
	);
};

const PulgadasFrancesas: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscPizarra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08]}}>
		<Pulgadas desde={W.pulgadas - 4} />
		<Brillos x={540} y={900} desde={W.largas} radio={380} />
	</Toma>
);

const Cuanto: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={CAM_TABLA}>
		<EnTabla x={300} cm={157}>
			<Personaje diseno={NAPOLEON} ojos="mirandoLado" cejas="sorprendido" boca="o" />
		</EnTabla>
		<Icono tipo="interrogacion" x={520} y={800} desde={d + 4} tam={160} rot={8} />
	</Toma>
);

const Mide169: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cm = interpolate(f, [W.m169 - 3, W.m169 + 5], [157, 169], {...clamp, easing: Easing.out(Easing.back(2))});
	return (
		<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={CAM_TABLA} golpes={[[W.m169, 0.07]]}>
			<EnTabla x={300} cm={cm}>
				<Personaje diseno={NAPOLEON} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={150} brazoDer={150} />
			</EnTabla>
			<MarcaAltura cm={169} desde={W.m169} color="#22a84f" lado="izq" x1={160} x2={560} />
			<Brillos x={300} y={1000} desde={W.m169 + 2} radio={220} />
		</Toma>
	);
};

const ElFrances: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const x = interpolate(f, [d, W.frances + 8], [1250, 780], {...clamp, easing: Easing.out(Easing.cubic)});
	return (
		<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={CAM_TABLA}>
			<EnTabla x={300} cm={169}>
				<Personaje diseno={NAPOLEON} ojos="mirandoLado" cejas="arrogante" boca="picara" brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
			</EnTabla>
			<MarcaAltura cm={169} desde={d - 30} color="#22a84f" lado="izq" x1={160} x2={560} />
			<EnTabla x={x} cm={165}>
				<Personaje diseno={FRANCES} caminando={f < W.frances + 6} ojos="normal" cejas="neutral" boca="sonrisa" semilla={3} />
			</EnTabla>
		</Toma>
	);
};

const Mide165: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscMedidas />} desde={d} hasta={h} entrada={e} salida={s} cam={CAM_TABLA} golpes={[[W.m165, 0.05]]}>
		<EnTabla x={300} cm={169}>
			<Personaje diseno={NAPOLEON} ojos="entrecerrados" cejas="arrogante" boca="picara" brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
		</EnTabla>
		<EnTabla x={780} cm={165}>
			<Personaje diseno={FRANCES} ojos="grandes" cejas="preocupado" boca="mueca" semilla={3} />
		</EnTabla>
		<MarcaAltura cm={169} desde={d - 60} color="#22a84f" lado="izq" x1={160} x2={560} />
		<MarcaAltura cm={165} desde={W.m165} color="#1f6fd1" lado="der" x1={560} x2={920} />
	</Toma>
);

/* ------------------------------ LA GUARDIA ------------------------------ */

const Guardia: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscDesfile />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.12], y: [20, 160]}} golpes={[[W.altos, 0.06]]}>
		<EnMundo x={210} y={1820} alto={1180}>
			<Personaje diseno={GRANADERO} ojos="entrecerrados" cejas="arrogante" boca="seria" semilla={1} />
		</EnMundo>
		<EnMundo x={870} y={1820} alto={1180}>
			<Personaje diseno={GRANADERO} ojos="entrecerrados" cejas="arrogante" boca="seria" semilla={4} />
		</EnMundo>
		<EnMundo x={540} y={1820} alto={860}>
			<Personaje diseno={NAPOLEON} ojos="mirandoLado" cejas="preocupado" boca="mueca" />
		</EnMundo>
		<Cartel x={540} y={280} texto="+1,80 m" desde={W.altos} color="#ffffff" tam={66} />
	</Toma>
);

const PequenoCabo: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscDesfile />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.14], y: [-20, -20]}}>
		<EnMundo x={210} y={1820} alto={1100}>
			<Personaje diseno={GRANADERO} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" semilla={1} brazoIzq={150} brazoDer={150} />
		</EnMundo>
		<EnMundo x={870} y={1820} alto={1100}>
			<Personaje diseno={GRANADERO} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" semilla={4} brazoIzq={150} brazoDer={150} />
		</EnMundo>
		<EnMundo x={540} y={1820} alto={860}>
			<Personaje diseno={{...NAPOLEON, mejillas: true}} ojos="feliz" cejas="arrogante" boca="sonrisa" />
		</EnMundo>
		<Bocadillo x={300} y={420} texto="¡Petit caporal!" desde={W.cabo - 2} cola="izq" ancho={520} tam={60} />
		<Corazones x={540} y={1300} desde={W.cabo} />
		<Sello x={540} y={760} texto="APODO CARIÑOSO" color="#1f9d48" desde={W.carinoso} tam={66} rot={-6} />
	</Toma>
);

/* ------------------------------ VEREDICTO Y PREGUNTA ------------------------------ */

const Veredicto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const mito = f >= W.mito;
	return (
		<Toma fondo="tribunal.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.14]}} golpes={[[W.mito, 0.08]]} encima={<Destello desde={W.mito} color="#ff8a7a" fuerza={0.45} duracion={12} />}>
			<EnMundo x={320} y={1790} alto={900}>
				<Personaje diseno={NAPOLEON} ojos={mito ? 'feliz' : 'normal'} cejas="arrogante" boca={mito ? 'sonrisaGrande' : 'seria'} brazoIzq={mito ? 150 : 15} brazoDer={mito ? 150 : 15} />
			</EnMundo>
			<EnMundo x={780} y={1790} alto={880}>
				<Personaje diseno={FRANCES} ojos={mito ? 'grandes' : 'normal'} cejas={mito ? 'sorprendido' : 'neutral'} boca={mito ? 'o' : 'seria'} semilla={3} />
			</EnMundo>
			<Sello x={540} y={560} texto="MITO" icono="✘" color="#d6262e" desde={W.mito} tam={130} rot={-8} />
		</Toma>
	);
};

const PrimerMeme: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const reacciones = interpolate(f, [d, W.meme + 6], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
	const asoma = interpolate(f, [d + 10, d + 22], [700, 0], {...clamp, easing: Easing.out(Easing.back(1.4))});
	return (
		<Toma escena={<EscCelular reacciones={reacciones} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.1], y: [0, 20]}} golpes={[[W.meme, 0.06], [W.historia, 0.08]]}>
			{/* el meme: la caricatura dentro del post */}
			<div style={{position: 'absolute', left: MEME.x, top: MEME.y, width: MEME.w, height: MEME.h, overflow: 'hidden', filter: 'grayscale(0.25) sepia(0.35) contrast(1.15)'}}>
				<div style={{position: 'absolute', top: 30, left: 0, right: 0, textAlign: 'center', fontFamily: TITULAR, fontWeight: 900, fontSize: 64, color: '#ffffff', WebkitTextStroke: `10px ${TINTA}`, paintOrder: 'stroke'}}>LITTLE BONEY</div>
				<EnMundo x={330} y={720} alto={480} rot={Math.sin(f * 1.4) * 10}>
					<Personaje diseno={NAPOLEON} ojos="cerrados" cejas="enojado" boca="grito" brazoIzq={150 + Math.sin(f) * 20} brazoDer={150 + Math.cos(f) * 20} caminando />
				</EnMundo>
				<Lagrimas x={320} y={350} desde={d} />
			</div>
			{/* el Napoleón real, ofendido, se asoma */}
			<EnMundo x={900 + asoma} y={2080} alto={1000} rot={-10}>
				<Personaje diseno={NAPOLEON} ojos="entrecerrados" cejas="enojado" boca="mueca" />
			</EnMundo>
			<Confeti desde={W.meme} n={40} />
			<Fundido desde={h - 12} duracion={12} />
		</Toma>
	);
};

/* ------------------------------ Montaje ------------------------------ */

type Plano = {desde: number; Comp: React.FC<P>; entrada: Transicion};

const PLANOS: Plano[] = [
	{desde: 0, Comp: Gancho, entrada: 'corte'},
	{desde: antes(palabra(1, 'Y')), Comp: Enano, entrada: 'corte'},
	{desde: antes(W.dibujante), Comp: Dibujante, entrada: 'latigoDer'},
	{desde: antes(palabra(2, 'En')), Comp: Poderoso, entrada: 'latigoIzq'},
	{desde: antes(palabra(3, 'Pero')), Comp: LoOdia, entrada: 'latigoDer'},
	{desde: antes(palabra(4, 'Lo')), Comp: Diminuto, entrada: 'zoom'},
	{desde: antes(W.boney), Comp: LittleBoney, entrada: 'corte'},
	{desde: antes(palabra(6, 'Los')), Comp: Periodicos, entrada: 'latigoArriba'},
	{desde: antes(palabra(7, 'Cuando')), Comp: Autopsia, entrada: 'latigoIzq'},
	{desde: antes(palabra(8, 'En')), Comp: Inglaterra, entrada: 'latigoDer'},
	{desde: antes(W.m157), Comp: Mide157, entrada: 'corte'},
	{desde: antes(palabra(10, 'Pero')), Comp: PulgadasFrancesas, entrada: 'latigoArriba'},
	{desde: antes(palabra(11, '¿Cuánto')), Comp: Cuanto, entrada: 'latigoIzq'},
	{desde: antes(W.m169), Comp: Mide169, entrada: 'corte'},
	{desde: antes(palabra(13, '¿Y')), Comp: ElFrances, entrada: 'corte'},
	{desde: antes(palabra(14, 'Unos')), Comp: Mide165, entrada: 'corte'},
	{desde: antes(palabra(15, 'Para')), Comp: Guardia, entrada: 'latigoArriba'},
	{desde: antes(palabra(16, 'Y')), Comp: PequenoCabo, entrada: 'zoom'},
	{desde: antes(palabra(17, 'VEREDICTO')), Comp: Veredicto, entrada: 'latigoDer'},
	{desde: antes(palabra(18, '¿Emperador')), Comp: PrimerMeme, entrada: 'zoom'},
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
export const SONIDOS: [string, number, number][] = [
	...PLANOS.filter((p) => p.entrada !== 'corte').map((p) => ['whoosh', p.desde - 5, 0.45] as [string, number, number]),
	['pop', W.alto, 0.45],
	['pop', W.promedio, 0.45],
	['boing', W.enano - 2, 0.6],
	['garabato', antes(W.dibujante) + 2, 0.4],
	['ding', W.poderoso, 0.35],
	['pop', W.anio1802, 0.4],
	['pop', W.londres - 1, 0.4],
	['dundun', W.odia - 2, 0.4],
	['garabato', antes(palabra(4, 'Lo')) + 2, 0.4],
	['boing', W.berrinches - 2, 0.4],
	['sello', W.boney, 0.6],
	['hoja', W.periodicos - 2, 0.4],
	['hoja', W.periodicos + 6, 0.4],
	['hoja', W.periodicos + 12, 0.4],
	['pop', W.anio1821, 0.4],
	['pop', W.cinco, 0.4],
	['boing', W.m157 - 2, 0.6],
	['pop', W.pulgadas - 4, 0.35],
	['pop', W.pulgadas + 8, 0.35],
	['boing', W.m169 - 3, 0.55],
	['ding', W.m169 + 2, 0.35],
	['pop', W.m165, 0.45],
	['ding', W.altos, 0.3],
	['aplausos', W.cabo, 0.4],
	['sello', W.carinoso, 0.45],
	['sello', W.mito, 0.7],
	['pop', W.meme, 0.45],
	['aplausos', W.meme, 0.4],
];

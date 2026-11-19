import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Actor, Muneco, alcanzar, manosEn, manosFrente} from '../componentes/Muneco';
import {Cuenta, JarraVotos} from '../componentes/Recurrentes';
import {Toma} from '../componentes/Toma';
import {HITLER_CANCILLER, LIDER_SPD, PAPEN, POLICIA_1923, SENOR_1, SENOR_2, SENOR_3, UNIFORME_MARRON} from '../componentes/Vestuario';
import {EscLiso, EscRincon, Humo, Jarra} from '../escenarios/Epoca';
import {CONDENSADA} from '../fuentes';
import {P, Plano, TINTA, antes, centrar, clamp, fin, golpeCam, ini, mezclaCam, pal, tramo} from './base';
import {ANGULO_PAPEN, Barra, ENCUADRE_CONTRATO, OficinaPapen} from './c0';
import {brazo} from './compartidas';
import {Bancadas, Calendario60, Camion, Candado, Cronometro, EscDachau, EscIncendio, Megafono, Papeleta, ParlamentoMini, Periodico, PuertaSalon, Silueta} from './utileria_c89';

/* CAPÍTULO 8 · Los dos meses (9:03–10:33). Rojo fuego; en Dachau, casi blanco y negro, quieto y en silencio.
   Desde el incendio, a Hitler se le filma a la altura de los ojos; al final, desde abajo. */

/* ---------- rótulo: el calendario de 60 días y el cronómetro de Papen ---------- */

const C1: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const t = interpolate(f, [d + 6, h], [0, 3], clamp);
	const celda = 3 - Math.floor(Math.min(2.99, t));
	return (
		<Toma escena={<EscLiso color="#2a2e38" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [10, -10]}}>
			<Calendario60 x={960} y={110} ancho={1000} tachados={t} />
			{/* la mano enguantada de Papen con el lápiz rojo */}
			<div style={{position: 'absolute', left: 520 + (3 - celda) * 85, top: 360, width: 150, height: 96, background: '#fff', border: `7px solid ${TINTA}`, borderRadius: '48px 48px 40px 40px', transform: `rotate(-24deg) translate(${Math.sin(f / 2) * 6}px, ${Math.cos(f / 2) * 6}px)`}} />
			<div style={{position: 'absolute', left: 500 + (3 - celda) * 85, top: 330, width: 18, height: 120, background: '#c8202a', border: `5px solid ${TINTA}`, transform: 'rotate(-30deg)'}} />
		</Toma>
	);
};

const C2: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#2e3742" luz="255,214,150" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.18], x: [20, -20], y: [60, 80]}} angulo={ANGULO_PAPEN}>
		<Actor x={900} y={1100} alto={980}>
			<Muneco ropa={PAPEN} pose={{...brazo(1, alcanzar(1, 330, 380)), md: 'agarra', ...manosEn([150, 560]), mi: 'abierta', cabeza: -6}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
		</Actor>
		<Cronometro x={1130} y={600} tam={210} desde={d} />
	</Toma>
);

/* ---------- el incendio y el detenido (sin chiste) ---------- */

const C3: React.FC<P> = ({d, h, e, s}) => <Toma escena={<EscIncendio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.12], y: [0, 30]}} />;

const C4: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscIncendio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.3, 1.36], x: [-40, -70], y: [-160, -180]}}>
		<div style={{position: 'absolute', inset: 0, background: 'rgba(10,4,4,0.45)'}} />
		<Silueta x={820} y={1010} alto={640} ropa={POLICIA_1923} pose={manosFrente(undefined, [300, 420])} />
		<Silueta x={1000} y={1010} alto={600} ropa={SENOR_1} pose={{...manosFrente([140, 520], [260, 520]), cabeza: 8}} />
		<Silueta x={1180} y={1010} alto={640} ropa={POLICIA_1923} voltear pose={manosFrente(undefined, [300, 420])} />
	</Toma>
);

/* ---------- el decreto: Hitler firma (a la altura de los ojos) y tres candados ---------- */

const C5: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const firma = Math.sin(f / 2.5) * 6;
	return (
		<Toma escena={<EscLiso color="#3a2a28" luz="255,190,130" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.12, 1.2], x: [0, -30], y: [40, 50]}}>
			<Actor x={960} y={1060} alto={900}>
				<Muneco ropa={HITLER_CANCILLER} pose={{...manosEn([120, 600], [250 + firma, 600]), mi: 'abierta', md: 'agarra', cabeza: 10, cuerpo: 4}} ojos="entrecerrados" cejas="neutral" boca="seria" />
			</Actor>
			<div style={{position: 'absolute', left: 360, right: 360, top: 760, height: 360, background: 'linear-gradient(180deg, #5a3420, #2e1a10)', borderTop: `10px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 820, top: 700, width: 300, height: 90, background: '#f4ecd6', border: `6px solid ${TINTA}`, transform: 'perspective(600px) rotateX(58deg)', fontFamily: CONDENSADA, fontSize: 40, textAlign: 'center', color: '#2a2218'}}>DECRETO</div>
		</Toma>
	);
};

const C6: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#24262e" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}}>
		<Periodico x={420} y={300} ancho={420} titular="LA VOZ LIBRE" fecha="28 FEB 1933" rot={-3} />
		<Megafono x={960} y={560} tam={360} />
		<PuertaSalon x={1500} y={860} alto={560} letrero="SALÓN DE REUNIONES" />
		<Candado x={420} y={560} tam={170} cierra={pal(188, 'prensa')} />
		<Candado x={960} y={600} tam={170} cierra={pal(188, 'reunión')} />
		<Candado x={1500} y={640} tam={170} cierra={pal(188, 'expresión')} />
	</Toma>
);

/* ---------- miles de presos: camiones de noche ---------- */

const C7: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscLiso color="#1a2236" luz="160,180,230" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], x: [30, -30]}}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 860, bottom: 0, background: '#08090f'}} />
			<Camion x={620} y={900} ancho={700} />
			<Camion x={1420} y={890} ancho={600} color="#14141a" />
			{[0, 1, 2, 3].map((i) => (
				<Silueta key={i} x={1180 + i * 150 - (f - d) * 2.2} y={900} alto={360} ropa={SENOR_2} camina={0.6} voltear tono={0.05} />
			))}
		</Toma>
	);
};

/* ---------- elecciones con matones en la calle ---------- */

const C8: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#3a3a40" luz="220,220,230" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.12], x: [40, -40]}}>
		<div style={{position: 'absolute', left: 0, right: 0, top: 820, bottom: 0, background: '#2a2a2e'}} />
		<div style={{position: 'absolute', left: 1080, top: 280, width: 520, height: 560, background: '#5a5248', border: `8px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: 1240, top: 470, width: 200, height: 370, background: '#1a1410', border: `6px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: 1140, top: 330, width: 400, padding: '10px 0', background: '#e9e4d6', border: `6px solid ${TINTA}`, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 52, color: TINTA}}>CENTRO DE VOTACIÓN</div>
		{/* las sombras de los matones, largas sobre la pared */}
		{[0, 1].map((i) => (
			<div key={i} style={{position: 'absolute', left: 760 + i * 230, top: 220, width: 380, height: 640, opacity: 0.55, transform: 'skewX(-12deg)'}}>
				<Silueta x={190} y={640} alto={660} ropa={UNIFORME_MARRON} tono={0} pose={{...manosEn([150, 548], [250, 548]), mi: 'puno', md: 'puno'}} />
			</div>
		))}
		<Actor x={1180} y={1000} alto={560} voltear>
			<Muneco ropa={UNIFORME_MARRON} pose={{...manosEn([150, 548], [250, 548]), mi: 'puno', md: 'puno'}} ojos="entrecerrados" cejas="enojado" boca="seria" />
		</Actor>
		<Actor x={420} y={1000} alto={520}>
			<Muneco ropa={SENOR_3} camina={0.4} pose={{cabeza: -10}} ojos="mirandoLado" cejas="preocupado" boca="mueca" />
		</Actor>
	</Toma>
);

/* ---------- 43,9 %: ni con miedo le alcanzó ---------- */

const C9: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const g = antes(ini(193));
	const nivel = 43.9 * tramo(f, pal(192, 'Tampoco'), pal(192, '43,9'), (t) => 1 - Math.pow(1 - t, 2.2));
	return (
		<Toma escena={<Barra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => golpeCam(ff, g, centrar(960, 520, 1.04 + 0.04 * tramo(ff, d, g)), centrar(960, 330, 2.4))}>
			{/* la sombra del uniformado junto a las urnas */}
			<div style={{position: 'absolute', left: 1220, top: 220, width: 420, height: 700, opacity: 0.6}}>
				<Silueta x={210} y={700} alto={720} ropa={UNIFORME_MARRON} tono={0} pose={{...manosEn([150, 548], [250, 548]), mi: 'puno', md: 'puno'}} />
			</div>
			<div style={{position: 'absolute', left: 1360, top: 700, width: 220, height: 170, background: '#5a4a3a', border: `7px solid ${TINTA}`}}>
				<div style={{position: 'absolute', left: 50, top: -7, width: 120, height: 14, background: TINTA}} />
				<div style={{fontFamily: CONDENSADA, fontSize: 40, color: '#e9e4d6', textAlign: 'center', marginTop: 50}}>URNA</div>
			</div>
			<JarraVotos x={900} y={880} alto={720} nivel={nivel} />
		</Toma>
	);
};

/* ---------- DACHAU · primer corte seco; quieto, casi blanco y negro, sin música ---------- */

const D1: React.FC<P> = ({d, h, e, s}) => <Toma escena={<EscDachau />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.035], y: [0, -6]}} />;

const D2: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscDachau abre={1} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.07], y: [-10, -16]}}>
			<div style={{position: 'absolute', inset: 0, filter: 'grayscale(1)'}}>
				{[0, 1, 2, 3, 4].map((i) => {
					const avance = (f - d) * 0.9;
					const esc = Math.max(0.25, 1 - avance / 260 - i * 0.08);
					return <Silueta key={i} x={960 + (i % 2 ? 40 : -40)} y={1000 - avance * 1.1 - i * 60} alto={560 * esc} ropa={SENOR_2} camina={0.4} tono={0.12} />;
				})}
			</div>
		</Toma>
	);
};

/* ---------- la ley habilitante: el Parlamento vota su propia desaparición ---------- */

const Sala: React.FC<{paredes: number}> = ({paredes}) => (
	<div style={{position: 'absolute', inset: 0, background: '#141418'}}>
		<div style={{position: 'absolute', inset: 0, opacity: paredes, background: 'linear-gradient(180deg, #5a4a38 0%, #3a2e22 60%)'}}>
			{Array.from({length: 7}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: 40 + i * 270, top: 30, width: 200, height: 400, border: '8px solid rgba(0,0,0,0.3)', borderRadius: '100px 100px 6px 6px'}} />
			))}
		</div>
	</div>
);

const GRIS = '#6a6a72';
const ROJO_SPD = '#8a3030';
const AZUL_CONS = '#3a4a6a';

const L1: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Sala paredes={1} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.12], y: [20, 0]}} tinte="rgba(90,90,100,0.6)">
		<div style={{position: 'absolute', inset: 0, filter: 'saturate(0.45)'}}>
			<Bancadas grupos={[{color: GRIS, n: 40, levanta: pal(196, 'vota')}]} />
		</div>
	</Toma>
);

const L2: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const paredes = 1 - tramo(f, d + 4, fin(198));
	return (
		<Toma escena={<Sala paredes={paredes} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.2, 1.0]}}>
			<div style={{position: 'absolute', inset: 0, filter: 'saturate(0.45)'}}>
				<Bancadas grupos={[{color: GRIS, n: 40, levanta: -1e9}]} />
			</div>
		</Toma>
	);
};

const L3: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Sala paredes={0.6} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.16], x: [-80, -40]}}>
		<div style={{position: 'absolute', inset: 0, filter: 'saturate(0.6)'}}>
			<Bancadas grupos={[{color: ROJO_SPD, n: 12}, {color: GRIS, n: 28, levanta: -1e9}]} />
		</div>
	</Toma>
);

/** «Pueden quitarnos la libertad y la vida. Pero no el honor.» — dignidad total, sin ironía */
const L4: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Sala paredes={0.5} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.15, 1.32], y: [80, 150]}}>
		<div style={{position: 'absolute', left: 1180, top: 0, width: 420, height: 1080, background: 'linear-gradient(100deg, rgba(255,240,210,0.0), rgba(255,240,210,0.35) 40%, rgba(255,240,210,0))', transform: 'skewX(-14deg)'}} />
		<Actor x={960} y={1120} alto={1000}>
			<Muneco ropa={LIDER_SPD} pose={{...manosEn([150, 560], [250, 560]), mi: 'relajada', md: 'relajada', cabeza: -3}} ojos="normal" cejas="neutral" boca="seria" parpadea={false} />
		</Actor>
		<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(90deg, rgba(0,0,0,0.5), rgba(0,0,0,0) 50%)'}} />
	</Toma>
);

/** los conservadores de Papen votan a favor, felices; el cronómetro sigue (Papen ya desde arriba) */
const L5: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Sala paredes={0.7} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.12, 1.2], y: [-40, -70]}} angulo={-6}>
		<Bancadas grupos={[{color: AZUL_CONS, n: 30, levanta: pal(202, 'Votan'), entusiasmo: true}]} filas={3} y0={520} />
		<Actor x={960} y={1130} alto={620}>
			<Muneco ropa={PAPEN} pose={{...brazo(1, {a: 160, c: 10}), md: 'abierta', ...manosEn([150, 560]), mi: 'agarra'}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
		</Actor>
		<Cronometro x={1560} y={300} tam={200} desde={ini(185)} />
	</Toma>
);

/* ---------- haz la cuenta: 52 días ---------- */

const C10: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const para = pal(204, 'Cincuenta');
	const t = 3 + 49 * tramo(f, d + 6, para, (u) => u * u * (3 - 2 * u));
	return (
		<Toma escena={<EscLiso color="#2a2e38" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [0, -10]}} golpes={[[para, 0.06]]}>
			<Calendario60 x={820} y={110} ancho={1000} tachados={t} marca={f >= para ? 52 : undefined} />
			<Cronometro x={1640} y={520} tam={260} desde={ini(185)} para={para} brillo={f >= para ? 1 : 0} />
		</Toma>
	);
};

/* ---------- «alguien iba a terminar chillando en un rincón» ---------- */

const C11: React.FC<P> = ({d, h, e, s}) => (
	<Toma
		escena={
			<div style={{position: 'absolute', inset: 0, filter: 'sepia(0.75) saturate(0.7) brightness(0.9)'}}>
				<OficinaPapen desliza={1} palmadas habla={useCurrentFrame() < fin(205)} />
			</div>
		}
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1, 1]}}
		angulo={ANGULO_PAPEN}
		camFn={(f) => mezclaCam(ENCUADRE_CONTRATO, centrar(1180, 420, 1.45), tramo(f, d, h))}
	/>
);

/** Papen, hoy: ya no tan seguro, desde arriba */
const C12: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#2e3742" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.15, 1.22], y: [-60, -80]}} angulo={-9}>
		<Actor x={960} y={1060} alto={760}>
			<Muneco ropa={PAPEN} pose={{...manosFrente([170, 520], [230, 520]), mi: 'agarra', md: 'agarra', cabeza: 8}} ojos="mirandoLado" cejas="preocupado" boca="mueca" />
		</Actor>
	</Toma>
);

/** el mismo barrido de la apertura al rincón: ahora está el Parlamento entero, y la sombra de Hitler lo cubre (desde abajo) */
const C13: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sombra = tramo(f, d + 4, d + 40);
	return (
		<Toma escena={<EscRincon />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.18, 1.3], x: [-160, -200], y: [-60, -90]}} angulo={8}>
			<ParlamentoMini x={1240} y={930} ancho={420} />
			<div style={{position: 'absolute', left: 200 + 300 * (1 - sombra), top: -60, width: 900, height: 1100, opacity: 0.55 * sombra}}>
				<Silueta x={450} y={1100} alto={1150} ropa={HITLER_CANCILLER} tono={0} pose={{...manosEn([150, 560], [250, 560])}} />
			</div>
		</Toma>
	);
};

/* ---------- todos los partidos menos uno, prohibidos ---------- */

const PARTIDOS = ['Socialdemócrata', 'Comunista', 'Centro', 'Nacional del Pueblo', 'Popular Bávaro', 'Estatal'];

const C14: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const t = 6.2 * tramo(f, pal(208, 'todos'), fin(208));
	return (
		<Toma escena={<EscLiso color="#2a2a30" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [30, -10]}}>
			<Papeleta x={960} y={90} ancho={760} tachados={t} partidos={PARTIDOS} unico="Lista única" />
		</Toma>
	);
};

/** el partido que nunca ganó una mayoría… ahora era el único: las otras jarras desaparecen */
const C15: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const unico = pal(210, 'único');
	return (
		<Toma escena={<Barra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.1], y: [20, 40]}} golpes={[[antes(unico), 0.06]]}>
			{[260, 470, 1450, 1660].map((x, i) => {
				const v = 1 - tramo(f, ini(210) + i * 3, ini(210) + i * 3 + 6);
				return v > 0.01 ? (
					<div key={i} style={{position: 'absolute', inset: 0, transform: `scale(${v})`, transformOrigin: `${x}px 880px`}}>
						<Jarra x={x} y={880} alto={260} />
					</div>
				) : null;
			})}
			<JarraVotos x={960} y={880} alto={640} nivel={43.9} />
		</Toma>
	);
};

/* ---------- los genios todavía no habían pagado la cuenta ---------- */

const C16: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const llega = tramo(f, d + 10, d + 34, (u) => 1 - Math.pow(1 - u, 3));
	return (
		<Toma escena={<EscLiso color="#0c0d12" luz="255,210,150" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.12], y: [0, 30]}}>
			<div style={{position: 'absolute', left: -40, right: -40, top: 700, bottom: -40, background: 'linear-gradient(180deg, #2a1a10, #0a0604)', borderTop: `8px solid ${TINTA}`}} />
			<Cronometro x={1380} y={640} tam={220} desde={ini(185)} />
			{/* las manos enguantadas de Papen */}
			<div style={{position: 'absolute', left: 1520, top: 780, width: 190, height: 110, background: '#fff', border: `7px solid ${TINTA}`, borderRadius: '55px 55px 40px 40px', transform: 'rotate(-12deg)'}} />
			<Cuenta x={interpolate(llega, [0, 1], [-300, 980])} y={560} ancho={380} rot={interpolate(llega, [0, 1], [-30, -6])} />
			<Humo color="200,180,160" densidad={0.08} />
		</Toma>
	);
};

export const PLANOS_C8: Plano[] = [
	{n: 'c8-calendario', d: ini(185) - 8, e: 'latigoDer', C: C1},
	{n: 'c8-cronometro', d: antes(pal(185, 'Ese')), e: 'zoom', C: C2},
	{n: 'c8-incendio', d: ini(186), e: 'fundido', C: C3},
	{n: 'c8-detenido', d: ini(187), e: 'fundido', C: C4},
	{n: 'c8-decreto', d: ini(188), e: 'fundido', C: C5},
	{n: 'c8-candados', d: antes(pal(188, 'suspende')), e: 'fundido', C: C6},
	{n: 'c8-presos', d: ini(189), e: 'fundido', C: C7},
	{n: 'c8-calles', d: ini(190), e: 'fundido', C: C8},
	{n: 'c8-jarra', d: ini(191), e: 'zoom', C: C9},
	{n: 'c8-dachau', d: fin(193) + 2, e: 'corte', C: D1},
	{n: 'c8-presos-politicos', d: antes(ini(195)), e: 'fundido', C: D2},
	{n: 'c8-ley', d: ini(196), e: 'fundido', C: L1},
	{n: 'c8-paredes', d: ini(197), e: 'fundido', C: L2},
	{n: 'c8-spd', d: ini(199), e: 'fundido', C: L3},
	{n: 'c8-honor', d: ini(200), e: 'fundido', C: L4},
	{n: 'c8-conservadores', d: ini(201), e: 'fundido', C: L5},
	{n: 'c8-52', d: ini(203), e: 'zoom', C: C10},
	{n: 'c8-papen-dijo', d: ini(205), e: 'latigoIzq', C: C11},
	{n: 'c8-papen-hoy', d: ini(207), e: 'zoom', C: C12},
	{n: 'c8-rincon', d: antes(pal(207, 'en')), e: 'latigoDer', C: C13},
	{n: 'c8-papeleta', d: ini(208), e: 'fundido', C: C14},
	{n: 'c8-unico', d: ini(209), e: 'zoom', C: C15},
	{n: 'c8-cuenta', d: ini(211), e: 'fundido', C: C16},
];

export const SONIDOS_C8: [string, number, number][] = [
	['tictac', antes(pal(185, 'Ese')), 0.6],
	['fuego', ini(186), 0.8],
	['fuego', ini(187), 0.6],
	['clic', pal(188, 'prensa'), 0.9],
	['clic', pal(188, 'reunión'), 0.9],
	['clic', pal(188, 'expresión'), 0.9],
	['motor', ini(189), 0.5],
	['burbujas', pal(192, 'Tampoco'), 0.6],
	['tictac', ini(201) + 4, 0.5],
	['tictac', ini(203), 0.6],
	['clic', pal(204, 'Cincuenta'), 1.0],
	['dundun', antes(pal(207, 'en')) + 8, 0.6],
	['tictac', ini(211), 0.5],
	['hoja', ini(211) + 12, 0.7],
];

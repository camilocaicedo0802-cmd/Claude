import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Destello} from '../componentes/Efectos';
import {MaquinaEscribir} from '../componentes/Gamer';
import {Colgante} from '../componentes/Hacker';
import {Actor, Muneco, animarPose, manosEn, manosFrente} from '../componentes/Muneco';
import {Cara} from '../componentes/Recurrentes';
import {Toma} from '../componentes/Toma';
import {Puf} from '../componentes/Utileria';
import {BANQUERO, EDITOR, HITLER_1923, HITLER_CELDA, HITLER_TRAJE, JUEZ, SENOR_1, SENOR_2, SENOR_3, UNIFORME_MARRON} from '../componentes/Vestuario';
import {ConoLuz, EscCerveceria, EscLiso, EscMesaArriba, EscTribunal, Humo, Jarra} from '../escenarios/Epoca';
import {CONDENSADA, SERIF} from '../fuentes';
import {P, Plano, TINTA, antes, centrar, clamp, fin, golpeCam, ini, mezcla, mezclaCam, pal, tramo} from './base';
import {MesaFrente} from './c1';
import {CuadroJuezDeportar, CuadroTiroTecho, PlanoMuletilla, golpeMuletilla} from './compartidas';
import {
	AutoViejo,
	Banquillo,
	BilleteGrande,
	LapizRojoMano,
	Cama,
	Carretilla,
	CasaNoche,
	CestaFrutas,
	EscCalabozo,
	EscCalleAlba,
	EscCeldaPastel,
	EtiquetaPrecio,
	Flashes,
	Flores,
	Humareda,
	Intertitulo,
	LetreroAustria,
	LibroLeyes,
	LibroManoLiso,
	Maleta,
	ManosPistola,
	MapaAustria,
	MontanaBilletes,
	MontanaCartas,
	Pan,
	Periodico,
	PortadaLisa,
	PuertaCarcel,
	SECRETARIO,
	Silueta,
	TronoBarriles,
	enActor,
} from './utileria_c12';

/* CAPÍTULO 2 · EL GOLPE DE LA CERVECERÍA (frases 39–85).
   Paleta: ámbar de noche en la cervecería, gris frío en la calle al amanecer, celda pastel exagerada.
   «Disparos» y «Mueren dieciséis…»: serios, con fundidos, cámara lenta a la altura de los ojos y sin chiste. */

const HITLER_JUICIO = HITLER_TRAJE;

/* ---------- rótulo: el billete de mil millones ---------- */

const C2Billete: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscLiso color="#2a2216" luz="255,214,150" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.12], r: [-2, 1], y: [0, 20]}}>
			<MontanaBilletes />
			<BilleteGrande x={960} y={460 + Math.sin(f / 10) * 6} ancho={1080} rot={-4} />
		</Toma>
	);
};

/* ---------- una barra de pan que cuesta miles de millones ---------- */

const Panaderia: React.FC = () => (
	<>
		<EscLiso color="#3a2a1e" luz="255,214,150" />
		{[220, 420].map((y) => (
			<div key={y} style={{position: 'absolute', left: 120, right: 120, top: y, height: 24, background: '#6a4a2a', border: `6px solid ${TINTA}`}} />
		))}
		{[300, 560, 820, 1100, 1360, 1620].map((x, i) => (
			<Pan key={i} x={x} y={i % 2 ? 418 : 218} ancho={170} />
		))}
		<div style={{position: 'absolute', left: -40, right: -40, top: 640, height: 40, background: '#8a5a32', border: `8px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: -40, right: -40, top: 680, bottom: -2000, background: 'linear-gradient(180deg, #5a3a1e, #3a2412)'}} />
	</>
);

const C2Precio: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const t = tramo(f, d + 4, h - 4);
	return (
		<Toma escena={<Panaderia />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => {
			const u = tramo(ff, d + 4, h);
			return {s: 1.2, x: 0, y: -u * 900};
		}}>
			<Pan x={820} y={640} ancho={380} />
			<div style={{position: 'absolute', left: 1036, top: 520, width: 8, height: 120, background: TINTA}} />
			<EtiquetaPrecio x={1040} y={590} ancho={220} desenrolla={t} />
		</Toma>
	);
};

/* ---------- el sueldo en carretillas ---------- */

const C2Carretilla: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cambio = antes(pal(41, 'carretillas'));
	const mx = interpolate(f, [d - 4, cambio - 4], [200, 760], clamp) - (f > cambio + 8 ? (f - cambio - 8) * 10 : 0);
	const llevaPan = f >= cambio;
	const [px, py] = enActor(mx, 1040, 720, 320, 470);
	return (
		<Toma escena={<Panaderia />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.08, 1.15], x: [60, 20], y: [-120, -140]}}>
			<Carretilla x={llevaPan ? 1060 : mx + 300} y={1040} ancho={460} voltear />
			<Actor x={mx} y={1040} alto={720} voltear={f > cambio + 8}>
				<Muneco ropa={SENOR_1} pose={llevaPan ? {...manosEn([120, 560], [320, 470]), mi: 'relajada', md: 'agarra'} : {...manosFrente([320, 640], [340, 620]), mi: 'agarra', md: 'agarra', cuerpo: 6}} camina={f < cambio - 4 || f > cambio + 8 ? 1 : 0} ojos="normal" cejas="preocupado" boca="mueca" />
			</Actor>
			{llevaPan && <Pan x={f > cambio + 8 ? px - 2 * (px - mx) : px} y={py + 40} ancho={170} />}
		</Toma>
	);
};

/* ---------- es ahora o nunca: el pan en los ojos ---------- */

const C2Ojos: React.FC<P> = ({d, h, e, s}) => {
	const g = antes(pal(42, 'ahora'));
	const T = 900;
	const u = T / 380;
	const left = 960 - T / 2;
	const top = 60;
	const ojo = (cx: number): [number, number] => [left + T * 0.0263 + (cx - 20) * u, top + 205 * u];
	return (
		<Toma escena={<EscLiso color="#2a1a0e" luz="255,190,110" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(f) => golpeCam(f, g, centrar(960, 520, 1.0 + 0.04 * tramo(f, d, g)), centrar(960, 548, 1.75))}>
			<Cara d={HITLER_1923.cabeza} tam={T} ojos="grandes" cejas="arrogante" boca="seria" style={{position: 'absolute', left, top}} />
			{[158, 242].map((cx) => {
				const [x, y] = ojo(cx);
				return (
					<React.Fragment key={cx}>
						<div style={{position: 'absolute', left: x - 50, top: y - 50, width: 100, height: 100, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,214,120,0.7), rgba(255,214,120,0) 70%)'}} />
						<Pan x={x} y={y + 14} ancho={64} />
					</React.Fragment>
				);
			})}
		</Toma>
	);
};

/* ---------- el mitin de políticos en OTRA cervecería ---------- */

const Politicos: React.FC<{asustados?: boolean}> = ({asustados = false}) => (
	<>
		{[
			[300, SENOR_1],
			[600, BANQUERO],
			[900, SENOR_2],
			[1200, SENOR_3],
		].map(([x, ropa], i) => (
			<Actor key={i} x={x as number} y={1020} alto={560} voltear={i % 2 === 0}>
				<Muneco ropa={ropa as typeof SENOR_1} semilla={i * 5} pose={asustados ? {...manosEn([20, 300], [380, 300]), mi: 'abierta', md: 'abierta', agacha: 0.3} : {...manosFrente([170, 600], [230, 600]), mi: 'agarra', md: 'agarra', agacha: 0.3}} ojos={asustados ? 'grandes' : 'normal'} cejas={asustados ? 'sorprendido' : 'arrogante'} boca={asustados ? 'o' : 'seria'} />
			</Actor>
		))}
	</>
);

const C2Mitin: React.FC<P> = ({d, h, e, s}) => {
	const g = antes(pal(44, 'otra', 2));
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscCerveceria tono="ambar" vacia humo={0.24} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => golpeCam(ff, g, centrar(960, 560, 1.04 + 0.06 * tramo(ff, d, g)), centrar(600, 800, 2.5))}>
			{/* atril con orador */}
			<Actor x={1620} y={980} alto={700} voltear>
				<Muneco ropa={SENOR_3} pose={{...brazo1(f)}} ojos="normal" cejas="arrogante" boca="seria" hablando={f < g} />
			</Actor>
			<div style={{position: 'absolute', left: 1500, top: 700, width: 240, height: 300, background: '#5a3a1e', border: `8px solid ${TINTA}`, clipPath: 'polygon(8% 0, 92% 0, 100% 100%, 0 100%)'}} />
			<Politicos />
			<MesaFrente x={760} y={860} ancho={1300} />
			{[360, 600, 900, 1160].map((x, i) => (
				<Jarra key={i} x={x} y={848} alto={110} />
			))}
		</Toma>
	);
};
const brazo1 = (f: number) => ({...manosEn([130, 560], [330 + Math.sin(f / 6) * 20, 300]), mi: 'puno' as const, md: 'abierta' as const});

/* ---------- Hitler entra con sus hombres ---------- */

const C2Entra: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const abre = tramo(f, d - 2, d + 5, (t) => 1 - Math.pow(1 - t, 3));
	const paso = tramo(f, d + 2, h - 4);
	return (
		<Toma escena={<EscCerveceria tono="ambar" vacia humo={0.24} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.12], x: [0, -40]}} golpes={[[d + 2, 0.06]]}>
			{/* la puerta que se abre de una patada */}
			<div style={{position: 'absolute', left: 760, top: 220, width: 420, height: 660, background: '#120a04', border: `10px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 760, top: 220, width: 420, height: 660, background: '#5a3a1e', border: `10px solid ${TINTA}`, transform: `perspective(1400px) rotateY(${-100 * abre}deg)`, transformOrigin: '0 50%'}} />
			{[1, 2, 0].map((i) => (
				<Actor key={i} x={[970, 800, 1140][i]} y={(i === 0 ? 930 : 880) + paso * 80 * (i === 0 ? 1 : 0.6)} alto={[700, 560, 560][i] + paso * 60}>
					<Muneco ropa={i === 0 ? HITLER_1923 : UNIFORME_MARRON} semilla={i} pose={i === 0 ? {...manosEn([20, 260], [380, 260]), mi: 'abierta', md: 'abierta'} : {...manosFrente([170, 560], [230, 560]), mi: 'puno', md: 'puno'}} camina={1} ojos={i === 0 ? 'grandes' : 'normal'} cejas="enojado" boca={i === 0 ? 'grito' : 'seria'} />
				</Actor>
			))}
			<Politicos asustados={f > d + 6} />
			<MesaFrente x={760} y={900} ancho={1300} />
		</Toma>
	);
};

/* ---------- se sube a una silla y dispara al techo ---------- */

const Hombres: React.FC = () => (
	<>
		{[380, 1540].map((x, i) => (
			<Actor key={i} x={x} y={1080} alto={640} voltear={i === 1}>
				<Muneco ropa={UNIFORME_MARRON} semilla={i * 2} pose={{...manosFrente([170, 560], [230, 560]), mi: 'puno', md: 'puno'}} ojos="normal" cejas="enojado" boca="seria" />
			</Actor>
		))}
	</>
);

const disparoTecho = () => antes(pal(45, 'dispara')) + 2;

const C2Tiro: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<CuadroTiroTecho disparo={disparoTecho()} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [30, 50]}} angulo={-5} golpes={[[disparoTecho(), 0.06]]}>
		<Hombres />
	</Toma>
);

const C2Grito: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sube = d + Math.round((h - d) * 0.5);
	return (
		<Toma
			escena={<CuadroTiroTecho disparo={disparoTecho()} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			angulo={interpolate(f, [sube, sube + 16], [0, -16], clamp)}
			camFn={(ff) => mezclaCam(centrar(960, 230, 2.3), centrar(960, 560, 1.0), tramo(ff, sube, sube + 16))}
		>
			<Hombres />
		</Toma>
	);
};

/* ---------- el dueño de Baviera por una noche ---------- */

const C2Trono: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const t = tramo(f, d, h);
	return (
		<Toma
			escena={
				<>
					<EscCerveceria tono="noche" vacia humo={0.15} />
					<div style={{position: 'absolute', left: 1380, top: 140, width: 380, height: 420, background: `linear-gradient(180deg, ${mezcla('#1c2440', '#f0a050', t)} 0%, ${mezcla('#2a3050', '#ffd08a', t)} 100%)`, border: `10px solid ${TINTA}`}}>
						<div style={{position: 'absolute', left: '50%', top: 0, bottom: 0, width: 10, background: TINTA, marginLeft: -5}} />
						<div style={{position: 'absolute', top: '50%', left: 0, right: 0, height: 10, background: TINTA, marginTop: -5}} />
					</div>
					<div style={{position: 'absolute', left: 900, top: 0, width: 1100, height: 1080, background: `radial-gradient(ellipse at 60% 30%, rgba(255,190,110,${0.35 * t}), rgba(255,190,110,0) 60%)`, mixBlendMode: 'screen'}} />
				</>
			}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.05, 1.15], y: [20, 50]}}
			angulo={-4}
		>
			{/* respaldo: un barril de pie, con cojín rojo */}
			<div style={{position: 'absolute', left: 730, top: 90, width: 340, height: 520, background: 'linear-gradient(90deg, #5a3a1e, #8a5a30 50%, #5a3a1e)', border: `9px solid ${TINTA}`, borderRadius: '70px / 120px'}}>
				<div style={{position: 'absolute', left: 60, right: 60, top: 70, bottom: 70, background: '#a8262e', border: `7px solid ${TINTA}`, borderRadius: 40}} />
			</div>
			<Actor x={900} y={600} alto={520}>
				<Muneco ropa={HITLER_1923} pose={{...manosEn([40, 520], [360, 520]), mi: 'puno', md: 'puno', cabeza: -4}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
			</Actor>
			<svg viewBox="0 0 200 110" width={150} height={82} style={{position: 'absolute', left: 900 - 75, top: 60, overflow: 'visible', transform: 'rotate(-8deg)'}}>
				<path d="M 10 100 L 10 30 L 55 70 L 100 10 L 145 70 L 190 30 L 190 100 Z" fill="#e0b23a" stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
			</svg>
			<TronoBarriles x={900} y={1040} ancho={640} corona={false} />
		</Toma>
	);
};

/* ---------- la marcha, la policía y los disparos (sin chiste) ---------- */

const Marchantes: React.FC<{x0: number; avance: number; n?: number; sale?: number}> = ({x0, avance, n = 9, sale = 0}) => {
	const f = useCurrentFrame();
	return (
		<>
			{Array.from({length: n}, (_, i) => {
				const fila = i % 3;
				const x = x0 + avance - Math.floor(i / 3) * 170 - fila * 50;
				return <Silueta key={i} x={x - sale * (300 + i * 60)} y={860 + fila * 60} alto={380 + fila * 40} tipo="civil" paso={f / 3 + i} opacidad={1 - sale} />;
			})}
		</>
	);
};

const C2Marcha: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscCalleAlba />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.08], x: [60, -40]}}>
			<Marchantes x0={300} avance={(f - d) * 3} />
		</Toma>
	);
};

const Policias: React.FC<{sale?: number}> = ({sale = 0}) => (
	<>
		{Array.from({length: 7}, (_, i) => (
			<Silueta key={i} x={1220 + i * 100 + sale * (200 + i * 40)} y={900 + (i % 2) * 20} alto={420} tipo="policia" color="#1c2026" opacidad={1 - sale} />
		))}
	</>
);

const C2Policia: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const tiros = ini(50);
	return (
		<Toma escena={<EscCalleAlba />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.08], x: [0, -20]}}>
			<Policias />
			<Marchantes x0={500} avance={Math.min(f, tiros) - d} />
			<Humareda x={960} y={780} desde={tiros} ancho={1100} />
			<Destello desde={tiros} color="#fffbe8" fuerza={0.7} duracion={8} />
		</Toma>
	);
};

const C2Muertos: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sale = tramo(f, d + 6, h);
	return (
		<Toma escena={<EscCalleAlba />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.06], x: [30, -30]}}>
			<Policias sale={sale} />
			<Marchantes x0={560} avance={0} sale={sale} />
			<Humareda x={960} y={780} desde={d - 40} ancho={1300} />
			<Humo color="220,224,230" densidad={0.22} />
		</Toma>
	);
};

/* ---------- se disloca el hombro, se sube a un auto… y se va ---------- */

const Cabestrillo = <path d="M 168 290 Q 140 420 196 506 L 286 480 Q 250 380 232 290 Z" fill="#f4f4f0" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />;

const C2Huye: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const auto = antes(pal(53, 'auto'));
	const x = interpolate(f, [d, auto], [120, 1240], clamp);
	const salta = tramo(f, auto, auto + 8);
	return (
		<Toma escena={<EscCalleAlba frio={0} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.1], x: [80, -80]}}>
			<AutoViejo x={1520} y={1010} ancho={640} puerta={f > auto - 6 && f < auto + 10 ? 1 : 0} />
			<Actor x={x + salta * 200} y={1010 - Math.sin(salta * Math.PI) * 140} alto={640} opacidad={1 - tramo(f, auto + 6, auto + 9)}>
				<Muneco ropa={HITLER_1923} pose={{...manosEn([236, 470]), mi: 'puno', bd: 70 + Math.sin(f / 2) * 30, cd: 30, md: 'abierta', cuerpo: 10}} objPecho={Cabestrillo} camina={f < auto ? 2.4 : 0} ojos="grandes" cejas="preocupado" boca="grito" />
			</Actor>
		</Toma>
	);
};

const C2Polvo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const x = interpolate(f, [d + 2, d + 20], [1300, 3000], {...clamp, easing: (t) => t * t});
	return (
		<Toma escena={<EscCalleAlba frio={0} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.14]}} sacudida={(ff) => (ff < d + 16 ? 4 : 0)}>
			<AutoViejo x={x} y={1010} ancho={640} rueda={f * 40} />
			<Puf x={1150} y={930} desde={d + 2} tam={900} />
			<Puf x={1500} y={960} desde={d + 6} tam={700} />
		</Toma>
	);
};

/* ---------- lo encuentran escondido; la mano que le quita la pistola ---------- */

const C2Escondido: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const avance = tramo(f, d, h);
	return (
		<Toma escena={<CasaNoche />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.16], x: [0, -60], y: [0, -20]}}>
			{/* Hitler asomado, escondido tras la ventana */}
			<div style={{position: 'absolute', left: 1108, top: 528, width: 164, height: 144, overflow: 'hidden'}}>
				<Cara d={HITLER_1923.cabeza} tam={120} ojos="grandes" cejas="preocupado" boca="mueca" style={{position: 'absolute', left: 36 + Math.sin(f / 8) * 14, top: 60 + Math.max(0, Math.sin(f / 11)) * 40}} />
			</div>
			{[0, 1, 2].map((i) => (
				<Silueta key={i} x={180 + avance * 520 - i * 130} y={880 + i * 10} alto={360} tipo="policia" color="#0e1220" paso={f / 4 + i} />
			))}
		</Toma>
	);
};

const C2Manos: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const toma = tramo(f, antes(pal(56, 'esposa')), pal(56, 'pistola') + 14);
	return <Toma escena={<ManosPistola toma={toma} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], x: [20, -20]}} />;
};

/* ---------- «Fin.» y el periódico ---------- */

const C2Fin: React.FC<P> = ({d, h, e, s}) => <Toma escena={<Intertitulo texto="Fin" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05]}} />;

const C2Periodico: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscMesaArriba tono="oscura" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.1], r: [1, -1]}}>
		<Periodico x={960} y={540} ancho={1200} titular="FRACASA EL GOLPE DE LA CERVECERÍA" sub="No duró ni un día" desde={d + 2} />
	</Toma>
);

/* ---------- el expediente: primer sello ---------- */

const C2Muletilla: React.FC<P> = (p) => <PlanoMuletilla {...p} i={59} n={1} />;

/* ---------- el juicio y el juez comprensivo ---------- */

const EstradoDelante: React.FC = () => <div style={{position: 'absolute', left: 560, top: 470, width: 800, height: 300, background: 'linear-gradient(180deg, #4a3220, #2e1e12)', border: `9px solid ${TINTA}`, borderRadius: 8}} />;

const C2Tribunal: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscTribunal tono="munich" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.1], x: [60, -40]}} angulo={-3}>
		<Actor x={960} y={800} alto={560}>
			<Muneco ropa={JUEZ} pose={{...manosFrente([170, 600], [230, 600]), mi: 'agarra', md: 'agarra'}} ojos="feliz" cejas="neutral" boca="sonrisa" />
		</Actor>
		<EstradoDelante />
		<Actor x={1520} y={1060} alto={620}>
			<Muneco ropa={HITLER_JUICIO} pose={{...manosFrente([170, 600], [230, 600]), mi: 'agarra', md: 'agarra', cabeza: -6}} ojos="mirandoLado" cejas="arrogante" boca="seria" />
		</Actor>
		<Banquillo x={1520} y={820} ancho={520} />
	</Toma>
);

const C2Juez: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const digamos = ini(62);
	return (
		<Toma escena={<EscTribunal tono="munich" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.12], y: [-10, -30]}} angulo={6}>
			<Actor x={960} y={1180} alto={1040}>
				<Muneco ropa={JUEZ} pose={{...manosEn(undefined, [224, 262]), md: 'puno', frenteD: 1, ...manosFrente([150, 640]), mi: 'relajada', cabeza: f >= digamos ? 10 : 4}} ojos="feliz" cejas="preocupado" boca="sonrisa" />
			</Actor>
			<div style={{position: 'absolute', left: 420, top: 820, width: 1080, height: 300, background: 'linear-gradient(180deg, #4a3220, #2e1e12)', border: `9px solid ${TINTA}`, borderRadius: 8}} />
			{f >= digamos &&
				[0, 1, 2].map((i) => {
					const u = ((f - digamos + i * 9) % 30) / 30;
					return (
						<svg key={i} width={70} height={64} viewBox="0 0 100 90" style={{position: 'absolute', left: 1200 + i * 60, top: 360 - u * 200, opacity: 1 - u}}>
							<path d="M 50 86 C 10 56 0 30 20 14 C 36 2 50 16 50 26 C 50 16 64 2 80 14 C 100 30 90 56 50 86 Z" fill="#f08ab0" stroke={TINTA} strokeWidth={7} />
						</svg>
					);
				})}
		</Toma>
	);
};

const C2Habla: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const rollo = tramo(f, d, h);
	const [hx, hy] = enActor(1240, 1060, 700, 320, 470);
	return (
		<Toma escena={<EscTribunal tono="munich" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.15, 1.25], x: [-140, -180], y: [-60, -80]}} angulo={-4}>
			<Actor x={760} y={800} alto={480}>
				<Muneco ropa={JUEZ} pose={{...manosFrente([170, 600], [230, 600]), mi: 'agarra', md: 'agarra', cabeza: Math.sin(f / 6) * 8}} ojos="feliz" cejas="neutral" boca="sonrisa" />
			</Actor>
			<EstradoDelante />
			<Actor x={1240} y={1060} alto={700}>
				<Muneco ropa={HITLER_JUICIO} pose={{...manosEn([60, 330 + Math.sin(f / 5) * 40]), mi: 'puno', ...manosFrente(undefined, [320, 470]), md: 'agarra'}} ojos="grandes" cejas="enojado" boca="abierta" hablando />
			</Actor>
			<Banquillo x={1240} y={820} ancho={520} />
			{/* el discurso, larguísimo, que se desenrolla hasta el suelo */}
			<div style={{position: 'absolute', left: hx - 50, top: hy, width: 120, height: 80 + rollo * 900, background: 'repeating-linear-gradient(180deg, #fbf8ef 0 30px, #e9e2cc 30px 34px)', border: `6px solid ${TINTA}`, borderRadius: 8, transform: 'rotate(-4deg)', transformOrigin: '50% 0'}} />
		</Toma>
	);
};

/* ---------- el juicio se vuelve un show… y sale famoso ---------- */

const C2Show: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const telon = tramo(f, d, d + 18);
	const famoso = antes(ini(65));
	return (
		<Toma
			escena={<EscTribunal tono="munich" />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			angulo={-3}
			camFn={(ff) => mezclaCam(centrar(960, 600, 1.7), centrar(960, 540, 1.0), tramo(ff, d + 6, famoso + 6))}
		>
			<div style={{position: 'absolute', inset: 0, background: `rgba(0,0,0,${0.45 * telon})`}} />
			<ConoLuz x={960} y={-80} ancho={900} alto={1160} fuerza={0.6 * telon} />
			<Actor x={960} y={1060} alto={700}>
				<Muneco ropa={HITLER_JUICIO} pose={{...manosEn([20, 250], [380, 250]), mi: 'abierta', md: 'abierta'}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
			</Actor>
			<Banquillo x={960} y={820} ancho={560} />
			{/* telón rojo */}
			{[0, 1].map((lado) => (
				<div key={lado} style={{position: 'absolute', top: -40, bottom: -40, width: 520 * telon + 20, [lado ? 'right' : 'left']: -20, background: 'repeating-linear-gradient(90deg, #8e1a22 0 60px, #b82a30 60px 120px)', border: `10px solid ${TINTA}`}} />
			))}
			<div style={{position: 'absolute', left: -20, right: -20, top: -40, height: 150 * telon, background: '#8e1a22', border: `10px solid ${TINTA}`, borderRadius: '0 0 60px 60px'}} />
			{/* candilejas */}
			{Array.from({length: 12}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: 100 + i * 155, top: 1040, width: 40, height: 30, borderRadius: '50% 50% 0 0', background: '#fff3c0', boxShadow: `0 0 30px 10px rgba(255,230,160,${0.6 * telon})`}} />
			))}
			{/* periódicos con su cara, volando */}
			{f >= famoso &&
				Array.from({length: 7}, (_, i) => {
					const t = f - famoso - i * 2;
					if (t < 0) return null;
					const x = -300 + t * (24 + i * 3) + i * 60;
					const y = 160 + ((i * 137) % 520) + Math.sin(t / 5 + i) * 30;
					return (
						<div key={i} style={{position: 'absolute', left: x, top: y, width: 220, height: 160, background: '#efe9d8', border: `5px solid ${TINTA}`, transform: `rotate(${Math.sin(t / 6 + i) * 25}deg)`, padding: 8, boxSizing: 'border-box'}}>
							<div style={{fontFamily: CONDENSADA, fontSize: 30, textAlign: 'center', color: '#1e1a14'}}>¡HITLER!</div>
							<Cara d={HITLER_JUICIO.cabeza} tam={80} ojos="feliz" cejas="arrogante" boca="sonrisa" style={{position: 'absolute', left: 64, top: 52}} />
						</div>
					);
				})}
		</Toma>
	);
};

/* ---------- cinco años… nueve meses ---------- */

const CalendarioCondena: React.FC<{x: number; y: number}> = ({x, y}) => {
	const f = useCurrentFrame();
	const t1 = ini(67);
	const t2 = antes(ini(68));
	const v = f < t1 ? 60 : Math.round(interpolate(f, [t1, t2], [60, 9], clamp));
	const texto = f < t1 ? ['5', 'AÑOS'] : [String(v), 'MESES'];
	const N = 14;
	return (
		<>
			<div style={{position: 'absolute', left: x - 330, top: y - 360, width: 660, height: 720, background: '#fbf8ef', border: `12px solid ${TINTA}`, borderRadius: 16, boxShadow: '18px 22px 0 rgba(0,0,0,0.35)', textAlign: 'center', fontFamily: CONDENSADA, color: '#2a2218', overflow: 'hidden'}}>
				<div style={{background: '#a8262e', color: '#fbf8ef', fontSize: 80, letterSpacing: 8, borderBottom: `10px solid ${TINTA}`, padding: '10px 0'}}>CONDENA</div>
				<div style={{fontSize: 330, lineHeight: 1.05, marginTop: 10}}>{texto[0]}</div>
				<div style={{fontSize: 110, letterSpacing: 10}}>{texto[1]}</div>
			</div>
			{Array.from({length: N}, (_, k) => {
				const tk = t1 + ((t2 - t1) * k) / N;
				const u = f - tk;
				if (u < 0 || u > 9) return null;
				const vale = Math.round(60 - (51 * k) / N);
				return (
					<div key={k} style={{position: 'absolute', left: x - 300 + u * (70 + (k % 3) * 20), top: y - 220 - u * u * 6, width: 600, height: 520, background: '#fbf8ef', border: `8px solid ${TINTA}`, borderRadius: 12, transform: `rotate(${u * (k % 2 ? 9 : -7)}deg) scale(${1 - u * 0.05})`, opacity: 1 - u / 9, textAlign: 'center', fontFamily: CONDENSADA, color: '#2a2218'}}>
						<div style={{fontSize: 300, lineHeight: 1.2}}>{vale}</div>
					</div>
				);
			})}
		</>
	);
};

const C2Calendario: React.FC<P> = ({d, h, e, s}) => {
	const g = antes(ini(68));
	return (
		<Toma escena={<EscLiso color="#2a2a30" luz="255,230,200" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(f) => golpeCam(f, g, centrar(960, 540, 1.0 + 0.04 * tramo(f, d, g)), centrar(960, 600, 1.45))}>
			<CalendarioCondena x={960} y={560} />
		</Toma>
	);
};

/* ---------- no en un calabozo: una celda de hotel ---------- */

const C2Calabozo: React.FC<P> = ({d, h, e, s}) => <Toma escena={<EscCalabozo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.18], y: [0, 30]}} />;

const Barriga: React.FC<{g: number}> = ({g}) => <ellipse cx={200} cy={470 + g * 10} rx={70 + g * 50} ry={60 + g * 40} fill={HITLER_CELDA.casaca} stroke={TINTA} strokeWidth={7} />;

const C2Celda: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const engorda = antes(ini(71));
	const g = tramo(f, engorda, engorda + 20);
	return (
		<Toma
			escena={<EscCeldaPastel />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => {
				const a = mezclaCam(centrar(620, 600, 1.3), centrar(1300, 600, 1.3), tramo(ff, d, engorda));
				return mezclaCam(a, centrar(1060, 640, 1.55), tramo(ff, engorda, engorda + 12));
			}}
		>
			<Cama x={520} y={940} ancho={620} />
			<MontanaCartas x={560} y={1000} ancho={420} />
			{/* puerta con NO MOLESTAR */}
			<div style={{position: 'absolute', left: 1660, top: 260, width: 240, height: 580, background: '#c9e8f5', border: `10px solid ${TINTA}`, borderRadius: '10px 10px 0 0'}} />
			<Colgante x={1720} y={520} texto={'NO\nMOLESTAR'} tam={0.8} color="#f6b9c9" />
			<div style={{position: 'absolute', left: 1360, top: 760, width: 260, height: 30, background: '#e9c9a0', border: `7px solid ${TINTA}`}} />
			<Flores x={1420} y={762} tam={0.9} />
			<CestaFrutas x={1540} y={762} tam={0.8} />
			<Actor x={1060} y={1020} alto={720}>
				<Muneco ropa={HITLER_CELDA} pose={{...manosFrente([170, 520], [250, 470]), mi: 'relajada', md: 'agarra', agacha: 0.2}} objPecho={g > 0 ? <Barriga g={g} /> : undefined} objDer={<g transform="translate(0 40)"><rect x={-40} y={0} width={80} height={56} fill="#fbf8ef" stroke={TINTA} strokeWidth={5} /></g>} ojos="feliz" cejas="neutral" boca="sonrisa" />
			</Actor>
			{/* regalos */}
			<div style={{position: 'absolute', left: 800, top: 900, width: 120, height: 100, background: '#7ab8e0', border: `7px solid ${TINTA}`}}>
				<div style={{position: 'absolute', left: 48, top: -6, width: 14, height: 106, background: '#f05a7a'}} />
			</div>
		</Toma>
	);
};

/* ---------- se aburre y dicta un libro ---------- */

const C2Dicta: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const titulo = ini(73);
	return (
		<Toma escena={<EscCeldaPastel />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => mezclaCam(centrar(900, 600, 1.12), centrar(1240, 760, 1.6), tramo(ff, titulo, titulo + 30))}>
			<Actor x={interpolate(f, [d, h], [520, 760], clamp)} y={1010} alto={720}>
				<Muneco ropa={HITLER_CELDA} pose={{...manosEn([40, 280 + Math.sin(f / 6) * 50], [300, 520]), mi: 'abierta', md: 'puno'}} objPecho={<Barriga g={1} />} camina={0.7} ojos="entrecerrados" cejas="arrogante" boca="abierta" hablando />
			</Actor>
			<Actor x={1240} y={1010} alto={620}>
				<Muneco ropa={SECRETARIO} pose={{...manosFrente([170, 600 + Math.sin(f) * 6], [230, 600 - Math.sin(f) * 6]), mi: 'relajada', md: 'relajada', agacha: 0.3}} ojos="entrecerrados" cejas="preocupado" boca="seria" />
			</Actor>
			<MesaFrente x={1240} y={860} ancho={480} color="#e9c9a0" mantel="#f6b9c9" />
			<MaquinaEscribir x={1240} y={860} ancho={380} hoja={0.6} titular=" " desde={1e9} />
		</Toma>
	);
};

/* ---------- el título original no cabe en la portada ---------- */

const TITULO_LARGO = 'Cuatro años y medio de lucha contra las mentiras, la estupidez y la cobardía';

const C2Titulo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const n = interpolate(f, [d + 2, fin(74) - 2], [0, 14], clamp);
	return (
		<Toma escena={<EscMesaArriba tono="oscura" luz={[900, 500]} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => mezclaCam(centrar(800, 480, 1.08), centrar(1180, 480, 1.08), tramo(ff, d, h))}>
			<PortadaLisa x={700} y={500} ancho={540} titulo={TITULO_LARGO} palabras={n} rot={0} />
			<MaquinaEscribir x={960} y={1260} ancho={1000} hoja={0} titular=" " desde={1e9} />
		</Toma>
	);
};

const C2Editor: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const t0 = antes(pal(75, 'mejor'));
	const t1 = antes(ini(76)) - 2;
	const tacha = tramo(f, t0, t1, (t) => t);
	const corto = tramo(f, antes(ini(76)), antes(ini(76)) + 12);
	const rayando = tacha > 0 && tacha < 1;
	const bd = rayando ? 92 + Math.sin(f * 0.9) * 22 - tacha * 10 : 40;
	return (
		<Toma escena={<EscLiso color="#3a3024" luz="255,220,170" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => mezclaCam(centrar(1100, 560, 1.05), centrar(1000, 560, 1.28), tramo(ff, t0 - 10, t0 + 10))}>
			<div style={{position: 'absolute', left: 700, top: 900, width: 30, height: 200, background: '#6a4a2a', border: `6px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 990, top: 900, width: 30, height: 200, background: '#6a4a2a', border: `6px solid ${TINTA}`}} />
			<PortadaLisa x={860} y={560} ancho={480} titulo={TITULO_LARGO} tachado={tacha} corto={corto} rot={0} ajustado />
			<Actor x={1480 + tacha * 60} y={1060} alto={820} voltear>
				<Muneco ropa={EDITOR} pose={{bd, cd: 8, md: 'agarra', ...manosFrente([170, 560]), cabeza: 6}} objDer={corto < 0.5 ? <LapizRojoMano /> : undefined} ojos="entrecerrados" cejas="arrogante" boca={rayando ? 'mueca' : 'seria'} hablando={f >= ini(75) + 30 && f < fin(75)} />
			</Actor>
		</Toma>
	);
};

/* ---------- ni siquiera era alemán: era austríaco ---------- */

const C2Austria: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const salta = antes(pal(78, 'austríaco'));
	const t = tramo(f, salta, salta + 12);
	const x = interpolate(t, [0, 1], [960, 1330]);
	const y = interpolate(t, [0, 1], [640, 790]) - Math.sin(t * Math.PI) * 160;
	return (
		<Toma escena={<MapaAustria flecha={0} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.2], x: [0, -60], y: [-40, -80]}} golpes={[[salta + 12, 0.06]]}>
			<div style={{position: 'absolute', left: x - 6, top: y + 40, width: 12, height: 50, background: TINTA}} />
			<Cara d={HITLER_CELDA.cabeza} tam={150} ojos={t > 0.9 ? 'grandes' : 'normal'} cejas={t > 0.9 ? 'sorprendido' : 'arrogante'} boca={t > 0.9 ? 'o' : 'seria'} style={{position: 'absolute', left: x - 75, top: y - 110}} />
		</Toma>
	);
};

/* ---------- la ley: se le deporta (flecha hacia Austria) ---------- */

const C2Ley: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const dep = antes(pal(79, 'deporta'));
	return (
		<Toma escena={<MapaAustria flecha={tramo(f, dep + 6, dep + 24)} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => mezclaCam(centrar(560, 380, 1.4), centrar(1130, 760, 1.35), tramo(ff, dep - 2, dep + 16))}>
			<LibroLeyes x={560} y={360} ancho={880} resalta={tramo(f, d + 20, d + 34)} />
		</Toma>
	);
};

/* ---------- ¿lo deportaron? No. ---------- */

const C2No: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const no = antes(ini(81));
	const porque = antes(ini(82));
	const niega = f >= no && f < porque ? Math.sin((f - no) / 2.2) * 12 : 0;
	return (
		<Toma escena={<EscTribunal tono="munich" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.12], y: [-10, -30]}} angulo={6} golpes={[[no, 0.06]]}>
			<Actor x={960} y={1180} alto={1040}>
				<Muneco ropa={JUEZ} pose={f >= porque ? {...manosEn(undefined, [240, 372]), md: 'abierta', ...manosFrente([150, 640]), cabeza: 8} : {...manosFrente([150, 640], [250, 640]), cabeza: niega}} ojos="feliz" cejas="neutral" boca="sonrisa" />
			</Actor>
			<div style={{position: 'absolute', left: 420, top: 820, width: 1080, height: 300, background: 'linear-gradient(180deg, #4a3220, #2e1e12)', border: `9px solid ${TINTA}`, borderRadius: 8}} />
		</Toma>
	);
};

/* ---------- el juez parte el sello de DEPORTAR (se cumple el adelanto) ---------- */

const C2Rompe: React.FC<P> = ({d, h, e, s}) => <Toma escena={<CuadroJuezDeportar rompe={antes(pal(83, 'alemana'))} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.3], y: [60, 110]}} angulo={4} />;

/* ---------- sale antes, sale famoso, sale con libro… y se queda ---------- */

const C2Sale: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const s1 = antes(pal(84, 'sale', 1));
	const s2 = antes(pal(84, 'sale', 2));
	const s3 = antes(pal(84, 'sale', 3));
	const queda = antes(ini(85));
	const sal = tramo(f, s1 + 4, s3);
	const alto = 560 + sal * 220;
	const pie = 860 + sal * 170;
	const suelta = f >= queda;
	const [mx, my] = enActor(960, pie, alto, 300, 650);
	return (
		<Toma
			escena={<PuertaCarcel abre={tramo(f, s1, s1 + 10)} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.02, 1.1]}}
			angulo={-4}
			golpes={[
				[s1, 0.04],
				[s2, 0.05],
				[s3, 0.05],
				[queda, 0.05],
			]}
		>
			<Actor x={960} y={pie} alto={alto} opacidad={tramo(f, s1 + 2, s1 + 8)}>
				<Muneco ropa={HITLER_TRAJE} pose={{...manosEn([140, 420]), mi: 'oculta', ...manosEn(undefined, [300, 640]), md: suelta ? 'abierta' : 'agarra'}} objIzq={f >= s3 ? <LibroManoLiso rot={-60} /> : undefined} camina={f > s1 + 4 && f < s3 ? 1 : 0} ojos={f >= s2 ? 'feliz' : 'normal'} cejas="arrogante" boca={f >= s2 ? 'sonrisaGrande' : 'seria'} />
			</Actor>
			{f > s1 + 4 && <Maleta x={suelta ? mx + 40 : mx} y={suelta ? Math.min(pie, my + 200 + (f - queda) * 40) : my + 140} ancho={180} rot={suelta ? 0 : -4} />}
			<LetreroAustria x={1520} y={420} opacidad={1 - tramo(f, queda + 4, queda + 18)} />
			<Flashes desde={s2} n={9} />
		</Toma>
	);
};

export const PLANOS_C2: Plano[] = [
	{n: 'c2-billete', d: fin(38) + 2, e: 'latigoDer', C: C2Billete},
	{n: 'c2-precio', d: antes(pal(39, 'cuesta')), e: 'latigoIzq', C: C2Precio},
	{n: 'c2-carretilla', d: ini(41), e: 'latigoDer', C: C2Carretilla},
	{n: 'c2-ojos', d: ini(42), e: 'zoom', C: C2Ojos},
	{n: 'c2-mitin', d: ini(43), e: 'latigoIzq', C: C2Mitin},
	{n: 'c2-entra', d: ini(45), e: 'latigoDer', C: C2Entra},
	{n: 'c2-tiro', d: antes(pal(45, 'sube')), e: 'latigoIzq', C: C2Tiro},
	{n: 'c2-grito', d: ini(46), e: 'zoom', C: C2Grito},
	{n: 'c2-trono', d: ini(47), e: 'latigoDer', C: C2Trono},
	{n: 'c2-marcha', d: ini(48), e: 'latigoIzq', C: C2Marcha},
	{n: 'c2-policia', d: ini(49), e: 'fundido', C: C2Policia},
	{n: 'c2-muertos', d: ini(51), e: 'fundido', C: C2Muertos},
	{n: 'c2-huye', d: ini(52), e: 'fundido', C: C2Huye},
	{n: 'c2-polvo', d: ini(54), e: 'latigoDer', C: C2Polvo},
	{n: 'c2-escondido', d: ini(55), e: 'latigoIzq', C: C2Escondido},
	{n: 'c2-manos', d: antes(pal(56, 'quiso')), e: 'fundido', C: C2Manos},
	{n: 'c2-fin', d: ini(57), e: 'fundido', C: C2Fin},
	{n: 'c2-periodico', d: ini(58), e: 'latigoDer', C: C2Periodico},
	{n: 'c2-muletilla', d: ini(59), e: 'zoom', C: C2Muletilla},
	{n: 'c2-tribunal', d: ini(60), e: 'latigoDer', C: C2Tribunal},
	{n: 'c2-juez', d: ini(61), e: 'zoom', C: C2Juez},
	{n: 'c2-habla', d: ini(63), e: 'latigoIzq', C: C2Habla},
	{n: 'c2-show', d: ini(64), e: 'zoom', C: C2Show},
	{n: 'c2-calendario', d: ini(66), e: 'latigoDer', C: C2Calendario},
	{n: 'c2-calabozo', d: ini(69), e: 'latigoIzq', C: C2Calabozo},
	{n: 'c2-celda', d: ini(70), e: 'latigoDer', C: C2Celda},
	{n: 'c2-dicta', d: ini(72), e: 'latigoIzq', C: C2Dicta},
	{n: 'c2-titulo', d: ini(74), e: 'zoom', C: C2Titulo},
	{n: 'c2-editor', d: ini(75), e: 'latigoDer', C: C2Editor},
	{n: 'c2-austria', d: ini(77), e: 'latigoIzq', C: C2Austria},
	{n: 'c2-ley', d: ini(79), e: 'latigoDer', C: C2Ley},
	{n: 'c2-no', d: ini(80), e: 'zoom', C: C2No},
	{n: 'c2-rompe', d: ini(83), e: 'latigoDer', C: C2Rompe},
	{n: 'c2-sale', d: ini(84), e: 'latigoIzq', C: C2Sale},
];

export const SONIDOS_C2: [string, number, number][] = [
	['caja', fin(38) + 8, 0.6],
	['ticket', antes(pal(39, 'cuesta')) + 4, 0.7],
	['objeto', antes(pal(41, 'carretillas')), 0.6],
	['dundun', antes(pal(42, 'ahora')), 0.6],
	['murmullo', ini(43), 0.6],
	['puerta', ini(45), 0.9],
	['disparo', antes(pal(45, 'dispara')) + 2, 0.9],
	['pasos', ini(48), 0.6],
	['disparo', ini(50), 0.55],
	['disparo', ini(50) + 5, 0.4],
	['motor', antes(pal(53, 'auto')), 0.6],
	['puertaauto', antes(pal(53, 'auto')) + 6, 0.7],
	['derrape', ini(54) + 2, 0.8],
	['viento', ini(55), 0.5],
	['proyector', ini(57), 0.6],
	['hoja', ini(58) + 2, 0.7],
	['sello', golpeMuletilla(59), 1.0],
	['mazo', ini(60) + 6, 0.9],
	['hoja', ini(63) + 6, 0.5],
	['aplausos', ini(64) + 10, 0.7],
	['sobres', antes(ini(65)), 0.6],
	['sobres', ini(67), 0.7],
	['ding', antes(ini(68)), 0.7],
	['arpa', ini(70), 0.6],
	['boing', antes(ini(71)), 0.6],
	['teclas', ini(72) + 10, 0.5],
	['teclas', ini(74) + 2, 0.8],
	['ding', fin(74), 0.6],
	['garabato', antes(pal(75, 'mejor')), 0.8],
	['boing', antes(pal(78, 'austríaco')), 0.7],
	['hoja', ini(79), 0.6],
	['crack', antes(pal(83, 'alemana')), 0.9],
	['puerta', antes(pal(84, 'sale', 1)), 0.7],
	['flash', antes(pal(84, 'sale', 2)), 0.8],
	['objeto', antes(ini(85)), 0.7],
];

export {SERIF};

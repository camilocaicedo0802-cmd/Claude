import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Bombilla} from '../componentes/Efectos';
import {Actor, Muneco, alcanzar, manosEn, manosFrente} from '../componentes/Muneco';
import {ExpedienteSellado, JarraVotos} from '../componentes/Recurrentes';
import {Toma} from '../componentes/Toma';
import {FUNCIONARIO, HITLER_TRAJE, PAPEN, SENOR_1, SENOR_2, SENOR_3} from '../componentes/Vestuario';
import {MaquinaEscribir} from '../componentes/Gamer';
import {EscLiso, EscMesaArriba} from '../escenarios/Epoca';
import {P, Plano, TINTA, antes, clamp, fin, ini, pal, tramo} from './base';
import {PlanoMuletilla, brazo, golpeMuletilla} from './compartidas';
import {Alcancia, Archivador, CajaPecho, EMPLEADO, EscJardinCerveza, Factura, HITLER_VIEJO, PROFESOR, PaginaDiario, Periodico, Perro, Postal} from './utileria_c67';

/* CAPÍTULO 6: ACABADO (noviembre-diciembre de 1932). Paleta desaturada, casi oscura. */

/** todo el capítulo va apagado: menos color y menos luz */
const Apagado: React.FC<{children: React.ReactNode; s?: number; b?: number}> = ({children, s = 0.45, b = 0.85}) => <div style={{position: 'absolute', inset: 0, filter: `saturate(${s}) brightness(${b})`}}>{children}</div>;

const SalaGris: React.FC<{luz?: number}> = ({luz = 0.18}) => (
	<>
		<EscLiso color="#26282c" foco luz="210,214,220" />
		<div style={{position: 'absolute', left: 0, right: 0, top: 760, bottom: 0, background: 'linear-gradient(180deg, #2e2c2a, #161514)'}} />
		<div style={{position: 'absolute', left: 0, right: 0, top: 752, height: 14, background: '#1a1918'}} />
		<div style={{position: 'absolute', inset: 0, background: `rgba(0,0,0,${0.3 - luz})`}} />
	</>
);

/* ---------- rótulo: el periódico de noviembre de 1932 ---------- */

const PERIODICO_FOTO = (
	<div style={{position: 'absolute', inset: 0, background: '#8a867c'}}>
		<div style={{position: 'absolute', left: '22%', top: '18%', width: '56%', height: '82%', background: '#5a5850', borderRadius: '50% 50% 0 0'}} />
		<div style={{position: 'absolute', left: '34%', top: '10%', width: '32%', height: '36%', background: '#d9d6cc', borderRadius: '50%', border: `3px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: '33%', top: '8%', width: '24%', height: '14%', background: '#1a1814', borderRadius: '50% 40% 10% 50%'}} />
		<div style={{position: 'absolute', left: '46%', top: '30%', width: '8%', height: '5%', background: '#1a1814'}} />
	</div>
);

const C6Periodico: React.FC<P> = ({d, h, e, s}) => (
	<Toma
		escena={
			<Apagado>
				<EscMesaArriba tono="gris" luz={[960, 420]} />
			</Apagado>
		}
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1.0, 1.16], r: [-2, 1], y: [10, 30]}}
	>
		<Apagado s={0.6} b={0.95}>
			<Periodico x={960} y={560} ancho={760} rot={-3} gris fecha="7 DE NOVIEMBRE DE 1932" titular="HITLER PIERDE FUELLE" sub="Dos millones de votos menos" foto={PERIODICO_FOTO} />
		</Apagado>
	</Toma>
);

/* ---------- la jarra baja del 37 al 33 % y la gente se va ---------- */

const GENTE = [SENOR_1, SENOR_2, SENOR_3, FUNCIONARIO, SENOR_1, SENOR_2];

const C6Jarra: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const baja = tramo(f, antes(pal(143, 'pierde')), pal(143, 'votos') + 8);
	const nivel = 37 - 4 * baja;
	return (
		<Toma
			escena={
				<Apagado>
					<SalaGris />
					{/* la puerta de salida, a la derecha */}
					<div style={{position: 'absolute', left: 1560, top: 300, width: 260, height: 470, background: '#0e0e10', border: `10px solid ${TINTA}`, boxShadow: 'inset 0 0 80px rgba(220,220,230,0.25)'}} />
					<div style={{position: 'absolute', left: 1540, top: 270, width: 300, height: 40, background: '#3a3632', border: `8px solid ${TINTA}`, textAlign: 'center', fontFamily: 'Anton', fontSize: 26, color: '#d9d4c8', lineHeight: '24px', letterSpacing: 4}}>SALIDA</div>
				</Apagado>
			}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.06, 1.12], x: [30, -30]}}
			angulo={-3}
		>
			<Apagado s={0.55} b={0.92}>
				{GENTE.map((r, i) => {
					const t0 = d + 4 + i * 9;
					const x = interpolate(f, [t0, t0 + 70], [1020 + (i % 3) * 70, 1700], clamp);
					const op = interpolate(x, [1600, 1700], [1, 0], clamp);
					return (
						<Actor key={i} x={x} y={780 + (i % 2) * 14} alto={330} opacidad={op}>
							<Muneco ropa={r} camina={1.2} semilla={i} pose={{cabeza: 4}} ojos="normal" cejas="neutral" boca="seria" />
						</Actor>
					);
				})}
				<JarraVotos x={620} y={900} alto={640} nivel={nivel} tono={0.25} />
			</Apagado>
		</Toma>
	);
};

/* ---------- el partido está quebrado: alcancía con polilla y facturas IMPAGO ---------- */

const C6Alcancia: React.FC<P> = ({d, h, e, s}) => (
	<Toma
		escena={
			<Apagado>
				<SalaGris />
				<div style={{position: 'absolute', left: 260, right: 260, top: 700, height: 44, background: '#4a4038', border: `8px solid ${TINTA}`, borderRadius: 8}} />
				<div style={{position: 'absolute', left: 290, right: 290, top: 744, height: 400, background: '#3a322c', border: `8px solid ${TINTA}`, borderTop: 'none'}} />
			</Apagado>
		}
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1.12, 1.24], y: [20, 50]}}
	>
		<Apagado s={0.55} b={0.95}>
			<Factura x={520} y={380} ancho={330} rot={-8} sello={pal(144, 'peor')} concepto="Imprenta del partido" />
			<Factura x={1400} y={360} ancho={330} rot={7} sello={pal(144, 'quebrado')} concepto="Alquiler del local" />
			<Alcancia x={960} y={712} tam={260} polilla={antes(pal(144, 'quebrado'))} />
		</Apagado>
	</Toma>
);

const C6Cajas: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma
			escena={
				<Apagado>
					<SalaGris />
					{/* pared con facturas clavadas */}
					{[0, 1, 2, 3].map((i) => (
						<div key={i} style={{position: 'absolute', left: 220 + i * 210, top: 170 + (i % 2) * 40, width: 160, height: 200, background: '#d9d4c8', border: `6px solid ${TINTA}`, transform: `rotate(${(i % 2 ? 4 : -5)}deg)`}}>
							<div style={{position: 'absolute', left: 10, right: 10, top: 70, border: '6px solid #b8202a', color: '#b8202a', fontFamily: 'Anton', fontSize: 30, textAlign: 'center', transform: 'rotate(-14deg)'}}>IMPAGO</div>
						</div>
					))}
					<div style={{position: 'absolute', left: 1500, top: 300, width: 260, height: 460, background: '#0e0e10', border: `10px solid ${TINTA}`, boxShadow: 'inset 0 0 80px rgba(220,220,230,0.25)'}} />
				</Apagado>
			}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.04, 1.1], x: [-20, -60]}}
		>
			<Apagado s={0.55} b={0.95}>
				{[EMPLEADO, FUNCIONARIO, SENOR_2].map((r, i) => {
					const t0 = d - 6 + i * 14;
					const x = interpolate(f, [t0, t0 + 90], [700 + i * 140, 1640], clamp);
					return (
						<Actor key={i} x={x} y={790 + i * 10} alto={560} opacidad={interpolate(x, [1560, 1640], [1, 0], clamp)}>
							<Muneco ropa={r} camina={1} semilla={i} pose={{...manosFrente([140, 470], [260, 470]), mi: 'oculta', md: 'oculta'}} delante={<CajaPecho />} ojos="normal" cejas="preocupado" boca="seria" />
						</Actor>
					);
				})}
			</Apagado>
		</Toma>
	);
};

/* ---------- serio: «Otra vez con lo del tiro» — Hitler en penumbra, el diario ---------- */

const Penumbra: React.FC<{cerca?: boolean}> = ({cerca = false}) => (
	<>
		<div style={{position: 'absolute', inset: 0, background: '#0c0c0e'}} />
		{/* una rendija de luz de ventana */}
		<div style={{position: 'absolute', left: 1180, top: -60, width: 300, height: 1200, background: 'linear-gradient(180deg, rgba(200,206,220,0.22), rgba(200,206,220,0.02))', transform: 'skewX(-18deg)', filter: 'blur(10px)'}} />
		<Actor x={1060} y={cerca ? 1180 : 1010} alto={cerca ? 1000 : 760}>
			<Muneco ropa={HITLER_TRAJE} pose={{...manosFrente([170, 520], [230, 520]), mi: 'agarra', md: 'agarra', cabeza: 10, cuerpo: 4}} ojos="entrecerrados" cejas="neutral" boca="seria" respira parpadea={false} />
		</Actor>
		<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 62% 40%, rgba(0,0,0,0.25) 0%, rgba(0,0,0,0.78) 55%)'}} />
		<div style={{position: 'absolute', left: -40, right: -40, top: 860, bottom: -40, background: 'linear-gradient(180deg, #1a1612, #0a0806)', borderTop: `8px solid ${TINTA}`}} />
	</>
);

const C6Penumbra: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Penumbra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], x: [0, -30], y: [0, 10], curva: 'lineal'}} />
);

const C6Diario: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscMesaArriba tono="oscura" luz={[960, 520]} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.12], curva: 'lineal'}}>
			<div style={{position: 'absolute', inset: 0, filter: 'saturate(0.5)'}}>
				<PaginaDiario x={960} y={540} ancho={1300} rot={-2} escribe={interpolate(f, [d - 10, h], [0.35, 1], clamp)} />
			</div>
			<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.65) 100%)'}} />
		</Toma>
	);
};

const C6Diario2: React.FC<P> = ({d, h, e, s}) => (
	<Toma
		escena={<Penumbra cerca />}
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1.0, 1.1], x: [0, -40], y: [0, 20], curva: 'lineal'}}
	>
		{/* el diario abierto en primer plano, sobre el escritorio */}
		<div style={{position: 'absolute', left: 120, top: 640, width: 1100, height: 520, transform: 'perspective(1100px) rotateX(48deg)', transformOrigin: '50% 100%', filter: 'saturate(0.4) brightness(0.8)'}}>
			<PaginaDiario x={550} y={260} ancho={1040} rot={-4} escribe={1} />
		</div>
	</Toma>
);

/* ---------- «Afuera ya lo están despidiendo»: el profesor británico ---------- */

const C6Profesor: React.FC<P> = ({d, h, e, s}) => (
	<Toma
		escena={
			<Apagado s={0.6} b={0.9}>
				<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #4a3a2e, #2a2018)'}} />
				{/* biblioteca */}
				{[0, 1, 2].map((r) => (
					<React.Fragment key={r}>
						<div style={{position: 'absolute', left: 80, right: 80, top: 160 + r * 190, height: 18, background: '#2a1a10', border: `5px solid ${TINTA}`}} />
						{Array.from({length: 26}, (_, i) => (
							<div key={i} style={{position: 'absolute', left: 100 + i * 66, top: 60 + r * 190, width: 46, height: 100 + ((i * 13) % 30), marginTop: -((i * 13) % 30), background: ['#6a2a24', '#2a4a3a', '#3a3a5a', '#7a5a2a'][(i + r) % 4], border: `4px solid ${TINTA}`}} />
						))}
					</React.Fragment>
				))}
				{/* titulares en la pared */}
				<div style={{position: 'absolute', left: 1300, top: 560, width: 480, padding: '10px 0', background: '#e6e0d0', border: `6px solid ${TINTA}`, transform: 'rotate(3deg)', textAlign: 'center', fontFamily: 'Anton', fontSize: 50, color: '#2a2218'}}>«EL FIN DE HITLER»</div>
				<div style={{position: 'absolute', left: 0, right: 0, top: 820, bottom: 0, background: '#3a2414', borderTop: `9px solid ${TINTA}`}} />
			</Apagado>
		}
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1.06, 1.16], x: [40, -10], y: [20, 40]}}
	>
		<Apagado s={0.6} b={0.95}>
			<Actor x={600} y={1060} alto={780}>
				<Muneco ropa={PROFESOR} pose={{...manosFrente([300, 600], [380, 590]), mi: 'relajada', md: 'relajada', cabeza: 8, cuerpo: 4}} ojos="entrecerrados" cejas="arrogante" boca="picara" />
			</Actor>
			<MaquinaEscribir x={1000} y={1010} ancho={480} hoja={1} titular="ACABADO" desde={ini(151)} />
			{/* taza de té */}
			<svg width={160} height={110} viewBox="0 0 160 110" style={{position: 'absolute', left: 1320, top: 860}}>
				<ellipse cx={70} cy={100} rx={66} ry={10} fill="#f4f4f0" stroke={TINTA} strokeWidth={5} />
				<path d="M 26 40 L 34 96 Q 70 108 106 96 L 114 40 Z" fill="#f4f4f0" stroke={TINTA} strokeWidth={6} />
				<path d="M 112 52 Q 140 56 134 80 Q 128 94 108 90" stroke={TINTA} strokeWidth={6} fill="none" />
			</svg>
		</Apagado>
	</Toma>
);

/* ---------- el futuro imaginado: un viejito en una cervecería de Baviera (postal sepia) ---------- */

const Jardin: React.FC<{bosteza: number; habla: boolean}> = ({bosteza, habla}) => {
	const f = useCurrentFrame();
	const gesto = Math.sin(f / 8);
	return (
		<>
			<EscJardinCerveza />
			{/* mesa y sillas vacías */}
			<div style={{position: 'absolute', left: 560, top: 760, width: 900, height: 36, background: '#8a6a3a', border: `8px solid ${TINTA}`, borderRadius: 6}} />
			<div style={{position: 'absolute', left: 620, top: 796, width: 24, height: 200, background: '#6a4a2a', border: `5px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 1380, top: 796, width: 24, height: 200, background: '#6a4a2a', border: `5px solid ${TINTA}`}} />
			{[1180, 1360].map((x) => (
				<div key={x} style={{position: 'absolute', left: x - 60, top: 640, width: 120, height: 240, border: `8px solid ${TINTA}`, borderBottom: 'none', borderRadius: '20px 20px 0 0', background: 'rgba(122,82,48,0.6)'}} />
			))}
			<Actor x={820} y={1000} alto={720}>
				<Muneco ropa={HITLER_VIEJO} pose={{...brazo(1, alcanzar(1, 360 + gesto * 20, 380 - gesto * 30)), md: 'abierta', ...manosEn([150, 560]), mi: 'agarra', cuerpo: -3, cabeza: 4}} ojos="normal" cejas="preocupado" boca="sonrisa" hablando={habla} />
			</Actor>
			{/* jarra en la mesa */}
			<svg width={110} height={130} viewBox="0 0 90 100" style={{position: 'absolute', left: 640, top: 640, overflow: 'visible'}}>
				<path d="M 64 30 Q 88 30 86 52 Q 84 72 62 72" stroke={TINTA} strokeWidth={9} fill="none" />
				<rect x={10} y={22} width={56} height={74} rx={6} fill="#e8a528" stroke={TINTA} strokeWidth={6} />
				<path d="M 6 26 Q 14 4 30 16 Q 40 0 52 14 Q 66 2 70 26 Z" fill="#fbf6ea" stroke={TINTA} strokeWidth={5} />
			</svg>
			<Perro x={1240} y={1000} tam={170} bosteza={bosteza} />
		</>
	);
};

const C6Postal: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscMesaArriba tono="madera" luz={[960, 500]} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.3], y: [0, 40], r: [-1, 0]}}>
			<Postal x={960} y={540} ancho={1500} rot={-2}>
				<Jardin bosteza={0} habla={f >= ini(152)} />
			</Postal>
		</Toma>
	);
};

const C6Postal2: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const bost = interpolate(f, [antes(pal(152, 'tomar')), pal(152, 'tomar') + 10, fin(152) + 6, fin(152) + 16], [0, 1, 1, 0], clamp);
	return (
		<Toma
			escena={
				<div style={{position: 'absolute', inset: 0, filter: 'sepia(0.85) contrast(0.95)'}}>
					<Jardin bosteza={bost} habla={f < fin(152)} />
				</div>
			}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.3, 1.42], x: [180, 120], y: [-60, -90]}}
			encima={<div style={{position: 'absolute', inset: 0, border: '34px solid #efe4c8', boxShadow: `inset 0 0 0 8px ${TINTA}`}} />}
		/>
	);
};

/* ---------- «Ese ya no llega a nada» (4.ª y última) y el cajón de CASOS CERRADOS ---------- */

const C6Muletilla: React.FC<P> = (p) => <PlanoMuletilla {...p} i={153} n={4} />;

const C6Cajon: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cae = tramo(f, d + 4, d + 22, (u) => u * u);
	const cierra = tramo(f, d + 26, d + 34, (u) => u * u);
	const abre = 1 - cierra;
	const apaga = interpolate(f, [antes(pal(154, 'suelo')), h - 2], [0, 1], clamp);
	return (
		<Toma
			escena={
				<Apagado>
					<SalaGris />
				</Apagado>
			}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.05, 1.18], y: [30, 70]}}
			golpes={[[d + 34, 0.04]]}
			encima={<div style={{position: 'absolute', inset: 0, background: '#000', opacity: apaga * 0.96}} />}
		>
			<Apagado s={0.55} b={0.95}>
				<Archivador x={960} y={1060} ancho={560} abre={abre} />
				{cae < 1 && (
					<div style={{position: 'absolute', inset: 0, transform: `translate(0px, ${interpolate(cae, [0, 1], [-520, 40])}px) scale(${interpolate(cae, [0, 1], [1, 0.45])})`, transformOrigin: '960px 420px', opacity: interpolate(cae, [0.85, 1], [1, 0], clamp)}}>
						<ExpedienteSellado x={960} y={420} ancho={620} rot={-4} n={4} />
					</div>
				)}
			</Apagado>
		</Toma>
	);
};

/* ---------- a oscuras: se enciende una bombilla sobre la chistera de Papen ---------- */

const C6Bombilla: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const idea = antes(pal(155, 'idea'));
	const luz = tramo(f, idea, idea + 8);
	return (
		<Toma
			escena={<div style={{position: 'absolute', inset: 0, background: '#050506'}} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.0, 1.1], y: [40, 70]}}
			angulo={5}
			golpes={[[idea, 0.05]]}
		>
			<div style={{position: 'absolute', left: 460, top: -120, width: 1000, height: 1000, borderRadius: '50%', background: `radial-gradient(circle at 50% 30%, rgba(255,236,170,${0.42 * luz}) 0%, rgba(255,236,170,0) 60%)`}} />
			<div style={{position: 'absolute', inset: 0, filter: `brightness(${0.12 + 0.88 * luz})`}}>
				<Actor x={960} y={1240} alto={1060}>
					<Muneco ropa={PAPEN} pose={{...manosEn(undefined, [212, 420], {}, true), md: 'oculta', ...manosEn([150, 560]), mi: 'relajada', cabeza: -4}} ojos={luz > 0.5 ? 'feliz' : 'entrecerrados'} cejas="arrogante" boca={luz > 0.5 ? 'sonrisaGrande' : 'seria'} />
				</Actor>
			</div>
			<Bombilla x={960} y={120} tam={200} desde={idea} />
		</Toma>
	);
};

export const PLANOS_C6: Plano[] = [
	{n: 'c6-periodico', d: ini(142), e: 'latigoDer', C: C6Periodico},
	{n: 'c6-jarra', d: ini(143), e: 'latigoIzq', C: C6Jarra},
	{n: 'c6-alcancia', d: ini(144), e: 'latigoDer', C: C6Alcancia},
	{n: 'c6-cajas', d: ini(145), e: 'latigoIzq', C: C6Cajas},
	{n: 'c6-penumbra', d: ini(146), e: 'fundido', C: C6Penumbra},
	{n: 'c6-diario', d: ini(148), e: 'fundido', C: C6Diario},
	{n: 'c6-diario2', d: ini(149), e: 'fundido', C: C6Diario2},
	{n: 'c6-profesor', d: ini(150), e: 'fundido', C: C6Profesor},
	{n: 'c6-postal', d: ini(152), e: 'zoom', C: C6Postal},
	{n: 'c6-postal2', d: pal(152, 'contándoles'), e: 'zoom', C: C6Postal2},
	{n: 'c6-muletilla', d: ini(153), e: 'zoom', C: C6Muletilla},
	{n: 'c6-cajon', d: ini(154), e: 'latigoArriba', C: C6Cajon},
	{n: 'c6-bombilla', d: ini(155), e: 'fundido', C: C6Bombilla},
];

export const SONIDOS_C6: [string, number, number][] = [
	['murmullo', ini(143) + 4, 0.4],
	['puerta', pal(143, 'votos') + 4, 0.5],
	['sello', pal(144, 'peor'), 0.7],
	['sello', pal(144, 'quebrado'), 0.7],
	['moscas', antes(pal(144, 'quebrado')), 0.5],
	['teclas', ini(151), 0.6],
	['sello', golpeMuletilla(153), 1.0],
	['objeto', ini(154) + 22, 0.7],
	['puerta', ini(154) + 32, 0.6],
	['clic', antes(pal(154, 'suelo')) + 6, 0.6],
	['clic', antes(pal(155, 'idea')), 0.7],
	['ding', antes(pal(155, 'idea')) + 2, 0.8],
];


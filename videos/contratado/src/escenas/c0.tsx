import React from 'react';
import {Freeze, interpolate, useCurrentFrame} from 'remotion';
import {Actor, Muneco, alcanzar, manosEn, manosFrente} from '../componentes/Muneco';
import {Chistera, Contrato, JarraVotos, Raton} from '../componentes/Recurrentes';
import {Toma} from '../componentes/Toma';
import {Sello} from '../componentes/Utileria';
import {AMIGO, BANQUERO, HITLER_TRAJE, PAPEN, SENOR_3} from '../componentes/Vestuario';
import {EscCerveceria, EscLiso, EscMesaArriba, EscOficinaBerlin, EscRincon, EscritorioBerlin, Jarra} from '../escenarios/Epoca';
import {CONDENSADA, SERIF} from '../fuentes';
import {P, Plano, TINTA, antes, centrar, clamp, fin, ini, mezclaCam, pal, suave, tramo} from './base';
import {CuadroEspia, CuadroHindenburgSello, CuadroJuezDeportar, CuadroTiroTecho, brazo} from './compartidas';

/* APERTURA (0:00–0:45). Paleta: invierno de Berlín azul grisáceo con una lámpara cálida. */


/** El encuadre del contrato: se repite igual en el capítulo 7 y en el final. */
export const ENCUADRE_VENTANA = centrar(470, 410, 1.75);
export const ENCUADRE_CONTRATO = centrar(1160, 560, 1.18);
export const ANGULO_PAPEN = 4;

/* ---------- la oficina con Papen, el amigo y el contrato ---------- */

export const OficinaPapen: React.FC<{desliza: number; habla?: boolean; palmadas?: boolean; papen?: boolean; amigo?: boolean; hitler?: boolean; sillaVacia?: boolean}> = ({desliza, habla = false, palmadas = true, papen = true, amigo = true, hitler = false, sillaVacia = false}) => {
	const f = useCurrentFrame();
	const pat = palmadas ? Math.max(0, Math.sin(f / 3.2)) * 10 : 0;
	const cx = interpolate(desliza, [0, 1], [930, 1210]);
	return (
		<>
			<EscOficinaBerlin />
			{sillaVacia && (
				<>
					<div style={{position: 'absolute', left: 1380, top: 330, width: 190, height: 420, background: 'linear-gradient(90deg, #4a1c20, #6a2a30 50%, #4a1c20)', border: `9px solid ${TINTA}`, borderRadius: '40px 40px 8px 8px'}} />
					<Chistera x={1475} y={360} ancho={150} rot={8} />
				</>
			)}
			{amigo && (
				<Actor x={1460} y={1010} alto={780} voltear>
					<Muneco ropa={AMIGO} pose={{...manosFrente([190, 470], [215, 470]), mi: 'agarra', md: 'agarra', cabeza: 4}} ojos="grandes" cejas="preocupado" boca="mueca" />
				</Actor>
			)}
			{papen && (
				<Actor x={1170} y={1010} alto={800}>
					<Muneco
						ropa={PAPEN}
						pose={{...brazo(1, alcanzar(1, 392, 330 - pat)), md: 'abierta', ...manosEn([60, 640]), mi: 'abierta', cabeza: -4, cuerpo: 3}}
						ojos={habla ? 'normal' : 'feliz'}
						cejas="arrogante"
						boca={habla ? 'sonrisa' : 'sonrisaGrande'}
						hablando={habla}
					/>
				</Actor>
			)}
			{hitler && (
				<Actor x={1170} y={1010} alto={800}>
					<Muneco ropa={HITLER_TRAJE} pose={{...manosEn([120, 600], [280, 600]), mi: 'puno', md: 'puno'}} ojos="entrecerrados" cejas="arrogante" boca="seria" />
				</Actor>
			)}
			<EscritorioBerlin>
				{/* el contrato acostado sobre el escritorio */}
				<div style={{position: 'absolute', left: cx - 120, top: 640, width: 240, height: 90, transform: 'perspective(600px) rotateX(62deg) rotate(-6deg)', transformOrigin: '50% 100%'}}>
					<Contrato x={120} y={-20} ancho={240} rot={0} sombra={false} />
				</div>
				{/* calendario de escritorio */}
				<div style={{position: 'absolute', left: 760, top: 600, width: 120, height: 104, background: '#f6efdc', border: `6px solid ${TINTA}`, borderRadius: 6, textAlign: 'center', fontFamily: CONDENSADA, color: '#2a2218'}}>
					<div style={{background: '#a8262e', color: '#f6efdc', fontSize: 22, letterSpacing: 2, borderBottom: `4px solid ${TINTA}`}}>ENERO</div>
					<div style={{fontSize: 52, lineHeight: 1.1}}>30</div>
					<div style={{fontSize: 16, marginTop: -6}}>1933</div>
				</div>
			</EscritorioBerlin>
		</>
	);
};

const P0: React.FC<P> = ({d, h, e, s}) => {
	const fin0 = pal(0, 'va');
	return (
		<Toma
			escena={<Interior desliza={[d + 30, fin0]} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			angulo={ANGULO_PAPEN}
			camFn={(f) => mezclaCam(ENCUADRE_VENTANA, ENCUADRE_CONTRATO, tramo(f, d + 6, fin0 + 4))}
		/>
	);
};

/** el contenido animado de la oficina (Papen habla y desliza el contrato) */
const Interior: React.FC<{desliza: [number, number]}> = ({desliza}) => {
	const f = useCurrentFrame();
	return (
		<div style={{position: 'absolute', inset: 0}}>
			<OficinaPapen desliza={tramo(f, desliza[0], desliza[1])} habla={f < fin(0)} />
		</div>
	);
};

/* ---------- el rincón y el ratón ---------- */

const P0b: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscRincon />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.25, 1.4], x: [-180, -220], y: [-200, -250]}}>
		<Raton x={1150} y={928} tam={170} chilla={useCurrentFrame() >= antes(pal(0, 'chillar'))} />
	</Toma>
);

/* ---------- «Eso lo dijo un aristócrata alemán…» ---------- */

const P1: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<OficinaPapen desliza={1} palmadas={false} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.14], x: [-60, -120], y: [-10, -30]}} angulo={ANGULO_PAPEN} />
);

/* ---------- el contrato desde arriba, zoom de golpe a la firma ---------- */

const P2: React.FC<P> = ({d, h, e, s}) => {
	const golpe = antes(pal(2, 'contratado'));
	return (
		<Toma
			escena={<EscMesaArriba tono="madera" luz={[1100, 380]} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(f) => {
				const t = tramo(f, golpe, golpe + 5, (u) => 1 - Math.pow(1 - u, 3));
				const a = centrar(960, 540, 1.0 + 0.04 * tramo(f, d, golpe));
				const b = centrar(900, 820, 2.1);
				return {s: a.s + (b.s - a.s) * t, x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t};
			}}
		>
			<Contrato x={960} y={560} ancho={640} rot={-4} />
			<Chistera x={1520} y={420} ancho={300} rot={-12} />
			{/* guante blanco de Papen sobre el papel */}
			<div style={{position: 'absolute', left: 1180, top: 690, width: 170, height: 110, background: '#ffffff', border: `7px solid ${TINTA}`, borderRadius: '50px 50px 40px 40px', transform: 'rotate(-20deg)'}} />
		</Toma>
	);
};

/* ---------- «A Adolf Hitler»: en una silla diminuta, desde arriba ---------- */

const SillaDiminuta: React.FC<{x: number; y: number}> = ({x, y}) => (
	<svg width={150} height={120} viewBox="0 0 150 120" style={{position: 'absolute', left: x - 75, top: y - 120, overflow: 'visible'}}>
		<rect x={10} y={30} width={130} height={22} rx={6} fill="#7a5230" stroke={TINTA} strokeWidth={6} />
		<line x1={22} y1={52} x2={18} y2={118} stroke={TINTA} strokeWidth={10} strokeLinecap="round" />
		<line x1={128} y1={52} x2={132} y2={118} stroke={TINTA} strokeWidth={10} strokeLinecap="round" />
	</svg>
);

const P3: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscOficinaBerlin />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.22, 1.3], x: [0, -30], y: [-120, -150]}} angulo={-10}>
		<SillaDiminuta x={960} y={900} />
		<Actor x={960} y={935} alto={560}>
			<Muneco ropa={HITLER_TRAJE} pose={{agacha: 0.62, ...manosFrente([170, 560], [230, 560]), mi: 'agarra', md: 'agarra', pi: 16, pd: 16}} ojos="grandes" cejas="sorprendido" boca="o" />
		</Actor>
		{/* el borde del escritorio, en primer plano */}
		<div style={{position: 'absolute', left: -40, right: -40, top: 960, height: 300, background: 'linear-gradient(180deg, #6a3e26, #3a2014)', borderTop: `10px solid ${TINTA}`}} />
	</Toma>
);

/* ---------- dos meses después: el rincón, y la imagen se congela con SPOILER ---------- */

const P4: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const congela = ini(5);
	const frio = f >= congela;
	return (
		<Toma
			escena={<EscRincon />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => centrar(1150, 760, 1.35 + 0.12 * tramo(Math.min(ff, congela), d, congela))}
			encima={
				<>
					{frio && <div style={{position: 'absolute', inset: 0, background: 'rgba(255,255,255,0.08)', backdropFilter: 'grayscale(0.6)'}} />}
					<Sello x={960} y={540} texto="SPOILER" desde={congela + 3} tam={150} rot={-14} solido />
				</>
			}
		>
			<Freeze frame={frio ? congela : f} active={frio}>
				<div style={{position: 'absolute', inset: 0}}>
					{/* calendario de pared: marzo de 1933 */}
					<div style={{position: 'absolute', left: 1360, top: 470, width: 210, height: 260, background: '#f6efdc', border: `7px solid ${TINTA}`, borderRadius: 6, textAlign: 'center', fontFamily: CONDENSADA, color: '#2a2218', transform: 'rotate(3deg)'}}>
						<div style={{background: '#a8262e', color: '#f6efdc', fontSize: 40, letterSpacing: 3, borderBottom: `5px solid ${TINTA}`}}>MARZO</div>
						<div style={{fontSize: 110, lineHeight: 1.2}}>23</div>
						<div style={{fontSize: 30}}>1933</div>
					</div>
					<Raton x={1150} y={928} tam={170} chilla />
				</div>
			</Freeze>
		</Toma>
	);
};

/* ---------- la jarra de votos (primera vez) ---------- */

export const Barra: React.FC = () => (
	<>
		<EscCerveceria tono="sepia" vacia humo={0.1} />
		<div style={{position: 'absolute', left: -40, right: -40, top: 860, height: 40, background: '#7a5230', border: `9px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: -40, right: -40, top: 900, bottom: -40, background: 'linear-gradient(180deg, #4a3220, #22160c)'}} />
	</>
);

const P6: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const nunca = ini(7);
	const nivel = 43.9 * tramo(f, d + 6, nunca - 4, (t) => 1 - Math.pow(1 - t, 2.4)) + Math.sin(f / 3) * 0.3 * tramo(f, nunca - 4, nunca + 10);
	return (
		<Toma
			escena={<Barra />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => {
				const t = tramo(ff, nunca - 2, nunca + 4, (u) => 1 - Math.pow(1 - u, 3));
				const a = centrar(960, 520, 1.04 + 0.05 * tramo(ff, d, nunca));
				const b = centrar(960, 400, 2.3);
				return mezclaCam(a, b, t);
			}}
		>
			<JarraVotos x={960} y={880} alto={720} nivel={nivel} />
		</Toma>
	);
};

/* ---------- los señores que se reían de él ---------- */

export const Copa: React.FC<{rot?: number}> = ({rot = 0}) => (
	<g transform={`rotate(${rot} 0 36)`}>
		<path d="M -30 -60 L 30 -60 L 14 -6 L -14 -6 Z" fill="#f6e7a8" stroke={TINTA} strokeWidth={5} />
		<line x1={0} y1={-6} x2={0} y2={40} stroke={TINTA} strokeWidth={6} />
		<line x1={-20} y1={40} x2={20} y2={40} stroke={TINTA} strokeWidth={6} strokeLinecap="round" />
		<circle cx={-8} cy={-40} r={4} fill="#fff" />
		<circle cx={6} cy={-26} r={3} fill="#fff" />
	</g>
);

export const EscSalon: React.FC = () => (
	<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #4a2a2a 0%, #2a1618 70%, #1a0e10 100%)'}}>
		{[0, 1, 2, 3, 4, 5].map((i) => (
			<div key={i} style={{position: 'absolute', left: 40 + i * 330, top: 90, width: 250, height: 600, border: '8px solid rgba(201,164,58,0.35)', borderRadius: '120px 120px 6px 6px'}} />
		))}
		{/* araña de cristal */}
		<div style={{position: 'absolute', left: 960 - 4, top: 0, width: 8, height: 120, background: '#c9a43a'}} />
		<div style={{position: 'absolute', left: 760, top: 110, width: 400, height: 90, borderRadius: '0 0 200px 200px', border: '10px solid #c9a43a', borderTop: 'none'}} />
		{[0, 1, 2, 3, 4].map((i) => (
			<div key={i} style={{position: 'absolute', left: 780 + i * 90, top: 168 + Math.abs(2 - i) * -18, width: 22, height: 40, borderRadius: '50%', background: '#fff3c0', boxShadow: '0 0 40px 12px rgba(255,230,160,0.7)'}} />
		))}
		<div style={{position: 'absolute', left: 260, top: -100, width: 1400, height: 1100, borderRadius: '50%', background: 'radial-gradient(circle at 50% 20%, rgba(255,226,160,0.35), rgba(255,226,160,0) 60%)', mixBlendMode: 'screen'}} />
		<div style={{position: 'absolute', left: 0, right: 0, top: 760, bottom: 0, background: 'linear-gradient(180deg, #3a1a1e, #1a0a0c)'}} />
	</div>
);

export const Senores: React.FC<{listos?: boolean}> = ({listos = false}) => {
	const f = useCurrentFrame();
	const risa = Math.abs(Math.sin(f / 4));
	const copa = (lado: -1 | 1) => (lado < 0 ? {...brazo(-1, alcanzar(-1, 20, 300 - risa * 10)), mi: 'agarra' as const} : {...brazo(1, alcanzar(1, 380, 300 - risa * 10)), md: 'agarra' as const});
	return (
		<>
			<Actor x={620} y={1020} alto={820}>
				<Muneco ropa={BANQUERO} pose={{...copa(1), ...manosEn([150, 560]), cabeza: -8 + risa * 4}} objDer={<Copa rot={180} />} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
			</Actor>
			<Actor x={960} y={1030} alto={860}>
				<Muneco
					ropa={PAPEN}
					pose={listos ? {...manosEn(undefined, [212, 420], {}, true), md: 'oculta', ...copa(-1), cabeza: 8, cuerpo: -3} : {...copa(-1), ...copa(1), cabeza: 6 - risa * 4}}
					objIzq={<Copa rot={180} />}
					objDer={listos ? undefined : <Copa rot={180} />}
					ojos={listos ? 'entrecerrados' : 'feliz'}
					cejas="arrogante"
					boca={listos ? 'picara' : 'sonrisaGrande'}
				/>
			</Actor>
			<Actor x={1300} y={1020} alto={820} voltear>
				<Muneco ropa={SENOR_3} pose={{...copa(1), ...manosEn([150, 560]), cabeza: -6 + risa * 5}} objDer={<Copa rot={180} />} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
			</Actor>
		</>
	);
};

const P8: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscSalon />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.12], x: [40, -20], y: [0, -20]}} angulo={3}>
		<Senores />
		{/* Hitler chiquito abajo, mirando hacia arriba: picado */}
		<div style={{position: 'absolute', left: 0, right: 0, top: 860, bottom: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,0.5))'}} />
		<Actor x={1660} y={1120} alto={440}>
			<Muneco ropa={HITLER_TRAJE} pose={{...manosFrente([180, 520], [220, 520]), mi: 'agarra', md: 'agarra', cabeza: -10}} ojos="grandes" cejas="preocupado" boca="mueca" />
		</Actor>
	</Toma>
);

const P9: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscSalon />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.45, 1.6], x: [0, 0], y: [140, 180]}} angulo={6}>
		<Senores listos />
	</Toma>
);

/* ---------- los cuatro adelantos (1,5–3 s cada uno, unidos con barridos) ---------- */

const T1: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<CuadroEspia />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.15, 1.3], x: [0, -40], y: [40, 60]}} angulo={-5} />
);
const T2: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<CuadroTiroTecho disparo={pal(12, 'cervecería') - 6} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.22], y: [60, 90]}} golpes={[[pal(12, 'cervecería') - 6, 0.08]]} />
);
const T3: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<CuadroJuezDeportar rompe={pal(13, 'deporta')} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.2, 1.36], y: [80, 120]}} />
);
const T4: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<CuadroHindenburgSello brillo={0.4} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.1], y: [80, 120]}} angulo={8} />
);

/* ---------- «Empecemos por el espía»: la cámara se mete en la espuma ---------- */

const P15: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Barra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.2, 1.5], y: [120, 260]}} focoSalida={[960, 330]}>
		<Jarra x={960} y={980} alto={760} />
	</Toma>
);

/* (los planos de la apertura viven en el proyecto del video largo; aquí solo se reutilizan sus piezas) */

export {suave, clamp, SERIF};

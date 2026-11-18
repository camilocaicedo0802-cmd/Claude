import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Actor, Muneco, POSES, Pose, alcanzar, manosFrente} from './componentes/Muneco';
import {Polaroid, Revista} from './componentes/Objetos';
import {ROPA_MJ_1978, ROPA_MJ_1991} from './componentes/Vestuario';
import {EscAlfombra, EscConcierto, EscCorcho} from './escenarios/Escenarios';
import {CONDENSADA} from './fuentes';

/* Portadas del short de Michael Jackson (1080x1920). Textos y caras dentro de y = 260..1650. */

const TINTA = '#111114';
const AMARILLO = '#ffc21a';
const ROJO = '#e3262e';

const brazo = (lado: -1 | 1, r: {a: number; c: number; k?: number}): Partial<Pose> => (lado < 0 ? {bi: r.a, ci: r.c, ai: r.k ?? 1} : {bd: r.a, cd: r.c, ad: r.k ?? 1});

const Titular: React.FC<{texto: string; tam: number; color?: string; rot?: number}> = ({texto, tam, color = '#fff', rot = 0}) => {
	const base: React.CSSProperties = {fontFamily: CONDENSADA, fontSize: tam, lineHeight: 0.95, letterSpacing: tam * 0.01, textAlign: 'center', whiteSpace: 'pre', textTransform: 'uppercase'};
	return (
		<div style={{position: 'relative', transform: `rotate(${rot}deg)`, filter: `drop-shadow(0 ${tam * 0.07}px 0 rgba(0,0,0,0.6))`}}>
			<div style={{...base, color: TINTA, WebkitTextStroke: `${tam * 0.17}px ${TINTA}`}}>{texto}</div>
			<div style={{...base, color, position: 'absolute', inset: 0}}>{texto}</div>
		</div>
	);
};

const Sello: React.FC<{texto: string; color: string; tam: number; rot?: number}> = ({texto, color, tam, rot = -10}) => (
	<div style={{transform: `rotate(${rot}deg)`, border: `${tam * 0.09}px solid ${color}`, borderRadius: tam * 0.16, padding: `${tam * 0.16}px ${tam * 0.22}px ${tam * 0.08}px`, background: 'rgba(255,255,255,0.94)', boxShadow: '0 14px 0 rgba(0,0,0,0.45)'}}>
		<div style={{fontFamily: CONDENSADA, fontSize: tam, lineHeight: 1, color, letterSpacing: tam * 0.03, whiteSpace: 'nowrap'}}>{texto}</div>
	</div>
);

const Retrato: React.FC<{ropa: typeof ROPA_MJ_1991; ancho: number}> = ({ropa, ancho}) => (
	<div style={{position: 'absolute', left: ancho * -0.1, top: ancho * 0.16, width: ancho * 1.2, height: ancho * 2.7}}>
		<Muneco ropa={ropa} pose={{}} ojos="normal" boca="sonrisa" sombra={false} parpadea={false} respira={false} />
	</div>
);

/* ---------- 1. ¿SE QUISO VOLVER BLANCO? ¡MITO! ---------- */

export const PortadaMito: React.FC = () => (
	<AbsoluteFill style={{background: '#1c1236'}}>
		<AbsoluteFill style={{transform: 'scale(1.05)'}}>
			<EscConcierto color="#1c1236" />
		</AbsoluteFill>
		<Actor x={540} y={2240} alto={1450}>
			<Muneco ropa={ROPA_MJ_1991} pose={{...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 332, 120)), md: 'senala', cabeza: -4}} ojos="entrecerrados" cejas="preocupado" boca="seria" parpadea={false} respira={false} />
		</Actor>
		<div style={{position: 'absolute', top: 266, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
			<Titular texto="¿SE QUISO VOLVER" tam={128} />
			<Titular texto="BLANCO?" tam={210} color={AMARILLO} />
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 1460, display: 'flex', justifyContent: 'center'}}>
			<Sello texto="¡ES UN MITO!" color={ROJO} tam={140} rot={-7} />
		</div>
	</AbsoluteFill>
);

/* ---------- 2. 1978 vs 1991: ¿QUÉ LE PASÓ? ---------- */

export const PortadaFotos: React.FC = () => (
	<AbsoluteFill style={{background: '#5a3b26'}}>
		<EscCorcho />
		<Polaroid x={300} y={930} ancho={460} leyenda="1978 · 20 AÑOS" desde={-100} rot={-7}>
			<Retrato ropa={ROPA_MJ_1978} ancho={432} />
		</Polaroid>
		<Polaroid x={790} y={1120} ancho={460} leyenda="1991 · 33 AÑOS" desde={-100} rot={6}>
			<Retrato ropa={{...ROPA_MJ_1991, cabeza: {...ROPA_MJ_1991.cabeza, gorra: undefined}}} ancho={432} />
		</Polaroid>
		<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
			<path d="M 300 650 Q 560 760 790 840" stroke="#c4262e" strokeWidth={10} fill="none" />
		</svg>
		<div style={{position: 'absolute', top: 266, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
			<Titular texto="¿QUÉ LE PASÓ" tam={150} />
			<Titular texto="A SU PIEL?" tam={170} color={AMARILLO} />
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 1480, display: 'flex', justifyContent: 'center'}}>
			<Sello texto="NO FUE A PROPÓSITO" color="#1f9d48" tam={96} rot={-5} />
		</div>
	</AbsoluteFill>
);

/* ---------- 3. EL CHISME MÁS CRUEL DEL POP ---------- */

export const PortadaChisme: React.FC = () => (
	<AbsoluteFill style={{background: '#1c1c26'}}>
		<EscAlfombra flashes={false} />
		{/* flashes fijos */}
		{[
			[140, 760], [930, 640], [880, 1300], [180, 1360],
		].map(([x, y], i) => (
			<div key={i} style={{position: 'absolute', left: x - 170, top: y - 170, width: 340, height: 340, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,255,255,0.75), rgba(255,255,255,0) 70%)'}} />
		))}
		<Revista x={145} y={760} ancho={270} nombre="EL CHISME" titular="¡WACKO JACKO!" rot={-12}>
			<div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(45deg,#ffe0e0,#ffe0e0 20px,#fff4f4 20px,#fff4f4 40px)'}} />
		</Revista>
		<Revista x={935} y={790} ancho={270} nombre="REVISTA" titular="¿SE BLANQUEA?" color="#1f6fd1" rot={10}>
			<div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(-45deg,#e3eefc,#e3eefc 20px,#f6f9ff 20px,#f6f9ff 40px)'}} />
		</Revista>
		<Actor x={540} y={2230} alto={1380}>
			<Muneco ropa={ROPA_MJ_1991} pose={{...POSES.encogeHombros, cabeza: 6}} ojos="normal" cejas="preocupado" boca="seria" parpadea={false} respira={false} />
		</Actor>
		<div style={{position: 'absolute', top: 266, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
			<Titular texto="EL CHISME" tam={180} color={AMARILLO} />
			<Titular texto="MÁS CRUEL DEL POP" tam={110} />
		</div>
	</AbsoluteFill>
);

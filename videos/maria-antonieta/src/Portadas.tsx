import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Actor, Muneco, POSES, ROPA_NAPOLEON, manosEn, senalar} from './componentes/Muneco';
import {Caricatura, Papel} from './componentes/Objetos';
import {Rayos} from './componentes/Utileria';
import {EscCelular, EscMedidas, MEME, PISO, altoParaCm} from './escenarios/Escenarios';
import {CONDENSADA} from './fuentes';

/* Portadas del short de Napoleón (1080x1920), con los personajes y la tipografía del video.
   Textos y caras dentro de la zona segura y = 260..1650. */

const TINTA = '#111114';
const AMARILLO = '#ffc21a';
const ROJO = '#e3262e';
const VERDE = '#22c55e';

/** Titular condensado con contorno grueso y sombra dura. */
const Titular: React.FC<{texto: string; tam: number; color?: string; rot?: number; estilo?: React.CSSProperties}> = ({texto, tam, color = '#fff', rot = 0, estilo}) => {
	const base: React.CSSProperties = {fontFamily: CONDENSADA, fontSize: tam, lineHeight: 0.95, letterSpacing: tam * 0.01, textAlign: 'center', whiteSpace: 'pre', textTransform: 'uppercase'};
	return (
		<div style={{position: 'relative', transform: `rotate(${rot}deg)`, filter: `drop-shadow(0 ${tam * 0.07}px 0 rgba(0,0,0,0.6))`, ...estilo}}>
			<div style={{...base, color: TINTA, WebkitTextStroke: `${tam * 0.17}px ${TINTA}`}}>{texto}</div>
			<div style={{...base, color, position: 'absolute', inset: 0}}>{texto}</div>
		</div>
	);
};

/** Sello rectangular inclinado. */
const Sello: React.FC<{texto: string; color: string; tam: number; rot?: number}> = ({texto, color, tam, rot = -10}) => (
	<div style={{transform: `rotate(${rot}deg)`, border: `${tam * 0.09}px solid ${color}`, borderRadius: tam * 0.16, padding: `${tam * 0.02}px ${tam * 0.22}px ${tam * 0.06}px`, background: 'rgba(255,255,255,0.92)', boxShadow: '0 14px 0 rgba(0,0,0,0.45)'}}>
		<div style={{fontFamily: CONDENSADA, fontSize: tam, lineHeight: 1, color, letterSpacing: tam * 0.04}}>{texto}</div>
	</div>
);

/** Etiqueta de estatura (verde o roja tachada). */
const Estatura: React.FC<{texto: string; color: string; tachada?: boolean; tam?: number}> = ({texto, color, tachada, tam = 96}) => (
	<div style={{position: 'relative', background: color, border: `9px solid ${TINTA}`, borderRadius: 22, padding: '2px 30px 8px', boxShadow: '0 12px 0 rgba(0,0,0,0.5)'}}>
		<div style={{fontFamily: CONDENSADA, fontSize: tam, color: '#fff', lineHeight: 1.05}}>{texto}</div>
		{tachada && (
			<svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{position: 'absolute', inset: -10, width: 'calc(100% + 20px)', height: 'calc(100% + 20px)'}}>
				<line x1={4} y1={88} x2={96} y2={12} stroke={TINTA} strokeWidth={14} strokeLinecap="round" vectorEffect="non-scaling-stroke" />
				<line x1={4} y1={88} x2={96} y2={12} stroke="#ffffff" strokeWidth={6} strokeLinecap="round" vectorEffect="non-scaling-stroke" />
			</svg>
		)}
	</div>
);

const Vineta: React.FC<{fuerza?: number}> = ({fuerza = 0.5}) => <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(0,0,0,${fuerza}) 100%)`}} />;

const Capa: React.FC<{escala?: number; x?: number; y?: number; children: React.ReactNode}> = ({escala = 1, x = 0, y = 0, children}) => (
	<AbsoluteFill style={{transform: `translate(${x}px, ${y}px) scale(${escala})`}}>{children}</AbsoluteFill>
);

/* ---------- 1. "¿NAPOLEÓN BAJITO? ¡MITO!" ---------- */

export const PortadaNoEraBajito: React.FC = () => (
	<AbsoluteFill style={{background: '#1d3150'}}>
		<Capa escala={1.08} y={-40}>
			<EscMedidas />
			<Actor x={540} y={PISO + 330} alto={altoParaCm(169) * 1.32}>
				<Muneco ropa={ROPA_NAPOLEON} pose={{...POSES.manoEnChaleco, ...manosEn([150, 548]), mi: 'puno', cabeza: -6}} ojos="entrecerrados" cejas="arrogante" boca="sonrisaGrande" parpadea={false} />
			</Actor>
		</Capa>
		<Vineta fuerza={0.45} />
		<div style={{position: 'absolute', top: 268, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4}}>
			<Titular texto="¿NAPOLEÓN" tam={170} />
			<Titular texto="BAJITO?" tam={230} color={AMARILLO} />
		</div>
		<div style={{position: 'absolute', left: 40, top: 1120, transform: 'rotate(-6deg)'}}>
			<Estatura texto="1,57 M" color={ROJO} tachada tam={84} />
		</div>
		<div style={{position: 'absolute', right: 34, top: 900, transform: 'rotate(5deg)'}}>
			<Estatura texto="1,69 M" color={VERDE} tam={104} />
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 1450, display: 'flex', justifyContent: 'center'}}>
			<Sello texto="¡MITO!" color={ROJO} tam={180} rot={-8} />
		</div>
	</AbsoluteFill>
);

/* ---------- 2. "EL PRIMER MEME DE LA HISTORIA" ---------- */

export const PortadaMeme: React.FC = () => (
	<AbsoluteFill style={{background: '#7b3fe4'}}>
		<Capa escala={0.86} x={-90} y={190}>
			<EscCelular reacciones={0.9} />
			<div style={{position: 'absolute', left: MEME.x, top: MEME.y, width: MEME.w, height: MEME.h, overflow: 'hidden', filter: 'sepia(0.55) saturate(0.8) contrast(1.15)'}}>
				<Caricatura ancho={MEME.w} alto={MEME.h} berrinche={-200} titulo={-100} trazo={false} />
			</div>
		</Capa>
		{/* el Napoleón real, furioso, señala su meme */}
		<Actor x={880} y={2260} alto={1380}>
			<Muneco ropa={ROPA_NAPOLEON} pose={{...manosEn([150, 548]), ...((r) => ({bi: r.a, ci: r.c}))(senalar(-1, -300, 40, 0.9)), mi: 'senala', md: 'puno', cabeza: -8}} ojos="grandes" cejas="enojado" boca="grito" parpadea={false} />
		</Actor>
		<div style={{position: 'absolute', top: 262, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
			<Titular texto="EL PRIMER MEME" tam={150} color={AMARILLO} />
			<Titular texto="DE LA HISTORIA" tam={112} />
		</div>
	</AbsoluteFill>
);

/* ---------- 3. "LO QUE TE CONTARON vs LA VERDAD" ---------- */

export const PortadaVersus: React.FC = () => (
	<AbsoluteFill style={{background: '#000'}}>
		{/* izquierda: la caricatura inglesa */}
		<div style={{position: 'absolute', left: 0, top: 0, width: 540, height: 1920, overflow: 'hidden', background: 'linear-gradient(180deg,#5a1a1a,#2a0c0c)'}}>
			<Papel x={270} y={1050} ancho={470} alto={640} rot={-4}>
				<Caricatura ancho={418} alto={588} berrinche={-200} titulo={-100} trazo={false} />
			</Papel>
		</div>
		{/* derecha: el Napoleón real en la tabla */}
		<div style={{position: 'absolute', left: 540, top: 0, width: 540, height: 1920, overflow: 'hidden'}}>
			<div style={{position: 'absolute', left: -540, top: 0, width: 1080, height: 1920}}>
				<EscMedidas />
				<Rayos x={810} y={900} color="#fff6c8" opacidad={0.18} />
				<Actor x={810} y={PISO} alto={altoParaCm(169)}>
					<Muneco ropa={ROPA_NAPOLEON} pose={POSES.pulgarArriba} ojos="entrecerrados" cejas="arrogante" boca="sonrisaGrande" parpadea={false} />
				</Actor>
			</div>
		</div>
		{/* raya diagonal y VS */}
		<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0}}>
			<path d="M 520 0 L 560 0 L 560 1920 L 520 1920 Z" fill={TINTA} />
		</svg>
		<div style={{position: 'absolute', left: 540, top: 1010, transform: 'translate(-50%,-50%) rotate(-8deg)', width: 230, height: 230, borderRadius: '50%', background: AMARILLO, border: `12px solid ${TINTA}`, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 14px 0 rgba(0,0,0,0.5)'}}>
			<div style={{fontFamily: CONDENSADA, fontSize: 130, color: TINTA, lineHeight: 1}}>VS</div>
		</div>
		<div style={{position: 'absolute', top: 268, left: 0, width: 540, display: 'flex', justifyContent: 'center'}}>
			<Titular texto={'LO QUE TE\nCONTARON'} tam={104} color="#ff8a80" />
		</div>
		<div style={{position: 'absolute', top: 268, left: 540, width: 540, display: 'flex', justifyContent: 'center'}}>
			<Titular texto={'LA\nVERDAD'} tam={104} color={VERDE} />
		</div>
		<div style={{position: 'absolute', top: 1430, left: 0, width: 540, display: 'flex', justifyContent: 'center'}}>
			<Estatura texto="1,57 M" color={ROJO} tam={96} />
		</div>
		<div style={{position: 'absolute', top: 1430, left: 540, width: 540, display: 'flex', justifyContent: 'center'}}>
			<Estatura texto="1,69 M" color={VERDE} tam={96} />
		</div>
	</AbsoluteFill>
);

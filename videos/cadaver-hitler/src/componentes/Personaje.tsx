import React from 'react';
import {useCurrentFrame} from 'remotion';

/*
 * Personaje 2D estilo "cabeza blanca redonda + contorno negro grueso + piernas de palito",
 * como en el reel de referencia. Todo es SVG para poder animarlo cuadro a cuadro.
 * Lienzo interno: 400 x 760, con los pies en (200, 730).
 */

export type Ojos = 'normal' | 'cerrados' | 'feliz' | 'x' | 'grandes' | 'entrecerrados' | 'mirandoLado' | 'guinoX';
export type Cejas = 'ninguna' | 'neutral' | 'enojado' | 'sorprendido' | 'preocupado' | 'arrogante';
export type Boca =
	| 'sonrisa'
	| 'seria'
	| 'abierta'
	| 'o'
	| 'mueca'
	| 'dientes'
	| 'sonrisaGrande'
	| 'lengua'
	| 'picara';

export type Diseno = {
	piel: string;
	pelo?: 'hitler' | 'raya' | 'corto' | 'ninguno';
	colorPelo?: string;
	gorra?: 'militar' | 'naval' | 'raf' | 'casco' | 'stahlhelm' | 'ninguna';
	colorGorra?: string;
	colorBanda?: string;
	bigote?: 'cepillo' | 'manubrio' | 'ninguno';
	colorBigote?: string;
	chaqueta: string;
	chaquetaSombra: string;
	botones: string;
	cinturon?: string;
	corbata?: string;
	galones?: boolean; // rayas doradas en las mangas (marina)
	maletin?: boolean;
	ojeras?: boolean;
	monoculo?: boolean;
};

/** Accesorios que se ponen y se quitan durante la escena */
export type Accesorios = {
	gafas?: boolean;
	aureola?: boolean;
	medalla?: boolean;
	salvavidas?: boolean;
};

export type PersonajeProps = {
	diseno: Diseno;
	ojos?: Ojos;
	cejas?: Cejas;
	boca?: Boca;
	hablando?: boolean;
	caminando?: boolean;
	/** ángulos de brazos en grados: 0 = colgando, 90 = horizontal hacia afuera, 160 = arriba */
	brazoIzq?: number;
	brazoDer?: number;
	codoIzq?: number;
	codoDer?: number;
	/** inclinación de la cabeza en grados */
	cabeza?: number;
	/** inclinación del cuerpo en grados */
	inclinacion?: number;
	respira?: boolean;
	parpadea?: boolean;
	/** semilla para desfasar respiración/parpadeo entre personajes */
	semilla?: number;
	sombra?: boolean;
	acc?: Accesorios;
	/** sustituye el color de la chaqueta (p. ej. camiseta antes del uniforme) */
	chaqueta?: string;
};

const TINTA = '#1b1b1f';

const ojosSVG = (tipo: Ojos, parpadeo: boolean) => {
	const pos = [
		[158, 205],
		[242, 205],
	];
	const base = parpadeo && (tipo === 'normal' || tipo === 'grandes' || tipo === 'mirandoLado') ? 'cerrados' : tipo;
	return pos.map(([x, y], i) => {
		const k = `ojo${i}`;
		const t: Ojos = base === 'guinoX' ? (i === 0 ? 'x' : 'feliz') : base;
		switch (t) {
			case 'cerrados':
				return <path key={k} d={`M ${x - 15} ${y} Q ${x} ${y + 8} ${x + 15} ${y}`} stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" />;
			case 'feliz':
				return <path key={k} d={`M ${x - 15} ${y + 6} Q ${x} ${y - 14} ${x + 15} ${y + 6}`} stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" />;
			case 'x':
				return (
					<g key={k} stroke={TINTA} strokeWidth={9} strokeLinecap="round">
						<line x1={x - 16} y1={y - 16} x2={x + 16} y2={y + 16} />
						<line x1={x + 16} y1={y - 16} x2={x - 16} y2={y + 16} />
					</g>
				);
			case 'grandes':
				return (
					<g key={k}>
						<circle cx={x} cy={y} r={27} fill="#fff" stroke={TINTA} strokeWidth={6} />
						<circle cx={x + (i === 0 ? 4 : -4)} cy={y + 2} r={11} fill={TINTA} />
						<circle cx={x + (i === 0 ? 8 : 0)} cy={y - 3} r={3.5} fill="#fff" />
					</g>
				);
			case 'entrecerrados':
				return (
					<g key={k}>
						<path d={`M ${x - 13} ${y - 2} L ${x + 13} ${y - 2} Q ${x + 12} ${y + 14} ${x} ${y + 14} Q ${x - 12} ${y + 14} ${x - 13} ${y - 2} Z`} fill={TINTA} />
						<line x1={x - 18} y1={y - 3} x2={x + 18} y2={y - 3} stroke={TINTA} strokeWidth={7} strokeLinecap="round" />
					</g>
				);
			case 'mirandoLado':
				return (
					<g key={k}>
						<ellipse cx={x + 8} cy={y} rx={11} ry={15} fill={TINTA} />
						<circle cx={x + 12} cy={y - 5} r={3.5} fill="#fff" />
					</g>
				);
			default:
				return (
					<g key={k}>
						<ellipse cx={x} cy={y} rx={11} ry={15} fill={TINTA} />
						<circle cx={x + 4} cy={y - 5} r={3.5} fill="#fff" />
					</g>
				);
		}
	});
};

const cejasSVG = (tipo: Cejas) => {
	const l = (d: string, k: string) => <path key={k} d={d} stroke={TINTA} strokeWidth={10} strokeLinecap="round" fill="none" />;
	switch (tipo) {
		case 'ninguna':
			return null;
		case 'enojado':
			return [l('M 128 158 L 182 180', 'a'), l('M 272 158 L 218 180', 'b')];
		case 'sorprendido':
			return [l('M 133 160 Q 158 138 183 158', 'a'), l('M 217 158 Q 242 138 267 160', 'b')];
		case 'preocupado':
			return [l('M 133 172 L 182 156', 'a'), l('M 267 172 L 218 156', 'b')];
		case 'arrogante':
			return [l('M 133 170 L 182 168', 'a'), l('M 217 160 Q 242 142 267 155', 'b')];
		default:
			return [l('M 135 167 L 180 165', 'a'), l('M 220 165 L 265 167', 'b')];
	}
};

const bocaSVG = (tipo: Boca) => {
	const y = 282;
	switch (tipo) {
		case 'sonrisa':
			return <path d={`M 172 ${y - 6} Q 200 ${y + 18} 228 ${y - 6}`} stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" />;
		case 'picara':
			return <path d={`M 175 ${y} Q 205 ${y + 10} 232 ${y - 12}`} stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" />;
		case 'seria':
			return <line x1={182} y1={y} x2={218} y2={y} stroke={TINTA} strokeWidth={8} strokeLinecap="round" />;
		case 'mueca':
			return <path d={`M 172 ${y + 4} Q 186 ${y - 8} 200 ${y + 2} Q 214 ${y + 10} 228 ${y - 2}`} stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" />;
		case 'o':
			return <ellipse cx={200} cy={y + 2} rx={12} ry={16} fill="#5a1414" stroke={TINTA} strokeWidth={7} />;
		case 'abierta':
			return (
				<g>
					<path d={`M 170 ${y - 8} Q 200 ${y - 12} 230 ${y - 8} Q 228 ${y + 30} 200 ${y + 30} Q 172 ${y + 30} 170 ${y - 8} Z`} fill="#5a1414" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
					<ellipse cx={200} cy={y + 20} rx={14} ry={7} fill="#e2626b" />
				</g>
			);
		case 'sonrisaGrande':
			return (
				<g>
					<path d={`M 164 ${y - 10} L 236 ${y - 10} Q 232 ${y + 32} 200 ${y + 32} Q 168 ${y + 32} 164 ${y - 10} Z`} fill="#5a1414" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
					<rect x={172} y={y - 8} width={56} height={10} fill="#fff" />
					<ellipse cx={200} cy={y + 22} rx={16} ry={7} fill="#e2626b" />
				</g>
			);
		case 'dientes':
			return (
				<g>
					<rect x={168} y={y - 12} width={64} height={30} rx={8} fill="#fff" stroke={TINTA} strokeWidth={7} />
					<line x1={168} y1={y + 3} x2={232} y2={y + 3} stroke={TINTA} strokeWidth={4} />
					{[184, 200, 216].map((x) => (
						<line key={x} x1={x} y1={y - 12} x2={x} y2={y + 18} stroke={TINTA} strokeWidth={4} />
					))}
				</g>
			);
		case 'lengua':
			return (
				<g>
					<path d={`M 196 ${y} Q 194 ${y + 30} 210 ${y + 30} Q 226 ${y + 28} 222 ${y}`} fill="#e2626b" stroke={TINTA} strokeWidth={6} />
					<path d={`M 172 ${y + 2} Q 200 ${y - 6} 232 ${y}`} stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" />
				</g>
			);
	}
};

const brazo = (hombroX: number, hombroY: number, ang: number, codo: number, lado: -1 | 1, color: string, colorSombra: string) => {
	const rad = (ang * Math.PI) / 180;
	const l1 = 62;
	const l2 = 60;
	const ex = hombroX + lado * Math.sin(rad) * l1;
	const ey = hombroY + Math.cos(rad) * l1;
	const rad2 = ((ang + codo) * Math.PI) / 180;
	const hx = ex + lado * Math.sin(rad2) * l2;
	const hy = ey + Math.cos(rad2) * l2;
	return {
		el: (
			<g>
				{/* manga */}
				<path d={`M ${hombroX} ${hombroY} L ${ex} ${ey}`} stroke={TINTA} strokeWidth={30} strokeLinecap="round" />
				<path d={`M ${hombroX} ${hombroY} L ${ex} ${ey}`} stroke={color} strokeWidth={18} strokeLinecap="round" />
				<path d={`M ${ex} ${ey} L ${hx} ${hy}`} stroke={TINTA} strokeWidth={9} strokeLinecap="round" />
				<circle cx={hx} cy={hy} r={15} fill="#fff" stroke={TINTA} strokeWidth={7} />
				<circle cx={hombroX} cy={hombroY} r={4} fill={colorSombra} opacity={0} />
			</g>
		),
		mano: [hx, hy] as const,
	};
};

const gorraSVG = (d: Diseno) => {
	const c = d.colorGorra ?? '#5d6448';
	const banda = d.colorBanda ?? '#2a2a2a';
	switch (d.gorra) {
		case 'militar':
			return (
				<g transform="rotate(-4 200 80)">
					<path d="M 72 92 Q 52 22 200 6 Q 352 18 330 92 Z" fill={c} stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
					<rect x={86} y={78} width={228} height={30} rx={6} fill={banda} stroke={TINTA} strokeWidth={8} />
					<path d="M 96 104 Q 200 150 304 104 Q 200 120 96 104 Z" fill="#111" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
					<path d="M 110 102 Q 200 118 290 102" stroke="#c9c9c9" strokeWidth={4} fill="none" />
					<circle cx={200} cy={93} r={9} fill="#c9c9c9" stroke={TINTA} strokeWidth={3} />
				</g>
			);
		case 'naval':
			return (
				<g transform="rotate(3 200 80)">
					<path d="M 64 88 Q 60 30 200 22 Q 340 30 336 88 Z" fill="#f4f4ef" stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
					<rect x={84} y={76} width={232} height={30} rx={6} fill="#1d1d1d" stroke={TINTA} strokeWidth={8} />
					<path d="M 96 102 Q 200 146 304 102 Q 200 116 96 102 Z" fill="#111" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
					<ellipse cx={200} cy={90} rx={20} ry={14} fill="#e7b93b" stroke={TINTA} strokeWidth={4} />
					<circle cx={200} cy={88} r={6} fill="#b0261e" />
				</g>
			);
		case 'raf':
			return (
				<g transform="rotate(-3 200 80)">
					<path d="M 70 90 Q 64 32 200 24 Q 336 32 330 90 Z" fill={c} stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
					<rect x={86} y={78} width={228} height={28} rx={6} fill="#1d1d1d" stroke={TINTA} strokeWidth={8} />
					<path d="M 98 102 Q 200 144 302 102 Q 200 116 98 102 Z" fill="#111" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
					<path d="M 176 90 L 200 80 L 224 90 L 200 98 Z" fill="#e7b93b" stroke={TINTA} strokeWidth={3} />
				</g>
			);
		case 'stahlhelm':
			return (
				<g>
					<path d="M 66 120 Q 60 6 200 2 Q 340 6 334 120 L 352 150 Q 300 132 290 112 L 110 112 Q 100 132 48 150 Z" fill={c} stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
					<path d="M 110 112 L 290 112" stroke={TINTA} strokeWidth={6} />
					<circle cx={300} cy={70} r={7} fill={TINTA} opacity={0.5} />
				</g>
			);
		case 'casco':
			return (
				<g>
					<ellipse cx={200} cy={92} rx={170} ry={30} fill={c} stroke={TINTA} strokeWidth={9} />
					<path d="M 90 92 Q 96 10 200 8 Q 304 10 310 92 Z" fill={c} stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
				</g>
			);
		default:
			return null;
	}
};

export const Personaje: React.FC<PersonajeProps> = ({
	diseno: dBase,
	ojos = 'normal',
	cejas = 'neutral',
	boca = 'seria',
	hablando = false,
	caminando = false,
	brazoIzq = 12,
	brazoDer = 12,
	codoIzq = 0,
	codoDer = 0,
	cabeza = 0,
	inclinacion = 0,
	respira = true,
	parpadea = true,
	semilla = 0,
	sombra = true,
	acc = {},
	chaqueta,
}) => {
	const d: Diseno = chaqueta ? {...dBase, chaqueta, chaquetaSombra: '#d8d8d8', botones: '#ffffff', corbata: undefined, cinturon: undefined} : dBase;
	const clipId = `cabeza-${React.useId().replace(/:/g, "")}`;
	const f = useCurrentFrame() + semilla * 17;
	const resp = respira ? Math.sin(f / 7) : 0;
	const parpadeo = parpadea && f % 97 > 93;
	const paso = caminando ? Math.sin(f / 2.6) : 0;
	const rebote = caminando ? Math.abs(Math.cos(f / 2.6)) * -10 : 0;

	let bocaFinal = boca;
	if (hablando) {
		const ciclo = Math.floor(f / 3) % 4;
		bocaFinal = (['abierta', 'o', 'abierta', 'seria'] as Boca[])[ciclo];
	}

	const bIzq = brazo(150, 380, brazoIzq + (caminando ? paso * 18 : 0), codoIzq, -1, d.chaqueta, d.chaquetaSombra);
	const bDer = brazo(250, 380, brazoDer - (caminando ? paso * 18 : 0), codoDer, 1, d.chaqueta, d.chaquetaSombra);

	const pierna = (x: number, ang: number) => {
		const rad = (ang * Math.PI) / 180;
		const px = x + Math.sin(rad) * 170;
		const py = 548 + Math.cos(rad) * 170;
		return (
			<g>
				<line x1={x} y1={548} x2={px} y2={py} stroke={TINTA} strokeWidth={9} strokeLinecap="round" />
				<ellipse cx={px + 10} cy={py + 4} rx={22} ry={11} fill={TINTA} />
			</g>
		);
	};

	return (
		<svg viewBox="0 0 400 760" width="100%" height="100%" style={{overflow: 'visible'}}>
			{sombra && <ellipse cx={200} cy={738} rx={120} ry={20} fill="rgba(0,0,0,0.28)" />}
			<g transform={`translate(0 ${rebote}) rotate(${inclinacion} 200 730)`}>
				{/* piernas */}
				{pierna(178, 4 + paso * 22)}
				{pierna(222, -4 - paso * 22)}
				<g transform={`translate(200 545) scale(${1 + resp * 0.012} ${1 - resp * 0.015}) translate(-200 -545)`}>
					{/* brazo de atrás */}
					{bIzq.el}
					{/* torso */}
					<path d="M 140 345 Q 122 450 130 532 Q 200 572 270 532 Q 278 450 260 345 Q 200 322 140 345 Z" fill={d.chaqueta} stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
					<path d="M 252 360 Q 266 450 262 528 Q 240 545 222 552 Q 248 470 236 352 Z" fill={d.chaquetaSombra} opacity={0.55} />
					{/* solapas y cuello */}
					<path d="M 168 338 L 200 400 L 232 338" fill="none" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
					{d.corbata && <path d="M 192 350 L 208 350 L 212 398 L 200 412 L 188 398 Z" fill={d.corbata} stroke={TINTA} strokeWidth={5} />}
					<line x1={200} y1={410} x2={200} y2={548} stroke={TINTA} strokeWidth={5} />
					{[430, 468, 506].map((y) => (
						<circle key={y} cx={212} cy={y} r={6.5} fill={d.botones} stroke={TINTA} strokeWidth={3} />
					))}
					{d.cinturon && (
						<g>
							<path d="M 128 482 Q 200 500 272 482 L 272 504 Q 200 522 128 504 Z" fill={d.cinturon} stroke={TINTA} strokeWidth={6} />
							<rect x={189} y={490} width={24} height={22} rx={3} fill="#c9a43a" stroke={TINTA} strokeWidth={4} />
						</g>
					)}
					{/* bolsillos */}
					<path d="M 146 400 L 182 400 L 182 430 L 146 430 Z" fill="none" stroke={TINTA} strokeWidth={4} opacity={0.6} />
					{acc.medalla && (
						<g transform={`rotate(${Math.sin(f / 5) * 8} 165 392)`}>
							<path d="M 152 372 L 165 420 L 178 372 Z" fill="#c3342b" stroke={TINTA} strokeWidth={4} />
							<path d="M 158 372 L 165 404 L 172 372" fill="#2a4fa8" />
							<circle cx={165} cy={432} r={19} fill="#f2c53d" stroke={TINTA} strokeWidth={5} />
							<path d="M 165 420 L 169 429 L 178 430 L 171 436 L 173 445 L 165 440 L 157 445 L 159 436 L 152 430 L 161 429 Z" fill="#fff3b0" />
						</g>
					)}
					{acc.salvavidas && (
						<g>
							<ellipse cx={200} cy={455} rx={92} ry={44} fill="none" stroke={TINTA} strokeWidth={46} />
							<ellipse cx={200} cy={455} rx={92} ry={44} fill="none" stroke="#f26b2a" strokeWidth={32} />
							<ellipse cx={200} cy={455} rx={92} ry={44} fill="none" stroke="#fff" strokeWidth={32} strokeDasharray="40 62" />
						</g>
					)}
					{/* brazo de adelante */}
					{bDer.el}
					{d.galones && (
						<g stroke="#e7b93b" strokeWidth={5}>
							<circle cx={bDer.mano[0]} cy={bDer.mano[1]} r={0} />
						</g>
					)}
					{d.maletin && (
						<g transform={`translate(${bDer.mano[0]} ${bDer.mano[1]})`}>
							<path d="M 0 0 Q 8 26 4 40" stroke="#8a8a8a" strokeWidth={4} fill="none" strokeDasharray="6 4" />
							<path d="M -18 44 Q -18 30 4 30 Q 26 30 26 44" stroke={TINTA} strokeWidth={7} fill="none" />
							<rect x={-44} y={42} width={96} height={68} rx={8} fill="#6b3f20" stroke={TINTA} strokeWidth={7} />
							<line x1={-44} y1={62} x2={52} y2={62} stroke={TINTA} strokeWidth={4} />
							<rect x={-2} y={56} width={14} height={12} rx={2} fill="#d4a93c" stroke={TINTA} strokeWidth={3} />
						</g>
					)}
				</g>
				{/* cabeza */}
				<g transform={`translate(0 ${resp * 2.5}) rotate(${cabeza} 200 330)`}>
					{d.pelo === 'raya' && (
						<path d="M 58 210 Q 40 90 150 52 Q 250 30 330 110 Q 352 150 345 210 Q 320 130 260 112 Q 180 100 120 150 Q 80 180 58 210 Z" fill={d.colorPelo ?? '#6b4a2b'} stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
					)}
					<circle cx={200} cy={200} r={150} fill={d.piel} stroke={TINTA} strokeWidth={11} />
					{d.ojeras && (
						<g fill="#9fb59a" opacity={0.7}>
							<ellipse cx={158} cy={232} rx={22} ry={8} />
							<ellipse cx={242} cy={232} rx={22} ry={8} />
						</g>
					)}
					<clipPath id={clipId}>
						<circle cx={200} cy={200} r={146} />
					</clipPath>
					{d.pelo === 'corto' && (
						<g>
							<g clipPath={`url(#${clipId})`}>
								<path d="M 30 30 L 370 30 L 370 150 Q 330 108 250 104 Q 236 86 222 104 Q 140 100 30 168 Z" fill={d.colorPelo ?? '#2f2a24'} />
							</g>
							<path d="M 62 146 Q 140 100 222 104 Q 236 86 250 104 Q 312 108 346 140" stroke={TINTA} strokeWidth={6} fill="none" strokeLinejoin="round" />
						</g>
					)}
					{d.pelo === 'hitler' && (
						<g>
							<g clipPath={`url(#${clipId})`}>
								<path d="M 40 40 L 300 40 L 300 100 Q 230 118 150 178 Q 120 196 96 214 L 40 200 Z" fill={d.colorPelo ?? '#141414'} />
							</g>
							<path d="M 300 100 Q 230 118 150 178 Q 120 196 96 214" stroke={TINTA} strokeWidth={6} fill="none" />
						</g>
					)}
					{d.pelo === 'raya' && (
						<path d="M 62 150 Q 110 92 200 80 Q 160 100 130 140 Z" fill={d.colorPelo ?? '#6b4a2b'} stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
					)}
					{ojosSVG(ojos, parpadeo)}
					{cejasSVG(cejas)}
					{d.bigote === 'cepillo' && <rect x={184} y={246} width={32} height={20} rx={4} fill={d.colorBigote ?? '#141414'} />}
					{bocaSVG(bocaFinal)}
					{d.bigote === 'manubrio' && (
						<path
							d="M 200 252 Q 170 240 150 256 Q 128 272 118 250 Q 124 280 150 274 Q 176 268 200 262 Q 224 268 250 274 Q 276 280 282 250 Q 272 272 250 256 Q 230 240 200 252 Z"
							fill={d.colorBigote ?? '#6b4a2b'}
							stroke={TINTA}
							strokeWidth={5}
							strokeLinejoin="round"
						/>
					)}
					{d.monoculo && (
						<g>
							<circle cx={242} cy={205} r={30} fill="rgba(255,255,255,0.25)" stroke="#c9a43a" strokeWidth={7} />
							<path d="M 268 222 Q 290 290 262 340" stroke="#c9a43a" strokeWidth={3} fill="none" />
						</g>
					)}
					{acc.gafas && (
						<g>
							<path d="M 118 192 Q 120 238 160 238 Q 192 236 192 196 Z" fill="#111" stroke={TINTA} strokeWidth={6} />
							<path d="M 208 196 Q 208 236 240 238 Q 280 238 282 192 Z" fill="#111" stroke={TINTA} strokeWidth={6} />
							<path d="M 112 190 L 288 190" stroke={TINTA} strokeWidth={9} strokeLinecap="round" />
							<path d="M 130 200 L 150 214" stroke="#fff" strokeWidth={5} strokeLinecap="round" opacity={0.7} />
							<path d="M 220 200 L 240 214" stroke="#fff" strokeWidth={5} strokeLinecap="round" opacity={0.7} />
						</g>
					)}
					{gorraSVG(d)}
					{acc.aureola && (
						<g transform={`translate(0 ${Math.sin(f / 8) * 6})`}>
							<ellipse cx={200} cy={20} rx={110} ry={26} fill="none" stroke="#fff3a0" strokeWidth={26} opacity={0.5} />
							<ellipse cx={200} cy={20} rx={110} ry={26} fill="none" stroke="#ffd84a" strokeWidth={14} />
						</g>
					)}
				</g>
			</g>
		</svg>
	);
};

/* ---------- Diseños de los personajes del guion ---------- */

export const HITLER: Diseno = {
	piel: '#ffffff',
	pelo: 'hitler',
	colorPelo: '#141414',
	gorra: 'militar',
	colorGorra: '#5f6848',
	colorBanda: '#3a3f2c',
	bigote: 'cepillo',
	chaqueta: '#6a7352',
	chaquetaSombra: '#454b33',
	botones: '#c9c9c9',
	cinturon: '#3b2a1a',
};

/** Ewen Montagu: oficial de inteligencia naval británico */
export const MONTAGU: Diseno = {
	piel: '#ffffff',
	pelo: 'raya',
	colorPelo: '#6b4a2b',
	gorra: 'naval',
	chaqueta: '#1f2c4f',
	chaquetaSombra: '#121a33',
	botones: '#e7b93b',
	corbata: '#111111',
	galones: true,
};

/** Charles Cholmondeley: teniente de la RAF, el del bigote */
export const CHOLMONDELEY: Diseno = {
	piel: '#ffffff',
	pelo: 'raya',
	colorPelo: '#3d2b1c',
	gorra: 'raf',
	colorGorra: '#5f7392',
	bigote: 'manubrio',
	colorBigote: '#4a3020',
	chaqueta: '#5f7392',
	chaquetaSombra: '#3e4e68',
	botones: '#e7b93b',
	corbata: '#1d1d1d',
};

/** "William Martin": el espía muerto, uniforme de los Royal Marines */
export const ESPIA_MUERTO: Diseno = {
	piel: '#dbe8d2',
	pelo: 'corto',
	colorPelo: '#3a3128',
	gorra: 'ninguna',
	chaqueta: '#8a7b4e',
	chaquetaSombra: '#5f5434',
	botones: '#c9a43a',
	cinturon: '#5a4426',
	corbata: '#3a3324',
	maletin: true,
	ojeras: true,
};

/** Soldado aliado genérico */
export const SOLDADO: Diseno = {
	piel: '#ffffff',
	gorra: 'casco',
	colorGorra: '#6d7046',
	chaqueta: '#7c7550',
	chaquetaSombra: '#57523a',
	botones: '#5a5236',
	cinturon: '#4a3c22',
};

/** Oficial alemán genérico (sin insignias), con monóculo */
export const OFICIAL_ALEMAN: Diseno = {
	piel: '#ffffff',
	pelo: 'raya',
	colorPelo: '#c9b27a',
	gorra: 'militar',
	colorGorra: '#5f6848',
	colorBanda: '#3a3f2c',
	chaqueta: '#6a7352',
	chaquetaSombra: '#454b33',
	botones: '#c9c9c9',
	cinturon: '#2b2016',
	monoculo: true,
};

/** Segundo oficial alemán, de bigotito y gorra gris */
export const OFICIAL_ALEMAN_2: Diseno = {
	piel: '#ffffff',
	pelo: 'raya',
	colorPelo: '#4a3426',
	gorra: 'militar',
	colorGorra: '#7b8068',
	colorBanda: '#2f3324',
	bigote: 'cepillo',
	colorBigote: '#4a3426',
	chaqueta: '#7b8068',
	chaquetaSombra: '#555946',
	botones: '#c9c9c9',
	cinturon: '#2b2016',
};

/** Soldado alemán con casco */
export const SOLDADO_ALEMAN: Diseno = {
	piel: '#ffffff',
	gorra: 'stahlhelm',
	colorGorra: '#5c6150',
	chaqueta: '#6a7352',
	chaquetaSombra: '#454b33',
	botones: '#9a9a9a',
	cinturon: '#2b2016',
};

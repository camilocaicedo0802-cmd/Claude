import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {CHOLMONDELEY, ESPIA_MUERTO, HITLER, MONTAGU, Personaje, SOLDADO} from './componentes/Personaje';

const P: React.FC<{x: number; y: number; h: number; children: React.ReactNode}> = ({x, y, h, children}) => (
	<div style={{position: 'absolute', left: x - (h * 400) / 760 / 2, top: y - h, width: (h * 400) / 760, height: h}}>{children}</div>
);

export const Prueba: React.FC = () => (
	<AbsoluteFill>
		<Img src={staticFile('fondos/oficina.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
		<P x={270} y={1000} h={560}><Personaje diseno={HITLER} cejas="enojado" boca="dientes" brazoDer={70} codoDer={40} /></P>
		<P x={800} y={1000} h={560}><Personaje diseno={MONTAGU} cejas="arrogante" boca="picara" /></P>
		<P x={270} y={1700} h={560}><Personaje diseno={CHOLMONDELEY} ojos="grandes" cejas="sorprendido" boca="sonrisaGrande" brazoIzq={150} codoIzq={10} /></P>
		<P x={800} y={1700} h={560}><Personaje diseno={ESPIA_MUERTO} ojos="x" cejas="ninguna" boca="lengua" cabeza={-12} brazoIzq={4} brazoDer={4} respira={false} /></P>
		<P x={540} y={1850} h={300}><Personaje diseno={SOLDADO} boca="sonrisa" /></P>
	</AbsoluteFill>
);

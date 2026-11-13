import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {COMPANERA, ENFERMERA, JUEZ, MEDICO, OFICINISTA, Personaje, VESNA} from './componentes/Personaje';
import {EnMundo} from './componentes/Toma';
import {Carrito} from './componentes/Vuelo';

export const Prueba: React.FC = () => (
	<AbsoluteFill>
		<Img src={staticFile('fondos/cabina.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
		<EnMundo x={200} y={900} alto={560}><Personaje diseno={VESNA} boca="sonrisa" brazoDer={120} /></EnMundo>
		<EnMundo x={540} y={900} alto={560}><Personaje diseno={COMPANERA} boca="sonrisaGrande" ojos="feliz" /></EnMundo>
		<EnMundo x={880} y={900} alto={560}><Personaje diseno={OFICINISTA} boca="mueca" cejas="preocupado" /></EnMundo>
		<EnMundo x={200} y={1500} alto={560}><Personaje diseno={MEDICO} boca="sonrisa" ojos="feliz" /></EnMundo>
		<EnMundo x={540} y={1500} alto={560}><Personaje diseno={VESNA} acc={{vendas: true, momia: true}} ojos="cerrados" boca="seria" /></EnMundo>
		<EnMundo x={880} y={1500} alto={560}><Personaje diseno={VESNA} acc={{pepinos: true, toalla: true}} boca="sonrisa" /></EnMundo>
		<EnMundo x={200} y={1900} alto={380}><Personaje diseno={JUEZ} boca="seria" /></EnMundo>
		<EnMundo x={420} y={1900} alto={380}><Personaje diseno={ENFERMERA} boca="sonrisa" /></EnMundo>
		<EnMundo x={640} y={1900} alto={380}><Personaje diseno={VESNA} boca="grito" ojos="grandes" cejas="sorprendido" brazoIzq={150} brazoDer={150} /></EnMundo>
		<Carrito x={900} y={1900} ancho={260} ojos="guino" medalla />
	</AbsoluteFill>
);

import React from 'react';
import {Composition, continueRender, delayRender, staticFile} from 'remotion';
import edl from './edl.json';
import {Main} from './Main';

const weights = ['500', '600', '700', '800', '900'];
const styles = ['normal', 'italic'];
if (typeof document !== 'undefined') {
	const handle = delayRender('Loading Poppins');
	const loads: Promise<unknown>[] = [];
	for (const w of weights) {
		for (const s of styles) {
			for (const sub of ['latin', 'latin-ext']) {
				const face = new FontFace('Poppins', `url(${staticFile(`fonts/poppins-${sub}-${w}-${s}.woff2`)}) format('woff2')`, {
					weight: w,
					style: s,
					unicodeRange: sub === 'latin' ? 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2212, U+2215' : 'U+0100-024F, U+1E00-1EFF',
				});
				loads.push(face.load().then((f) => document.fonts.add(f)).catch(() => undefined));
			}
		}
	}
	Promise.all(loads).then(() => continueRender(handle));
}

export const Root: React.FC = () => (
	<Composition id="Main" component={Main} durationInFrames={edl.durationInFrames} fps={edl.fps} width={edl.width} height={edl.height} />
);

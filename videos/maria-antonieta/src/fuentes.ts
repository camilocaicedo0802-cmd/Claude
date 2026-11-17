import {continueRender, delayRender, staticFile} from 'remotion';

/* Fuentes guardadas en public/fuentes (el subconjunto "latin" ya trae á é í ó ú ñ ¿ ¡). */
export const TITULAR = 'Montserrat';
export const SERIF = 'Playfair Display';
/** condensada y gruesa, como los textos del video de referencia */
export const CONDENSADA = 'Anton';

const fuentes: [string, string][] = [
	[TITULAR, 'fuentes/montserrat-latin.woff2'],
	[SERIF, 'fuentes/playfair-latin.woff2'],
	[CONDENSADA, 'fuentes/anton-latin.woff2'],
];

if (typeof document !== 'undefined') {
	const handle = delayRender('Cargando fuentes locales');
	Promise.all(
		fuentes.map(([familia, archivo]) => {
			const ff = new FontFace(familia, `url(${staticFile(archivo)}) format('woff2')`, {weight: '100 900'});
			(document.fonts as unknown as {add: (f: FontFace) => void}).add(ff);
			return ff.load();
		}),
	)
		.then(() => continueRender(handle))
		.catch((e) => {
			console.error(e);
			continueRender(handle);
		});
}

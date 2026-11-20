// Renderiza cuadros sueltos (para revisar) con un solo empaquetado.
// Uso: node scripts/cuadros.mjs <carpeta_salida> <escala> f1 f2 f3 ...
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';

const [salida, escala, ...cuadros] = process.argv.slice(2);
const navegador = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const comp = await selectComposition({serveUrl, id: 'Completo', browserExecutable: navegador});
for (const c of cuadros) {
	const f = Number(c);
	await renderStill({composition: comp, serveUrl, frame: f, output: path.join(salida, `c${String(f).padStart(4, '0')}.png`), scale: Number(escala), browserExecutable: navegador});
	process.stdout.write(`${f} `);
}
console.log('listo');

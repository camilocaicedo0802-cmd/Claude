import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition, ensureBrowser} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';

const BROWSER = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
const frames = process.argv.slice(2).map(Number);
const outDir = path.resolve('stills');
fs.mkdirSync(outDir, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), publicDir: path.resolve('public')});
const composition = await selectComposition({serveUrl, id: 'Main', browserExecutable: BROWSER});
for (const frame of frames) {
	await renderStill({composition, serveUrl, frame, output: path.join(outDir, `f_${String(frame).padStart(4, '0')}.png`), browserExecutable: BROWSER, scale: Number(process.env.SCALE ?? 0.5)});
	console.log('still', frame);
}

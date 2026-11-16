// Fotogramas de control: node scripts/stills.mjs 1.2 4.0 ...   (segundos)
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
const secs = process.argv.slice(2).map(Number);
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const composition = await selectComposition({serveUrl, id: 'Ganador4', chromiumOptions: {gl: 'angle'}});
fs.mkdirSync('out/stills', {recursive: true});
for (const s of secs) {
  const frame = Math.round(s * 60);
  await renderStill({composition, serveUrl, output: `out/stills/t${s.toFixed(2)}.jpg`, frame, imageFormat: 'jpeg', jpegQuality: 80, scale: 0.5, chromiumOptions: {gl: 'angle'}});
  console.log('ok', s);
}

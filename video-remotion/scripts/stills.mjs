// Renderiza fotogramas de control: node scripts/stills.mjs 15 70 130 ...
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';
const frames = process.argv.slice(2).map(Number);
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const composition = await selectComposition({serveUrl, id: 'Video1Grow', chromiumOptions: {gl: 'angle'}});
for (const frame of frames) {
  await renderStill({composition, serveUrl, output: `out/stills/f${String(frame).padStart(5, '0')}.jpg`, frame, imageFormat: 'jpeg', jpegQuality: 80, scale: 0.5, chromiumOptions: {gl: 'angle'}});
  console.log('ok', frame);
}

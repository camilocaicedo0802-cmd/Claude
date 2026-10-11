// Renderiza fotogramas sueltos de "Main" para revisión visual: OUT_DIR=/ruta node scripts/stills.mjs 1.0 2.5 ...
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
const out = process.env.OUT_DIR;
const secs = process.argv.slice(2).map(Number);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const comp = await selectComposition({ serveUrl, id: "Main" });
for (const s of secs) {
  const frame = Math.min(comp.durationInFrames - 1, Math.round(s * comp.fps));
  await renderStill({ serveUrl, composition: comp, frame, output: `${out}/t_${s.toFixed(2).padStart(5, "0")}.png`, scale: 0.5 });
  console.log("ok", s);
}

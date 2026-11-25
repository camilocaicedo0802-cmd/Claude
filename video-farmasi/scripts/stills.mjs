import fs from "node:fs";
// Renderiza fotogramas sueltos (segundos de edición) para revisión: node scripts/stills.mjs 1.0 2.6 ...
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
const tiempos = process.argv.slice(2).map(Number);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const composition = await selectComposition({ serveUrl, id: process.env.COMP ?? "Farmasi" });
for (const t of tiempos) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(t * composition.fps));
  const output = path.resolve(`out/stills/${process.env.COMP ?? "Farmasi"}_${t.toFixed(2)}.jpg`);
  await renderStill({ serveUrl, composition, frame, output, imageFormat: "jpeg", jpegQuality: 80, scale: 0.4, chromiumOptions: { gl: "swangle" } });
  console.log("ok", t, output);
}
fs.rmSync(serveUrl, { recursive: true, force: true }); // no dejar copias del bundle en /tmp

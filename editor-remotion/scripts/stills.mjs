// Renderiza fotogramas sueltos para revisar el montaje: node scripts/stills.mjs 1.2 3.5 12 …  (segundos)
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";

const times = process.argv.slice(2).map(Number);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), webpackOverride: (c) => c });
const composition = await selectComposition({ serveUrl, id: "ArmandoBits" });
for (const t of times) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(t * composition.fps));
  const output = `out/stills/t_${t.toFixed(2).padStart(6, "0")}.jpg`;
  await renderStill({ composition, serveUrl, output, frame, imageFormat: "jpeg", jpegQuality: 88, scale: 0.5 });
  console.log("ok", t, output);
}

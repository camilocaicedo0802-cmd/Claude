// Renderiza fotogramas sueltos para revisar el montaje:
//   node scripts/stills.mjs 1.2 3.5 12 …                       (segundos, opción A)
//   node scripts/stills.mjs --comp=ArmandoBitsHorizontal 1.2 …  (opción B)
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";

const args = process.argv.slice(2);
const id = (args.find((a) => a.startsWith("--comp=")) ?? "--comp=ArmandoBits").slice(7);
const scale = Number((args.find((a) => a.startsWith("--scale=")) ?? "--scale=0.5").slice(8));
const times = args.filter((a) => !a.startsWith("--")).map(Number);
const dir = id === "ArmandoBits" ? "out/stills" : `out/stills-${id}`;
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), webpackOverride: (c) => c });
const composition = await selectComposition({ serveUrl, id });
for (const t of times) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(t * composition.fps));
  const output = `${dir}/t_${t.toFixed(2).padStart(6, "0")}.jpg`;
  await renderStill({ composition, serveUrl, output, frame, imageFormat: "jpeg", jpegQuality: 88, scale });
  console.log("ok", t, output);
}

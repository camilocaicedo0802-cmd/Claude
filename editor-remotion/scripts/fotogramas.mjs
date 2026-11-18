// Renderiza fotogramas sueltos para revisar el montaje sin exportar el vídeo entero.
// Uso: node scripts/fotogramas.mjs 0.5 3.9 6.3 ...   (segundos)  [--escala=0.5]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const escala = Number((args.find((a) => a.startsWith("--escala=")) ?? "--escala=0.5").split("=")[1]);
const tiempos = args.filter((a) => !a.startsWith("--")).map(Number);
const salida = path.resolve("out/stills");
fs.mkdirSync(salida, { recursive: true });

const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const composition = await selectComposition({ serveUrl, id: "SemillaCertificada" });
for (const t of tiempos) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(t * composition.fps));
  const output = path.join(salida, `t${t.toFixed(2).padStart(5, "0")}.jpg`);
  await renderStill({ composition, serveUrl, frame, output, imageFormat: "jpeg", jpegQuality: 88, scale: escala });
  console.log("ok", output);
}

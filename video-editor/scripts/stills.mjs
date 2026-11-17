// Renderiza fotogramas sueltos para revisión. Uso: node scripts/stills.mjs <dir> f1 f2 ...
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
import fs from "node:fs";

const [outDir, ...frames] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id: "Main" });
for (const f of frames.map(Number)) {
  const t = Date.now();
  await renderStill({ composition, serveUrl, frame: f, output: path.join(outDir, `f${String(f).padStart(4, "0")}.jpg`), imageFormat: "jpeg", jpegQuality: 85, scale: 0.5 });
  console.log("frame", f, Date.now() - t, "ms");
}

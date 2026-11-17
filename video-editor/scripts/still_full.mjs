// Un fotograma a resolución completa en PNG. Uso: node scripts/still_full.mjs <salida.png> <frame>
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
const [out, frame] = process.argv.slice(2);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id: "Main" });
await renderStill({ composition, serveUrl, frame: Number(frame), output: out, imageFormat: "png" });
console.log("ok", out);

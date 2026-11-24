// Sonido v2 (UGC sencillo). SOLO SFX de la carpeta del cliente (public/sfx_sel, copiados de "SFX PACK 1/2").
import { BLOQUES, DURACION_TOTAL_S, ESCENAS, UI } from "./plan";
import { PALABRAS, f, inicio, limpio } from "./util";

export type Sfx = { at: number; src: string; vol: number; dur?: number }; // at en fotogramas (60 fps)
const ev: Sfx[] = [];
const add = (at: number, src: string, vol: number, dur?: number) => ev.push({ at: Math.max(0, Math.round(at)), src, vol, dur });

// Tecleo suave en los destacados (regla del cliente): ≤ 4 teclas por destacado, vol. 0,3
const teclas = ["tecla_1", "tecla_2", "tecla_3", "tecla_4", "tecla_5"];
let k = 0;
const teclear = (desde: number, n: number) => {
  for (let i = 0; i < n; i++) add(desde + i * 3, teclas[k++ % teclas.length], 0.3);
};
for (const b of BLOQUES) {
  if (!b.destacado.length) continue;
  const t0 = f(inicio(b.destacado[0]));
  const letras = b.destacado.map((i) => limpio(PALABRAS[i].text)).join("").length;
  const n = Math.min(4, Math.max(2, Math.round(letras / 3)));
  teclear(b.estilo === "detras" ? t0 - 20 : t0 - 8, n);
  if (b.icono) add(t0 + 4, "pop", 0.18);
}
// Cortes secos a b-roll y vuelta: swoosh suave
for (const e of ESCENAS) {
  add(f(e.desde) - 3, "swoosh_6", 0.2);
  add(f(e.hasta) - 3, "swoosh_4", 0.14);
}
// Superposición de glucosa: pop al entrar y clic en el chip
for (const [r, palabra] of [[UI.graficaSube, 58], [UI.graficaBaja, 87]] as const) {
  add(f(r.desde), "pop", 0.22);
  add(f(inicio(palabra)) - 6, "click_4", 0.3);
}
export const SFX: Sfx[] = ev.sort((a, b) => a.at - b.at);

// Música: constante bajo la voz y fundido final de 0,8 s
export const volumenMusica = (frame: number) => {
  const finF = f(DURACION_TOTAL_S);
  return 0.12 * Math.min(1, Math.max(0, (finF - frame) / 48));
};

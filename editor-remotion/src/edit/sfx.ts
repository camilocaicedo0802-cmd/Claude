// Diseño de sonido. TODOS los efectos salen de las carpetas del cliente (material/drive/SFX → public/media/sfx).
// La correspondencia con el archivo original está en src/data/sfx.json. Reglas: estilo.md §8.4.
import { rnd } from "../anim";
import { BEAT_PARTITURA, CUTS, END, T, seg } from "../timeline";
import { BEAT_LINES } from "./beat";

export type Sfx = { t: number; name: string; vol: number; lead?: number; trim?: [number, number] };
const list: Sfx[] = [];
const add = (t: number, name: string, vol: number, extra: Partial<Sfx> = {}) => list.push({ t, name, vol, ...extra });
/** Teclas: una por palabra/letra, alternando 5 muestras distintas para que no suene a metralleta. */
const KEYS = ["key_1", "key_2", "key_3", "key_4", "key_5"];
export const typeKeys = (times: number[], vol = 0.3) => times.forEach((t, i) => add(t, KEYS[Math.floor(rnd(t * 31 + i) * KEYS.length)], vol * (0.8 + 0.4 * rnd(i + t))));
const typeLetters = (start: number, n: number, cps: number, vol = 0.26) => typeKeys(Array.from({ length: n }, (_, i) => start + i / cps), vol);
/** Barras + destello: whoosh grave que llega al pico y golpe. */
const bars = (t: number) => {
  add(t, "whoosh_deep", 0.36, { lead: 0.85 });
  add(t, "boom", 0.34);
};
/** Palabra gigante detrás del sujeto: el plano se abre (whoosh) y la palabra cae con cuerpo grave. */
const behind = (zoomAt: number, wordAt: number) => {
  add(zoomAt, "whoosh_fast", 0.3, { lead: 0.05 });
  add(wordAt, "sub_hit", 0.36);
  add(wordAt, "pop", 0.22);
};

// ── Gancho ──
add(0.0, "swish_a", 0.5); // apertura con zoom
behind(0.12, T("s01", 4)); // «Años»
add(T("s01", 6) + 0.02, "swish_b", 0.3); // cierre de plano
add(T("s01", 8), "pop", 0.3); // «Personaje»
add(T("s01", 8) + 0.05, "whoosh_1", 0.2, { lead: 0.14 }); // icono neón
add(T("s01", 9) - 0.02, "shutter", 0.45); // desenfoque = obturador (confirmado en la referencia)
typeLetters(T("s01", 13), 6, 30, 0.22); // nombre 1
typeLetters(T("s01", 14) + 0.12, 5, 30, 0.22); // nombre 2
typeLetters(T("s01", 16), 6, 30, 0.24); // nombre 3
add(T("s01", 16), "sub_hit", 0.34); // «Nombre»

// ── Problema ──
bars(CUTS.problema);
add(T("s02", 0) + 0.02, "notif", 0.5); // llega el casting
typeKeys([T("s02", 0) + 0.12, T("s02", 1) + 0.1, T("s02", 2) + 0.1, T("s02", 3) + 0.12], 0.22);
add(T("s02", 3), "pop", 0.26); // «Casting»
add(T("s02", 6) - 0.02, "whoosh_2", 0.3, { lead: 0.21 }); // sale el b-roll
add(T("s02", 8), "sub_hit", 0.28); // «El mismo tono» + salto de zoom
[14, 17, 20].forEach((i, k) => {
  add(T("s02", i) - 0.03, k === 1 ? "click_2" : "click_1", 0.42); // cada ficha: clic…
  add(T("s02", i) - 0.03, "sub_hit", 0.24); // …con cuerpo grave
});
add(T("s03", 0), "swish_b", 0.34);
add(T("s03", 7), "pop", 0.26);
add(seg("s03").cuts[0], "swish_a", 0.28);
add(T("s03", 11) + 0.22, "marker", 0.6, { trim: [0.05, 0.5] }); // tachado a mano
add(T("s04", 6), "pop", 0.26);
add(T("s04", 7) - 0.08, "click_double", 0.36); // tarjeta 1
typeKeys([10, 11, 12, 13, 14].map((i) => T("s04", i)), 0.3);
add(T("s04", 15) - 0.06, "click_double", 0.36); // tarjeta 2
typeKeys([17, 18, 19, 20, 21, 23].map((i) => T("s04", i)), 0.3);
behind(seg("s05").start + 0.05, T("s05", 3)); // «Problema»
add(T("s05", 7), "swish_b", 0.3);
add(T("s05", 7), "pop", 0.26); // «Decisiones»
add(T("s05", 10), "shutter_click", 0.5); // visor REC
add(T("s05", 14) + 0.1, "shutter", 0.36); // «cámara»
add(END("s05") - 0.05, "sub_drop", 0.5); // cierre del problema (caída de subgrave, como la referencia)

// ── Solución ──
bars(CUTS.solucion);
add(T("s06", 3), "pop", 0.26);
add(seg("s06").cuts[0], "swish_a", 0.26);
behind(seg("s06").cuts[0] + 0.06, T("s06", 13)); // «BITS»
[17, 18, 19, 20].forEach((i) => add(T("s06", i), "click_1", 0.34)); // nodos BIT 1–4
add(T("s06", 22), "whoosh_fast", 0.36, { lead: 0.25 }); // el punto recorre los BITS
add(BEAT_PARTITURA.start - 0.05, "whoosh_3", 0.34, { lead: 0.17 }); // entra el b-roll de la partitura
typeKeys(BEAT_LINES.flat().map((w) => w.t), 0.34); // frase tecleada «Piénsalo como una partitura…»
add(T("s08", 1), "pop", 0.2);
add(T("s08", 4), "swish_b", 0.26); // ligaduras
add(T("s08", 12), "sub_hit", 0.32); // «Melodía»
[3, 6, 11].forEach((i, k) => {
  add(T("s09", i) - 0.03, k === 1 ? "click_2" : "click_1", 0.42);
  add(T("s09", i) - 0.03, "sub_hit", 0.22);
});
add(T("s10", 2), "pop", 0.26);
behind(T("s10", 7) - 0.08, T("s10", 10)); // «Avance»
add(T("s11", 1) - 0.05, "whoosh_2", 0.3, { lead: 0.21 }); // b-roll de la actriz
add(T("s11", 2), "pop", 0.24);
add(T("s11", 5), "sub_hit", 0.3); // «Multidimensionales»
add(T("s11", 5) + 0.35, "swish_a", 0.26); // vuelve Armando
add(T("s11", 7), "pop", 0.24);
add(T("s11", 10) - 0.1, "whoosh_3", 0.3, { lead: 0.17 }); // b-roll del ojo
add(T("s11", 11), "sub_hit", 0.3); // «Atención»

// ── Testimonio ──
add(CUTS.testimonio - 0.1, "whoosh_fast", 0.4, { lead: 0.25 }); // glitch + corte
add(CUTS.testimonio, "shutter_click", 0.4);
seg("s12").cuts.forEach((c) => add(c, "swish_a", 0.2)); // cortes de silencio
[2, 11, 24, 33, 36, 48, 54, 61].forEach((i) => add(T("s12", i), "pop", 0.16));
add(T("s12", 41), "sub_hit", 0.3); // «BITS»
add(T("s12", 69), "sub_hit", 0.3); // «Partner»

// ── CTA ──
// Aquí el whoosh es corto para no pisar el final de la frase del testimonio («…la respuesta de mi partner»).
add(CUTS.cta, "whoosh_fast", 0.36, { lead: 0.25 });
add(CUTS.cta, "boom", 0.34);
behind(CUTS.cta + 0.05, T("s13", 4)); // «Repitas»
add(T("s13", 8), "swish_b", 0.3);
add(T("s13", 11), "pop", 0.26); // «Personajes»
add(seg("s14").start - 0.02, "whoosh_1", 0.3, { lead: 0.14 });
add(T("s14", 0), "click_double", 0.32); // píldora
typeLetters(T("s14", 1), 3, 15, 0.42); // B · I · T
add(T("s14", 1) + 0.47, "pop", 0.34); // botón enviar
add(T("s14", 6), "sub_hit", 0.34); // «Masterclass»
add(T("s14", 7) - 0.05, "whoosh_2", 0.3, { lead: 0.21 }); // tarjeta de la clase
add(T("s14", 7) + 0.32, "click_1", 0.36); // sello GRATIS
add(T("s14", 24), "sub_hit", 0.34); // «Casting»

export const SFX = list;

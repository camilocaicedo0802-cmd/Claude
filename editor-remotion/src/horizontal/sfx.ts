// Sonido de la opción B: la misma lista que el montaje vertical (todo de las carpetas del cliente) más las teclas
// de los titulares que se teclean arriba. No se añade ningún efecto que no esté en src/data/sfx.json.
import { rnd } from "../anim";
import { SFX, Sfx } from "../edit/sfx";
import { T } from "../timeline";
import { HEADLINES, NAMES } from "./plan";
import { TYPE_CPS } from "./TopZone";

const KEYS = ["key_1", "key_2", "key_3", "key_4", "key_5"];
const extra: Sfx[] = [];
const keysAt = (start: number, n: number, step: number, vol: number) => {
  for (let i = 0; i < n; i++) {
    const t = start + i * step;
    extra.push({ t, name: KEYS[Math.floor(rnd(t * 31 + i) * KEYS.length)], vol: vol * (0.8 + 0.4 * rnd(i + t)) });
  }
};
// Titulares tecleados: una tecla cada dos letras (10 por segundo) para que no suene a metralleta.
HEADLINES.filter((h) => h.typed !== false).forEach((h) => keysAt(h.start + 0.12, Math.ceil(h.text.replace(/ /g, "").length / 2), 2 / TYPE_CPS, 0.2));
// Primer nombre del globo «PERSONAJE» (los tres siguientes ya están en la lista común).
keysAt(NAMES[0].t, NAMES[0].text.length, 1 / 30, 0.22);
// Flecha que barre la zona inferior en «que el conflicto avance».
extra.push({ t: T("s10", 10) + 0.04, name: "whoosh_1", vol: 0.22, lead: 0.14 });

export const SFX_H: Sfx[] = [...SFX, ...extra];

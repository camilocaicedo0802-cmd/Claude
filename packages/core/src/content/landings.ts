import { img } from "./chapters";
import type { ImageAsset } from "./types";

/** A landing page shown as a scrollable phone preview and as a full-length page of its own. */
export interface Landing {
  slug: string;
  title: string;
  /** Short line shown under the title. */
  context: string;
  description: string;
  role: string;
  /** The landing's screens, top to bottom (pages of the source PDF). */
  pages: ImageAsset[];
}

const thermobeltScreens = [
  "Portada: Adiós al dolor, calor real en 30 segundos a donde vayas, con el botón Quiero mi alivio ahora",
  "Sección ¿Te suena familiar?, con los dolores del día a día que resuelve el producto",
  "Sección El cambio se siente en minutos, con un antes y después",
  "Sección Beneficios que mejoran tu día a día, con íconos de calor, autonomía y portabilidad",
  "Sección Características técnicas del cinturón térmico",
  "Sección Un solo producto, múltiples alivios, con las zonas del cuerpo donde se usa",
  "Sección Así de fácil, con el modo de uso en cuatro pasos",
  "Sección de opiniones de clientas con calificación y fotos",
  "Comparación del cinturón térmico frente a la bolsa de agua caliente y los parches térmicos",
  "Oferta de lanzamiento con precio, descuento, cuenta regresiva y medios de pago",
  "Preguntas frecuentes y cierre con llamado a la compra",
];

export const landings: Landing[] = [
  {
    slug: "almohadilla-termica",
    title: "Almohadilla térmica",
    context: "Landing page de producto para ecommerce",
    description:
      "Landing de venta para un cinturón térmico, pensada para leerse en el celular pantalla por pantalla: portada con la promesa y el llamado a la compra, los dolores que resuelve, un antes y después, beneficios, características técnicas, modo de uso, opiniones de clientas, comparación con otras opciones, oferta de lanzamiento y preguntas frecuentes.",
    role: "Diseño de la landing page",
    pages: thermobeltScreens.map((alt, i) => img(`landing-thermobelt-${String(i + 1).padStart(2, "0")}`, `Landing almohadilla térmica, pantalla ${i + 1}: ${alt}`)),
  },
];

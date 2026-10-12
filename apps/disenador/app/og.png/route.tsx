import { ogImage } from "@jcc/core/lib/og";

export const dynamic = "force-static";

/** Share card exported as /og.png (with extension, so any static host serves it as image/png). */
export function GET() {
  return ogImage({
    role: "Diseñador digital y audiovisual",
    headline: ["Diseño que detiene el", "scroll y se mueve."],
    subtitle: "Diseño digital · Motion Graphics · Contenido con IA",
    poster: "tiempo-motion",
  });
}

import { ogImage } from "@jcc/core/lib/og";

export const dynamic = "force-static";

/** Share card exported as /og.png (with extension, so any static host serves it as image/png). */
export function GET() {
  return ogImage({
    role: "Editor de video y diseñador digital",
    // Non-breaking spaces keep "que se sienten." together on the second line of the card.
    headline: ["Transformo ideas en", "experiencias visuales que\u00A0se\u00A0sienten."],
    subtitle: "Edición de video · Motion graphics · Diseño · IA",
    poster: "editor-promo",
  });
}

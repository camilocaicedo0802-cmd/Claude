import { ogImage } from "@jcc/core/lib/og";

export const dynamic = "force-static";

/** Share card exported as /og.png (with extension, so any static host serves it as image/png). */
export function GET() {
  return ogImage({
    role: "Editor de video y motion designer",
    headline: ["Transformo ideas en", "experiencias que se sienten."],
    subtitle: "Video Editing · Motion Graphics · Visual Storytelling",
    poster: "editor-promo",
  });
}

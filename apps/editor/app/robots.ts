import type { MetadataRoute } from "next";
import { copy } from "./site";

export const dynamic = "force-static";

export default function robots(): MetadataRoute.Robots {
  return { rules: { userAgent: "*", allow: "/" }, sitemap: `${copy.url}/sitemap.xml` };
}

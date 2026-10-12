import type { MetadataRoute } from "next";
import { copy, projects } from "./site";

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: `${copy.url}/`, changeFrequency: "monthly", priority: 1 },
    ...projects.map((p) => ({ url: `${copy.url}/trabajos/${p.slug}/`, changeFrequency: "yearly" as const, priority: 0.7 })),
  ];
}

import type { MetadataRoute } from "next";
import { landings } from "@jcc/core/content/landings";
import { caseHref, landingHref } from "@jcc/core/lib/paths";
import { chapters, copy } from "./site";

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: `${copy.url}/`, changeFrequency: "monthly", priority: 1 },
    ...chapters.map((c) => ({ url: `${copy.url}/${caseHref(c.slug).replace(/^\//, "")}`, changeFrequency: "yearly" as const, priority: 0.7 })),
    ...landings.map((l) => ({ url: `${copy.url}/${landingHref(l.slug).replace(/^\//, "")}`, changeFrequency: "yearly" as const, priority: 0.6 })),
  ];
}

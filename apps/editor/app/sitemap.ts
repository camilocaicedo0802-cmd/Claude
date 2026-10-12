import type { MetadataRoute } from "next";
import { caseHref } from "@jcc/core/lib/paths";
import { chapters, copy } from "./site";

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: `${copy.url}/`, changeFrequency: "monthly", priority: 1 },
    ...chapters.map((c) => ({ url: `${copy.url}/${caseHref(c.slug).replace(/^\//, "")}`, changeFrequency: "yearly" as const, priority: 0.7 })),
  ];
}

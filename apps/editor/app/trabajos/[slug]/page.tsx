import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SiteShell } from "@jcc/core/components/SiteShell";
import { pieceSrc, posterSrc } from "@jcc/core/content/media";
import { caseHref, homeHref } from "@jcc/core/lib/paths";
import { ChapterPage } from "@jcc/core/sections/ChapterPage";
import { Contact } from "@jcc/core/sections/Contact";
import { chapters, copy, links, otherSite } from "../../site";

export const dynamicParams = false;

export function generateStaticParams() {
  return chapters.map((c) => ({ slug: c.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const chapter = chapters.find((c) => c.slug === slug);
  if (!chapter) return {};
  const first = chapter.items[0];
  const image = first.kind === "video" ? posterSrc(first.video) : pieceSrc(first.image.file);
  const title = `${chapter.title}: ${chapter.context}`;
  return {
    title,
    description: chapter.description,
    alternates: { canonical: caseHref(slug) },
    openGraph: { title, description: chapter.description, images: [{ url: image }] },
  };
}

export default async function ProjectPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const index = chapters.findIndex((c) => c.slug === slug);
  if (index === -1) notFound();
  const homeLinks = links.map((l) => ({ ...l, href: homeHref(l.href) }));
  return (
    <SiteShell links={links} role={copy.role} home={homeHref()}>
      <ChapterPage
        chapter={chapters[index]}
        prev={chapters[(index - 1 + chapters.length) % chapters.length]}
        next={chapters[(index + 1) % chapters.length]}
      />
      <Contact links={homeLinks} otherSite={otherSite} role={copy.role} />
    </SiteShell>
  );
}

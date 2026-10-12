import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SiteShell } from "@jcc/core/components/SiteShell";
import { pieceSrc, posterSrc } from "@jcc/core/content/media";
import { CaseStudy } from "@jcc/core/sections/CaseStudy";
import { Contact } from "@jcc/core/sections/Contact";
import { copy, links, otherSite, projects } from "../../site";

export const dynamicParams = false;

export function generateStaticParams() {
  return projects.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const project = projects.find((p) => p.slug === slug);
  if (!project) return {};
  const image = project.media.kind === "video" ? posterSrc(project.media.video) : pieceSrc(project.media.images[0].file);
  const title = project.client ? `${project.title} para ${project.client}` : project.title;
  return {
    title,
    description: project.description,
    alternates: { canonical: `/trabajos/${slug}/` },
    openGraph: { title, description: project.description, images: [{ url: image }] },
  };
}

export default async function ProjectPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const index = projects.findIndex((p) => p.slug === slug);
  if (index === -1) notFound();
  const homeLinks = links.map((l) => ({ ...l, href: `/${l.href}` }));
  return (
    <SiteShell links={links} role={copy.role} home="/">
      <CaseStudy
        project={projects[index]}
        index={index}
        total={projects.length}
        prev={projects[(index - 1 + projects.length) % projects.length]}
        next={projects[(index + 1) % projects.length]}
      />
      <Contact links={homeLinks} otherSite={otherSite} role={copy.role} />
    </SiteShell>
  );
}

import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SiteShell } from "@jcc/core/components/SiteShell";
import { landings } from "@jcc/core/content/landings";
import { pieceSrc } from "@jcc/core/content/media";
import { homeHref, landingHref } from "@jcc/core/lib/paths";
import { Contact } from "@jcc/core/sections/Contact";
import { LandingPage } from "@jcc/core/sections/LandingPage";
import { copy, links } from "../../site";

export const dynamicParams = false;

export function generateStaticParams() {
  return landings.map((l) => ({ slug: l.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const landing = landings.find((l) => l.slug === slug);
  if (!landing) return {};
  const title = `Landing page: ${landing.title}`;
  return {
    title,
    description: landing.description,
    alternates: { canonical: landingHref(slug) },
    openGraph: { title, description: landing.description, images: [{ url: pieceSrc(landing.pages[0].file) }] },
  };
}

export default async function LandingRoute({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const landing = landings.find((l) => l.slug === slug);
  if (!landing) notFound();
  const homeLinks = links.map((l) => ({ ...l, href: homeHref(l.href) }));
  return (
    <SiteShell links={links} role={copy.role} home={homeHref()}>
      <LandingPage landing={landing} />
      <Contact links={homeLinks} role={copy.role} />
    </SiteShell>
  );
}

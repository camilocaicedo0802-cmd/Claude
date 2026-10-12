import type { Metadata } from "next";
import { profile, siteCopy, whatsappUrl } from "../content/profile";
import type { SiteId } from "../content/types";

export function siteMetadata(site: SiteId): Metadata {
  const copy = siteCopy[site];
  return {
    metadataBase: new URL(copy.url),
    title: { default: copy.title, template: `%s | ${profile.name}` },
    description: copy.description,
    keywords: copy.keywords,
    authors: [{ name: profile.name }],
    creator: profile.name,
    alternates: { canonical: "/" },
    openGraph: {
      type: "website",
      locale: "es_CO",
      url: "/",
      siteName: profile.name,
      title: copy.title,
      description: copy.description,
      images: [{ url: "/og.png", width: 1200, height: 630, alt: `${profile.name}, ${copy.role}` }],
    },
    twitter: { card: "summary_large_image", title: copy.title, description: copy.description, images: ["/og.png"] },
    robots: { index: true, follow: true },
  };
}

export function personJsonLd(site: SiteId) {
  const copy = siteCopy[site];
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Person",
        name: profile.name,
        jobTitle: copy.role,
        email: `mailto:${profile.email}`,
        telephone: profile.whatsappDisplay,
        url: copy.url,
        sameAs: profile.socials.map((s) => s.href),
      },
      {
        "@type": "ProfessionalService",
        name: `${profile.name} | ${copy.role}`,
        description: copy.description,
        url: copy.url,
        areaServed: "Worldwide",
        contactPoint: { "@type": "ContactPoint", contactType: "sales", url: whatsappUrl(), availableLanguage: ["es"] },
      },
    ],
  };
}

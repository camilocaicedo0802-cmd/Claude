/**
 * Internal URLs. With NEXT_PUBLIC_RELATIVE_EXPORT=1 the static export uses
 * relative, file-based URLs (index.html, trabajo-<slug>.html, media/...) so
 * the output folder works from any sub-path or plain file host.
 */
export const RELATIVE_EXPORT = process.env.NEXT_PUBLIC_RELATIVE_EXPORT === "1";

/** Home page, optionally with a section hash ("#contacto"). */
export const homeHref = (hash = "") => (RELATIVE_EXPORT ? `index.html${hash}` : `/${hash}`);

/** Case study page of a project. */
export const caseHref = (slug: string) => (RELATIVE_EXPORT ? `trabajo-${slug}.html` : `/trabajos/${slug}/`);

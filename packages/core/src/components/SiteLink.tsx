import Link from "next/link";
import type { ComponentProps } from "react";
import { RELATIVE_EXPORT } from "../lib/paths";

type Props = Omit<ComponentProps<typeof Link>, "href"> & { href: string };

/** Next.js Link, or a plain anchor in relative exports (no client router or RSC requests). */
export function SiteLink({ href, prefetch, replace, scroll, ...rest }: Props) {
  if (RELATIVE_EXPORT) return <a href={href} {...rest} />;
  return <Link href={href} prefetch={prefetch} replace={replace} scroll={scroll} {...rest} />;
}

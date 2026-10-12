"use client";
import type { ReactNode } from "react";
import { ViewerProvider } from "./MediaViewer";
import { Nav, type NavLink } from "./Nav";
import { ScrollProgress } from "./ScrollProgress";
import { SmoothScroll } from "./SmoothScroll";
import { WhatsAppFloat } from "./WhatsAppFloat";

interface Props {
  children: ReactNode;
  links: NavLink[];
  role: string;
  /** "" on the home page, "/" on inner pages so anchors point back home. */
  home?: string;
}

export function SiteShell({ children, links, role, home = "" }: Props) {
  return (
    <ViewerProvider>
      <a
        href="#contenido"
        className="fixed left-4 top-3 z-[90] -translate-y-20 bg-signal px-4 py-2 text-sm font-medium focus:translate-y-0"
      >
        Saltar al contenido
      </a>
      <SmoothScroll />
      <ScrollProgress />
      <Nav links={links} role={role} home={home} />
      <main id="contenido">{children}</main>
      <WhatsAppFloat />
    </ViewerProvider>
  );
}

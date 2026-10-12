import type { Metadata, Viewport } from "next";
import { personJsonLd, siteMetadata } from "@jcc/core/lib/seo";
import "./globals.css";

export const metadata: Metadata = siteMetadata("disenador");

export const viewport: Viewport = {
  themeColor: "#080808",
  colorScheme: "dark",
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        {children}
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(personJsonLd("disenador")) }} />
      </body>
    </html>
  );
}

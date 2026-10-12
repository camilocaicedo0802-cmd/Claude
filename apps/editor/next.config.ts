import path from "node:path";
import type { NextConfig } from "next";

// NEXT_PUBLIC_RELATIVE_EXPORT=1: relative asset URLs (assets/_next) so the export works from any folder or sub-path.
const relative = process.env.NEXT_PUBLIC_RELATIVE_EXPORT === "1";

const nextConfig: NextConfig = {
  assetPrefix: relative ? "./assets" : undefined,
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  transpilePackages: ["@jcc/core"],
  turbopack: { root: path.join(__dirname, "..", "..") },
};

export default nextConfig;

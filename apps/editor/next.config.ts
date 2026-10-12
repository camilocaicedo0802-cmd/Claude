import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  transpilePackages: ["@jcc/core"],
  turbopack: { root: path.join(__dirname, "..", "..") },
};

export default nextConfig;

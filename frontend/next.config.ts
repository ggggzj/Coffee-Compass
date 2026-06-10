import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Pin the workspace root to this app so a stray lockfile elsewhere on the
  // machine can't make Next infer the wrong root.
  turbopack: {
    root: path.resolve(__dirname),
  },
};

export default nextConfig;

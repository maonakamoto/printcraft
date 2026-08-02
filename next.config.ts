import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // scripts/hetzner/deploy.sh rsyncs .next/standalone; without this the deploy
  // aborts with "no standalone output".
  output: "standalone",
  images: {
    remotePatterns: [
      {
        // Self-hosted Supabase storage (Hetzner migration 2026-06)
        protocol: "https",
        hostname: "supabase.orangecat.ch",
        pathname: "/storage/v1/object/**",
      },
    ],
  },
};

export default nextConfig;

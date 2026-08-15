import type { NextConfig } from "next";

/**
 * Backend origin for the same-origin `/api/v1/*` calls made by the client.
 * Build-time inlined so it works identically on Vercel and on a self-hosted
 * VPS. Override with NEXT_PUBLIC_API_BASE_URL at build; default is the VPS
 * API host. The path is forwarded unchanged; the backend nginx terminates
 * TLS and reverse-proxies to the FastAPI service.
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://api.mypapyr.com";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${API_BASE_URL}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;

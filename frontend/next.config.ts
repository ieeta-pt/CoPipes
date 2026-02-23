import type { NextConfig } from "next";

const apiUrl: string = process.env.NEXT_PUBLIC_API_URL || "";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;

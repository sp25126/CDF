/** @type {import('next').NextConfig} */
const nextConfig = {
  /**
   * Dev Proxy — rewrites /api/* → http://localhost:8000/api/*
   *
   * This means:
   *   - The browser always calls same-origin /api/...  (no CORS preflight)
   *   - The Next.js dev server forwards the request to FastAPI on :8000
   *   - In production, your reverse proxy (nginx / Vercel / Railway) does the same
   *
   * The backend URL comes from NEXT_PUBLIC_BACKEND_URL env var so it is
   * easy to change without touching code.
   */
  async rewrites() {
    const backendUrl =
      process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },

  /**
   * Security headers for production classroom use.
   * These are no-ops in dev but protect the app when deployed.
   */
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

module.exports = nextConfig;

/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    mdxRs: true
  },
  async redirects() {
    return [
      {
        source: "/lab.html",
        destination: "/lab",
        permanent: false
      }
    ];
  },
  async rewrites() {
    return [
      {
        source: "/chat",
        destination: "/legacy/chat.html"
      },
      {
        source: "/news",
        destination: "/legacy/news.html"
      },
      {
        source: "/:path*.html",
        destination: "/legacy/:path*.html"
      },
      {
        source: "/docs/:path*",
        destination: "/legacy/:path*"
      }
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**"
      }
    ]
  }
};

export default nextConfig;

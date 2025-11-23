/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // No Vercel, não usar standalone (é para Docker)
  // output: process.env.NODE_ENV === 'production' ? 'standalone' : undefined,
  images: {
    domains: ["localhost"],
  },
  env: {
    API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
  // Configuração para garantir processamento correto do CSS
  webpack: (config, { isServer }) => {
    // Garantir que o CSS seja processado corretamente
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }
    return config;
  },
};

module.exports = nextConfig;

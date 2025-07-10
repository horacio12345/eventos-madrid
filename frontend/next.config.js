//frontend/next.config.js

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configuración optimizada para servidor Hetzner
  output: 'standalone',
  
  // Variables de entorno públicas
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
    NEXT_PUBLIC_APP_NAME: process.env.APP_NAME || 'Eventos Mayores Madrid'
  },

  // Optimizaciones para performance
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // ============= BUILD PERMISIVO =============
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // ==========================================

  // Configuración de imágenes
  images: {
    domains: ['localhost'],
    formats: ['image/webp', 'image/avif'],
  },

  // Headers de seguridad
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },

  // Redirects para admin
  async redirects() {
    return [
      {
        source: '/admin',
        destination: '/admin/dashboard',
        permanent: false,
      },
    ]
  },

  // Configuración de Webpack para optimización
  webpack: (config, { dev, isServer }) => {
    // Optimizaciones de producción
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
        },
      }
    }

    return config
  },

  // Experimental features para Next.js 14
  experimental: {
    serverComponentsExternalPackages: ['axios'],
  },
}

module.exports = nextConfig
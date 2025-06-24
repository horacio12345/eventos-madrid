// app/layout.tsx

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter'
});

export const metadata: Metadata = {
  title: 'Eventos Mayores Madrid',
  description: 'Descubre eventos gratuitos y de bajo coste para personas mayores en la Comunidad de Madrid',
  keywords: ['eventos', 'mayores', 'Madrid', 'actividades', 'cultura', 'gratuito', 'tercera edad'],
  authors: [{ name: 'Eventos Mayores Madrid' }],
  creator: 'Eventos Mayores Madrid',
  publisher: 'Eventos Mayores Madrid',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    title: 'Eventos Mayores Madrid',
    description: 'Descubre eventos gratuitos y de bajo coste para personas mayores en la Comunidad de Madrid',
    url: 'https://eventos-mayores-madrid.com',
    siteName: 'Eventos Mayores Madrid',
    locale: 'es_ES',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Eventos Mayores Madrid',
    description: 'Descubre eventos gratuitos y de bajo coste para personas mayores en la Comunidad de Madrid',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'tu-google-verification-code',
    yandex: 'tu-yandex-verification-code',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className={inter.variable}>
      <head>
        {/* Favicon y iconos */}
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        
        {/* Meta tags adicionales para accesibilidad */}
        <meta name="theme-color" content="#0ea5e9" />
        <meta name="msapplication-TileColor" content="#0ea5e9" />
        <meta name="msapplication-TileImage" content="/ms-icon-144x144.png" />
        
        {/* Preload de fonts críticas */}
        <link
          rel="preload"
          href="/fonts/inter-var.woff2"
          as="font"
          type="font/woff2"
          crossOrigin=""
        />
      </head>
      <body 
        className={`
          ${inter.className} 
          min-h-screen 
          bg-gray-50 
          text-gray-900 
          antialiased
          selection:bg-primary-100 
          selection:text-primary-900
        `}
        suppressHydrationWarning={true}
      >
        {/* Skip link para accesibilidad */}
        <a
          href="#main-content"
          className="
            sr-only 
            focus:not-sr-only 
            focus:absolute 
            focus:top-4 
            focus:left-4 
            focus:z-50 
            bg-primary-600 
            text-white 
            px-4 
            py-2 
            rounded-lg 
            font-medium 
            focus-ring
          "
        >
          Saltar al contenido principal
        </a>

        {/* Contenido principal */}
        <div id="main-content" className="min-h-screen">
          {children}
        </div>

        {/* Scripts de analytics (solo en producción) */}
        {process.env.NODE_ENV === 'production' && (
          <>
            {/* Google Analytics */}
            <script
              dangerouslySetInnerHTML={{
                __html: `
                  // Google Analytics code aquí si es necesario
                  console.log('Eventos Mayores Madrid - Producción');
                `,
              }}
            />
          </>
        )}
      </body>
    </html>
  );
}
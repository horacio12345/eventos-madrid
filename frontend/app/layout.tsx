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
  title: 'Agenda Activa',
  description: 'Descubre eventos gratuitos y de bajo coste para personas mayores en la Comunidad de Madrid',
  keywords: ['eventos', 'mayores', 'Madrid', 'actividades', 'cultura', 'gratuito', 'tercera edad'],
  authors: [{ name: 'Agenda Activa' }],
  creator: 'Horacio Rodriguez C.',
  publisher: 'Horacio Rodriguez C.',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    title: 'Agenda Activa',
    description: 'Eventos gratuitos y de bajo coste para Seniors',
    url: 'seniors.horacioai.com',
    siteName: 'Agenda Activa',
    locale: 'es_ES',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Agenda Activa',
    description: 'Eventos gratuitos y de bajo coste para Seniors',
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
      <body 
        className={`
          ${inter.className} 
          min-h-screen 
          bg-white 
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
      </body>
    </html>
  );
}
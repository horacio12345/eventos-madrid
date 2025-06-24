/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      './pages/**/*.{js,ts,jsx,tsx,mdx}',
      './components/**/*.{js,ts,jsx,tsx,mdx}',
      './app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
      extend: {
        // Colores accesibles para personas mayores
        colors: {
          primary: {
            50: '#f0f9ff',
            100: '#e0f2fe',
            200: '#bae6fd',
            300: '#7dd3fc',
            400: '#38bdf8',
            500: '#0ea5e9',
            600: '#0284c7',
            700: '#0369a1',
            800: '#075985',
            900: '#0c4a6e',
          },
          secondary: {
            50: '#fdf2f8',
            100: '#fce7f3',
            200: '#fbcfe8',
            300: '#f9a8d4',
            400: '#f472b6',
            500: '#ec4899',
            600: '#db2777',
            700: '#be185d',
            800: '#9d174d',
            900: '#831843',
          },
          success: {
            50: '#f0fdf4',
            100: '#dcfce7',
            200: '#bbf7d0',
            300: '#86efac',
            400: '#4ade80',
            500: '#22c55e',
            600: '#16a34a',
            700: '#15803d',
            800: '#166534',
            900: '#14532d',
          },
          warning: {
            50: '#fffbeb',
            100: '#fef3c7',
            200: '#fde68a',
            300: '#fcd34d',
            400: '#fbbf24',
            500: '#f59e0b',
            600: '#d97706',
            700: '#b45309',
            800: '#92400e',
            900: '#78350f',
          },
          error: {
            50: '#fef2f2',
            100: '#fee2e2',
            200: '#fecaca',
            300: '#fca5a5',
            400: '#f87171',
            500: '#ef4444',
            600: '#dc2626',
            700: '#b91c1c',
            800: '#991b1b',
            900: '#7f1d1d',
          }
        },
        
        // Tipografía optimizada para lectura fácil
        fontFamily: {
          sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
          serif: ['Georgia', 'Times New Roman', 'serif'],
          mono: ['Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace'],
        },
        
        // Tamaños de fuente grandes para accesibilidad
        fontSize: {
          'xs': ['0.75rem', { lineHeight: '1.5' }],
          'sm': ['0.875rem', { lineHeight: '1.6' }],
          'base': ['1rem', { lineHeight: '1.6' }],
          'lg': ['1.125rem', { lineHeight: '1.6' }],
          'xl': ['1.25rem', { lineHeight: '1.6' }],
          '2xl': ['1.5rem', { lineHeight: '1.5' }],
          '3xl': ['1.875rem', { lineHeight: '1.4' }],
          '4xl': ['2.25rem', { lineHeight: '1.3' }],
          '5xl': ['3rem', { lineHeight: '1.2' }],
          '6xl': ['3.75rem', { lineHeight: '1.1' }],
        },
        
        // Espaciado consistente
        spacing: {
          '18': '4.5rem',
          '72': '18rem',
          '84': '21rem',
          '96': '24rem',
        },
        
        // Animaciones suaves para UX
        animation: {
          'fade-in': 'fadeIn 0.5s ease-in-out',
          'slide-up': 'slideUp 0.3s ease-out',
          'bounce-gentle': 'bounceGentle 1s ease-in-out infinite',
        },
        
        keyframes: {
          fadeIn: {
            '0%': { opacity: '0' },
            '100%': { opacity: '1' },
          },
          slideUp: {
            '0%': { transform: 'translateY(10px)', opacity: '0' },
            '100%': { transform: 'translateY(0)', opacity: '1' },
          },
          bounceGentle: {
            '0%, 100%': { transform: 'translateY(-5%)' },
            '50%': { transform: 'translateY(0)' },
          },
        },
        
        // Sombras más suaves
        boxShadow: {
          'gentle': '0 2px 8px rgba(0, 0, 0, 0.1)',
          'card': '0 4px 16px rgba(0, 0, 0, 0.1)',
          'strong': '0 8px 32px rgba(0, 0, 0, 0.15)',
        },
        
        // Breakpoints personalizados
        screens: {
          'xs': '475px',
          '3xl': '1600px',
        },
      },
    },
    plugins: [
      require('@tailwindcss/forms'),
      require('@tailwindcss/typography'),
      
      // Plugin personalizado para estilos de accesibilidad
      function({ addUtilities }) {
        const newUtilities = {
          '.focus-ring': {
            '&:focus': {
              outline: '2px solid #0ea5e9',
              outlineOffset: '2px',
            },
          },
          '.btn-primary': {
            '@apply bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 focus-ring transition-colors': {},
          },
          '.btn-secondary': {
            '@apply bg-gray-200 text-gray-900 px-6 py-3 rounded-lg font-medium hover:bg-gray-300 focus-ring transition-colors': {},
          },
          '.card': {
            '@apply bg-white rounded-xl shadow-card p-6 border border-gray-100': {},
          },
          '.text-readable': {
            '@apply text-lg leading-relaxed': {},
          },
          '.contrast-high': {
            '@apply bg-white text-gray-900 border-2 border-gray-900': {},
          }
        }
        
        addUtilities(newUtilities)
      }
    ],
  }
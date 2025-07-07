module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#7033ff',
          foreground: '#ffffff',
        },
        secondary: {
          DEFAULT: '#edf0f4',
          foreground: '#080808',
        },
        accent: {
          DEFAULT: '#e2ebff',
          foreground: '#1e69dc',
        },
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
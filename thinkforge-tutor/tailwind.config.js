/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      colors: {
        // Exact palette from the brief — solid colors only, no gradients.
        bg: {
          DEFAULT: '#0B1120',
          alt: '#0F172A',
        },
        card: {
          DEFAULT: '#111827',
          alt: '#172033',
        },
        borderc: '#243047',
        primary: {
          DEFAULT: '#2563EB',
          hover: '#1D4ED8',
        },
        success: {
          DEFAULT: '#10B981',
          hover: '#059669',
        },
        warning: {
          DEFAULT: '#F59E0B',
          hover: '#D97706',
        },
      },
      borderRadius: {
        lg2: '0.625rem',
      },
    },
  },
  plugins: [],
}

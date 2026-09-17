/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#18332d',
        moss: '#2e6b57',
        lime: '#c8f169',
        sand: '#f3f0e8',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        panel: '0 20px 50px rgba(23, 51, 45, 0.14)',
      },
    },
  },
  plugins: [],
}

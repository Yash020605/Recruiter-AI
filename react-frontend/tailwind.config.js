/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        background: '#0b0c10',
        card: '#15161b',
        primary: '#6366f1',
        secondary: '#8b5cf6'
      }
    },
  },
  plugins: [],
}

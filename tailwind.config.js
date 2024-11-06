/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        satoshi: ['Satoshi', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
        poppins: ['Poppins', 'sans-serif'],
      },
      colors: {
        'teal': '#2F4F4F',
        'navbar': '#112D2C',
        'light_teal': '#406969',
        'dark_teal': '#1B2E2E',
        'intro': '#1A3C3B',
        'intro_button': '#17252A',
        'intro_button_dark': '#0F171B',
      },
      screens: {
        'xxs': '400px', // min-width
      },
    },
  },
  plugins: [],
}
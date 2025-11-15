/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./nuxt.config.{js,ts}"
  ],
  theme: {
    extend: {
      colors: {
        
        'vg-bg': {
          DEFAULT: '#121224',     
          softer: '#16162a',        
          card: '#1a1a30',        
        }
      }
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: false, 
    base: true,
    styled: true,
    utils: true,
    rtl: false,
    prefix: "",
    logs: true,
  },
}
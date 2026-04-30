/** @type {import('tailwindcss').Config} */
module.exports = {
  // NOTE: Update this to include the paths to all files that contain Nativewind classes.
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./screens/**/*.{js, jsx, ts, tsx}",
    "./components/**/*.{js, jsx, ts, tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {

        primaryPurple: '#404CCF',
        accentGreen: '#4DBF69',
        backgroundGrey: '#F6F6F6',
        textWhite: '#FFFFFF',
        textBlack: '#000000'
        
      }



    },
  },
  plugins: [],
}

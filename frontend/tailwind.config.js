/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        renaultYellow: "#FFD700",
        renaultDark: "#111827",
        renaultGrey: "#E5E7EB",
      },
    },
  },
  plugins: [],
};

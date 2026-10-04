/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101828",
        slateText: "#475467",
        navy: "#132238",
        teal: "#0F766E",
        mint: "#DFF7F2",
        cream: "#F8FAFC",
        gold: "#C99A3E",
        danger: "#C2414B"
      },
      boxShadow: {
        premium: "0 18px 60px rgba(16,24,40,.10)"
      }
    }
  },
  plugins: []
};

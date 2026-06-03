/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js}"],
  theme: {
    extend: {
      colors: {
        navy:   "#0E1117",
        navy2:  "#161B27",
        dss:    "#E31E24",
        green:  "#16A34A",
        amber:  "#F59E0B",
        water:  "#0891B2",
        violet: "#7C3AED",
      },
      fontFamily: {
        head: ["Syne", "sans-serif"],
        body: ["DM Sans", "sans-serif"],
      },
    },
  },
  plugins: [],
};

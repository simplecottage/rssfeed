/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{html,js,svelte,ts}"],
  theme: {
    extend: {
      fontFamily: {
        mono: ["Courier New", "monospace"],
        sans: ["Helvetica", "Arial", "sans-serif"],
      },
      colors: {
        primary: {
          DEFAULT: "#3b82f6",
          dark: "#1d4ed8",
        },
        secondary: {
          DEFAULT: "#6b7280",
          dark: "#4b5563",
        },
        background: {
          DEFAULT: "#f8fafc",
          dark: "#0f172a",
        },
        retro: {
          beige: "#f5f5dc",
          gray: "#808080",
          blue: "#87ceeb",
          green: "#90ee90",
        },
      },
    },
  },
  plugins: [],
};

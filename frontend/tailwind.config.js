/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Exact palette from user's architectural reference image
        med: {
          950: "#081525", // Darkest Navy / Shadow
          900: "#0e233d", // Deep Navy Accent
          800: "#13355c", // Deep Cobalt
          700: "#1a508b", // Rich Cobalt Wall Blue (Primary)
          600: "#2466b0", // Mid-tone Wall Blue
          500: "#327ed4", // Bright Tile Blue
          100: "#deebf9", // Soft Blue Wash
          50:  "#f0f6fd",
        },
        cognac: {
          900: "#481c0c",
          800: "#682e18", // Dark Saddle
          700: "#863e20", // Deep Leather
          600: "#a05634", // Warm Cognac Leather Sofa (Accent)
          500: "#b76741", // Terracotta Leather
          400: "#cb855d", // Warm Clay / Brass
          100: "#f6e8e0",
          50:  "#fcf6f3",
        },
        chalk: {
          50:  "#ffffff", // Crisp Porcelain White (Sinks, Cabinet Doors)
          100: "#f9f8f6", // Off-White
          200: "#f3f0ea", // Painted Wall Stripe Cream
          300: "#e7e2d7", // Warm Sand
          400: "#d3ccbf", // Neutral Linen
          500: "#aea493", // Muted Sand Taupe
          800: "#3b362c",
          900: "#221f19",
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

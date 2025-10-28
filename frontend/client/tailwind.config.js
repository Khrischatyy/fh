/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./pages/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./src/pages/**/*.{vue,ts}",
    "./src/app/**/*.{vue,ts}",
    "./src/widgets/**/*.{vue,ts}",
    "./src/shared/**/*.{vue,ts}",
    "./src/feature/**/*.{vue,ts}",
    "./src/entities/**/*.{vue,ts}",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue",
  ],
  theme: {
    container: {},
    borderRadius: {
      none: "0",
      sm: ".3rem",
      md: ".6rem",
      DEFAULT: "1.25rem",
      xl: "1.9rem",
      full: "9999px",
    },
    fontFamily: {
      sans: ["Roboto", "Mazard", "sans-serif"],
    },
    extend: {
      gridTemplateColumns: {
        "auto-fit": "repeat(auto-fit, minmax(100px, 1fr))",
        "auto-fill": "repeat(auto-fill, minmax(100px, 1fr))",
      },
      fontSize: {
        xs: ["12px", "14px"],
        sm: ["14px", "16px"],
        DEFAULT: ["16px", "18px"],
        base: ["16px", "18px"],
        lg: ["18px", "20px"],
        xl: ["20px", "22px"],
        xxl: ["22px", "24px"],
        headline: ["26px", "30px"],
        title: ["48px", "56px"],
      },
      colors: {
        google: {
          "text-gray": "#3c4043",
          "button-blue": "#1a73e8",
          "button-blue-hover": "#5195ee",
          "button-dark": "#171717",
          "button-dark-hover": "#171717",
          "button-border-light": "#dadce0",
          "logo-blue": "#4285f4",
          "logo-green": "#34a853",
          "logo-yellow": "#fbbc05",
          "logo-red": "#ea4335",
        },
        purple: {
          DEFAULT: "#6A60F2",
          100: "#C3BFFA",
          700: "#4a42a9",
          300: "#C3BFFA",
          200: "#E1DFFC",
        },
        black: {
          DEFAULT: "#0F0E0E",
          100: "#0F0E0E",
        },
        gray: {
          DEFAULT: "#F3F5FD",
          100: "#989FB1",
          200: "#D1D6DF",
          300: "#E6EAF9",
          600: "#CDD0DF",
        },
        white: {
          DEFAULT: "#FFFFFF",
        },
        red: {
          DEFAULT: "#E75032",
        },
        darkred: {
          DEFAULT: "#A80101",
        },
        green: {
          DEFAULT: "#66AA3B",
        },
        yellow: {
          DEFAULT: "#FD9302",
        },
        "custom-gray": "#171717",
      },
      boxShadow: {
        DEFAULT: "0px 4px 25px 0px rgba(0, 0, 0, 0.08)",
      },
      keyframes: {
        virtualAssistantLogoPop: {
          "50%, 80%": { transform: "translate(0, 0)" },
          "60%": { transform: "translate(0, -15%)" },
          "63%, 69%": { transform: "translate(0, -15%) rotate(15deg)" },
          "66%, 72%": { transform: "translate(0, -15%) rotate(-15deg)" },
        },
      },
      animation: {
        valogo: "virtualAssistantLogoPop 6s infinite",
      },
    },
  },
  plugins: [],
}

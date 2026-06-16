/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Space Grotesk", "Inter", "sans-serif"],
        hand: ['"Gochi Hand"', "Caveat", "cursive"],
      },
      colors: {
        // AURA dark-space palette — nebula background + translucent dark glass
        aura: {
          void: "#050B17",        // deepest space
          bg: "#0A1628",          // base background
          panel: "#0E1C33",       // panel shadow base
          ink: "#E6F2FF",         // primary text on dark
          soft: "#9BB4D4",        // secondary text
          muted: "#6D86A8",       // tertiary text
          line: "rgba(180, 210, 255, 0.10)",
          glass: "rgba(14, 28, 51, 0.45)",
          glassStrong: "rgba(14, 28, 51, 0.62)",
          accent: "#2EA8FF",
          accentSoft: "#7DC8FF",
          accentDeep: "#1A78D2",
          cyan: "#4FD1FF",
          mint: "#8FF0D1",
        },
      },
      borderRadius: {
        xl: "14px",
        "2xl": "18px",
        "3xl": "22px",
      },
      boxShadow: {
        glass: "0 10px 34px 0 rgba(0, 0, 0, 0.35)",
        glassHover: "0 14px 46px 0 rgba(0, 0, 0, 0.45)",
        glow: "0 0 32px rgba(46, 168, 255, 0.55)",
        glowSoft: "0 0 60px rgba(125, 200, 255, 0.55)",
        innerGlow: "inset 0 1px 0 rgba(255,255,255,0.08)",
      },
      backdropBlur: {
        xs: "2px",
      },
      keyframes: {
        float: {
          "0%,100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        pulseSoft: {
          "0%,100%": { opacity: "0.55" },
          "50%": { opacity: "1" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        drip: {
          "0%,100%": {
            borderRadius: "50% 50% 50% 50% / 45% 45% 55% 55%",
          },
          "50%": {
            borderRadius: "48% 52% 46% 54% / 42% 48% 52% 58%",
          },
        },
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        "pulse-soft": "pulseSoft 2.4s ease-in-out infinite",
        shimmer: "shimmer 2.4s linear infinite",
        drip: "drip 6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

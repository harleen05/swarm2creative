export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        glass: "rgba(255,255,255,0.08)",
        glow: "#9f7aea"
      },
      backdropBlur: {
        xl: "20px"
      }
    }
  },
  plugins: []
};

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    host: true,
  },
  // ── Electron renderer config ──────────────────────────────────────────────
  // When Electron loads the built app from dist/ it uses file:// protocol.
  // Setting base to "./" ensures all asset paths are relative, not absolute,
  // so they resolve correctly from any file system path.
  // In dev mode (vite dev server) base defaults to "/" which is fine.
  base: process.env.ELECTRON_BUILD ? "./" : "/",
  build: {
    // Output into frontend-v2/dist — where Electron's MAIN_URL points
    outDir: "dist",
    emptyOutDir: true,
  },
});

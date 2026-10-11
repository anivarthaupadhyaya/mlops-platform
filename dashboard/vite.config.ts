import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api/ingest": { target: "http://localhost:8001", changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") },
      "/api/search": { target: "http://localhost:8003", changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") },
      "/api/index": { target: "http://localhost:8003", changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") },
      "/api": { target: "http://localhost:8000", changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") },
      "/ws": { target: "ws://localhost:8002", ws: true },
    },
  },
});

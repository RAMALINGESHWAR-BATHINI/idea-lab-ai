import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The voice assistant is its own app but talks to the SAME FastAPI backend as the website.
// In development "/api" is proxied to the backend, so no CORS setup is needed locally.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  preview: { port: 4174 },
});

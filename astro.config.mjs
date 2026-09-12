import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  site: 'https://www.startresearching.com',
  // Staging on GitHub Pages lives under /StartResearching; custom domain uses '/'.
  // CI sets PAGES_BASE=/StartResearching (see .github/workflows/deploy.yml).
  base: process.env.PAGES_BASE ?? '/',
  output: 'static',
});

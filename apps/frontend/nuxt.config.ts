// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  modules: [
    '@nuxt/ui',
    '@nuxt/icon',
    '@nuxt/image',
    '@nuxt/content',
    '@nuxt/eslint',
    '@pinia/nuxt',
    '@logto/nuxt',
    '@nuxtjs/robots',
    '@nuxtjs/sitemap',
  ],

  typescript: {
    strict: true,
    typeCheck: false, // TODO: Enable when vite-plugin-checker is compatible with current Node.js
  },

  // Logto Auth Configuration
  logto: {
    appId: '', // TODO: Add your Logto App ID
    endpoint: '', // TODO: Add your Logto endpoint URL
  },

  // SEO defaults
  site: {
    url: 'https://nanahouse.vn', // TODO: Update with actual domain
    name: 'NanaHouse',
  },

  // Sitemap configuration
  sitemap: {
    strictNuxtContentPaths: true,
  },
})

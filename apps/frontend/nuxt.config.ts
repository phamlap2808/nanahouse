// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: false,

  modules: [
    '@nuxt/icon',
    '@nuxt/image',
    '@nuxt/eslint',
    '@pinia/nuxt',
    '@nuxtjs/robots',
    '@nuxtjs/sitemap',
  ],

  css: ['~/assets/css/glassmorphism.css'],

  app: {
    head: {
      script: [
        {
          // Inline blocking script to prevent theme flash (FOUC)
          innerHTML: `(function(){try{var t=localStorage.getItem('nanahouse_theme');if(!t){t=window.matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'}document.documentElement.setAttribute('data-theme',t)}catch(e){}})()`,
          type: 'text/javascript',
        },
      ],
    },
  },

  typescript: {
    strict: true,
    typeCheck: false, // TODO: Enable when vite-plugin-checker is compatible with current Node.js
  },

  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000',
    },
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

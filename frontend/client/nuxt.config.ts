import { fileURLToPath, URL } from "url"
// @ts-ignore
export default defineNuxtConfig({
  ssr: true,
  watchers: {
    webpack: {
      poll: 1000, // Check for changes every second
      aggregateTimeout: 300, // Delay before rebuilding
    },
  },
  security: {
    headers: {
      // your security headers
    },
  },
  app: {
    head: {
      charset: "utf-8",
      viewport:
        "width=device-width, initial-scale=1, viewport-fit=cover, maximum-scale=1",
      title: "Funny How - Empowering Artists Everywhere",
      meta: [
        {
          name: "description",
          content:
            "Book, Record, and Create with Ease. Empowering Artists Everywhere.",
        },
        {
          name: "keywords",
          content:
            "music, studio, booking, recording, artists, schedule, payments",
        },
        { name: "author", content: "Funny-how LLC" },
        {
          name: "google-site-verification",
          content: "evvuLgCt6o39oe6HrkxWAV-GHJqT-ODFg98jfAtjm9o",
        },
        {
          property: "og:title",
          content: "Funny How - Empowering Artists Everywhere",
        },
        {
          property: "og:description",
          content:
            "Book, Record, and Create with Ease. Seamless Scheduling, Integrated Payment System, Collaborative Planning Tools.",
        },
        { property: "og:image", content: "/meta/open-graph-image.png" },
        { property: "og:url", content: "https://funny-how.com/" },
        { property: "og:type", content: "website" },
        { name: "twitter:card", content: "summary_large_image" },
        {
          name: "twitter:title",
          content: "Funny How - Empowering Artists Everywhere",
        },
        {
          name: "twitter:description",
          content:
            "Book, Record, and Create with Ease. Seamless Scheduling, Integrated Payment System, Collaborative Planning Tools.",
        },
        { name: "twitter:image", content: "/meta/twitter-card-image.png" },
      ],
      link: [
        { rel: "icon", type: "image/svg+xml", href: "/meta/favicon.svg" },
        { rel: "manifest", href: "/meta/site.webmanifest" },
        {
          rel: "apple-touch-icon",
          sizes: "180x180",
          href: "/meta/apple-touch-icon.png",
        },
      ],
    },
    //pageTransition: { name: 'page', mode: 'out-in' }
  },
  build: {
    transpile: ["@googlemaps/js-api-loader"],
    sourcemap: false,
  },
  dir: {
    app: fileURLToPath(new URL("./src/app", import.meta.url)),
    entities: fileURLToPath(new URL("./src/entities", import.meta.url)),
    features: fileURLToPath(new URL("./src/features", import.meta.url)),
    pages: fileURLToPath(new URL("./src/pages", import.meta.url)),
    shared: fileURLToPath(new URL("./src/shared", import.meta.url)),
    widgets: fileURLToPath(new URL("./src/widgets", import.meta.url)),
    middleware: fileURLToPath(new URL("./src/middleware", import.meta.url)),
  },
  components: {
    dirs: [],
  },
  devtools: {
    enabled: true,

    timeline: {
      enabled: true,
    },
  },
  imports: {
    autoImport: false,
  },
  modules: ["@pinia/nuxt", "@vueuse/nuxt"],

  vueTransitions: {
    name: "slide",
    duration: 500,
    mode: "out-in",
  },
  nitro: {
    routeRules: {
      "/api/**": {
        proxy: process.env.NUXT_PUBLIC_API_BASE,
      },
    },
  },
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },
  runtimeConfig: {
    public: {
      googleMapKey: process.env.NUXT_ENV_GOOGLE_MAPS_API,
      googlePlacesApi: process.env.GOOGLE_PLACES_API,
      baseUrlClient: process.env.AXIOS_BASEURL_CLIENT,
      apiBase: process.env.AXIOS_BASEURL
        ? process.env.AXIOS_BASEURL + process.env.AXIOS_API_VERSION
        : "",
      apiBaseClient: process.env.AXIOS_BASEURL_CLIENT
        ? process.env.AXIOS_BASEURL_CLIENT + process.env.AXIOS_API_VERSION
        : "",
      supportUserId: process.env.SUPPORT_USER_ID || "1",
      supportAddressId: process.env.SUPPORT_ADDRESS_ID || "1",
    },
  },
  tailwindcss: {
    cssPath: "@/src/shared/assets/style/tailwind.css",
  },
  css: ["@/src/shared/assets/style/index.scss", "animate.css/animate.min.css"],
  buildModules: ["@nuxtjs/tailwindcss", "@nuxtjs/onesignal", "@nuxtjs/pwa"],
  oneSignal: {
    init: {
      appId: "95b21da8-652b-4cdf-aefb-65e77884aaab",
      allowLocalhostAsSecureOrigin: true,
      welcomeNotification: {
        disable: true,
      },
    },
  },
  plugins: ["~/plugins/click-outside.ts"],
})

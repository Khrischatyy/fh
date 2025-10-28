// plugins/router-override.ts
import { defineNuxtPlugin, useRouter } from "#app"
import { Router } from "vue-router"

export default defineNuxtPlugin((nuxtApp) => {
  const router: Router = useRouter()
  const originalPush = router.push.bind(router)

  // Initialize _lastClickEvent on the window object
  if (
    process.client &&
    typeof window !== "undefined" &&
    !("_lastClickEvent" in window)
  ) {
    ;(window as any)._lastClickEvent = null
  }

  function handleNavigation(event: MouseEvent | null, location: any) {
    if (event && (event.ctrlKey || event.metaKey)) {
      const { href } = router.resolve(location)
      window.open(href, "_blank")
      return Promise.resolve(true)
    }
    return originalPush(location)
  }

  router.push = function (location: any) {
    return handleNavigation((window as any)._lastClickEvent, location)
  }

  nuxtApp.vueApp.config.globalProperties.$navigateTo = function (
    location: any,
  ) {
    return handleNavigation((window as any)._lastClickEvent, location)
  }

  router.beforeEach((to, from, next) => {
    const event = (window as any)._lastClickEvent
    if (event && (event.ctrlKey || event.metaKey)) {
      const { href } = router.resolve(to)
      window.open(href, "_blank")
      next(false)
    } else {
      next()
    }
  })

  if (process.client) {
    window.addEventListener(
      "click",
      (event) => {
        ;(window as any)._lastClickEvent = event
      },
      true,
    )
  }
})

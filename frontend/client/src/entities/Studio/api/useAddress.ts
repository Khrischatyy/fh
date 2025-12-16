import type { Ref } from "vue"
import { watch } from "vue"
import { useApi } from "~/src/lib/api"
import { useAsyncData } from "#app"
import type { RouteParamValue } from "vue-router"
import { navigateTo } from "nuxt/app"
import { useToastStore } from "~/src/shared/stores/useToastStore"
export type AddressResponse = {
  success: boolean
  data: AddressFull
  code: number
  message: string
}
export type AddressFull = {
  equipments: any
  id: number
  latitude: string
  longitude: string
  street: string
  created_at: string
  updated_at: string
  city_id: number
  company_id: number
  company: {
    id: number
    name: string
    logo: string
    slug: string
    founding_date: string
    rating: string
    created_at: string
    updated_at: string
    logo_url: string
    user_id: number
  }
  badges: {
    id: number
    name: string
    image: string
    description: string
    image_url: string
    pivot: {
      address_id: number
      badge_id: number
    }
  }[]
  prices: {
    id: number
    address_id: number
    hours: number
    is_enabled: boolean
    total_price: string
    price_per_hour: string
  }[]
  photos: {
    id: number
    address_id: number
    path: string
    index: number
    url: string
  }
  operating_hours: {
    id: number
    address_id: number
    mode_id: number
    day_of_week: number
    open_time: string
    close_time: string
    is_closed: boolean
  }[]
}
export function useAddress(slug: string | RouteParamValue[]) {
  const resolvedSlug = typeof slug === "string" ? slug : slug.value
  const { fetch: getBrand } = useApi<AddressResponse>({
    url: `/address/studio/${resolvedSlug}`,
    auth: true,
  })

  //useAsyncData helps to serve it server-side
  const {
    data: address,
    pending,
    error,
  } = useAsyncData<AddressFull>(`address-${resolvedSlug}`, async () => {
    const response = await getBrand()

    // The response IS the address object itself (already unwrapped by useApi)
    return response
  })

  // Watch for errors and handle them
  watch(error, (newError) => {
    if (newError) {
      // Only redirect to 404 for actual "studio not found" errors
      if (newError.statusCode == 404) {
        navigateTo("/404")
      } else {
        // For other errors, show a toast instead of redirecting
        try {
          const toastStore = useToastStore()
          const message = newError.message || "Failed to load studio"
          toastStore.error(message)
        } catch (e) {
          console.error("Error loading studio:", newError)
        }
      }
    }
  })

  return { address, pending, error }
}

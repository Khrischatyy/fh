import { reactive, ref } from "vue"
import { useApi } from "~/src/lib/api"
import { useSessionStore } from "~/src/entities/Session"
import { navigateTo } from "nuxt/app"

export type StudioFormValues = {
  logo: File | null
  company: string
  address: string
  country: string
  zip: string
  city: string
  street: string
  about: string
  longitude: string
  latitude: string
  logo_preview: string | null
  timezone?: string
  company_id?: number
}

export type ResponseBrand = {
  success: boolean
  data: {
    slug: string
    address_id: number
  }
  message: string
  code: number
}

export function useCreateStudio() {
  const formValues = reactive<StudioFormValues>({
    logo: null,
    company: "",
    address: "",
    country: "",
    city: "",
    street: "",
    about: "",
    zip: "",
    longitude: "",
    latitude: "",
    logo_preview: null,
  })

  const errors = ref({})
  const isLoading = ref(false)

  async function createStudio(data: StudioFormValues) {
    const formData = new FormData()
    Object.keys(data).forEach((key: any) => {
      if (key in data) {
        const value = data[key as keyof StudioFormValues]
        if (value !== null) {
          formData.append(key, value as string | Blob)
        }
      }
    })

    const { post } = useApi<ResponseBrand>({
      url: "/brand",
      auth: true,
    })

    // Clear previous errors before a new submission
    errors.value = {}

    try {
      const response = await post(formData)
      //response returns slug of the created brand and address_id
      useSessionStore().setBrand(response?.data.slug || "")
      const room_id = response?.data?.room_id
      navigateTo(
        `/company/@${response?.data?.slug}/setup/${response?.data?.address_id}/hours?room_id=${room_id}`,
      )
      return response
    } catch (error: any) {
      console.error("Failed to create studio:", error)
      if (error.errors) {
        // Update UI or state with specific field errors
        errors.value = error.errors
      } else {
        // Handle general error message
        errors.value.general = [error.message]
      }
      throw error // Rethrow the error to allow further handling
    } finally {
      isLoading.value = false
    }
  }
  async function addStudio(data: StudioFormValues) {
    const formData = new FormData()
    Object.keys(data).forEach((key: any) => {
      if (key in data) {
        const value = data[key as keyof StudioFormValues]
        if (value !== null) {
          formData.append(key, value as string | Blob)
        }
      }
    })

    const { post } = useApi<ResponseBrand>({
      url: "/address/add-studio",
      auth: true,
    })

    // Clear previous errors before a new submission
    errors.value = {}

    try {
      const response = await post(formData)
      //response returns slug of the created brand and address_id
      useSessionStore().setBrand(response?.data.slug || "")
      const room_id = response?.data?.rooms?.[0]?.id
      navigateTo(
          `/company/@${response?.data?.company_slug}/setup/${response?.data?.id}/hours?room_id=${room_id}`,
      )
      return response
    } catch (error: any) {
      console.error("Failed to create studio:", error)
      if (error.errors) {
        // Update UI or state with specific field errors
        errors.value = error.errors
      } else {
        // Handle general error message
        errors.value.general = [error.message]
      }
      throw error // Rethrow the error to allow further handling
    } finally {
      isLoading.value = false
    }
  }

  return { createStudio, addStudio, errors, isLoading, formValues }
}

import { reactive, ref } from "vue"
import type { UnwrapNestedRefs } from "vue"
import { Loader } from "@googlemaps/js-api-loader"
import { useRuntimeConfig } from "#imports"
export type AddressData = {
  formattedAddress: string
  location: { lat: string; lng: string }
  addressComponents: Record<string, { longName: string; shortName: string }>
  placeId: string
  url: string
}

const addressComponentsExample = {
  street_number: {
    longName: "435",
    shortName: "435",
  },
  route: {
    longName: "West Katella Avenue",
    shortName: "W Katella Ave",
  },
  locality: {
    longName: "Orange",
    shortName: "Orange",
  },
  administrative_area_level_2: {
    longName: "Orange County",
    shortName: "Orange County",
  },
  administrative_area_level_1: {
    longName: "California",
    shortName: "CA",
  },
  country: {
    longName: "United States",
    shortName: "US",
  },
  postal_code: {
    longName: "92867",
    shortName: "92867",
  },
}

export function useGoogleMaps() {
  const config = useRuntimeConfig()
  const autocomplete = ref(null)
  const addressData: UnwrapNestedRefs<AddressData> = reactive({
    formattedAddress: "",
    location: { lat: "", lng: "" },
    addressComponents: {
      street_number: { longName: "", shortName: "" },
      route: { longName: "", shortName: "" },
      locality: { longName: "", shortName: "" },
      administrative_area_level_2: { longName: "", shortName: "" },
      administrative_area_level_1: { longName: "", shortName: "" },
      country: { longName: "", shortName: "" },
      postal_code: { longName: "", shortName: "" },
    },
    placeId: "",
    url: "",
  })

  async function initGoogleMaps(inputElement: HTMLInputElement) {
    const loader = new Loader({
      apiKey: config.public.googleMapKey,
      version: "weekly",
      language: "en",
    })

    const Places = await loader.importLibrary("places")

    const options = {
      componentRestrictions: { country: ["us", "ca", "ru", "rs"] },
      types: ["address"],
      language: "en",
    }

    autocomplete.value = new Places.Autocomplete(inputElement, options)

    if (!autocomplete.value) {
      console.error("Google Maps Places Autocomplete failed to initialize")
      return
    }

    autocomplete.value.addListener("place_changed", () => {
      const place = autocomplete.value.getPlace()
      if (place.geometry) {
        addressData.formattedAddress = place.formatted_address
        addressData.location.lat = place.geometry.location.lat()
        addressData.location.lng = place.geometry.location.lng()
        addressData.addressComponents = place.address_components.reduce(
          (acc, component) => {
            acc[component.types[0]] = {
              longName: component.long_name,
              shortName: component.short_name,
            }
            return acc
          },
          {},
        )
        addressData.placeId = place.place_id
        addressData.url = place.url
      }
    })
  }

  return {
    autocomplete,
    addressData,
    initGoogleMaps,
  }
}

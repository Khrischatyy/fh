<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { definePageMeta, useRuntimeConfig } from "#imports"
import { useSessionStore } from "~/src/entities/Session"
import { onMounted, ref, type UnwrapRef } from "vue"
import {
  BrandingLogo,
  BrandingLogoSample,
  BrandingLogoSmall,
} from "~/src/shared/ui/branding"
import { navigateTo } from "nuxt/app"
import {
  type formValues,
  type inputValues,
  type StudioFormValues,
  useCreateStudioFormStore,
} from "~/src/entities/RegistrationForms"
import { IconElipse, IconLine } from "~/src/shared/ui/common"
import { Loader } from "@googlemaps/js-api-loader"
definePageMeta({
  middleware: ["auth"],
})

useHead({
  title: "Dashboard | Setup",
  meta: [{ name: "Funny How", content: "Dashboard" }],
})

const isLoading = ref(false)

function isError(form: string, field: string): boolean {
  let formErrors: Record<string, any> = useCreateStudioFormStore().errors
  return formErrors.hasOwnProperty(field) ? formErrors[field][0] : false
}

const session = ref()
onMounted(async () => {
  const config = useRuntimeConfig()
  session.value = useSessionStore()

  const loader = new Loader({
    apiKey: config.public.googlePlacesApi,
    version: "weekly",
  })

  const Places = await loader.importLibrary("places")

  // the center, defaultbounds are not necessary but are best practices to limit/focus search results
  const center = { lat: 34.082298, lng: -82.284777 }
  // Create a bounding box with sides ~10km away from the center point
  const defaultBounds = {
    north: center.lat + 0.1,
    south: center.lat - 0.1,
    east: center.lng + 0.1,
    west: center.lng - 0.1,
  }

  //this const will be the first arg for the new instance of the Places API

  const input = document.getElementById("place") //binds to our input element

  //this object will be our second arg for the new instance of the Places API
  const options = {
    componentRestrictions: { country: ["us", "ca"] },
    fields: ["address_components", "geometry"],
    types: ["address"],
  }

  // per the Google docs create the new instance of the import above. I named it Places.
  const autocomplete = new Places.Autocomplete(input, options)

  //add the place_changed listener to display results when inputs change
  autocomplete.addListener("place_changed", () => {
    const place = autocomplete.getPlace()

    getFormValues().address = input?.value
    getFormValues().country = place.address_components.find((item) =>
      item.types.includes("country"),
    )?.short_name
    getFormValues().city = place.address_components.find((item) =>
      item.types.includes("locality"),
    )?.short_name
    getFormValues().street = place.address_components.find((item) =>
      item.types.includes("route"),
    )?.short_name
    getFormValues().longitude = place.geometry.viewport?.Gh?.hi
    getFormValues().latitude = place.geometry.viewport?.Wh?.hi
  })
})

function getFormValues(): StudioFormValues {
  return useCreateStudioFormStore().inputValues
}

function changeLogo() {
  const input = document.getElementById("studio_logo") as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    getFormValues().logo = file
    const reader = new FileReader()
    reader.onload = (e) => {
      getFormValues().logo_preview = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

function setupStudio() {
  useCreateStudioFormStore().submit()
}

function signOut() {
  session.value.logout()
}
</script>

<template>
  <div
    class="grid min-h-screen h-full animate__animated animate__fadeInRight"
    style="min-height: -webkit-fill-available"
  >
    <div
      class="w-full mt-20 h-full flex-col justify-between items-start gap-7 inline-flex"
    >
      <div
        class="relative w-full flex-col justify-start items-center gap-2.5 flex"
      >
        <BrandingLogo class="mb-20" />
        <div class="animate__animated animate__fadeInRight">
          <div
            class="breadcrumbs mb-10 text-white text-sm font-normal tracking-wide flex gap-1.5 justify-center items-center"
          >
            <icon-elipse :class="'opacity-100'" class="h-4" />
            <button :class="'opacity-100'">Add Studio</button>
            <icon-line :class="'opacity-100'" class="h-2 only-desktop" />
            <icon-elipse :class="'opacity-20'" class="h-4" />
            <button :class="'opacity-20'">Price Plans</button>
          </div>
        </div>

        <div
          class="w-96 justify-center items-center inline-flex mb-10 text-center"
        >
          <div class="text-white text-xl font-bold text-center tracking-wide">
            Setup Your Studio
          </div>
        </div>

        <div class="flex-col justify-start items-start gap-1.5 flex">
          <div class="w-96 justify-between items-start inline-flex">
            <div class="text-white text-sm font-normal tracking-wide">
              Studio name and logo
            </div>
            <div
              :class="isError('setup', 'studio_name') ? '' : 'hidden'"
              class="text-right text-red-500 text-sm font-normal tracking-wide"
            >
              {{ isError("setup", "studio_name") }}
            </div>
          </div>
          <div class="justify-start items-center w-full gap-2.5 inline-flex">
            <div class="justify-center w-96 items-center gap-2.5 inline-flex">
              <label
                for="studio_logo"
                :style="`background: url(${
                  getFormValues().logo_preview
                }) no-repeat center; background-size: cover`"
                class="flex-col justify-center items-center h-[58px] px-3.5 py-3.5 cursor-pointer outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-[#c1c1c1] text-xs font-light tracking-wide text-center"
              >
                <div class="flex flex-col justify-end h-full">
                  <BrandingLogoSample v-if="!getFormValues().logo" />
                  <span class="font-bold shadow-text text-white"
                    >upload...</span
                  >
                </div>
              </label>
              <input
                class="hidden"
                id="studio_logo"
                @change="changeLogo()"
                type="file"
                placeholder="Enter Your Studio Name"
              />

              <input
                v-model="getFormValues().company"
                class="w-full h-11 px-3.5 py-7 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
                type="text"
                placeholder="Enter Your Studio Name"
              />
            </div>
          </div>
        </div>

        <div class="flex-col justify-start items-start gap-1.5 flex">
          <div class="w-96 justify-between items-start inline-flex">
            <div class="text-white text-sm font-normal tracking-wide">
              Address
            </div>
            <div
              :class="isError('setup', 'address') ? '' : 'hidden'"
              class="text-right text-red-500 text-sm font-normal tracking-wide"
            >
              {{ isError("setup", "address") }}
            </div>
          </div>
          <div class="justify-start items-center gap-2.5 inline-flex">
            <input
              id="place"
              class="w-96 h-11 px-3.5 py-7 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
              type="text"
              placeholder="Enter Your Address"
            />
          </div>
        </div>
        <div class="flex-col justify-start items-start gap-1.5 flex">
          <div class="w-96 justify-between items-start inline-flex">
            <div class="text-white text-sm font-normal tracking-wide">
              About
            </div>
            <div
              :class="isError('setup', 'about') ? '' : 'hidden'"
              class="text-right text-red-500 text-sm font-normal tracking-wide"
            >
              {{ isError("setup", "about") }}
            </div>
          </div>
          <div class="justify-start items-center gap-2.5 inline-flex">
            <textarea
              name="about"
              type="text"
              v-model="getFormValues().about"
              :class="{
                'border-red':
                  isError('setup', 'about') || isError('setup', 'about'),
              }"
              class="w-96 h-20 no-scrollbar px-3.5 py-3.5 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
            />
          </div>
        </div>
        <div class="justify-center items-center gap-2.5 inline-flex">
          <button
            @click="setupStudio()"
            class="w-96 h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
          >
            Save And Continue
          </button>
        </div>
        <div class="justify-center items-center gap-2.5 inline-flex">
          <button
            @click="signOut()"
            class="w-96 h-11 p-3.5 hover:opacity-90 border border-white rounded-[10px] text-white text-sm font-medium tracking-wide"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.shadow-text {
  text-shadow: 2px 3px 1px rgba(0, 0, 0, 0.8), 12px 14px 1px rgba(0, 0, 0, 0.8);
}
.checkbox-wrapper {
  display: flex;
  gap: 5px;
  cursor: pointer;

  .custom-checkbox {
    display: inline-block;
    vertical-align: middle;
    position: relative;

    &:after {
      content: "";
      position: absolute;
      display: none;
    }
  }

  input[type="checkbox"] {
    &:checked ~ .custom-checkbox {
      padding: 3px;
      position: relative;
      display: flex;
      justify-content: center;
      align-items: center;

      &:after {
        position: relative;
        top: 0;
        left: 0;
        display: block;
        width: 100%;
        height: 100%;
        border: solid white;
        background: #f3f5fd;
        border-radius: 2px;
      }
    }
  }
}
</style>

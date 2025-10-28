<script setup lang="ts">
import { useHead } from "@unhead/vue"
import { definePageMeta, storeToRefs, useRuntimeConfig } from "#imports"
import { useSessionStore } from "~/src/entities/Session"
import { computed, onMounted, ref, watch } from "vue"
import { BrandingLogo } from "~/src/shared/ui/branding"
import { navigateTo, useRoute } from "nuxt/app"
import { IconElipse, IconLine, IconUpload } from "~/src/shared/ui/common"
import { useCreateStudio } from "~/src/entities/Studio/api"
import { useGoogleMaps } from "~/src/shared/utils"

useHead({
  title: "Dashboard | Create Studio",
  meta: [{ name: "Funny How", content: "Dashboard" }],
})

definePageMeta({
  middleware: ["auth", "owner"],
})

const { createStudio, addStudio, errors, isLoading, formValues } =
  useCreateStudio()

const route = useRoute()

function isError(field: string): boolean {
  return errors.value.hasOwnProperty(field) ? errors.value[field][0] : false
}
const session = useSessionStore()
const { existedCompany } = storeToRefs(session)

const { initGoogleMaps, autocomplete, addressData } = useGoogleMaps()
const place = ref<HTMLInputElement | undefined>()

watch(
  addressData,
  (newVal) => {
    formValues.address = newVal.formattedAddress
    formValues.latitude = newVal.location.lat.toString()
    formValues.longitude = newVal.location.lng.toString()
    formValues.country = newVal.addressComponents["country"]?.longName || ""
    formValues.zip =
      newVal.addressComponents["postal_code"]?.longName || "000000"

    const administrativeArea =
      newVal.addressComponents["administrative_area_level_2"]?.longName.replace(
        /county/i,
        "",
      ) || ""
    const locality = newVal.addressComponents["locality"]?.longName || ""

    formValues.city = administrativeArea.trim() || locality

    formValues.street = `${
      newVal.addressComponents["street_number"]?.longName || ""
    } ${newVal.addressComponents["route"]?.longName || ""}`
  },
  { deep: true },
)

onMounted(async () => {
  const config = useRuntimeConfig()

  //Init google map and autocomplete on ref place.value that is InputElement
  await initGoogleMaps(place?.value)
})

function changeLogo() {
  const input = document.getElementById("studio_logo") as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    formValues.logo = file
    const reader = new FileReader()
    reader.onload = (e) => {
      formValues.logo_preview = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

async function addNewStudio() {
  isLoading.value = true
  formValues.company_id = existedCompany.value.id
  //Add timezone of creator
  formValues.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
  try {
    await addStudio(formValues) // Use composable to submit form
    // Navigate or handle success as needed
  } catch (error) {
    console.error("Error submitting studio form:", error)
  } finally {
    isLoading.value = false
  }
}

async function setupStudio() {
  isLoading.value = true
  //Add timezone of creator
  formValues.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
  try {
    await createStudio(formValues) // Use composable to submit form
    // Navigate or handle success as needed
  } catch (error) {
    console.error("Error submitting studio form:", error)
  } finally {
    isLoading.value = false
  }
}

const upperCase = (str: string) => {
  return str.charAt(0).toUpperCase() + str.slice(1)
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
        class="relative w-full flex-col justify-start items-center gap-2.5 flex px-3"
      >
        <BrandingLogo @click="navigateTo('/')" class="mb-20" />
        <div class="animate__animated animate__fadeInRight">
          <div
            class="breadcrumbs mb-10 text-white text-sm font-normal tracking-wide flex gap-1.5 justify-center items-center"
          >
            <icon-elipse :class="'opacity-100'" class="h-4" />
            <button :class="'opacity-100'">
              {{ existedCompany ? "Add Address" : "Add Studio" }}
            </button>
            <icon-line :class="'opacity-100'" class="h-2 only-desktop" />
            <icon-elipse :class="'opacity-20'" class="h-4" />
            <button :class="'opacity-20'">Setup Hours</button>
          </div>
        </div>

        <div
          class="max-w-96 justify-center items-center inline-flex mb-10 text-center"
        >
          <div class="text-white text-xl font-bold text-center tracking-wide">
            {{ existedCompany ? "Add Address" : "Setup Your First Studio" }}
          </div>
        </div>
        <div
          v-if="isError('general')"
          class="max-w-96 justify-center items-center inline-flex"
        >
          <div class="text-red-500 text-sm font-normal tracking-wide">
            {{ isError("general") }}
          </div>
        </div>

        <div class="w-full flex justify-center flex-col max-w-96 gap-1.5">
          <div class="flex-col justify-start items-start gap-1.5 flex w-full">
            <div
              class="max-w-96 w-full justify-between items-start inline-flex"
            >
              <div class="text-white text-sm font-normal tracking-wide">
                Studio name and logo
              </div>
              <div
                v-if="errors.hasOwnProperty('company') && !formValues.company"
                class="text-right text-red-500 text-sm font-normal tracking-wide"
              >
                {{ isError("company") }}
              </div>
            </div>
            <div class="flex justify-start items-center w-full gap-2.5">
              <div
                class="flex w-full justify-center max-w-96 items-center gap-2.5"
              >
                <label
                  v-if="!existedCompany"
                  for="studio_logo"
                  class="w-[58px] h-[58px] flex flex-col justify-center items-center px-1.5 py-1.5 cursor-pointer outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-[#c1c1c1] text-xs font-light tracking-wide text-center"
                >
                  <div class="flex flex-col justify-end h-full">
                    <IconUpload
                      class="mx-1.5 my-1.5 opacity-50 hover:opacity-100"
                      v-if="!formValues.logo"
                    />
                    <img
                      :src="`${formValues.logo_preview}`"
                      v-if="formValues.logo_preview"
                      class="w-[58px] h-[58px] object-contain"
                    />
                  </div>
                </label>
                <input
                  v-if="!existedCompany"
                  class="hidden"
                  id="studio_logo"
                  @change="changeLogo()"
                  type="file"
                />
                <input
                  :disabled="existedCompany"
                  v-model="formValues.company"
                  :class="
                    errors.hasOwnProperty('company') && !formValues.company
                      ? 'border border-red border-opacity-80'
                      : 'border border-white border-opacity-20'
                  "
                  class="w-full h-11 px-3.5 py-7 outline-none rounded-[10px] focus:border-white bg-transparent text-white text-sm font-medium tracking-wide"
                  type="text"
                  :placeholder="
                    existedCompany
                      ? upperCase(existedCompany?.name)
                      : 'Ex. Section Studios'
                  "
                />
              </div>
            </div>
          </div>

          <div class="flex-col justify-start items-start gap-1.5 flex w-full">
            <div
              class="max-w-96 w-full justify-between items-start inline-flex"
            >
              <div class="text-white text-sm font-normal tracking-wide">
                Address
              </div>
              <div
                v-if="errors.hasOwnProperty('street') && !formValues.street"
                class="text-right text-red-500 text-sm font-normal tracking-wide"
              >
                {{ isError("street") }}
              </div>
            </div>
            <div
              class="justify-start max-w-96 w-full items-center gap-2.5 inline-flex"
            >
              <input
                id="place"
                ref="place"
                :class="
                  errors.hasOwnProperty('street') && !formValues.street
                    ? 'border border-red border-opacity-80 placeholder-red'
                    : 'border border-white border-opacity-20'
                "
                class="max-w-96 w-full h-11 px-3.5 py-7 outline-none rounded-[10px] focus:border-white bg-transparent text-white text-sm font-medium tracking-wide"
                type="text"
                placeholder="Ex. 435 East 30th street, Los Angeles, CA 90011"
              />
            </div>
          </div>
        </div>
        <div class="justify-center items-center gap-2.5 inline-flex w-full">
          <button
            v-if="!existedCompany"
            @click="setupStudio()"
            class="max-w-96 w-full h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
          >
            Save And Continue
          </button>
          <button
            v-else
            @click="addNewStudio()"
            class="max-w-96 w-full h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
          >
            Add studio
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

.placeholder-red::placeholder {
  @apply text-red-500;
}
</style>

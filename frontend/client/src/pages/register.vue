<script setup lang="ts">
import { CreateForm } from "~/src/features/Register/create"
import BrandingLogo from "~/src/shared/ui/branding/BrandingLogo.vue"
import { useHead } from "@unhead/vue"
import Particles from "~/src/shared/ui/components/Particles/Particles.vue"
import { useRuntimeConfig } from "#imports"
import axios from "axios"
import { useSessionStore } from "~/src/entities/Session"
import { nextTick, onMounted, reactive, ref, watch, watchEffect } from "vue"
import {
  IconUser,
  IconMic,
  IconElipse,
  IconCopyright,
  IconLine,
  IconLeft,
  IconCheck,
} from "~/src/shared/ui/common/Icon"
import { Loader } from "@googlemaps/js-api-loader"
import { BrandingLogoSample, BrandingLogoSmall } from "~/src/shared/ui/branding"

useHead({
  title: "Funny How – Book a Session Time",
  meta: [{ name: "Funny How", content: "Book A Studio Time" }],
})

const isLoading = ref(false)

const step = ref("auth")
const forms = reactive([
  {
    name: "auth",
    title: "Sign In",
    formValuesStorage: {
      email: "",
      password: "",
    },
    errors: [],
  },
  {
    name: "create_account",
    title: "Sign Up",
    formValuesStorage: {
      name: "",
      email: "",
      password: "",
      password_confirmation: "",
      role: "",
    },
    errors: [],
    inputFields: [
      { name: "name", title: "Name", type: "text" },
      { name: "email", title: "Email", type: "email" },
      { name: "password", title: "Password", type: "password" },
      {
        name: "password_confirmation",
        title: "Confirm Password",
        type: "password",
      },
    ],
  },
  {
    name: "setup",
    title: "Set-Up",
    formValuesStorage: {
      address: "",
      about: "",
      gender: "",
      place: {},
      studio_name: "",
    },
    errors: [],
  },
  {
    name: "forgot",
    title: "Forgot Password",
    errors: [],
    formValuesStorage: {
      email: "",
    },
  },
])

type Form = {
  name: string
  title: string
  formValuesStorage?: {
    email?: string
    password?: string
    name?: string
    password_confirmation?: string
    role?: string
  }
  errors?: any[]
  inputFields?: { name: string; title: string; type: string }[]
}
function getAuthTitleByName(name: string) {
  return forms.find((form: Form) => form.name === name)?.title
}

function chooseRole(role: string) {
  let roleValue = "create_account"
  forms.find(
    (form: Form) => form.name === "create_account",
  ).formValuesStorage.role = role
  step.value = roleValue
}

function chooseGender(gender: string) {
  forms.find((form: Form) => form.name === "setup").formValuesStorage.gender =
    gender
}

function getFormValues(name: string) {
  return forms.find((form: Form) => form.name === name)?.formValuesStorage
}
function setFormValue(name: string, fieldName: string, value: any) {
  const form = forms.find((form: Form) => form.name === name)
  if (form) {
    form.formValuesStorage[fieldName] = value
  } else {
    console.error(`Form with name '${name}' not found.`)
  }
}

function getFormErrors(name: string) {
  return forms.find((form: Form) => form.name === name)?.errors
}

function isError(form: string, field: string) {
  let formErrors = getFormErrors(form)

  return formErrors.hasOwnProperty(field) ? formErrors[field][0] : false
}

function getFormFields(name: string) {
  return forms.find((form: Form) => form.name === name)?.inputFields
}

const steps = ref([
  { name: "auth", title: "Sign In", order: 1 },
  { name: "create", title: "Sign Up", order: 2 },
  { name: "create", title: "Personal Info", order: 3 },
  { name: "forgot", title: "Forgot Password", order: 3 },
])

const session = ref()
const place = ref()
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
    const place = autocomplete.getPlace() //this callback is inherent you will see it if you logged autocomplete

    getFormValues("setup").place = place
  })
})

function createForm() {
  step.value = "create"
  return
}

function createAccount() {
  const config = useRuntimeConfig()
  isLoading.value = true
  let requestConfig = {
    method: "post",
    credentials: true,
    url: `${config.public.apiBaseClient}/auth/register`,
    data: getFormValues("create_account"),
    headers: {
      Accept: "application/json",
    },
  }
  axios.defaults.headers.common["X-Api-Client"] = `web`
  axios
    .request(requestConfig)
    .then((response) => {
      if (response.data.token) {
        session.value.setAccessToken(response.data.token)
        session.value.setAuthorized(true)
        isLoading.value = false
        step.value = "account"
      }
    })
    .catch((error) => {
      console.error(error)
    })
}

function signOut() {
  session.value.logout()
  step.value = "auth"
}

function authForm() {
  const config = useRuntimeConfig()

  let requestConfig = {
    method: "post",
    credentials: true,
    url: `${config.public.apiBaseClient}/auth/login`,
    data: getFormValues("auth"),
    headers: {
      Accept: "application/json",
    },
  }
  axios.defaults.headers.common["X-Api-Client"] = `web`
  axios
    .request(requestConfig)
    .then((response) => {
      if (response.data.token) {
        session.value.setAccessToken(response.data.token)
        session.value.setAuthorized(true)
      }
    })
    .catch((error) => {
      let errors = getFormErrors("auth")
      Object.assign(errors, error.response.data.errors)
    })
}

function verifyUser() {
  const config = useRuntimeConfig()

  let requestConfig = {
    method: "post",
    credentials: true,
    url: `${config.public.apiBaseClient}/auth/email/verify/2/07573a3c93dad6e7c283ea427d9f6cf94cf22783?expires=1713901523&signature=fc718ddc61b7cebdbe3dd9eeafb546e2505a5725468334a93e9ba8bf6f3bb884`,
    headers: {
      Accept: "application/json",
    },
  }
  axios.defaults.headers.common["X-Api-Client"] = `web`
  axios
    .request(requestConfig)
    .then((response) => {})
    .catch((error) => {
      console.error(error)
    })
}
</script>

<template>
  <div
    :class="
      step == 'auth' && !session?.isAuthorized
        ? 'lg:grid-cols-[486px_1fr] duration-700'
        : 'lg:grid-cols-[0px_1fr] duration-[700ms]'
    "
    class="ease-in-out grid min-h-screen h-full"
    style="min-height: -webkit-fill-available"
  >
    <div
      :class="
        step == 'auth' && !session?.isAuthorized
          ? 'w-full translate-x-[0px] duration-[700ms]'
          : 'translate-x-[-486px] duration-300'
      "
      class="z-10 ease-in-out bg-black hidden lg:block text-white px-[50px] py-[60px] min-h-screen h-full"
      style="min-height: -webkit-fill-available"
    >
      <div
        class="w-full mt-10 h-full flex-col justify-between items-start gap-7 inline-flex"
      >
        <div class="description">
          <BrandingLogo />
          <div class="description mt-10 font-bold text-xl leading-8">
            Empowering Artists Everywhere —<br />Book, Record, and Create with
            Ease
          </div>
          <div class="points mt-10">
            <div
              class="w-full flex-col justify-start items-start gap-7 inline-flex"
            >
              <div class="justify-start items-start gap-5 inline-flex">
                <div class="w-8 h-8 relative">
                  <div class="left-0 top-0 absolute"><IconCheck /></div>
                </div>
                <div
                  class="flex-col justify-start items-start gap-2.5 inline-flex"
                >
                  <div class="text-white text-base font-bold tracking-wide">
                    Seamless Scheduling
                  </div>
                  <div
                    class="w-80 text-white text-sm font-normal tracking-wide"
                  >
                    Our intuitive calendar interface makes it easy to see studio
                    availability and schedule sessions without back-and-forth
                    communication.
                  </div>
                </div>
              </div>
              <div class="justify-start items-start gap-5 inline-flex">
                <div class="w-8 h-8 relative">
                  <div class="left-0 top-0 absolute"><IconCheck /></div>
                </div>
                <div
                  class="flex-col justify-start items-start gap-2.5 inline-flex"
                >
                  <div class="text-white text-base font-bold tracking-wide">
                    Integrated Payment System
                  </div>
                  <div
                    class="w-80 text-white text-sm font-normal tracking-wide"
                  >
                    Secure and straightforward in-app payments to reserve your
                    studio time without hassle.
                  </div>
                </div>
              </div>
              <div class="justify-start items-start gap-5 inline-flex">
                <div class="w-8 h-8 relative">
                  <div class="left-0 top-0 absolute"><IconCheck /></div>
                </div>
                <div
                  class="flex-col justify-start items-start gap-2.5 inline-flex"
                >
                  <div class="text-white text-base font-bold tracking-wide">
                    Collaborative Planning Tools
                  </div>
                  <div
                    class="w-80 text-white text-sm font-normal tracking-wide"
                  >
                    Coordinate with producers, engineers, and artists within the
                    app to ensure everyone is prepared for the session.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="footer mt-10 mb-10">
          <div
            class="w-full flex-col justify-between items-start gap-7 mb-5 inline-flex"
          >
            <div class="w-full justify-between items-start gap-7 inline-flex">
              <div class="text-white text-base font-normal tracking-wide">
                Contact us
              </div>
              <div class="text-white text-base font-normal tracking-wide">
                Terms of Service
              </div>
              <div class="text-white text-base font-normal tracking-wide">
                About us
              </div>
            </div>
          </div>
          <div
            class="w-full h-5 justify-start items-center gap-1.5 inline-flex"
          >
            <div class="text-white text-base font-semibold tracking-wide">
              2024
            </div>
            <div class="w-5 h-5 relative"><IconCopyright /></div>
            <div class="text-white text-base font-semibold tracking-wide">
              Funny-how LLC
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="auth-panel bg-[#000000] relative">
      <div class="w-full h-full grid items-center justify-center mb-10">
        <div
          class="relative bottom-[10%] flex-col justify-start items-center gap-7 inline-flex"
        >
          <BrandingLogo class="lg:hidden mb-10" />
          <div
            :class="
              step == 'auth'
                ? 'translate-x-[0px] duration-[700ms] opacity-0'
                : '-translate-x-96/2 duration-700'
            "
            class="breadcrumbs text-white text-sm font-normal tracking-wide flex gap-1.5 justify-center items-center"
          >
            <icon-elipse
              :class="step == 'create' ? 'opacity-100' : 'opacity-20'"
              class="h-4"
            />
            <button :class="step == 'create' ? 'opacity-100' : 'opacity-20'">
              Your Role
            </button>
            <icon-line
              :class="step == 'create' ? 'opacity-100' : 'opacity-20'"
              class="h-2 only-desktop"
            />
            <icon-elipse
              :class="step == 'create_account' ? 'opacity-100' : 'opacity-20'"
              class="h-4"
            />
            <button
              :class="step == 'create_account' ? 'opacity-100' : 'opacity-20'"
            >
              Personal Info
            </button>
            <icon-line
              :class="step == 'create_account' ? 'opacity-100' : 'opacity-20'"
              class="h-2 only-desktop"
            />
            <icon-elipse
              :class="step == 'price_plans' ? 'opacity-100' : 'opacity-20'"
              class="h-4"
            />
            <button
              :class="step == 'price_plans' ? 'opacity-100' : 'opacity-20'"
            >
              Price Plans
            </button>
            <icon-line
              :class="step == 'price_plans' ? 'opacity-100' : 'opacity-20'"
              class="h-2 only-desktop"
            />
            <icon-elipse
              :class="step == 'add_studio' ? 'opacity-100' : 'opacity-20'"
              class="h-4"
            />
            <button
              :class="step == 'add_studio' ? 'opacity-100' : 'opacity-20'"
            >
              Add Studio
            </button>
          </div>
          <div
            v-if="!session?.isAuthorized"
            class="relative text-white text-3xl font-bold tracking-wider"
          >
            {{ getAuthTitleByName(step) }}
          </div>
          <div
            class="relative h-full min-h-[500px] forms flex justify-start items-center"
          >
            <div
              v-if="step == 'auth' && !session?.isAuthorized"
              ref="auth"
              :class="
                step == 'auth'
                  ? 'translate-x-[0px] duration-[700ms]'
                  : 'opacity-0 -translate-x-96 duration-700'
              "
              class="relative w-full flex-col justify-start items-center gap-2.5 flex"
            >
              <div class="flex-col justify-start items-start gap-1.5 flex">
                <div class="w-96 justify-between items-start inline-flex">
                  <div class="text-white text-sm font-normal tracking-wide">
                    E-mail
                  </div>
                  <div
                    :class="isError('auth', 'email') ? '' : 'hidden'"
                    class="text-right text-red-500 text-sm font-normal tracking-wide"
                  >
                    {{ isError("auth", "email") }}
                  </div>
                </div>
                <div class="justify-start items-center gap-2.5 inline-flex">
                  <input
                    name="email"
                    type="email"
                    v-model="getFormValues('auth')['email']"
                    :class="{ 'border-red': isError('auth', 'email') }"
                    class="w-96 h-11 px-3.5 py-7 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
                  />
                </div>
              </div>
              <div class="flex-col justify-start items-start gap-1.5 flex">
                <div class="w-96 justify-between items-start inline-flex">
                  <div class="text-white text-sm font-normal tracking-wide">
                    Password
                  </div>
                  <div
                    :class="isError('auth', 'email') ? '' : 'hidden'"
                    class="text-right text-red-500 text-sm font-normal tracking-wide"
                  >
                    {{ isError("auth", "email") }}
                  </div>
                </div>
                <div class="justify-start items-center gap-2.5 inline-flex">
                  <input
                    name="password"
                    type="password"
                    v-model="getFormValues('auth')['password']"
                    :class="{
                      'border-red':
                        isError('auth', 'email') || isError('auth', 'password'),
                    }"
                    class="w-96 h-11 px-3.5 py-7 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
                  />
                </div>
              </div>
              <div
                class="w-96 h-7 rounded-lg justify-start items-center gap-2.5 inline-flex"
              >
                <label class="checkbox-wrapper flex">
                  <div class="w-4 h-4 justify-center items-center flex">
                    <input type="checkbox" class="hidden" />
                    <div
                      class="w-4 h-4 rounded-[3px] border border-white custom-checkbox"
                    ></div>
                  </div>
                  <div class="text-white text-sm font-normal tracking-wide">
                    Stay signed in for a month
                  </div>
                </label>
              </div>
              <div class="justify-center items-center gap-2.5 inline-flex">
                <button
                  @click="authForm()"
                  class="w-96 h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
                >
                  Sign In
                </button>
              </div>
              <div class="justify-center items-center gap-2.5 inline-flex">
                <button
                  @click="createForm()"
                  class="w-96 h-11 p-3.5 hover:opacity-90 rounded-[10px] text-white border text-sm font-medium tracking-wide"
                >
                  Don’t have an account? Create account
                </button>
              </div>
              <div
                class="w-96 h-11 p-3.5 justify-center items-center gap-2.5 inline-flex"
              >
                <button
                  class="w-96 h-11 p-3.5 hover:opacity-90 rounded-[10px] text-white text-sm font-medium tracking-wide"
                >
                  Forgot password?
                </button>
              </div>
            </div>

            <create-form
              v-if="step == 'create' && !session?.isAuthorized"
              ref="create"
              :class="
                step == 'create'
                  ? 'translate-x-[0px] duration-[700ms]'
                  : 'ml-96 translate-x-96 duration-700 opacity-0'
              "
              class="relative w-full flex-col justify-start items-center gap-2.5 flex"
            />

            <div
              v-if="step == 'create_account' && !session?.isAuthorized"
              ref="create_account"
              :class="
                step == 'create_account'
                  ? 'translate-x-[0px] duration-[700ms]'
                  : 'opacity-0 translate-x-96 duration-700'
              "
              class="relative w-full flex-col justify-start items-center gap-2.5 flex"
            >
              <div
                v-for="field in getFormFields('create_account')"
                class="flex-col justify-start items-start gap-1.5 flex"
              >
                <div class="w-96 justify-between items-start inline-flex">
                  <div class="text-white text-sm font-normal tracking-wide">
                    {{ field.title }}
                  </div>
                  <div
                    class="hidden text-right text-red-500 text-sm font-normal tracking-wide"
                  >
                    Error message
                  </div>
                </div>
                <div class="justify-start items-center gap-2.5 inline-flex">
                  <input
                    :name="field.name"
                    v-model="getFormValues('create_account')[field.name]"
                    :type="field.type"
                    class="w-96 h-11 px-3.5 py-7 outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-white text-sm font-medium tracking-wide"
                  />
                </div>
              </div>
              <div class="justify-center items-center gap-2.5 inline-flex">
                <button
                  @click="createAccount()"
                  :disabled="isLoading"
                  class="w-96 h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
                >
                  Submit {{ isLoading ? "loading..." : "" }}
                </button>
              </div>
              <div
                class="w-96 h-11 p-3.5 justify-between items-center gap-2.5 inline-flex"
              >
                <button
                  @click="step = 'auth'"
                  class="w-full flex justify-center h-11 p-3.5 hover:opacity-70 rounded-[10px] text-white text-sm font-medium tracking-wide"
                >
                  Back to Sign In
                </button>
              </div>
            </div>

            <div
              v-if="session?.isAuthorized"
              ref="authorized"
              :class="
                session?.isAuthorized
                  ? 'translate-x-[0px] duration-[700ms]'
                  : 'opacity-0 -translate-x-96 duration-700'
              "
              class="relative w-full flex-col justify-start items-center gap-2.5 flex"
            >
              <BrandingLogo class="mb-10" />
              <div class="w-96 justify-between items-start inline-flex">
                <div class="text-white text-xl font-bold tracking-wide">
                  Setup Your Account
                </div>
              </div>

              <!--              <div class="flex-col justify-start items-start gap-1.5 flex">-->
              <!--                <div class="w-96 justify-between items-start inline-flex">-->
              <!--                  <div class="text-white text-sm font-normal tracking-wide">Gender</div>-->
              <!--                  <div :class="isError('setup', 'gender') ? '' : 'hidden'" class=" text-right text-red-500 text-sm font-normal tracking-wide">{{ isError('setup', 'gender') }}</div>-->
              <!--                </div>-->
              <!--                <div class="justify-start items-center w-full gap-2.5 inline-flex">-->
              <!--                  <button @click="chooseGender('male')" :class="getFormValues('setup')?.gender == 'male' ? 'bg-white text-neutral-900 ' : 'text-white'" class="w-full h-11 p-3.5 hover:opacity-90 rounded-[10px] border text-sm font-medium tracking-wide flex items-center justify-center">-->

              <!--                    Male-->
              <!--                  </button>-->
              <!--                  <button @click="chooseGender('female')" :class="getFormValues('setup')?.gender == 'female' ? 'bg-white text-neutral-900 ' : 'text-white'" class="w-full h-11 p-3.5 hover:opacity-90 rounded-[10px] border text-sm font-medium tracking-wide flex items-center justify-center">-->

              <!--                    Female-->
              <!--                  </button>-->
              <!--                </div>-->
              <!--              </div>-->

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
                <div
                  class="justify-start items-center w-full gap-2.5 inline-flex"
                >
                  <div
                    class="justify-center w-96 items-center gap-2.5 inline-flex"
                  >
                    <label
                      for="studio_logo"
                      class="flex-col justify-center items-center h-[58px] px-3.5 py-3.5 cursor-pointer outline-none rounded-[10px] focus:border-white border border-white border-opacity-20 bg-transparent text-[#c1c1c1] text-xs font-light tracking-wide text-center"
                    >
                      <BrandingLogo />
                      upload...
                    </label>
                    <input
                      class="hidden"
                      id="studio_logo"
                      @change="getFormValues('setup')['studio_logo']"
                      type="file"
                      placeholder="Enter Your Studio Name"
                    />

                    <input
                      v-model="getFormValues('setup')['studio_name']"
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
                    v-model="getFormValues('setup')['address']"
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
                    v-model="getFormValues('setup')['about']"
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
                  @click="signOut()"
                  class="w-96 h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div
        v-if="!session?.isAuthorized"
        class="fixed left-0 bottom-0 w-full pointer-events-none"
      ></div>
    </div>
    <client-only>
      <Particles />
    </client-only>
  </div>
</template>

<style scoped lang="scss">
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

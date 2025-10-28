import { defineStore } from "pinia"
import { useRuntimeConfig } from "#imports"
import axios from "axios"
import { useSessionStore } from "~/src/entities/Session"
import { useRouter } from "vue-router"
import { navigateTo } from "nuxt/app"
const router = useRouter()

type inputField = {
  name: string
  title: string
  type: string
}

export type StudioFormValues = {
  dayoffs: dayOff[]
}

type formValues = {
  inputValues: StudioFormValues
  errors: string[]
  inputFields: inputField[]
  hoursMods: string[]
}

type dayOff = {
  day: string
  start: string
  end: string
}

export const useCreateStudioFormStore = defineStore({
  id: "create-studio-hours-store",
  state: (): formValues => ({
    inputValues: {
      dayoffs: [
        {
          day: "",
          start: "",
          end: "",
        },
      ],
    },
    errors: [],
    hoursMods: [],
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
  }),
  actions: {
    submit() {
      const config = useRuntimeConfig()

      const formData = new FormData()
      // @ts-ignore
      formData.append("logo", this.inputValues.logo as File)
      // @ts-ignore
      formData.append("company", this.inputValues.company)
      // @ts-ignore
      formData.append("address", this.inputValues.address)
      // @ts-ignore
      formData.append("country", this.inputValues.country)
      // @ts-ignore
      formData.append("city", this.inputValues.city)
      // @ts-ignore
      formData.append("street", this.inputValues.street)
      // @ts-ignore
      formData.append("about", this.inputValues.about)
      // @ts-ignore
      formData.append("longitude", this.inputValues.longitude)
      // @ts-ignore
      formData.append("latitude", this.inputValues.latitude)

      let requestConfig = {
        method: "post",
        credentials: true,
        url: `${config.public.apiBaseClient}/brand`,
        data: formData,
        headers: {
          Accept: "application/json",
          "Content-Type": "multipart/form-data",
          Authorization: "Bearer " + useSessionStore().accessToken,
        },
      }
      axios.defaults.headers.common["X-Api-Client"] = `web`
      axios
        .request(requestConfig)
        .then((response) => {
          //function that redirect to route /@[slug]

          navigateTo("/company/@" + response.data?.data?.slug)
        })
        .catch((error) => {
          console.error(error)
        })
    },
  },
})

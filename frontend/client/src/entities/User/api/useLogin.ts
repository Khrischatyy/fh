import { reactive, ref } from "vue"
import { useApi } from "~/src/lib/api"
import { useSessionStore } from "~/src/entities/Session"
import { navigateTo } from "nuxt/app"

type loginValues = {
  email: string
  password: string
}
type ErrorType = {
  email?: string[]
  password?: string[]
}

type ErrorField = "email" | "password" // Add other field names as needed

export function useLogin() {
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

  const formValues = reactive({
    email: "",
    password: "",
  })

  const errors = ref<ErrorType>({})
  const isLoading = ref(false)

  function isError(field: ErrorField): string | boolean {
    if (errors.value.hasOwnProperty(field)) {
      const errorMessages = errors.value[field]
      if (errorMessages && errorMessages.length > 0) {
        return errorMessages[0] // Return the first error message
      }
    }
    return false // Return false if no errors are found
  }

  async function loginUser(data: loginValues) {
    const session = useSessionStore()
    const formData = new FormData()
    Object.keys(data).forEach((key: any) => {
      if (key in data) {
        const value = data[key as keyof loginValues]
        if (value !== null) {
          formData.append(key, value as string | Blob)
        }
      }
    })

    const { post } = useApi({
      url: "/auth/login",
      auth: false,
    })

    // Clear previous errors before a new submission
    errors.value = {}

    try {
      const response = await post(formData)

      session.setUserRole(response?.role)
      session.authorize(response?.token)

      //Resume booking if there is any stored data
      const storedBookingData = localStorage.getItem("bookingData")
      if (storedBookingData) {
        navigateTo("/booking-resume")
        return response
      }

      if (response?.role === "studio_owner" && !response?.has_company) {
        navigateTo("/create")
      } else {
        navigateTo("/")
      }

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

  return { loginUser, errors, isLoading, formValues, isError }
}

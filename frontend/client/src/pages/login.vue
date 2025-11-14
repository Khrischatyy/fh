<script setup lang="ts">
import {
  ChooseRole,
  CreateAccountForm,
} from "~/src/features/Register/createAccount"
import BrandingLogo from "~/src/shared/ui/branding/BrandingLogo.vue"
import { useHead } from "@unhead/vue"
import Particles from "~/src/shared/ui/components/Particles/Particles.vue"
import { definePageMeta, navigateTo } from "#imports"
import { computed, onBeforeMount, reactive, ref } from "vue"
import {
  IconElipse,
  IconCopyright,
  IconLine,
  IconCheck,
  IconNumbers,
} from "~/src/shared/ui/common/Icon"
import { useCreateAccount, useLogin } from "~/src/entities/User/api"
import { FInputClassic } from "~/src/shared/ui/common"
import GoogleSignInButton from "~/src/shared/ui/components/GoogleSignInButton.vue"
import PhoneSignInButton from "~/src/shared/ui/components/PhoneSignInButton.vue"
import PhoneAuthInput from "~/src/features/Auth/phone-login/ui/PhoneAuthInput.vue"
import { CreateAccountFlow } from "~/src/widgets/CreateAccount"

useHead({
  title: "Funny How – Book a Session Time",
  meta: [{ name: "Funny How", content: "Book A Studio Time" }],
})

definePageMeta({
  middleware: "guest",
})

const { loginUser, errors, isLoading, formValues, isError } = useLogin()
const showPhoneAuth = ref(false)

const {
  formValues: registrationFormValues,
  errors: registrationErrors,
  isLoading: isRegistrationLoading,
  isError: isRegistrationError,
  registerUser,
} = useCreateAccount()

const step = ref("auth")

function getAuthTitleByName(name: string) {
  return steps.find((step: any) => step.name === name)?.title
}

const steps = reactive([
  { name: "auth", title: "Sign In", order: 1 },
  { name: "create", title: "Choose Role", order: 2 },
  { name: "create_account", title: "Personal Info", order: 3 },
  { name: "forgot", title: "Forgot Password", order: 4 },
])

const session = ref()

function createForm() {
  step.value = "create"
  return
}

const handleRoleUpdate = (role: string) => {
  registrationFormValues.role = role
  step.value = "create_account"
}

const stepUpdate = ($event: string) => {
  step.value = $event //Navigate to the step
}

async function authForm() {
  isLoading.value = true
  try {
    await loginUser(formValues)
    // Navigate or handle success as needed
  } catch (error) {
    console.error("Error submitting studio form:", error)
  } finally {
    isLoading.value = false
  }
}

function handlePhoneAuthSuccess() {
  showPhoneAuth.value = false
  // User is now authenticated via session store
}

function handlePhoneAuthCancel() {
  showPhoneAuth.value = false
}

const bookingData = computed(() => {
  if (process.client) {
    return localStorage.getItem("bookingData") || false
  } else {
    return false
  }
})
</script>

<template>
  <div
    :class="
      step == 'auth' && !session?.isAuthorized
        ? 'lg:grid-cols-[486px_1fr] duration-700'
        : 'lg:grid-cols-[0px_1fr] duration-[700ms]'
    "
    class="ease-in-out grid min-h-screen h-[100vh]"
    style="min-height: -webkit-fill-available"
  >
    <div
      :class="
        step == 'auth' && !session?.isAuthorized
          ? 'w-full translate-x-[0px] duration-[700ms]'
          : 'translate-x-[-486px] duration-300'
      "
      class="z-10 ease-in-out bg-black hidden lg:block text-white px-[50px] py-[60px] min-h-screen h-[100vh]"
      style="min-height: -webkit-fill-available"
    >
      <div
        class="w-full mt-10 h-full flex-col justify-between items-start gap-7 inline-flex"
      >
        <div class="description">
          <BrandingLogo
            class="cursor-pointer hover:opacity-80"
            @click="navigateTo('/')"
          />
          <div
            class="description mt-10 font-bold text-base text-wide leading-7"
          >
            Empowering Artists Everywhere —<br />Book, Record, and Create with
            Ease
          </div>
          <div class="points mt-10">
            <div
              class="w-full flex-col justify-start items-start gap-7 inline-flex"
            >
              <div class="justify-start items-start gap-5 inline-flex">
                <div class="w-8 h-8 relative">
                  <div class="left-0 top-0 absolute">
                    <IconNumbers :number="1" />
                  </div>
                </div>
                <div
                  class="flex-col justify-start items-start gap-2.5 inline-flex"
                >
                  <div class="text-white text-base font-bold tracking-wide">
                    Seamless Scheduling
                  </div>
                  <div
                    class="w-80 text-white text-sm font-normal tracking-wide leading-6"
                  >
                    Our intuitive calendar interface makes it easy to see studio
                    availability and schedule sessions without back-and-forth
                    communication.
                  </div>
                </div>
              </div>
              <div class="justify-start items-start gap-5 inline-flex">
                <div class="w-8 h-8 relative">
                  <div class="left-0 top-0 absolute">
                    <IconNumbers :number="2" />
                  </div>
                </div>
                <div
                  class="flex-col justify-start items-start gap-2.5 inline-flex"
                >
                  <div class="text-white text-base font-bold tracking-wide">
                    Integrated Payment System
                  </div>
                  <div
                    class="w-80 text-white text-sm font-normal tracking-wide leading-6"
                  >
                    Secure and straightforward in-app payments to reserve your
                    studio time without hassle.
                  </div>
                </div>
              </div>
              <div class="justify-start items-start gap-5 inline-flex">
                <div class="w-8 h-8 relative">
                  <div class="left-0 top-0 absolute">
                    <IconNumbers :number="3" />
                  </div>
                </div>
                <div
                  class="flex-col justify-start items-start gap-2.5 inline-flex"
                >
                  <div class="text-white text-base font-bold tracking-wide">
                    Collaborative Planning Tools
                  </div>
                  <div
                    class="w-80 text-white text-sm font-normal tracking-wide leading-6"
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

    <div class="auth-panel bg-black relative">
      <div
        class="w-full h-full flex sm:grid items-start lg:items-center justify-center mb-0 md:md-10"
      >
        <div
          class="relative w-full flex-col justify-start items-center gap-7 inline-flex"
        >
          <BrandingLogo class="lg:hidden mt-10" />
          <div
            :class="
              step == 'auth'
                ? 'translate-x-[0px] duration-[700ms] opacity-0'
                : '-translate-x-96/2 duration-700'
            "
            class="breadcrumbs hidden sm:flex mt-10 text-white text-sm font-normal tracking-wide gap-1.5 justify-center items-center"
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
            class="relative hidden sm:block text-white text-3xl font-bold tracking-wider"
          >
            {{ getAuthTitleByName(step) }}
          </div>
          <div
            class="relative h-full w-full m-2 md:m-0 md:w-96 min-h-auto sm:min-h-[500px] flex justify-start items-center bg-gradient-to-b from-black via-black to-transparent rounded-xl p-5 z-10"
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
              <FInputClassic
                size="lg"
                v-model="formValues.email"
                label="E-mail"
                type="email"
                :error="isError('email')"
              />
              <FInputClassic
                size="lg"
                v-model="formValues.password"
                label="Password"
                type="password"
                :error="isError('password')"
              />
              <div
                class="w-full h-7 rounded-lg justify-start items-center gap-2.5 inline-flex"
              >
                <label for="sign-in-for-a-month" class="checkbox-wrapper flex">
                  <div class="w-4 h-4 justify-center items-center flex">
                    <input
                      id="sign-in-for-a-month"
                      type="checkbox"
                      class="hidden"
                    />
                    <div
                      class="w-4 h-4 rounded-[3px] border border-white custom-checkbox"
                    ></div>
                  </div>
                  <div class="text-white text-sm font-normal tracking-wide">
                    Stay signed in for a month
                  </div>
                </label>
              </div>

              <div class="flex flex-col w-full items-center gap-2.5">
                <button
                  @click="authForm()"
                  class="w-full h-11 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
                >
                  Sign In
                </button>

                <div
                  class="justify-center w-full items-center gap-2.5 inline-flex"
                >
                  <button
                    @click="createForm()"
                    class="w-full min-h-11 h-auto p-3.5 hover:opacity-90 rounded-[10px] text-white border text-sm font-medium tracking-wide"
                  >
                    Don't have an account? Create account
                  </button>
                </div>

                <!-- Auth Options -->
                <div class="flex flex-col gap-3">
                  <GoogleSignInButton />

                  <!-- Phone Sign In Button (toggles inline form) -->
<!--                  <PhoneSignInButton-->
<!--                    v-if="!showPhoneAuth"-->
<!--                    @click="showPhoneAuth = true"-->
<!--                  />-->

                  <!-- Inline Phone Auth Form -->
                  <PhoneAuthInput
                    v-if="showPhoneAuth"
                    @success="handlePhoneAuthSuccess"
                    @cancel="handlePhoneAuthCancel"
                  />
                </div>
              </div>
              <div
                class="w-full h-11 p-3.5 justify-center items-center gap-2.5 inline-flex"
              >
                <button
                  @click="navigateTo('/forgot-password')"
                  class="w-full h-11 p-3.5 hover:opacity-90 rounded-[10px] text-white text-sm font-medium tracking-wide"
                >
                  Forgot password?
                </button>
              </div>
            </div>

            <CreateAccountFlow
              @step-update="stepUpdate"
              v-if="step == 'create'"
            />
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
.numberSubHead {
  font-family: "Montserrat";
  font-style: normal;
  font-weight: 700;
  font-size: 36px;
  line-height: 44px;

  letter-spacing: 0.04em;
  border: 1px solid #efc933;
}
</style>

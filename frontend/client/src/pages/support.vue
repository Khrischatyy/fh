<template>
  <div class="w-full min-h-screen bg-black px-5 py-10">
    <Spinner :is-loading="isLoading" />
    <div class="flex flex-col gap-10 justify-center items-center">
      <div class="text-center flex flex-col gap-5">
        <h1 class="text-4xl font-bold text-white">Contact Support</h1>
        <p class="text-xl text-white/70">
          Have a question or need help? Send us a message and we'll get back to you.
        </p>
      </div>

      <!-- Success Message -->
      <div
        v-if="success"
        class="max-w-xl w-full p-4 bg-green-500/20 border border-green-500 rounded-lg text-green-400 text-center"
      >
        {{ success }}
      </div>

      <!-- Support Form -->
      <div
        v-if="!success"
        class="flex flex-col gap-4 max-w-xl w-full"
      >
        <!-- Name -->
        <div class="flex flex-col gap-1.5">
          <label class="text-white text-sm">Name</label>
          <FInputClassic
            :error="isError('name')"
            type="text"
            class="w-full"
            v-model="form.name"
            placeholder="Your name"
            required
          />
        </div>

        <!-- Email -->
        <div class="flex flex-col gap-1.5">
          <label class="text-white text-sm">Email</label>
          <FInputClassic
            :error="isError('email')"
            type="email"
            class="w-full"
            v-model="form.email"
            placeholder="your@email.com"
            required
          />
        </div>

        <!-- Subject -->
        <div class="flex flex-col gap-1.5">
          <label class="text-white text-sm">Subject</label>
          <FInputClassic
            :error="isError('subject')"
            type="text"
            class="w-full"
            v-model="form.subject"
            placeholder="What is this about?"
            required
          />
        </div>

        <!-- Message -->
        <div class="flex flex-col gap-1.5">
          <label class="text-white text-sm">Message</label>
          <textarea
            v-model="form.message"
            :class="[
              'w-full min-h-[150px] px-3.5 py-3.5 outline-none rounded-[10px] focus:border-white border border-white/20 bg-transparent text-white text-sm font-medium tracking-wide resize-none',
              isError('message') ? 'border-red-500' : ''
            ]"
            placeholder="Describe your issue or question in detail..."
            required
          ></textarea>
          <span v-if="isError('message')" class="text-red-500 text-xs">
            {{ isError('message') }}
          </span>
        </div>

        <!-- Submit Button -->
        <button
          @click="submitTicket"
          :disabled="isLoading"
          class="w-full h-11 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide mt-4 disabled:opacity-50"
        >
          {{ isLoading ? 'Sending...' : 'Send Message' }}
        </button>
      </div>

      <!-- Back to Home -->
      <div class="max-w-xl w-full">
        <button
          @click="navigateTo('/')"
          class="w-full flex justify-center h-11 p-3.5 hover:opacity-70 rounded-[10px] text-white text-sm font-medium tracking-wide"
        >
          <icon-left />
          Back to Home
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { FInputClassic, Spinner, IconLeft } from "~/src/shared/ui/common"
import { navigateTo, definePageMeta } from "#app"
import { useApi } from "~/src/lib/api"
import { useSessionStore } from "~/src/entities/Session"

definePageMeta({
  layout: "error",
})

const isLoading = ref(false)
const errors = ref<Record<string, string[]>>({})
const success = ref<string>("")
const session = useSessionStore()

const form = reactive({
  name: "",
  email: "",
  subject: "",
  message: "",
})

// Pre-fill form if user is logged in
onMounted(() => {
  if (session.user) {
    form.name = session.user.firstname
      ? `${session.user.firstname} ${session.user.lastname || ''}`.trim()
      : session.user.name || ''
    form.email = session.user.email || ''
  }
})

function isError(field: string): string | boolean {
  if (errors.value?.hasOwnProperty(field)) {
    const errorMessages = errors.value[field]
    if (errorMessages && errorMessages.length > 0) {
      return errorMessages[0]
    }
  }
  return false
}

const submitTicket = async () => {
  isLoading.value = true
  errors.value = {}
  success.value = ""

  // Client-side validation
  if (!form.name.trim()) {
    errors.value.name = ["Name is required"]
    isLoading.value = false
    return
  }
  if (!form.email.trim()) {
    errors.value.email = ["Email is required"]
    isLoading.value = false
    return
  }
  if (!form.subject.trim()) {
    errors.value.subject = ["Subject is required"]
    isLoading.value = false
    return
  }
  if (!form.message.trim() || form.message.trim().length < 10) {
    errors.value.message = ["Message must be at least 10 characters"]
    isLoading.value = false
    return
  }

  const { post } = useApi({
    url: "support",
    auth: session.isAuthorized,
  })

  try {
    const response = await post({
      name: form.name,
      email: form.email,
      subject: form.subject,
      message: form.message,
    })

    isLoading.value = false
    success.value = "Your message has been sent successfully! We'll get back to you soon."

    // Reset form
    form.name = ""
    form.email = ""
    form.subject = ""
    form.message = ""
  } catch (error: any) {
    isLoading.value = false
    if (error?.data?.errors) {
      errors.value = error.data.errors
    } else {
      errors.value = { message: ["Failed to send message. Please try again."] }
    }
  }
}
</script>

<style scoped lang="scss"></style>

<template>
  <div>
    <NuxtLayout
      title="Profile"
      class="text-white flex flex-col min-h-screen"
      name="dashboard"
    >
      <div
        class="container flex flex-col relative gap-10 mx-auto px-2 overflow-x-hidden md:px-4 mb-10"
      >
        <Spinner :is-loading="isLoading" />
        <div
          class="flex gap-2 w-full p-5 max-w-2xl bg-[#171717] border border-white border-opacity-10 rounded-[10px] justify-center items-center"
        >
          <div
            class="group relative min-w-32 cursor-pointer w-32 h-32 avatar rounded-full border border-white border-opacity-20 flex justify-center items-center"
          >
            <img
              v-if="userForm.profile_photo"
              class="object-cover rounded-full w-full"
              :src="userForm.profile_photo"
            />
            <div class="absolute w-full h-full z-10">
              <FInputClassic
                input-style="plain"
                type="file"
                class="opacity-20 w-full h-full rounded-full group-hover:opacity-100"
                v-model="uploadingPhoto"
                @change="updateProfilePhoto"
              />
            </div>
          </div>
          <div class="flex flex-col gap-5 w-full">
            <FInputClassic
              @blur="saveUser"
              label="First Name"
              placeholder="First name"
              v-model="userForm.firstname"
            />
            <FInputClassic
              @blur="saveUser"
              label="Last Name"
              placeholder="Last name"
              v-model="userForm.lastname"
            />
          </div>
        </div>
        <div
          class="flex gap-2 w-full p-5 max-w-2xl bg-[#171717] border border-white border-opacity-10 rounded-[10px]"
        >
          <div class="flex flex-col gap-5 w-full">
            <FInputClassic
              @blur="saveUser"
              label="Phone"
              placeholder="000-00-00"
              v-model="userForm.phone"
            />
            <FInputClassic
              @blur="saveUser"
              disabled
              label="E-mail"
              placeholder="E-mail address"
              v-model="userForm.email"
            />
          </div>
        </div>
        <div
          class="flex gap-2 w-full p-5 max-w-2xl bg-[#171717] border border-white border-opacity-10 rounded-[10px]"
        >
          <div class="flex flex-col gap-5 w-full">
            <FInputClassic
              type="date"
              @blur="saveUser"
              label="Date Of Birth"
              placeholder="mm/dd/yy"
              v-model="userForm.date_of_birth"
            />
            <FInputClassic
              @blur="saveUser"
              label="Username"
              placeholder="Visible to others"
              v-model="userForm.username"
            />
          </div>
        </div>
        <div class="flex gap-2 w-full justify-center max-w-2xl">
          <button
            @click="navigateTo('/forgot-password')"
            class="w-full max-w-[376px] h-11 hover:opacity-90 bg-white rounded-[10px] text-neutral-900 text-sm font-medium tracking-wide"
          >
            Reset password
          </button>
          <button
            @click="navigateTo('/logout')"
            class="w-full h-11 max-w-[218px] hover:opacity-90 border-red border rounded-[10px] text-red text-sm font-medium tracking-wide"
          >
            Logout
          </button>
        </div>
      </div>
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue"
import { FInputClassic, IconUpload, Spinner } from "~/src/shared/ui/common"
import { useApi } from "~/src/lib/api"
import { filterUnassigned } from "~/src/shared/utils"
import { navigateTo } from "nuxt/app"
const isLoading = ref(false)

const userForm = reactive({
  firstname: "",
  lastname: "",
  email: "",
  date_of_birth: "",
  phone: "",
  username: "",
  profile_photo: "",
})
const uploadingPhoto = ref("")
onMounted(async () => {
  const { fetch: fetchUser } = useApi({ url: "/user/me", auth: true })
  isLoading.value = true
  await fetchUser().then((response) => {
    isLoading.value = false
    userForm.firstname = response?.data.user.firstname
    userForm.lastname = response?.data.user.lastname
    userForm.profile_photo = response?.data.user.profile_photo
    userForm.email = response?.data.user.email
    userForm.phone = response?.data.user.phone
    userForm.date_of_birth = response?.data.user.date_of_birth
    userForm.username = response?.data.user.username
  })
})

const saveUser = async () => {
  isLoading.value = true
  const { put: saveUser } = useApi({ url: "/user/update", auth: true })
  try {
    let data = filterUnassigned(userForm)
    await saveUser(data).then((response) => {
      isLoading.value = false
    })
  } catch (error) {
    console.error("Error saving user:", error)
    isLoading.value = false
  }
}

const updateProfilePhoto = async (event: Event) => {
  const { post: updatePhoto } = useApi({
    url: "/user/update-photo",
    auth: true,
  })
  const file = (event.target as HTMLInputElement).files?.[0]
  const formData = new FormData()
  formData.append("photo", file)
  try {
    isLoading.value = true
    await updatePhoto(formData).then((response) => {
      userForm.profile_photo = response.data.photo_url
      uploadingPhoto.value = ""
      isLoading.value = false
    })
  } catch (error) {
    console.error("Error updating photo:", error)
    isLoading.value = false
  }
}
</script>

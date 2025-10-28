<script setup lang="ts">
import defaultLogo from "~/src/shared/assets/image/studio.png"
import {Popup} from "~/src/shared/ui/components"
import {getStatus, getColor, getRatingColor} from "~/src/shared/utils"
import {computed, onMounted, onUnmounted, reactive, ref} from "vue"
import {FInput, FInputClassic, FSelect, FSelectClassic, IconLike} from "~/src/shared/ui/common"
import IconStar from "~/src/shared/ui/common/Icon/IconStar.vue"
import IconAddress from "~/src/shared/ui/common/Icon/IconAddress.vue"
import {useApi} from "~/src/lib/api"
import {Spinner} from "~/src/shared/ui/common/Spinner"
import {debounce} from "@antfu/utils";

const props = withDefaults(
    defineProps<{
      showPopup: boolean,
      addresses:  {id: number | string, name: string}[],
      activeAddress: string | number,
    }>(),
    {
      showPopup: false,
    },
)
const isLoading = ref(false)

const engineer = reactive({
  address: props.activeAddress,
  name: "",
  role: "studio_engineer",
  email: "",
  rate_per_hour: 0,
})

const roles = [
  {
    id: 'studio_engineer',
    name: "Engineer",
    label: "Engineer",
  },
]

type Engineer = {
  address: string
  name: string
  role: string
  email: string
  rate_per_hour: number
}

const emit = defineEmits<{
  (e: "togglePopup"): void
  (e: "closePopup"): void
  (e: "onCreateEngineer", engineer: Engineer): void
}>()

const closePopup = () => {
  emit("closePopup")
}


const isErrorVisible = ref(false)

const errorFromServer = ref("")

const isFormValid = computed(() => {
  return !!engineer.address && !!engineer.name && !!engineer.email && !!engineer.role && !!engineer.rate_per_hour
})

const showError = (field: string) => {
  return !engineer[field] ? `field is required` : ""
}


const checkEngineerEmail = debounce(700,async () => {
  const {fetch: checkEmail} = useApi({
    url: `/team/email/check?q=${engineer.email}`,
    auth: true,
  })

  if(!engineer.email) return

  await checkEmail().then((response) => {
    console.log('response', response)
  }).catch((error) => {
    console.error('error checking email', error)
  })
})

const createEngineer = async () => {
  isLoading.value = true
  //api/v1/address/{address_id}/staff

  isErrorVisible.value = false
  if (!isFormValid.value) {
    isErrorVisible.value = true
    isLoading.value = false
    return
  }

  const {post: createEngineer} = useApi({
    url: `team/member`,
    auth: true,
  })

  await createEngineer({
    name: engineer.name,
    role: engineer.role,
    email: engineer.email,
    rate_per_hour: engineer.rate_per_hour,
    address_id: engineer.address,
  }).then((response) => {
    isLoading.value = false
    // teammates.value = response.data.map((teammate: { id: number; role: string; username: string; phone: string; email: string; booking_count: number; address: string; profile_photo: string }) => ({
    //   id: teammate.id,
    //   role: teammate.roles[0].name == 'studio_engineer' ? 'Engineer' : 'Manager',
    //   username: teammate.username,
    //   phone: teammate.phone,
    //   email: teammate.email,
    //   booking_count: teammate.booking_count,
    //   address: addressesForPopup.value.find((address) => address.id === teammate.pivot.address_id) || '',
    //   profile_photo: teammate.profile_photo,
    // }))
    let teammate = {
      id: response.data.id,
      address: props.addresses.find((address) => address.id == engineer.address),
      username: engineer.name,
      role: 'Engineer',
      email: engineer.email,
    }
    emit("onCreateEngineer", teammate)
    closePopup()
  }).catch((error) => {
    isLoading.value = false
    console.error('error creating engineer', error)
    // ///
    // {
    //   "email": [
    //   "The email has already been taken."
    // ]
    // }
    errorFromServer.value = error.message
  })

  // emit("onCreateEngineer", engineer)
  // closePopup()
}
</script>

<template>
  <Popup
      :scroll-to-close="true"
      type="small"
      :title="'Manage Booking'"
      :open="showPopup"
      @close="closePopup"
  >
    <template #header>
      <div class="flex justify-start items-center gap-5">
        <div>
          <h3 class="text-xl font-bold text-white">
            Create Engineer
          </h3>
        </div>
      </div>
    </template>
    <template #body>
      <div class="flex flex-col gap-7 justify-between items-center relative">
        <Spinner :is-loading="isLoading"/>
        <div class="w-full relative flex justify-start gap-10 items-center">
          <div class="flex w-full justify-start gap-2">
            <div class="relative flex flex-col w-full gap-0.5">
              <FSelectClassic
                  :wide="true"
                  label="Address"
                  :error="isErrorVisible ? showError('address') : ''"
                  size="lg"
                  v-model="engineer.address"
                  :options="addresses"
                  placeholder="Select address"
                  class="w-full"/>
            </div>
          </div>
        </div>
        <div class="w-full relative flex justify-start gap-10 items-center">
          <div class="flex w-full justify-start gap-2">
            <div class="relative w-full flex flex-col gap-0.5">
              <FInputClassic label="Name" :error="isErrorVisible ? showError('name') : ''" :wide="true" v-model="engineer.name" placeholder="Enter name" class="w-full"/>
            </div>
          </div>
        </div>
        <div class="w-full relative flex justify-start gap-10 items-center">
          <div class="flex w-full justify-start gap-2">
            <div class="relative w-full flex flex-col gap-0.5">
              <FInputClassic label="E-mail" :wide="true"
                             @change="checkEngineerEmail"
                             :error="isErrorVisible ? showError('email') : ''"
                             v-model="engineer.email" placeholder="Enter e-mail" class="w-full"/>
            </div>
          </div>
        </div>
        <div class="w-full relative flex justify-start gap-10 items-center">
          <div class="flex w-full justify-start gap-2">
            <div class="relative w-full flex flex-col gap-0.5">
              <FInputClassic label="Rate per hour"
                             :error="isErrorVisible ? showError('rate_per_hour') : ''"
                             type="number" :wide="true" v-model="engineer.rate_per_hour" placeholder="Enter engineer's rate per hour" class="w-full">
                <template #icon>
                  <div
                      class="text-white text-xl font-normal tracking-wide opacity-20"
                  >
                    $
                  </div>
                </template>
              </FInputClassic>
            </div>
          </div>
        </div>
        <div class="w-full relative flex justify-start gap-10 items-center">
          <div class="flex w-full justify-start gap-2">
            <div class="relative flex flex-col w-full gap-0.5">
              <FSelectClassic
                  :wide="true"
                  label="Role"
                  size="lg"
                  :error="isErrorVisible ? showError('role') : ''"
                  v-model="engineer.role"
                  :options="roles"
                  placeholder="Select role"
                  class="w-full"/>
            </div>
          </div>
        </div>
        <div v-if="errorFromServer" class="w-full relative flex justify-start gap-10 items-center">
          <div class="flex w-full justify-start gap-2">
            <div class="relative w-full
             text-red-500 text-sm font-medium tracking-wide
             text-center
             flex flex-col gap-0.5">
            {{errorFromServer}}
            </div>
          </div>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-between items-center gap-2 w-full">
        <button
            @click="createEngineer"
            class="w-full h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-black text-sm font-medium tracking-wide"
        >
          Add Engineer
        </button>
      </div>
    </template>
  </Popup>
</template>

<style scoped lang="scss"></style>

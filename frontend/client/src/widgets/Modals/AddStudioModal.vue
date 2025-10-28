<script setup lang="ts">
import {Popup} from "~/src/shared/ui/components"
import {
  computed,
  inject,
  onMounted,
  onUpdated,
  provide,
  reactive,
  ref,
  watch,
} from "vue"
import {FInputClassic} from "~/src/shared/ui/common"
import {HoursChoose} from "~/src/widgets/HoursChoose"
import {BadgesChoose} from "~/src/widgets/BadgesChoose"
import {EquipmentChoose} from "~/src/widgets/EquipmentChoose"
import {AddStudioButton} from "~/src/features/addStudio"
import {useApi} from "~/src/lib/api"
import {ScrollContainer} from "~/src/shared/ui/common/ScrollContainer"
import {usePhotoSwipe} from "~/src/shared/ui/components/PhotoSwipe"
import type {SlideData} from "photoswipe"
import {AddRoomModal} from "~/src/widgets/Modals"
import {navigateTo} from "#app"
import {RoomCard} from "~/src/entities/Studio";

const props = withDefaults(
    defineProps<{
      showPopup: boolean,
      studioForPopup: Studio,
    }>(),
    {
      showPopup: false,
    },
)

const showRoomPopup = ref(false)
const activeRoom = ref(null)
const activeRoomId = ref(null)
const emit = defineEmits(["togglePopup", "closePopup", "update-studios"])

type Studio = {
  id: number
  name: string
  address: string
  description: string
  rooms: any[]
  hours: string
  price: number
  logo: string
  badges: string[]
  equipment: string[]
}
// const studio = inject("studioForPopup")
const studio = computed(() => props.studioForPopup)
const isLoading = ref(false)

const studioForm = reactive({
  name: "",
  address: "",
  rooms: [],
  description: "",
  slug: "",
  hours: "",
  price: 0,
  logo: "",
  badges: [],
  equipment: [],
  photos: [],
})

const isDragOver = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const onFileChange = async (event: Event) => {
  const files = (event.target as HTMLInputElement).files
  if (files) {
    await handleFile(files)
  }
}

const addRoom = (id: any) => {
  activeRoomId.value = id
  activeRoom.value = studio.value.rooms.find((room) => room.id === id)
  toggleRoomPopup()
  console.log("Room Popup Opened")
  console.log("show", showRoomPopup)
}


const addressId = computed(() => studio?.value.id)

const newRoom = reactive({
  name: "",
  address_id: addressId,
})

const showNewRoomPopup = ref(false)
const closeNewRoomPopup = () => {
  showNewRoomPopup.value = false
  newRoom.name = ""
}
const roomUpdateKey = ref(0)
const displayNewRoomPopup = () => {
  showNewRoomPopup.value = true
}
const addRoomRequest = () => {
  const { post: addRoom } = useApi({
    url: `/room/add-room`,
    auth: true,
  })
  addRoom(newRoom)
      .then((response) => {
        emit("update-studios")
        closeNewRoomPopup()
        roomUpdateKey.value++

      })
      .catch((error) => {
        console.error("Add failed:", error)
      })
}

const openFileDialog = () => {
  fileInputRef.value?.click()
}

const onDragOver = () => {
  isDragOver.value = true
}

const onDragLeave = () => {
  isDragOver.value = false
}

const onDrop = async (event: DragEvent) => {
  isDragOver.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    await handleFile(files)
  }
}

const getImageUrlByFile = (file: File) => {
  return URL.createObjectURL(file)
}
const getImageBase64 = (file: File) => {
  const reader = new FileReader()
  reader.readAsDataURL(file)
  reader.onload = () => {
  }
}

const togglePopup = () => {
  emit("togglePopup")
}

const toggleRoomPopup = () => {
  showRoomPopup.value = !showRoomPopup.value
}

const resetForm = () => {
  Object.keys(studioForm).forEach((key) => {
    studioForm[key] = ""
  })
  studioForm.photos = []
}
// Reset form when the popup is closed
watch(
    () => props.showPopup,
    (newVal) => {
      if (!newVal) {
        resetForm()
      }
    },
)

const closePopup = () => {
  Object.keys(studioForm).forEach((key) => {
    studioForm[key] = ""
  })
  emit("closePopup")
}

const closeRoomPopup = () => {
  showRoomPopup.value = false
}
const handleUpdateStudios = () => {
  emit("update-studios")
  roomUpdateKey.value++
  activeRoom.value = studio.value.rooms.find((room) => room.id === activeRoomId.value)
}
const updatedSlug = ref<string>("")
const updateSlug = () => {
  let slug = updatedSlug.value ? updatedSlug.value : studio.value?.slug
  const {put: updateSlug} = useApi({
    url: `/address/${slug}/update-slug`,
    auth: true,
  })

  updateSlug({new_slug: studioForm.slug})
      .then((response) => {
        updatedSlug.value = response.data?.slug
        emit("update-studios")
      })
      .catch((error) => {
        console.error("Update failed:", error)
      })
}
</script>

<template>
  <Popup :title="'Add Studio'" type="large" :open="showPopup" @close="closePopup">
    <template #header>
      <div class="input-container flex gap-2">
        <div v-if="studio.company.logo_url" class="logo">
          <img
              :src="studio.company.logo_url"
              alt="logo"
              class="w-[40px] h-[40px] object-cover rounded-[10px]"
          />
        </div>
        <div class="name font-bold text-xl">
          Studio edit
        </div>
      </div>
    </template>
    <template #body>
      <div class="photos mb-5">
        <div class="text-white text-sm font-normal tracking-wide opacity-20 mb-1">
          Room
        </div>
        <div
          :class="[
            studio?.rooms.length > 0
              ? 'sm:grid-cols-1 grid-rows-1'
              : '',
            { 'grid-rows-1': studio?.rooms.length === 0 },
          ]"
          class="grid-cols-1 sm:grid-rows-1 grid gap-5"
        >
          <div
              class="grid grid-cols-1 grid-rows-1 gap-5"
          >
            <div :key="roomUpdateKey" class="mt-5 sm:mt-0 w-full flex flex-wrap gap-2">

                <div
                    v-for="(room, index) in studio?.rooms.sort((a, b) => a.id - b.id)"

                    class="max-h-30 w-[150px] sm:w-[250px] bg-transparent scrollElement no-margin"
                >
                  <RoomCard
                      @click="addRoom(room.id)"
                      :room="room"
                      :key="index"
                      @update-studios="emit('update-studios')"/>

                </div>
              <div
                  @dragover.prevent="onDragOver"
                  @dragleave="onDragLeave"
                  @drop.prevent="onDrop"
                  class="add-photo w-[150px] lg:w-[250px] h-[150px] lg:h-[234px]"
              >
                <input
                    ref="fileInputRef"
                    type="file"
                    multiple
                    @change="onFileChange"
                    style="display: none"
                />
                <AddStudioButton
                    :border-opacity="isDragOver ? '100' : '20'"
                    type="room"
                    title="Add Room"
                    @click="displayNewRoomPopup"
                />
              </div>
            </div>
          </div>

        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div class="w-full flex flex-col gap-5">
          <div class="name w-full flex-col flex gap-1.5">
            <div
                class="text-white text-sm font-normal tracking-wide opacity-20"
            >
              Address
            </div>
            <FInputClassic
                :wide="true"
                :disabled="true"
                placeholder="Address"
                v-model="studio.street"
            />
          </div>
          <div class="slug w-full flex-col flex gap-1.5">
            <div
                class="text-white text-sm font-normal tracking-wide opacity-20"
            >
              Short name for url
            </div>
            <FInputClassic
                :wide="true"
                @blur="updateSlug"
                :placeholder="studio.slug"
                v-model="studioForm.slug"
            >
              <template #icon>
                <div
                    class="text-white text-xl font-normal tracking-wide opacity-20"
                >
                  @
                </div>
              </template>
            </FInputClassic>
          </div>
          <div class="equipment w-full flex-col flex gap-1.5">
            <EquipmentChoose v-model="studioForm.equipment"/>
          </div>

        </div>
        <div class="w-full flex-col flex gap-1.5">
          <div class="badgees w-full flex-col flex gap-1.5">
            <BadgesChoose v-model="studioForm.badges"/>
          </div>
          <div
              v-if="!studio.stripe_account_id && !studio.is_complete"
              class="payouts w-full flex-col flex gap-1.5 mt-3.5"
          >
            <div
                class="relative w-full flex-col justify-start items-center gap-1.5 flex"
            >
              <div
                  class="flex-col w-full justify-start items-start gap-1.5 flex"
              >
                <div class="w-full justify-between items-center flex">
                  <div
                      class="text-red w-full text-sm font-normal tracking-wide"
                  >
                    Setup your payouts information
                  </div>
                </div>
              </div>

              <div
                  class="flex-col w-full justify-center items-center gap-1.5 flex"
              >
                <div
                    class="w-full justify-center items-center gap-2.5 inline-flex"
                >
                  <button
                      @click="navigateTo('/payout')"
                      class="w-full h-11 p-3.5 hover:opacity-70 text-white rounded-[10px] border-red border text-sm font-medium tracking-wide"
                  >
                    Setup Payouts
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="hours w-full mt-3.5 flex-col flex gap-1.5">
            <HoursChoose
                @update-studios="emit('update-studios')"
                v-model="studioForm.hours"
            />
          </div>
        </div>


      </div>
      <Teleport v-if="showRoomPopup" to="body">
        <AddRoomModal
            :show-popup="showRoomPopup"
            :room="studio.rooms.find((room) => room.id === activeRoomId)"
            :key="roomUpdateKey"
            @update-studios="handleUpdateStudios"
            @closePopup="closeRoomPopup"
            @togglePopup="toggleRoomPopup"
        />
      </Teleport>
      <Teleport to="body">
        <Popup
            :title="'Add equipment'"
            type="small"
            :open="showNewRoomPopup"
            @close="closeNewRoomPopup"
        >
          <template #header>
            <h1 class="text-white text-[22px]/[26px]">Add room</h1>
          </template>
          <template #body>
            <div class="equipment w-full grid grid-cols-1 gap-2">
              <FInputClassic
                  :wide="true"
                  label="Name"
                  placeholder="e.g Room 1 / Studio A / Space Room"
                  v-model="newRoom.name"
              />
            </div>
          </template>
          <template #footer>
            <div class="flex justify-between items-center gap-2 w-full">
              <button
                  @click="closeNewRoomPopup"
                  class="w-full h-11 p-3.5 hover:opacity-90 bg-transparent rounded-[10px] text-white border-white border text-sm font-medium tracking-wide"
              >
                Cancel
              </button>
              <button
                  :disabled="!newRoom.name"
                  :class="{
              'opacity-80': !newRoom.name,
            }"
                  @click="addRoomRequest"
                  class="w-full h-11 p-3.5 hover:opacity-80 bg-white rounded-[10px] text-neutral-700 border-white border text-sm font-medium tracking-wide"
              >
                Add
              </button>
            </div>
          </template>
        </Popup>
      </Teleport>
    </template>
  </Popup>
</template>

<style scoped lang="scss">
.drag-item {
  cursor: grab;
}

.drag-item:active {
  cursor: grabbing;
  opacity: 0.5;
}

.drag-item:active {
  cursor: grabbing;
}

.custom-drag-image {
  opacity: 0.8;
  border-style: dashed;
  border-width: 2px;
  animation: float 1.5s infinite ease-in-out,
  border-rolling 1.5s infinite linear;
}

@keyframes float {
  0% {
    scale: 1;
  }
  50% {
    scale: 1.1;
  }
  100% {
    scale: 1;
  }
}

@keyframes border-rolling {
  0% {
    border-color: #ccc;
  }
  25% {
    border-color: #f00;
  }
  50% {
    border-color: #0f0;
  }
  75% {
    border-color: #00f;
  }
  100% {
    border-color: #ccc;
  }
}
</style>

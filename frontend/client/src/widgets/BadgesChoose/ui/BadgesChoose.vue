<script setup lang="ts">
import { useRuntimeConfig } from "#imports"
import { useSessionStore } from "~/src/entities/Session"
import { inject, onMounted, ref } from "vue"
import { useCreateStudioFormStore } from "~/src/entities/RegistrationForms"
import {
  IconPeople,
  IconWeed,
  IconMic,
  IconMonitor,
} from "~/src/shared/ui/common"

import { isBadgeTaken } from "~/src/shared/utils/checkBadge"
import { useApi } from "~/src/lib/api"

const badges = ref([])

const error = ref(null)
const isLoading = ref(false)

function isError(form: string, field: string): boolean {
  let formErrors: Record<string, any> = useCreateStudioFormStore().errors
  return formErrors.hasOwnProperty(field) ? formErrors[field][0] : false
}

const session = ref()
const studio = inject("studioForPopup")

onMounted(async () => {
  session.value = useSessionStore()
  getBadges()
})

function toogleBadge(badge_id) {
  isLoading.value = true
  const { post: updateBadge } = useApi({
    url: `/address/${studio.value.id}/badge`,
    auth: true,
  })

  updateBadge({ badge_id }).then((response) => {
    badges.value.taken_badges = response.data
    isLoading.value = false
  })
}
function getBadges() {
  isLoading.value = true
  const { fetch: fetchBadges } = useApi({
    url: `/address/${studio.value.id}/badges`,
    auth: true,
  })

  fetchBadges().then((response) => {
    badges.value = response.data
    isLoading.value = false
  })
}

function isBadge(badgeId: number, badges): boolean {
  if (badges.length > 0) return isBadgeTaken(badgeId, badges)
}
const sampleBadges = [
  {
    id: 1,
    name: "Record",
    icon: IconMic,
  },
  {
    id: 2,
    name: "Rent",
    icon: IconMonitor,
  },
  {
    id: 3,
    name: "10 Max",
    icon: IconPeople,
  },
  {
    id: 4,
    name: "Friendly",
    icon: IconWeed,
  },
]
</script>

<template>
  <div class="relative w-full flex-col justify-start items-center gap-1.5 flex">
    <div class="flex-col w-full justify-start items-start gap-1.5 flex">
      <div class="w-wull justify-between items-start inline-flex">
        <div
          class="text-whit w-full opacity-20 text-sm font-normal tracking-wide"
        >
          Studio Information
        </div>
      </div>
    </div>

    <div class="flex-col w-full justify-center items-center gap-1.5 flex">
      <div class="w-full justify-center items-center gap-2.5 inline-flex">
        <div class="w-full max-w-full grid grid-cols-2 lg:grid-cols-3 gap-2.5">
          <div v-if="isLoading" class="spinner-container">
            <div class="spinner"></div>
            <!-- Replace with a proper loading indicator -->
          </div>
          <div
            v-for="badge in badges?.all_badges"
            :class="
              isBadge(badge.id, badges?.taken_badges)
                ? 'border-opacity-100'
                : 'border-opacity-20'
            "
            @click="toogleBadge(badge.id)"
            class="w-full flex gap-2.5 justify-center items-center cursor-pointer h-11 outline-none rounded-[10px] focus:border-white px-1.5 border border-white bg-transparent text-white text-sm font-medium tracking-wide"
          >
            <img class="h-[29px]" :src="badge.image" />
            <span>{{ badge.name }}</span>
          </div>
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
select {
  -webkit-appearance: none;
  -moz-appearance: none;
  text-indent: 1px;
  text-overflow: "";
  cursor: pointer;
}
</style>

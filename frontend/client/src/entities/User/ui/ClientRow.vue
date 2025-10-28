<template>
  <div class="bg-black p-4 rounded-md shadow-lg flex flex-col sm:flex-row gap-10 justify-between p-5">
    <div class="flex w-auto justify-start items-center">
      <div class="flex justify-start items-center gap-5">
        <div v-if="client?.profile_photo" class="h-[35px] w-[35px]">
          <img :src="client?.profile_photo" alt="Logo" class="h-auto w-full object-cover" />
        </div>
        <div class="flex flex-col gap-2">
          <h3 class="text-xl font-bold text-white">{{ client?.firstname }}</h3>
          <Clipboard v-if="client?.username" :text-to-copy="phoneNormalizer(client?.username)">
            <div class="group flex relative gap-2 items-center justify-start">
              <p class="font-['Montserrat']">{{ client?.username }}</p>
            </div>
          </Clipboard>
        </div>
      </div>
    </div>
    <div class="flex w-auto flex-col sm:flex-row gap-8 min-w-[210px] justify-center items-start sm:items-center">
      <Clipboard v-if="client?.phone" :text-to-copy="client?.phone">
        <div class="flex items-center relative gap-2">
          <IconPhone class="opacity-20" />
          <div class="flex flex-col group-hover:opacity-100">
            <span class="text-white opacity-20">Phone</span>
            <p class="text-white">{{ client?.phone }}</p>
          </div>
        </div>
      </Clipboard>
      <Clipboard v-if="client?.email" :text-to-copy="client?.email">
        <div class="flex items-center relative gap-2 group-hours-block group">
          <IconEmail class="opacity-20" />
          <div class="flex flex-col group-hover:opacity-100">
            <span class="text-white opacity-20">Email</span>
            <span class="text-white">{{ client?.email }}</span>
          </div>
        </div>
      </Clipboard>
      <div class="flex items-center gap-2 min-w-[210px] relative group-price group">
        <IconStat class="opacity-20" />
        <div class="flex flex-col group-hover:opacity-100">
          <span class="text-white opacity-20">Booking count</span>
          <span class="text-white">{{ client?.booking_count }}</span>
        </div>
      </div>
    </div>

    <!-- Используем компонент ChatModal -->
    <ChatModal :client="client" />

    <Tooltip>
      Phone: {{ tooltipData.content }}
    </Tooltip>
  </div>
</template>

<script setup lang="ts">
import {
  IconCalendar,
  IconCheckmark,
  IconClock,
  IconCopy,
  IconEmail,
  IconPhone,
  IconStat,
  IconUser
} from "~/src/shared/ui/common";
import IconAddress from "~/src/shared/ui/common/Icon/IconAddress.vue";
import { inject, ref } from "vue";
import { Tooltip } from "~/src/shared/ui/Tooltip";
import { Clipboard } from "~/src/shared/ui/common/Clipboard";
import ChatModal from "~/src/widgets/Modals/ChatModal.vue";

const { tooltipData, showTooltip, hideTooltip } = inject('tooltipData');

type Client = {
  id: number,
  firstname: string,
  username: string,
  phone: string,
  email: string,
  booking_count: number
}

const props = defineProps<{ client: Client }>();
</script>

<style scoped>
</style>

<script setup lang="ts">
import { ScrollContainer } from "~/src/shared/ui/common/ScrollContainer"
import { computed, inject, ref } from "vue"
import { defineProps } from "vue"
import { IconBooking, IconMic, IconMonitor } from "~/src/shared/ui/common"
import { Tooltip } from "~/src/shared/ui/Tooltip"
const props = withDefaults(
  defineProps<{
    badges: { id: number; name: string; description: string }[]
    theme?: string
    size?: "default" | "sm" | "lg"
    justifyContent?: "center" | "start" | "end"
  }>(),
  {
    theme: "default",
    size: "default",
    justifyContent: "center",
  },
)
const isTooltipVisible = ref(false)

const showTooltipHandler = (event, content) => {
  isTooltipVisible.value = true
  showTooltip(event, content)
}
const hideTooltipHandler = () => {
  isTooltipVisible.value = false
  hideTooltip()
}
const { tooltipData, showTooltip, hideTooltip } = inject("tooltipData")
const ICON_MAP = {
  mixing: IconMonitor,
  record: IconMic,
  rent: IconBooking,
}
</script>

<template>
  <div>
    <ScrollContainer
      v-bind="$attrs"
      :justify-content-mobile="'center'"
      :justify-content="justifyContent"
      :theme="theme"
    >
      <div
        v-for="(badge, index) in badges"
        :key="badge.id"
        @click.stop="showTooltipHandler($event, badge?.description || '')"
        @mouseenter="showTooltipHandler($event, badge?.description || '')"
        @mouseleave="hideTooltipHandler"
        @touchstart="showTooltipHandler($event, badge?.description || '')"
        @touchend="hideTooltipHandler"
        class="scrollElement"
      >
        <img
          :src="badge.image"
          :alt="badge.name"
          :class="[
            { 'h-8': size === 'default' },
            { 'h-6': size === 'sm' },
            { 'h-10': size === 'lg' },
          ]"
          class="w-full object-contain"
        />
        <div
          class="text-white text-xs text-center mt-1 group-hover:opacity-70 font-[BebasNeue]"
        >
          {{ badge.name }}
        </div>
      </div>
    </ScrollContainer>
    <div v-show="isTooltipVisible">
      <Tooltip>
        {{ tooltipData.content }}
      </Tooltip>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>

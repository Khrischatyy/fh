<template>
  <div>
    <!-- Задний слой для блёра -->
    <div
      class="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-40 transition-opacity duration-300 ease-in-out"
      :class="{ 'opacity-100': isOpen, 'opacity-0': !isOpen }"
      @click="closeMenu"
      v-show="isOpen"
    ></div>
    <!-- Само меню -->
    <div
      v-if="!isLoading"
      class="fixed z-0 inset-y-0 left-0 w-full p-4 bg-[#000] bg-opacity-70 transform transition-transform duration-300 ease-in-out z-50 sm:relative sm:w-auto sm:p-0 sm:bg-transparent sm:transform-none sm:transition-none sm:ease-none sm:duration-0"
      :class="{ 'translate-x-0': isOpen, '-translate-x-full': !isOpen }"
    >
      <nav class="space-y-4">
        <NuxtLink
          v-for="(item, index) in filteredSideMenu"
          :key="item.name"
          :to="item.link"
          :class="selectedValue == index ? 'border border-white ' : ''"
          class="block text-lg py-2 rounded-[10px] px-1.5 py-3 flex items-center leading-tight"
        >
          <Component v-if="item.icon" :is="item.icon" class="w-8 h-8 mr-2" />
          <img v-else :src="item.path" alt="Icon" class="h-8 w-8 mr-2" />
          {{ item.name }}
        </NuxtLink>
        <button
          @click="closeMenu"
          class="text-white mt-4 flex items-center lg:hidden"
        >
          <i class="fas fa-times mr-2"></i> Close menu
        </button>
      </nav>
    </div>
    <div v-else class="items-center justify-center hidden sm:flex lg:w-64">
      <div class="spinner"></div>
      <!-- Replace with a proper loading indicator -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineExpose, onMounted, computed } from "vue"
import { useRouter } from "vue-router"
import { useSessionStore } from "~/src/entities/Session"

const props = defineProps({
  sideMenu: {
    type: Array,
    required: true,
  },
  isDataLoading: {
    type: Boolean,
    default: false,
  },
})
const router = useRouter()

const selected = ref(0)
const isOpen = ref(false)
const isLoading = ref(true)
const session = useSessionStore()
const userRole = computed(() => session.userRole)

// Use a computed property for filteredSideMenu
const filteredSideMenu = computed(() =>
  props.sideMenu.filter((item) => !item.role || item.role === userRole.value),
)

// watch(() => router.currentRoute.value.path, (path) => {
//   let route = path.split('/')[1];
//   selected.value = filteredSideMenu.value.findIndex((item) => item.link.includes(route));
// });

// watch(()=> userRole, (role) => {
//   filteredSideMenu = props.sideMenu.filter((item) => !item.role || item.role === role);
// });
const route = router.currentRoute.value.path.split("/")[1]
const selectedValue = computed(() =>
  filteredSideMenu.value.findIndex((item) => item.link.includes(route)),
)

onMounted(() => {
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeMenu()
    }
  })

  isLoading.value = false
})
const toggleMenu = () => {
  isOpen.value = !isOpen.value
}

const closeMenu = () => {
  isOpen.value = false
}

interface MenuItem {
  name: string
  path: string
  link?: string
}

defineExpose({ toggleMenu, closeMenu })
</script>

<style scoped>
@media (min-width: 1024px) {
  .transform {
    transform: none !important;
  }
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-left-color: #ffffff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

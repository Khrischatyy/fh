<template>
  <div>
    <NuxtLayout
      title="Clients"
      class="text-white flex flex-col min-h-screen"
      name="dashboard"
    >
      <div class="container mx-auto px-2 md:px-4">
        <div class="grid grid-cols-1 gap-6">
          <ClientRow
            class="border border-white border-opacity-30"
            v-for="client in clients"
            :key="client.id"
            :client="client"
          />
        </div>
      </div>
    </NuxtLayout>
  </div>
</template>

<style scoped>
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

<script setup lang="ts">
import { FilterBar } from "~/src/shared/ui/components"
import { computed, onMounted, ref } from "vue"
import { useApi } from "~/src/lib/api"
import ClientRow from "~/src/entities/User/ui/ClientRow.vue"
import { useSessionStore } from "~/src/entities/Session"
const showPopup = ref(false)

type Client = {
  id: number
  firstname: string
  username: string
  phone: string
  email: string
  booking_count: number
}

const clients = ref<Client[]>([])
const currentPage = ref(1)
const lastPage = ref(1)
const isLoading = ref(false)
const session = computed(() => useSessionStore())
const companySlug = computed(() => session.value.brand)
onMounted(() => {
  getClients()
})

const getClients = async (page = 1) => {
  isLoading.value = true
  const { post: fetchClients } = useApi({
    url: `/address/clients`,
    auth: true,
  })

  fetchClients({
    company_slug: companySlug.value,
  })
    .then((response) => {
      clients.value = response?.data

      isLoading.value = false
    })
    .catch((error) => {
      console.error("Error fetching bookings:", error)
    })
}

const togglePopup = () => {
  showPopup.value = !showPopup.value
}
</script>

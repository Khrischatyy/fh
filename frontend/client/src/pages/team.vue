<template>
  <div>
    <NuxtLayout
      title="Team"
      class="text-white flex flex-col min-h-screen"
      name="dashboard"
    >
      <Spinner :is-loading="isLoading"/>
      <template #action>
        <div class="flex gap-2">

        <button @click="createEngineerPopup" class="subhead__actions outline-none hover:opacity-70 flex justify-center items-center rounded-[10px] border border-dashed w-auto px-10">
          Add Engineer
        </button>
        </div>
      </template>
      <div class="container mx-auto px-2 md:px-4">
        <div class="grid grid-cols-1 gap-6">
          <TeammateRow
            class="border border-white border-opacity-30"
            v-for="teammate in teammates"
            @on-dismiss-teammate="handleDismissTeammate"
            :key="teammate.id"
            :teammate="teammate"
          />
        </div>
        <AddEngineerModal
          v-if="showPopup"
          :active-address="activeAddress"
          :addresses="addressesForPopup"
          @on-create-engineer="handleCreateEngineer"
          :showPopup="showPopup"
          @closePopup="closePopup"/>
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
import TeammateRow from "~/src/entities/User/ui/TeammateRow.vue";
import {storeToRefs} from "#imports";
import AddEngineerModal from "~/src/widgets/Modals/AddEngineerModal.vue";
import {FSelectClassic, IconUser, Spinner} from "~/src/shared/ui/common";
const showPopup = ref(false)

type Teammate = {
  id: number
  role: string
  username: string
  phone: string
  email: string
  booking_count: number
  address: string
  profile_photo: string
}

const teammates = ref<Teammate[]>([])
const addressesForPopup = ref<{ id: number; name: string; label: string; }[]>([]);
const currentPage = ref(1)
const lastPage = ref(1)
const isLoading = ref(true)
const session = useSessionStore()
const {brand} = storeToRefs(session)
const companySlug = brand
onMounted(async () => {
  await getAddresses()
  await getTeammates()
})

const activeAddress = ref();

const closePopup = () => {
  showPopup.value = false
}
const createEngineerPopup = () => {
  showPopup.value = true
}
const handleCreateEngineer = (teammate: Teammate) => {
  console.log('created engineer', teammate)
  teammates.value.push(teammate)
  showPopup.value = false
}

const handleDismissTeammate = (teammate: Teammate) => {
  console.log('dismissed', teammate)
  teammates.value = teammates.value.filter((t) => t.id !== teammate.id)
}

const getAddresses = async () => {
  isLoading.value = true
  const {fetch: fetchAddresses} = useApi({
    url: `/address/list`,
    auth: true,
  });

  await fetchAddresses().then((response) => {
   //response is response.data id, street
    addressesForPopup.value = response?.data.map((address: { id: number; street: string }) => ({
      id: address.id,
      name: address.street,
      label: address.street,
    }));
    activeAddress.value = addressesForPopup.value[0].id;
  }).finally(() => {
    isLoading.value = false;
  });
};

const getTeammates = async () => {
  isLoading.value = true
  const { fetch: fetchTeammates } = useApi({
    url: `/team/member`,
    auth: true,
  })


  fetchTeammates().then((response) => {
    teammates.value = response.data.map((teammate: { id: number; role: string; username: string; phone: string; email: string; booking_count: number; address: string; profile_photo: string }) => ({
      id: teammate.id,
      role: teammate.roles[0].name == 'studio_engineer' ? 'Engineer' : 'Manager',
      username: teammate.username,
      phone: teammate.phone,
      email: teammate.email,
      booking_count: teammate.booking_count,
      address: addressesForPopup.value.find((address) => address.id === teammate.pivot.address_id) || '',
      profile_photo: teammate.profile_photo,
    }))
    isLoading.value = false
  })
}
</script>

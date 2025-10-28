<script setup lang="ts">
import { definePageMeta, useRuntimeConfig } from "#imports"
import { useSessionStore } from "~/src/entities/Session"
import { inject, onMounted, ref, type UnwrapRef } from "vue"
import {
  type StudioFormValues,
  useCreateStudioFormStore,
} from "~/src/entities/RegistrationForms"
import {
  FInputClassic,
  FSelectClassic,
  IconClose,
} from "~/src/shared/ui/common"
import { Loader } from "@googlemaps/js-api-loader"
import axios from "axios"
import { Popup } from "~/src/shared/ui/components"
import { useApi } from "~/src/lib/api"

const closePopup = () => {
  showPopup.value = false
}
function isError(form: string, field: string): boolean {
  let formErrors: Record<string, any> = useCreateStudioFormStore().errors
  return formErrors.hasOwnProperty(field) ? formErrors[field][0] : false
}

const getEquipmentTypes = async () => {
  const { fetch: getTypes } = useApi({
    url: "/address/equipment-type",
  })
  const { data } = await getTypes()
  equipmentTypes.value = data
}

const session = ref()
onMounted(async () => {
  const config = useRuntimeConfig()
  session.value = useSessionStore()
  await getEquipment()
  await getEquipmentTypes()
})

export type EquipmentType = {
  id: number
  type: number
  value: string
  icon?: string
  deletable?: boolean
}

const equipmentTypes = ref<string[]>([])

const equipment = ref<EquipmentType[]>([
  {
    id: 1,
    type: 1,
    value: "",
    deletable: false,
  },
  {
    id: 2,
    type: 3,
    value: "",
    deletable: false,
  },
  {
    id: 3,
    type: 4,
    value: "",
    deletable: false,
  },
])
const showPopup = ref(false)
const togglePopup = () => {
  showPopup.value = !showPopup.value
}

const addEquipmentForm = ref({
  type: "",
  value: "",
})

const studio = inject("studioForPopup")
const isLoading = ref(false)

export type equipmentResponseType = {
  id: number
  equipment_type_id: number
  name: string
  type: {
    id: number
    name: string
    icon: string
  }
}
const getEquipment = async () => {
  isLoading.value = true
  const { fetch: getEquipment } = useApi({
    url: `/address/${studio.value.id}/equipment`,
    auth: true,
  })
  getEquipment().then((response) => {
    equipment.value = response.data.map((eq: any) => {
      return {
        id: eq.id,
        type: eq.equipment_type_id,
        value: eq.name,
        icon: eq.type.icon,
        deletable: true,
      }
    })
    isLoading.value = false
  })
}
const addEquipment = () => {
  isLoading.value = true
  const { post: sendEquipment } = useApi({
    url: `/address/${studio.value.id}/equipment`,
    auth: true,
  })

  sendEquipment({
    equipment_type_id: addEquipmentForm.value.type,
    name: addEquipmentForm.value.value,
  }).then((response) => {
    equipment.value = response.data.map((eq: any) => {
      return {
        id: eq.id,
        type: eq.equipment_type_id,
        value: eq.name,
        icon: eq.type.icon,
        deletable: true,
      }
    })
    isLoading.value = false
  })

  addEquipmentForm.value.value = ""
  addEquipmentForm.value.type = ""
  togglePopup()
}

const deleteEquipment = (id: number) => {
  isLoading.value = true
  const { delete: deleteEquipment } = useApi({
    url: `/address/${studio.value.id}/equipment?equipment_id=${id}`,
    auth: true,
  })

  deleteEquipment().then(() => {
    equipment.value = equipment.value.filter((eq) => eq.id !== id)
    isLoading.value = false
  })
}
</script>

<template>
  <div class="relative w-full flex-col justify-start items-center gap-2.5 flex">
    <Popup
      :title="'Add equipment'"
      type="small"
      :open="showPopup"
      @close="closePopup"
    >
      <template #header>
        <h1 class="text-white text-[22px]/[26px]">Add equipment</h1>
      </template>
      <template #body>
        <div class="equipment w-full grid grid-cols-2 gap-2">
          <FInputClassic
            label="Value"
            placeholder="Value"
            v-model="addEquipmentForm.value"
          />
          <FSelectClassic
            label="Type"
            placeholder="Type"
            v-model="addEquipmentForm.type"
            :options="equipmentTypes"
          />
        </div>
      </template>
      <template #footer>
        <div class="flex justify-between items-center gap-2 w-full">
          <button
            @click="togglePopup"
            class="w-full h-11 p-3.5 hover:opacity-90 bg-transparent rounded-[10px] text-white border-white border text-sm font-medium tracking-wide"
          >
            Cancel
          </button>
          <button
            :disabled="!addEquipmentForm.type || !addEquipmentForm.value"
            :class="{
              'opacity-80': !addEquipmentForm.type || !addEquipmentForm.value,
            }"
            @click="addEquipment"
            class="w-full h-11 p-3.5 hover:opacity-80 bg-white rounded-[10px] text-neutral-700 border-white border text-sm font-medium tracking-wide"
          >
            Add
          </button>
        </div>
      </template>
    </Popup>
    <div class="flex-col w-full justify-start items-start gap-1.5 flex">
      <div class="w-full justify-between items-start inline-flex">
        <div class="text-neutral-700 text-sm font-normal tracking-wide">
          Equipment
        </div>
        <div
          :class="isError('setup', 'studio_name') ? '' : 'hidden'"
          class="text-right text-red-500 text-sm font-normal tracking-wide"
        >
          {{ isError("setup", "studio_name") }}
        </div>
      </div>
      <div
        class="flex-col w-full mb-1 justify-center items-center gap-1.5 flex"
      >
        <div class="justify-center w-full items-center gap-2.5 inline-flex">
          <button
            @click="togglePopup"
            class="w-full h-11 p-3.5 hover:opacity-90 bg-white rounded-[10px] text-neutral-700 border-white border text-sm font-medium tracking-wide mt-2"
          >
            Add equipment
          </button>
        </div>
      </div>
    </div>

    <div
      class="equipment-inputs flex-col w-full justify-center items-center gap-1.5 flex"
    >
      <div class="equipment w-full grid grid-cols-2 lg:grid-cols-3 gap-2">
        <div v-if="isLoading" class="spinner-container">
          <div class="spinner"></div>
          <!-- Replace with a proper loading indicator -->
        </div>
        <div v-for="(eq, index) in equipment" class="flex gap-2">
          <FInputClassic
            :label="equipmentTypes.find((et) => et.id == eq.type)?.name"
            :placeholder="`Name ${eq.type}`"
            v-model="eq.value"
          >
            <template #action>
              <button
                v-if="eq.deletable"
                @click="deleteEquipment(eq.id)"
                class="flex items-center justify-end rounded-[10px] opacity-20 hover:opacity-100 bg-transparent text-white text-xs font-medium tracking-wide cursor-pointer"
              >
                <IconClose class="h-5" />
              </button>
            </template>
          </FInputClassic>
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
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* For Firefox */
input[type="number"] {
  -moz-appearance: textfield;
}
</style>

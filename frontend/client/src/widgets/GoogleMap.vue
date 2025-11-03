<script setup>
import { GoogleMap, MarkerCluster } from "vue3-google-map"
import { ref, computed, onMounted, watch } from "vue"
import MarkerList from "~/src/widgets/MarkerList.vue"
import { useRuntimeConfig } from "#imports"
import darkTheme from "~/src/shared/assets/maps/dark-theme.json"

const config = useRuntimeConfig()

const props = defineProps({
  lat: {
    type: String,
  },
  lng: {
    type: String,
  },
  logo: {
    type: String,
  },
  title: {
    type: String,
  },
  markers: {
    type: Array,
  },
})

const defaultLat = 48.21888549557031
const defaultLng = 11.625109549171704

const center = computed(() => ({
  lat: props.lat ? parseFloat(props.lat) : defaultLat,
  lng: props.lng ? parseFloat(props.lng) : defaultLng,
}))

const zoom = ref(15)
const studios = ref([])

const updateStudios = (markers) => {
  studios.value = markers.map((studio) => {
    // Get first room's data
    const firstRoom = studio.rooms && studio.rooms.length > 0 ? studio.rooms[0] : null

    // Get first photo from first room
    let photoPath = ""
    if (firstRoom && firstRoom.photos && firstRoom.photos.length > 0) {
      photoPath = firstRoom.photos[0].path
    }

    // Get first price from first room
    let price = "N/A"
    if (firstRoom && firstRoom.prices && firstRoom.prices.length > 0) {
      price = firstRoom.prices[0].total_price
    }

    return {
      id: studio.id,
      name: studio.company?.name || studio.name,
      lat: parseFloat(studio.latitude),
      lng: parseFloat(studio.longitude),
      street: studio.street,
      price: price,
      operatingHours:
        studio.operating_hours && studio.operating_hours.length > 0
          ? `${studio.operating_hours[0].open_time} - ${studio.operating_hours[0].close_time}`
          : "N/A",
      photos: photoPath,
      url: `/@${studio?.slug}`,
    }
  })
}

function mapFitBounds(mapRef, markers) {
  let bounds
  const api = mapRef.value.api
  const map = mapRef.value.map

  bounds = new api.LatLngBounds()
  for (let i = 0; i < markers.length; i++) {
    bounds.extend(new api.LatLng(markers[i].lat, markers[i].lng))
  }
  map.fitBounds(bounds)
}

onMounted(() => {
  if (props.markers) {
    updateStudios(props.markers)
  }
})

const mapRef = ref(null)

watch(
  () => mapRef.value?.ready,
  (ready) => {
    if (!ready) return
    if (props.markers && props.markers.length > 0)
      mapFitBounds(mapRef, studios.value)
  },
)

const mapOptions = computed(() => ({
  disableDefaultUI: true,
  zoomControl: false,
  mapTypeControl: false,
  scaleControl: false,
  streetViewControl: false,
  rotateControl: false,
  fullscreenControl: false,
}))

watch(
  () => props.markers,
  (newMarkers) => {
    if (newMarkers) {
      updateStudios(newMarkers)
    }
  },
  { immediate: true },
)
</script>

<template>
  <ClientOnly>
    <GoogleMap
      ref="mapRef"
      :api-key="config.public.googleMapKey"
      class="map"
      :center="center"
      :zoom="zoom"
      :styles="darkTheme"
      v-bind="mapOptions"
    >
      <MarkerCluster v-if="studios.length > 0" :options="{ position: center }">
        <MarkerList
          v-for="studio in studios"
          :key="studio.id"
          :logo="props.logo || '/logo.png'"
          :marker="studio"
        />
      </MarkerCluster>
    </GoogleMap>
  </ClientOnly>
</template>

<style>
.map {
  width: 100%;
  height: 100%;
}
.gmnoprint {
  display: none;
}
</style>

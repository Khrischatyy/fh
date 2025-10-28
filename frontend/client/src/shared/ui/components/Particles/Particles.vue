<template>
  <div
    class="fixed left-0 bottom-0 w-full pointer-events-none"
    style="height: -webkit-fill-available"
  >
    <div ref="container" class="threejs-container"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue"
import * as THREE from "three"
import Spinner from "../../common/Spinner/Spinner.vue"
const container = ref(null)
const isLoading = ref(true)
const SEPARATION = 50,
  AMOUNTX = 60,
  AMOUNTY = 30
let camera, scene, renderer
let particles = []
let count = 0

// Function to create a high-resolution canvas texture for the sprite
function createCanvasTexture() {
  const resolution = 256 // Higher resolution for smoother appearance
  const canvas = document.createElement("canvas")
  canvas.width = resolution
  canvas.height = resolution

  const context = canvas.getContext("2d")
  if (!context) {
    throw new Error("Failed to get 2D context")
  }

  // Draw a smooth circle on the canvas
  const radius = resolution / 2
  context.beginPath()
  context.arc(radius, radius, radius * 0.8, 0, Math.PI * 2, false) // Smaller radius for antialiasing margin
  context.fillStyle = "#ffffff"
  context.shadowColor = "rgba(0, 0, 0, 0.5)"
  context.shadowBlur = radius * 0.5 // Soft shadow for a smoother appearance
  context.fill()

  return new THREE.CanvasTexture(canvas)
}

const props = defineProps({
  position: {
    type: Object,
    default: () => ({ x: 0, y: 180, z: 20 }),
  },
})

function init() {
  if (!container.value) {
    console.error("Container element not found")
    return
  }

  camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    1,
    10000,
  )
  camera.position.set(props.position.x, props.position.y, props.position.z)
  camera.rotation.x = 0.35

  scene = new THREE.Scene()

  const texture = createCanvasTexture()
  const material = new THREE.SpriteMaterial({ map: texture })

  let i = 0
  for (let ix = 0; ix < AMOUNTX; ix++) {
    for (let iy = 0; iy < AMOUNTY; iy++) {
      const particle = (particles[i++] = new THREE.Sprite(material))
      particle.position.set(
        ix * SEPARATION - (AMOUNTX * SEPARATION) / 2,
        0,
        iy * SEPARATION - (AMOUNTY * SEPARATION - 10),
      )
      scene.add(particle)
    }
  }

  try {
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
    renderer.setPixelRatio(window.devicePixelRatio) // Ensure maximum quality
    renderer.setSize(window.innerWidth, window.innerHeight)
    container.value.appendChild(renderer.domElement)
  } catch (error) {
    console.error("Error creating WebGL context:", error)
    // container.value.innerHTML =
    //   "<p>WebGL not supported in your browser or graphics card. Please try a different setup.</p>"
    return
  }
}

function onWindowResize() {
  if (camera && renderer) {
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()
    renderer.setSize(window.innerWidth, window.innerHeight)
  }
}

function animate() {
  if (!renderer || !scene || !camera) return

  requestAnimationFrame(animate)

  let i = 0
  for (let ix = 0; ix < AMOUNTX; ix++) {
    for (let iy = 0; iy < AMOUNTY; iy++) {
      const particle = particles[i++]
      particle.position.y =
        Math.sin((ix + count) * 0.3) * 50 + Math.sin((iy + count) * 0.5) * 50

      // Original scale calculation with added randomness
      const baseScale =
        (Math.sin((ix + count) * 0.3) + 1) * 2 +
        (Math.sin((iy + count) * 0.5) + 1) * 2
      particle.scale.x = particle.scale.y = baseScale + Math.random() * 0.5 // Add some randomness to the scale
    }
  }

  renderer.render(scene, camera)

  count += 0.1
}

onMounted(() => {
  init()
  animate()
  window.addEventListener("resize", onWindowResize, false)
})

onUnmounted(() => {
  window.removeEventListener("resize", onWindowResize)
  // Perform any additional cleanup if necessary
})
</script>

<style>
.threejs-container {
  width: 100%;
  height: 100vh;
  /* Additional styles if needed */
}
</style>

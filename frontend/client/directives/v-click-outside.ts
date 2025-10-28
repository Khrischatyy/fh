import type { DirectiveBinding } from "vue"

interface ClickOutsideElement extends HTMLElement {
  clickOutsideEvent: (event: Event) => void
}

const clickOutsideDirective = {
  beforeMount(el: ClickOutsideElement, binding: DirectiveBinding) {
    if (typeof binding.value !== "function") {
      console.warn("v-click-outside: binding value must be a function")
      return
    }

    el.clickOutsideEvent = (event: Event) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value(event)
      }
    }
    document.body.addEventListener("click", el.clickOutsideEvent)
  },
  unmounted(el: ClickOutsideElement) {
    document.body.removeEventListener("click", el.clickOutsideEvent)
  },
}

export default clickOutsideDirective

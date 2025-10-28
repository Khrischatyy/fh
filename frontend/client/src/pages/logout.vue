<script setup lang="ts">
import {definePageMeta} from "#imports";
import {onMounted} from "vue";
import {navigateTo} from "nuxt/app";
import {useSessionStore} from "~/src/entities/Session";

definePageMeta({
  middleware: 'logout'
});
onMounted(() => {
  useSessionStore().logout();
});
</script>

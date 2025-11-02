import {defineNuxtRouteMiddleware, navigateTo} from "nuxt/app";
import {useCookie} from "#app";
import {useSessionStore, ACCESS_TOKEN_KEY} from "~/src/entities/Session";

export default defineNuxtRouteMiddleware(() => {
    const token = useCookie(ACCESS_TOKEN_KEY).value
    const sessionStore = useSessionStore();

    if(process.client) {
        sessionStore.setAuthorized(false)
        navigateTo('/login')
    }

    useCookie(ACCESS_TOKEN_KEY).value = null;

})
import { defineNuxtRouteMiddleware, navigateTo } from 'nuxt/app'
import { useCookie } from "#app";
import { ACCESS_TOKEN_KEY } from "~/src/lib/api/config";

export default defineNuxtRouteMiddleware(() => {
    const token = useCookie(ACCESS_TOKEN_KEY).value;

    if (token) {
        navigateTo('/');  // Redirect if token exists
        return false;  // Prevent further navigation
    }

    return true;  // Continue with the navigation if no token is found
});
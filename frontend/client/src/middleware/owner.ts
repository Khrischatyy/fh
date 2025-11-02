import { defineNuxtRouteMiddleware, navigateTo } from 'nuxt/app'
import { useCookie } from "#app";
import {useSessionStore, ACCESS_TOKEN_KEY} from "~/src/entities/Session";

export default defineNuxtRouteMiddleware((to, from) => {
    const token = useCookie(ACCESS_TOKEN_KEY).value;
    const brand = useSessionStore().brand;
    if (token && useSessionStore().brand && to.path === '/create') {
        //navigateTo(`/@${useSessionStore().brand}/dashboard`)
        return true;
    }else if(token && useSessionStore().userRole === 'studio_owner'){
        return true;
    }

    return true;  // Continue with the navigation if no token is found
});
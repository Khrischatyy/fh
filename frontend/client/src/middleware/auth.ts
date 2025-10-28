import { watch } from 'vue'
import { onBeforeMount } from 'vue'
import {defineNuxtRouteMiddleware, navigateTo} from 'nuxt/app'
import { useRouter } from 'vue-router'
import { useSessionStore } from '~/src/entities/Session'
import {useCookie} from "#app";
import {ACCESS_TOKEN_KEY} from "~/src/lib/api/config";
import {useApi} from "~/src/lib/api";
import type {ResponseDto} from "~/src/lib/api/types";
import type {UserRoleEnum} from "~/src/entities/@abstract/User";
type meResponse = {
    role: string;
    has_company: boolean;
    company_slug: number;
}

function getMe() {
    const api = useApi<ResponseDto<meResponse>>({ url: '/user/me', 'auth': true });

    return api.fetch();
}

export default defineNuxtRouteMiddleware(() => {
    const token = useCookie(ACCESS_TOKEN_KEY).value

        if (!token) {
            navigateTo('/login')
            return false;
        }


    return true
})
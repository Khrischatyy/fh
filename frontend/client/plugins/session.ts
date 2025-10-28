import {
    useSessionStore, USER_INFO_KEY,
    ACCESS_TOKEN_KEY, RESERVES_KEY, PAYMENT_SESSION, BRAND_KEY
} from '~/src/entities/Session/model'
import {defineNuxtPlugin, useCookie} from "#app";
import {navigateTo} from "nuxt/app";

export default defineNuxtPlugin(nuxtApp => {
    nuxtApp.hook('app:beforeMount', async () => {
        if(process.client) {
            const sessionStore = useSessionStore();
            // Check for reservations and payment session in cookies or initiate them if needed
            const reservesCookie = useCookie(RESERVES_KEY);
            const paymentSessionCookie = useCookie(PAYMENT_SESSION);

            if (reservesCookie.value) {
                sessionStore.setReservations(reservesCookie.value);
            }

            if (paymentSessionCookie.value) {
                sessionStore.setPaymentSession(paymentSessionCookie.value);
            }

            // Fetch user info if access token is available
            if (sessionStore.accessToken) {
                await sessionStore.fetchUserInfo().then((response) => {
                    if(!response?.role && process.client){
                        navigateTo('/settings/role')
                        return
                    }
                });
            } else {
                sessionStore.setAuthorized(false);
            }
        }
    });
});
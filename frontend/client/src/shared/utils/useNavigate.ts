import {navigateTo} from "nuxt/app";

export function useNavigate() {
    function goToLogin() {
        navigateTo('/login');
    }

    return { goToLogin };
}
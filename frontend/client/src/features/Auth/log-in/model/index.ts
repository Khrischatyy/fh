import { useSessionStore } from '~/src/entities/Session/model'
import { login } from '../api'
import { ref } from 'vue'

export const useAuthorization = () => {
    const model = ref<{
        login: string,
        password: string,
        rememberMe: boolean
    }>({
        login: '',
        password: '',
        rememberMe: false
    })

    const sessionStore = useSessionStore()

    const isLoading = ref<boolean>(false)

    const authorize = async () => {
        isLoading.value = true

        const {
            data: response,
        } = await login(model.value)

        if (response.value) {
            const userInfo = response.value?.data.firstname + ' ' + response.value?.data.lastname

            sessionStore.setAccessToken(response.value.data.token)
            sessionStore.setUserInfo(userInfo)
            sessionStore.setAuthorized(true)
        }

        isLoading.value = false

        return { data: response.value }
    }

    const resetData = () => {
        model.value.login = ''
        model.value.password = ''
        model.value.rememberMe = false
    }

    return {
        model,
        isLoading,
        resetData,
        authorize
    }
}

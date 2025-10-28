import {useApi} from "~/src/lib/api";
import {ref} from "#imports";

export type Teammate = {
    id: number
    role: string
    username: string
    phone: string
    email: string
    booking_count: number
    address: string
    profile_photo: string
}
export function useTeammates() {
    const teammates = ref([])
    const isLoading = ref(false)
    const getTeammates = async (address_id: number) => {
        isLoading.value = true
        const {fetch: fetchTeammates} = useApi({
            url: `/address/${address_id}/staff`,
            auth: true,
        })

        if (!address_id) {
            isLoading.value = false
            return
        }
        fetchTeammates().then((response) => {
            teammates.value = response?.data
            isLoading.value = false
        })
    }

    return {getTeammates, teammates, isLoading}
}
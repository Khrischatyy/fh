import { useNuxtApp } from '#app';
import {useApi} from "~/src/lib/api";

interface SideMenuResponse {
    success: boolean;
    data: Record<string, any>;
    message: string;
    code: number;
}

export const getSideMenu = async () => {
    const { fetch } = useApi<SideMenuResponse>({
        url: '/menu',
        auth: true
    })
    const response = await fetch();
    return response;
}
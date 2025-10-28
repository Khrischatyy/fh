import {useApi} from "~/src/lib/api";

export interface City {
    id: number;
    name: string;
}

export interface GetCityResponse {
    success: boolean;
    data: City[];
    message: string;
    code: number;
}

export const getCities = async (countryId: string) => {
    const { fetch } = useApi<GetCityResponse>({
        url: `/countries/${countryId}/cities`,
        auth: true
    })

    const response = await fetch()
    return response ? response.data : []
}
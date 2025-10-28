import {useApi} from "~/src/lib/api";
import {filterUnassigned} from "~/src/shared/utils";

export interface Badge {
    id: number;
    name: string;
    image: string;
}

export interface Company {
    id: number;
    name: string;
    logo: string;
    slug: string;
    founding_date: string;
    rating: string;
}

export interface Studio {
    id: number;
    latitude: string;
    longitude: string;
    street: string;
    created_at: string;
    updated_at: string;
    city_id: number;
    company_id: number;
    photos: {
        address_id: number,
        path: string,
        index: number,
        url: string,
    }
    company: Company;
    badges: Badge[];
}

interface GetStudiosResponse {
    success: boolean;
    data: Studio[];
    message: string;
    code: number;
}

export const getMyStudios = async () => {
    const { fetch } = useApi<GetStudiosResponse>({
        url: `my-studios`,
        auth: true
    })

    const response = await fetch()
    return response ? response.data : []
}

export const getMyStudiosFilter = async (filterShow) => {
    const body = filterShow.reduce((acc, filter) => {
        acc[filter.key] = filter.value;
        return acc;
    }, {});

    const { post } = useApi<GetStudiosResponse>({
        url: `my-studios/filter`,
        auth: true
    })

    const response = await post(filterUnassigned(body))
    return response ? response.data : []
}

export const getCities = async () => {

    const { fetch } = useApi<GetStudiosResponse>({
        url: `my-studios/cities`,
        auth: true
    })

    const response = await fetch()
    return response ? response.data : []
}
import {useApi} from "~/src/lib/api";

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
    addresses: any[];
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
    prices: Prices[];
    operating_hours: OperatingHours[];
}

interface OperatingHours {
    id: number;
    address_id: number;
    mode_id: number;
    day_of_week: number | null;
    open_time: string;
    close_time: string;
    is_closed: boolean;
}

interface Prices {
    address_id: number;
    hours: string;
    id: number;
    is_enabled: boolean;
    price_per_hour: string;
    total_price: string;
}

interface GetStudiosResponse {
    success: boolean;
    data: Studio[];
    message: string;
    code: number;
}

export const getStudios = async (cityId: string) => {
    const { fetch } = useApi<GetStudiosResponse>({
        url: `/city/${cityId}/studios`,
        auth: true
    })

    const response = await fetch()
    return response ? response.data : []
}

import { Ref } from 'vue';
import {useApi} from "~/src/lib/api";
import {useAsyncData} from "#app";

export type  BrandFull = {
    id: number,
    name: string,
    logo: string,
    slug: string,
    founding_date: string,
    rating: string,
    created_at: string,
    updated_at: string,
    logo_url: string,
    addresses: {
        id: number,
        latitude: string,
        longitude: string,
        street: string,
        created_at: string,
        updated_at: string,
        city_id: number,
        company_id: number,
        badges: {
            id: number,
            name: string,
            image: string,
            description: string,
            image_url: string,
            pivot: {
                address_id: number,
                badge_id: number
            }
        }[]
    }[]
}
export type ResponseBrandFull = {
    success: boolean,
    data: BrandFull,
    code: number,
    message: string
}
export function useBrand(slug: Ref<string> | string) {
    const resolvedSlug = typeof slug === 'string' ? slug : slug.value;

    const { fetch: getBrand } = useApi<ResponseBrandFull>({
        url: `/company/${resolvedSlug}`,
        auth: true
    });

    //useAsyncData helps to serve it server-side
    const { data: brand, pending, error } = useAsyncData<BrandFull>('brand', async () => {
        const response = await getBrand();
        return response?.data; // Assuming 'data' contains the desired BrandFull object
    });

    return { brand, pending, error };
}
import {useApi} from "~/src/lib/api";

export interface Country {
  id: number;
  name: string;
}

export interface GetCountriesResponse {
  success: boolean;
  data: Country[];
  message: string;
  code: number;
}

export const getCountries = async () => {
  const { fetch } = useApi<GetCountriesResponse>({
    url: '/countries'
  })

  const response = await fetch()
  return response ? response.data : []
}
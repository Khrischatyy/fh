import { ACCESS_TOKEN_KEY } from "./config"
import { computed, ref } from "vue"
import { useCookie, useRuntimeConfig } from "#app"
import { ErrorHandler } from "~/src/shared/utils/"

interface FetchOptions {
  baseURL: string
  headers: Record<string, string>
}

interface RequestOptions {
  method: "GET" | "POST" | "PUT" | "DELETE"
  params?: Record<string, any>
  body?: any
}

interface ApiResponse<T> {
  data: T
  message: string
  status: number
  errors?: Record<string, any>
}

interface ApiError {
  status: number
  message: string
  errors?: Record<string, any>
}

export function useApi<ResponseT, MappedResponseT = ResponseT>({
  url,
  options,
  token = useCookie(ACCESS_TOKEN_KEY).value,
  auth = false,
}: {
  url: (() => string) | string
  options?: { transformResponse?: (data: ResponseT) => MappedResponseT }
  token?: string | null | undefined
  auth?: boolean
}) {
  const config = useRuntimeConfig()
  const apiBase = process.client
    ? config.public.apiBaseClient
    : config.public.apiBase

  const urlPath = computed<string>(() => {
    return typeof url === "function" ? url() : url
  })

  const fetchOptions = ref<FetchOptions>({
    baseURL: apiBase,
    headers: { accept: "application/json" },
  })

  if (auth) {
    const sessionCookie = useCookie(ACCESS_TOKEN_KEY)
    //const token = sessionCookie.value;
    if (token) {
      fetchOptions.value.headers.Authorization = `Bearer ${decodeURIComponent(
        token,
      )}`
    }
  }

  const makeRequest = async (
    requestOptions: RequestOptions,
  ): Promise<MappedResponseT | null> => {
    try {
      const response = await $fetch<ApiResponse<ResponseT>>(urlPath.value, {
        ...fetchOptions.value,
        ...requestOptions,
      })
      if (options?.transformResponse) {
        return options.transformResponse(response.data)
      }
      return response as MappedResponseT // Call handleResponse here
    } catch (error) {
      await ErrorHandler.handleApiError(error)
      throw error // Rethrow the error to maintain promise chain integrity
    }
  }

  return {
    fetch: (requestOptions?: RequestOptions) =>
      makeRequest({ ...requestOptions, method: "GET" }),
    post: (data: any, requestOptions?: RequestOptions) =>
      makeRequest({ ...requestOptions, method: "POST", body: data }),
    put: (data: any, requestOptions?: RequestOptions) =>
      makeRequest({ ...requestOptions, method: "PUT", body: data }),
    delete: (requestOptions?: RequestOptions) =>
      makeRequest({ ...requestOptions, method: "DELETE" }),
  }
}

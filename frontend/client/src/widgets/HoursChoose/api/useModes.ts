import type { ResponseDto } from "~/src/lib/api/types"
import { useApi } from "~/src/lib/api"

export type Mode = {
  id: number
  mode: string
  description: string
}

export const getModes = async (): Promise<ResponseDto<any> | null> => {
  const { fetch } = useApi<ResponseDto<Mode[]>>({
    url: "/operation-modes",
    auth: true,
  })
  const response = await fetch()
  return response
}

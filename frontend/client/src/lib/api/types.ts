export type ResponseDto<T> = {
    success: boolean,
    data: T,
    message: string,
    code: number
}
// Compare this snippet from frontend/client/src/entities/Studio/api/useStudio.ts:
export type ResponseErrorDto = {
    success: boolean,
    message: string,
    code: number
}
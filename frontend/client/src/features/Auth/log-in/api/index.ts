import { type ResponseDto, useApi } from 'shared/lib/api'
import { UserRoleEnum } from 'entities/@abstract/User'

export type LoginRequestDto = {
    login: string,
    password: string,
    rememberMe: boolean
}

export type LoginResponseDto = ResponseDto<{
    id: number,
    firstname: string,
    lastname: string,
    token: string,
    role: UserRoleEnum,
}>

export const login = (data: LoginRequestDto) => {
	return useApi<LoginResponseDto>({
		url: '/api/login',
		options: {
			method: 'post',
			body: {
				login: data.login,
				password: data.password,
			},
			watch: false
		},
		auth: true
	})
}

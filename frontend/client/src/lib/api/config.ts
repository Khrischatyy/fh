export const ACCESS_TOKEN_KEY = 'access-token-key'

export class UnauthenticatedError extends Error {
    constructor(message: string) {
        super(message)
        this.name = 'UnauthenticatedError'
    }
}

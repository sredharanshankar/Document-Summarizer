export class ApiError extends Error {
  readonly code: string
  readonly status: number

  constructor(status: number, code: string, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

export class NetworkError extends Error {
  constructor() {
    super('We could not reach the server. Check your connection and try again.')
    this.name = 'NetworkError'
  }
}

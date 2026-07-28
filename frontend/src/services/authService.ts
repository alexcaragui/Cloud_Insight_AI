import { apiService } from './apiService'

export type AuthUser = {
  name: string
  roles: string[]
  defaultTheme: 'dark' | 'light'
}

export type AuthCredentials = {
  email: string
  password: string
}

const USER_KEY = 'auth_user'

export const authService = {
  async login(credentials: AuthCredentials): Promise<AuthUser> {
    const { token, user } = await apiService.post<{ token: string; user: AuthUser }>(
      '/auth/login',
      credentials,
    )
    localStorage.setItem('token', token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    return user
  },

  logout(): void {
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem('token')
  },

  getStoredUser(): AuthUser | null {
    try {
      const raw = localStorage.getItem(USER_KEY)
      return raw ? (JSON.parse(raw) as AuthUser) : null
    } catch {
      return null
    }
  },
}

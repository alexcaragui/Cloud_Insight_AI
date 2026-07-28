import { apiService } from './apiService'

export const themeService = {
  setTheme(theme: 'dark' | 'light'): Promise<void> {
    return apiService.patch('/user/theme', { theme })
  },
}

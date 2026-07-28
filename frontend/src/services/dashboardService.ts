import { apiService } from './apiService'

export const dashboardService = {
  getDashboard(): Promise<string> {
    return apiService.get<string>('/dashboard')
  },
}

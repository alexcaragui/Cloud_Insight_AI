import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15_000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('auth_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

const unwrap = <T>(res: AxiosResponse<T>): T => res.data

export const apiService = {
  get<T>(url: string, config?: AxiosRequestConfig) {
    return api.get<T>(url, config).then(unwrap)
  },
  post<T>(url: string, data?: unknown, config?: AxiosRequestConfig) {
    return api.post<T>(url, data, config).then(unwrap)
  },
  put<T>(url: string, data?: unknown, config?: AxiosRequestConfig) {
    return api.put<T>(url, data, config).then(unwrap)
  },
  patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig) {
    return api.patch<T>(url, data, config).then(unwrap)
  },
  delete<T>(url: string, config?: AxiosRequestConfig) {
    return api.delete<T>(url, config).then(unwrap)
  },
}

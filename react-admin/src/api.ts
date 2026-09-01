import type { Brand, BrandPayload, CarModel, CarModelPayload, TokenResponse } from './types'

const tokenKey = 'vehicle-admin-token'
export const clearToken = () => localStorage.removeItem(tokenKey)
export const hasToken = () => Boolean(localStorage.getItem(tokenKey))
const request = async <T,>(path: string, options: RequestInit = {}, protectedRoute = false): Promise<T> => {
  const headers = new Headers(options.headers)
  headers.set('Content-Type', 'application/json')
  if (protectedRoute) headers.set('Authorization', `Bearer ${localStorage.getItem(tokenKey) ?? ''}`)
  const response = await fetch(`/api${path}`, { ...options, headers })
  if (!response.ok) {
    if (response.status === 401) clearToken()
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ?? '请求失败，请稍后重试')
  }
  return response.status === 204 ? undefined as T : response.json() as Promise<T>
}
export const login = async (username: string, password: string) => {
  const result = await request<TokenResponse>('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) })
  localStorage.setItem(tokenKey, result.access_token)
}
export const listBrands = () => request<Brand[]>('/brands')
export const saveBrand = (value: BrandPayload, id?: number) => request<Brand>(id ? `/brands/${id}` : '/brands', { method: id ? 'PUT' : 'POST', body: JSON.stringify(value) }, true)
export const removeBrand = (id: number) => request<void>(`/brands/${id}`, { method: 'DELETE' }, true)
export const listModels = (brandId?: number) => request<CarModel[]>(`/car-models${brandId ? `?brand_id=${brandId}` : ''}`)
export const saveModel = (value: CarModelPayload, id?: number) => request<CarModel>(id ? `/car-models/${id}` : '/car-models', { method: id ? 'PUT' : 'POST', body: JSON.stringify(value) }, true)
export const removeModel = (id: number) => request<void>(`/car-models/${id}`, { method: 'DELETE' }, true)

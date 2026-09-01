export interface Brand { id: number; name: string; country: string; description: string | null }
export interface BrandPayload { name: string; country: string; description: string | null }
export interface CarModel { id: number; name: string; year: number; price: string | number; brand_id: number }
export interface CarModelPayload { name: string; year: number; price: number; brand_id: number }
interface TokenResponse { access_token: string; token_type: string }
export type { TokenResponse }

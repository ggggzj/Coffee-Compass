import { ShopFeatures, SuitabilityScore } from '@/lib/scoring'

export interface Shop {
  id: string
  name: string
  address: string
  city: string
  latitude: number
  longitude: number
  rating: number
  priceLevel: number
  tags: string[]
  features: ShopFeatures
  suitability?: SuitabilityScore | null
  distance?: number // in meters
  isOpen?: boolean
  createdAt: string
}

export interface ShopWithDistance extends Shop {
  distance: number
  isOpen: boolean
}


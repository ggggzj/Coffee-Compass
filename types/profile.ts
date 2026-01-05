import { Shop } from './shop'

export interface Review {
  id: string
  shopId: string
  shopName: string
  userId: string
  ratings: {
    noise: number
    outlets: number
    wifi: number
    seating: number
    lighting: number
    privacy: number
    busyness: number
  }
  text?: string
  createdAt: string
}

export interface VisitHistory {
  id: string
  shopId: string
  shopName: string
  visitedAt: string
}

export interface UserPreference {
  prefersQuiet: boolean
  prefersNaturalLight: boolean
  prefersLargeTables: boolean
  prefersOutlets: boolean
  prefersFastWifi: boolean
  preferredPriceLevel: number
  preferredScenes: string[]
}

export interface WeeklyRecommendation {
  scene: string
  shops: Shop[]
}


import { Shop } from './shop'
import { Review } from './profile'

export type ShopStatus = 'pending' | 'approved' | 'rejected'

export interface AdminShop extends Shop {
  status: ShopStatus
  submittedAt: string
  submittedBy?: string
}

export interface Report {
  id: string
  type: 'review' | 'shop' | 'user'
  targetId: string
  targetName: string
  reason: string
  reportedBy: string
  reportedAt: string
  status: 'pending' | 'resolved' | 'dismissed'
}

export interface Metrics {
  dailyActiveUsers: number[]
  searchToClickRate: number
  favoriteRate: number
  apiLatency: number
  errorRate: number
}

export interface AdminMetrics {
  dau: number[]
  dauLabels: string[]
  searchToClickRate: number
  favoriteRate: number
  apiLatency: number
  errorRate: number
}


'use client'

import { useQuery } from '@tanstack/react-query'
import ShopCard from './ShopCard'
import type { Shop } from '@/types/shop'

interface ResultsListProps {
  city: string
  scene: string
  sort: string
  bounds: string | null
  onShopClick: (shopId: string) => void
  onShopHover: (shopId: string | null) => void
  hoveredShopId: string | null
}

async function fetchShops(city: string, scene: string, sort: string, bounds: string | null) {
  const params = new URLSearchParams()
  params.set('city', city)
  params.set('scene', scene)
  params.set('sort', sort)
  if (bounds) {
    params.set('bounds', bounds)
  }
  params.set('page', '1')
  params.set('pageSize', '50')

  const response = await fetch(`/api/shops?${params.toString()}`)
  if (!response.ok) {
    throw new Error('Failed to fetch shops')
  }
  return response.json()
}

export default function ResultsList({
  city,
  scene,
  sort,
  bounds,
  onShopClick,
  onShopHover,
  hoveredShopId,
}: ResultsListProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['shops', city, scene, sort, bounds],
    queryFn: () => fetchShops(city, scene, sort, bounds),
  })

  if (isLoading) {
    return (
      <div className="p-4 space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="animate-pulse border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <div className="flex-1">
                <div className="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
              <div className="h-8 w-12 bg-gray-200 rounded"></div>
            </div>
            <div className="h-2 bg-gray-200 rounded mb-3"></div>
            <div className="flex gap-4 mb-3">
              <div className="h-4 bg-gray-200 rounded w-12"></div>
              <div className="h-4 bg-gray-200 rounded w-16"></div>
              <div className="h-4 bg-gray-200 rounded w-20"></div>
            </div>
            <div className="flex gap-2">
              <div className="h-6 bg-gray-200 rounded-full w-20"></div>
              <div className="h-6 bg-gray-200 rounded-full w-24"></div>
              <div className="h-6 bg-gray-200 rounded-full w-16"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 text-red-600">
        Failed to load, please try again later
      </div>
    )
  }

  const shops = data?.shops || []

  return (
    <div className="p-4 space-y-4">
      {shops.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          No coffee shops found
        </div>
      ) : (
        shops.map((shop: Shop) => (
          <ShopCard
            key={shop.id}
            shop={shop}
            scene={scene}
            onClick={() => onShopClick(shop.id)}
            onHover={() => onShopHover(shop.id)}
            onLeave={() => onShopHover(null)}
            isHovered={hoveredShopId === shop.id}
          />
        ))
      )}
    </div>
  )
}


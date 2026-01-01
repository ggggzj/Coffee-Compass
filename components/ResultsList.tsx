'use client'

import { useQuery } from '@tanstack/react-query'
import ShopCard from './ShopCard'

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
          <div key={i} className="animate-pulse">
            <div className="h-32 bg-gray-200 rounded-lg"></div>
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
        shops.map((shop: any) => (
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


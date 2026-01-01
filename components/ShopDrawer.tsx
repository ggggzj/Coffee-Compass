'use client'

import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
// Icons as simple SVG components
const XIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    strokeWidth={1.5}
    stroke="currentColor"
    className={className}
  >
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
  </svg>
)

const HeartIcon = ({ className, filled }: { className?: string; filled?: boolean }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill={filled ? 'currentColor' : 'none'}
    viewBox="0 0 24 24"
    strokeWidth={1.5}
    stroke="currentColor"
    className={className}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.312-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"
    />
  </svg>
)

interface ShopDrawerProps {
  shopId: string
  scene: string
  onClose: () => void
}

async function fetchShop(shopId: string, scene: string) {
  const params = new URLSearchParams()
  params.set('scene', scene)
  const response = await fetch(`/api/shops/${shopId}?${params.toString()}`)
  if (!response.ok) {
    throw new Error('Failed to fetch shop')
  }
  return response.json()
}

function getFavorites(): string[] {
  if (typeof window === 'undefined') return []
  const favorites = localStorage.getItem('coffeecompass-favorites')
  return favorites ? JSON.parse(favorites) : []
}

function saveFavorites(favorites: string[]) {
  if (typeof window === 'undefined') return
  localStorage.setItem('coffeecompass-favorites', JSON.stringify(favorites))
}

export default function ShopDrawer({ shopId, scene, onClose }: ShopDrawerProps) {
  const [isFavorite, setIsFavorite] = useState(false)

  const { data: shop, isLoading } = useQuery({
    queryKey: ['shop', shopId, scene],
    queryFn: () => fetchShop(shopId, scene),
  })

  useEffect(() => {
    if (shop) {
      const favorites = getFavorites()
      setIsFavorite(favorites.includes(shop.id))
    }
  }, [shop])

  const handleToggleFavorite = () => {
    if (!shop) return
    const favorites = getFavorites()
    if (isFavorite) {
      const newFavorites = favorites.filter((id) => id !== shop.id)
      saveFavorites(newFavorites)
      setIsFavorite(false)
    } else {
      saveFavorites([...favorites, shop.id])
      setIsFavorite(true)
    }
  }

  if (isLoading) {
    return (
      <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl z-50 overflow-y-auto">
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!shop) {
    return null
  }

  const priceSymbols = '$'.repeat(shop.priceLevel)
  const features = shop.features as any
  const suitability = shop.suitability

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl z-50 overflow-y-auto">
      <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-900">咖啡店详情</h2>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
        >
          <XIcon className="w-5 h-5" />
        </button>
      </div>

      <div className="p-6 space-y-6">
        <div>
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-2xl font-bold text-gray-900">{shop.name}</h3>
            <button
              onClick={handleToggleFavorite}
              className={`p-2 rounded-full transition-colors ${
                isFavorite
                  ? 'text-red-500 hover:bg-red-50'
                  : 'text-gray-400 hover:bg-gray-100'
              }`}
            >
              <HeartIcon className="w-6 h-6" filled={isFavorite} />
            </button>
          </div>
          <p className="text-gray-600">{shop.address}</p>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <span className="text-yellow-500 text-xl">★</span>
            <span className="text-lg font-semibold text-gray-900">{shop.rating.toFixed(1)}</span>
          </div>
          <div className="text-gray-600 text-lg">{priceSymbols}</div>
        </div>

        {shop.tags && shop.tags.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">标签</h4>
            <div className="flex flex-wrap gap-2">
              {shop.tags.map((tag: string) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {suitability && (
          <div className="border-t border-gray-200 pt-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">
              适用性评分: {suitability.score}/100
            </h4>
            <p className="text-sm text-gray-600 mb-4">
              场景: <span className="font-medium">{scene}</span>
            </p>

            <div className="space-y-3">
              <h5 className="text-sm font-medium text-gray-700">评分明细:</h5>
              {suitability.breakdown.map((item: any, index: number) => (
                <div key={index} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-700 capitalize">{item.feature}</span>
                    <span className="text-gray-600">
                      {item.contribution.toFixed(1)}% (权重: {(item.weight * 100).toFixed(0)}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${item.contribution}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="border-t border-gray-200 pt-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">设施详情</h4>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-600">噪音:</span>
              <span className="ml-2 font-medium">{features.noise}/5</span>
            </div>
            <div>
              <span className="text-gray-600">插座:</span>
              <span className="ml-2 font-medium">{features.outlets}/5</span>
            </div>
            <div>
              <span className="text-gray-600">WiFi:</span>
              <span className="ml-2 font-medium">{features.wifi}/5</span>
            </div>
            <div>
              <span className="text-gray-600">座位:</span>
              <span className="ml-2 font-medium">{features.seating}/5</span>
            </div>
            <div>
              <span className="text-gray-600">照明:</span>
              <span className="ml-2 font-medium">{features.lighting}/5</span>
            </div>
            <div>
              <span className="text-gray-600">隐私:</span>
              <span className="ml-2 font-medium">{features.privacy}/5</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}


'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { Shop } from '@/types/shop'

const HeartIcon = ({ filled }: { filled?: boolean }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill={filled ? 'currentColor' : 'none'}
    viewBox="0 0 24 24"
    strokeWidth={1.5}
    stroke="currentColor"
    className="w-5 h-5"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.312-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"
    />
  </svg>
)

async function checkFavorite(shopId: string) {
  const response = await fetch('/api/favorites')
  if (!response.ok) return false
  const data = await response.json()
  return data.favorites?.some((fav: any) => fav.shopId === shopId) || false
}

async function toggleFavorite(shopId: string, isFavorite: boolean) {
  if (isFavorite) {
    await fetch(`/api/favorites?shopId=${shopId}`, { method: 'DELETE' })
  } else {
    await fetch('/api/favorites', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ shopId }),
    })
  }
}

interface ShopCardProps {
  shop: Shop
  scene: string
  onClick: () => void
  onHover: () => void
  onLeave: () => void
  isHovered: boolean
}

export default function ShopCard({
  shop,
  scene,
  onClick,
  onHover,
  onLeave,
  isHovered,
}: ShopCardProps) {
  const { data: session } = useSession()
  const queryClient = useQueryClient()
  const [isFavorite, setIsFavorite] = useState(false)
  const priceSymbols = '$'.repeat(shop.priceLevel)

  useEffect(() => {
    if (session) {
      checkFavorite(shop.id).then(setIsFavorite)
    }
  }, [shop.id, session])

  const favoriteMutation = useMutation({
    mutationFn: () => toggleFavorite(shop.id, isFavorite),
    onSuccess: () => {
      setIsFavorite(!isFavorite)
      queryClient.invalidateQueries({ queryKey: ['favorites'] })
    },
  })

  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (!session) {
      window.location.href = '/auth/signin'
      return
    }
    favoriteMutation.mutate()
  }

  // Format distance
  const formatDistance = (meters?: number): string => {
    if (!meters) return ''
    if (meters < 1000) {
      return `${Math.round(meters)}m`
    }
    return `${(meters / 1000).toFixed(1)}km`
  }

  // Get tag display names
  const getTagDisplayName = (tag: string): string => {
    const tagMap: Record<string, string> = {
      wifi: 'Fast WiFi',
      outlets: 'Outlets',
      quiet: 'Quiet',
      'good lighting': 'Good Lighting',
      'private seating': 'Comfortable Seating',
      'good for conversation': 'Good for Conversation',
    }
    return tagMap[tag] || tag
  }

  return (
    <div
      onClick={onClick}
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
      className={`p-4 border rounded-lg cursor-pointer transition-all ${
        isHovered
          ? 'border-blue-500 shadow-lg bg-blue-50'
          : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
      }`}
    >
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-lg text-gray-900">{shop.name}</h3>
            {shop.isOpen !== undefined && (
              <span
                className={`text-xs px-2 py-0.5 rounded-full ${
                  shop.isOpen
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                }`}
              >
                {shop.isOpen ? 'Open' : 'Closed'}
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600">{shop.address}</p>
        </div>
        <div className="flex flex-col items-end gap-2 ml-4">
          {session && (
            <button
              onClick={handleFavoriteClick}
              disabled={favoriteMutation.isPending}
              className={`p-1.5 rounded-full transition-colors ${
                isFavorite
                  ? 'text-red-500 hover:bg-red-50'
                  : 'text-gray-400 hover:bg-gray-100'
              } disabled:opacity-50`}
              title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
            >
              <HeartIcon filled={isFavorite} />
            </button>
          )}
          {shop.suitability && (
            <div className="flex flex-col items-end gap-1">
              <span className="text-xs font-medium text-gray-600">Suitability</span>
              <span className="text-2xl font-bold text-blue-600">{shop.suitability.score}</span>
            </div>
          )}
        </div>
      </div>

      {/* Suitability Bar */}
      {shop.suitability && (
        <div className="mb-3">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${shop.suitability.score}%` }}
            />
          </div>
        </div>
      )}

      {/* Rating, Price, Distance */}
      <div className="flex items-center gap-4 text-sm mb-3">
        <div className="flex items-center gap-1">
          <span className="text-yellow-500">★</span>
          <span className="text-gray-700 font-medium">{shop.rating.toFixed(1)}</span>
        </div>
        <div className="text-gray-600 font-medium">{priceSymbols}</div>
        {shop.distance !== undefined && (
          <div className="text-gray-500 text-xs">
            {formatDistance(shop.distance)} away
          </div>
        )}
      </div>

      {/* Tags */}
      {shop.tags && shop.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {shop.tags.slice(0, 4).map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded-full"
            >
              {getTagDisplayName(tag)}
            </span>
          ))}
          {shop.tags.length > 4 && (
            <span className="px-2 py-0.5 text-gray-500 text-xs">
              +{shop.tags.length - 4} more
            </span>
          )}
        </div>
      )}
    </div>
  )
}


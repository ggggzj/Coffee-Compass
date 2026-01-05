'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import type { Shop } from '@/types/shop'

interface FavoriteWithShop {
  id: string
  shopId: string
  createdAt: string
  shop: Shop
}

export default function FavoritesList() {
  const { data: session } = useSession()
  const [favorites, setFavorites] = useState<FavoriteWithShop[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!session) {
      setIsLoading(false)
      return
    }

    fetch('/api/favorites')
      .then((res) => res.json())
      .then((data) => {
        setFavorites(data.favorites || [])
        setIsLoading(false)
      })
      .catch((error) => {
        console.error('Error fetching favorites:', error)
        setIsLoading(false)
      })
  }, [session])

  const handleRemoveFavorite = async (shopId: string) => {
    try {
      const response = await fetch(`/api/favorites?shopId=${shopId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        setFavorites(favorites.filter((fav) => fav.shopId !== shopId))
      }
    } catch (error) {
      console.error('Error removing favorite:', error)
    }
  }

  if (!session) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Favorites</h2>
        <p className="text-gray-500 text-center py-8">
          Please sign in to view your favorites
        </p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Favorites</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="animate-pulse border border-gray-200 rounded-lg p-4">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (favorites.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Favorites</h2>
        <p className="text-gray-500 text-center py-8">No favorite coffee shops yet</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Favorites</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {favorites.map((favorite) => {
          const shop = favorite.shop
          return (
            <div
              key={favorite.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{shop.name}</h3>
                  <p className="text-sm text-gray-600">{shop.address}</p>
                </div>
                <button
                  onClick={() => handleRemoveFavorite(shop.id)}
                  className="ml-4 text-red-500 hover:text-red-700 transition-colors"
                  title="Remove from favorites"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                    className="w-5 h-5"
                  >
                    <path d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.312-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                  </svg>
                </button>
              </div>
              <div className="flex items-center gap-3 mt-2 text-sm">
                <div className="flex items-center gap-1">
                  <span className="text-yellow-500">★</span>
                  <span className="text-gray-700">{shop.rating.toFixed(1)}</span>
                </div>
                <div className="text-gray-600">{'$'.repeat(shop.priceLevel)}</div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}


'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import type { Shop } from '@/types/shop'
import type { UserPreference } from '@/types/profile'

interface FavoriteWithShop {
  id: string
  shopId: string
  shop: Shop
}

function derivePreferences(favoriteShops: Shop[]): UserPreference {
  if (favoriteShops.length === 0) {
    return {
      prefersQuiet: false,
      prefersNaturalLight: false,
      prefersLargeTables: false,
      prefersOutlets: false,
      prefersFastWifi: false,
      preferredPriceLevel: 3,
      preferredScenes: [],
    }
  }

  const avgNoise =
    favoriteShops.reduce((sum, shop) => sum + (shop.features as any).noise, 0) /
    favoriteShops.length
  const avgLighting =
    favoriteShops.reduce((sum, shop) => sum + (shop.features as any).lighting, 0) /
    favoriteShops.length
  const avgSeating =
    favoriteShops.reduce((sum, shop) => sum + (shop.features as any).seating, 0) /
    favoriteShops.length
  const avgOutlets =
    favoriteShops.reduce((sum, shop) => sum + (shop.features as any).outlets, 0) /
    favoriteShops.length
  const avgWifi =
    favoriteShops.reduce((sum, shop) => sum + (shop.features as any).wifi, 0) /
    favoriteShops.length
  const avgPriceLevel =
    favoriteShops.reduce((sum, shop) => sum + shop.priceLevel, 0) / favoriteShops.length

  return {
    prefersQuiet: avgNoise <= 2.5,
    prefersNaturalLight: avgLighting >= 4,
    prefersLargeTables: avgSeating >= 4,
    prefersOutlets: avgOutlets >= 4,
    prefersFastWifi: avgWifi >= 4,
    preferredPriceLevel: Math.round(avgPriceLevel),
    preferredScenes: ['Study', 'Remote Work'], // Mock for now
  }
}

export default function PreferenceCard() {
  const { data: session } = useSession()
  const [preferences, setPreferences] = useState<UserPreference | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!session) {
      setIsLoading(false)
      return
    }

    fetch('/api/favorites')
      .then((res) => res.json())
      .then((data) => {
        const favorites: FavoriteWithShop[] = data.favorites || []
        const shops = favorites.map((fav) => fav.shop)
        setPreferences(derivePreferences(shops))
        setIsLoading(false)
      })
      .catch((error) => {
        console.error('Error fetching shops for preferences:', error)
        setIsLoading(false)
      })
  }, [session])

  if (!preferences) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Preferences</h2>
        <p className="text-gray-500 text-sm">Add favorites to see your preferences</p>
      </div>
    )
  }

  const preferenceChips = [
    preferences.prefersQuiet && { label: 'Quiet Places', color: 'bg-blue-100 text-blue-800' },
    preferences.prefersNaturalLight && { label: 'Natural Light', color: 'bg-yellow-100 text-yellow-800' },
    preferences.prefersLargeTables && { label: 'Large Tables', color: 'bg-green-100 text-green-800' },
    preferences.prefersOutlets && { label: 'Plenty of Outlets', color: 'bg-purple-100 text-purple-800' },
    preferences.prefersFastWifi && { label: 'Fast WiFi', color: 'bg-indigo-100 text-indigo-800' },
  ].filter(Boolean) as Array<{ label: string; color: string }>

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Preference Profile</h2>
      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-600 mb-2">Based on your favorites, you prefer:</p>
          <div className="flex flex-wrap gap-2">
            {preferenceChips.length > 0 ? (
              preferenceChips.map((chip, index) => (
                <span
                  key={index}
                  className={`px-3 py-1 rounded-full text-xs font-medium ${chip.color}`}
                >
                  {chip.label}
                </span>
              ))
            ) : (
              <span className="text-sm text-gray-500">No strong preferences detected</span>
            )}
          </div>
        </div>
        <div className="pt-4 border-t border-gray-100">
          <p className="text-sm text-gray-600">
            Preferred price level: <span className="font-medium">{'$'.repeat(preferences.preferredPriceLevel)}</span>
          </p>
        </div>
      </div>
    </div>
  )
}


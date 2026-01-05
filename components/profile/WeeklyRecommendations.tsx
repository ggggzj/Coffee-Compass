'use client'

import { useQuery } from '@tanstack/react-query'
import { useSession } from 'next-auth/react'
import type { Shop } from '@/types/shop'
import Link from 'next/link'

interface Recommendation {
  scene: string
  shops: (Shop & {
    suitability: { score: number; breakdown: any[] }
    recommendationScore: number
    matchCount: number
  })[]
}

interface RecommendationsResponse {
  recommendations: Recommendation[]
  userPreferences: {
    prefersQuiet: boolean
    prefersNaturalLight: boolean
    prefersLargeTables: boolean
    prefersOutlets: boolean
    prefersFastWifi: boolean
    preferredPriceLevel: number
    preferredScenes: string[]
  }
  stats: {
    favoritesCount: number
    visitsCount: number
  }
}

async function fetchRecommendations(): Promise<RecommendationsResponse> {
  const response = await fetch('/api/recommendations')
  if (!response.ok) {
    throw new Error('Failed to fetch recommendations')
  }
  return response.json()
}

export default function WeeklyRecommendations() {
  const { data: session } = useSession()
  const { data, isLoading } = useQuery({
    queryKey: ['recommendations'],
    queryFn: fetchRecommendations,
    enabled: !!session,
  })

  if (!session) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Weekly Recommendations</h2>
        <p className="text-gray-500 text-sm">
          Sign in to get personalized recommendations based on your preferences
        </p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Weekly Recommendations</h2>
        <div className="space-y-3">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!data || !data.recommendations || data.recommendations.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Weekly Recommendations</h2>
        <p className="text-gray-500 text-sm">
          Add some favorites to get personalized recommendations!
        </p>
      </div>
    )
  }

  const sceneLabels: Record<string, string> = {
    Study: 'Best Study Spots',
    'Remote Work': 'Best Remote Work Spots',
    Date: 'Best Date Spots',
    Meeting: 'Best Meeting Spots',
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Weekly Recommendations</h2>
        {data.stats && (
          <div className="text-xs text-gray-500">
            Based on {data.stats.favoritesCount} favorites
          </div>
        )}
      </div>
      <div className="space-y-6">
        {data.recommendations.map((rec) => {
          if (rec.shops.length === 0) return null

          return (
            <div key={rec.scene}>
              <h3 className="font-medium text-gray-900 mb-3">
                {sceneLabels[rec.scene] || rec.scene}
              </h3>
              <div className="space-y-2">
                {rec.shops.slice(0, 3).map((shop) => (
                  <Link
                    key={shop.id}
                    href={`/?shop=${shop.id}&scene=${rec.scene}`}
                    className="block p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 text-sm">{shop.name}</p>
                        <p className="text-xs text-gray-500 mt-1">{shop.address}</p>
                        {shop.matchCount > 0 && (
                          <p className="text-xs text-blue-600 mt-1">
                            Matches {shop.matchCount} preferences
                          </p>
                        )}
                      </div>
                      <div className="ml-3 text-right">
                        <span className="text-xs font-semibold text-blue-600">
                          {shop.suitability.score}
                        </span>
                        <p className="text-xs text-gray-500">score</p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}


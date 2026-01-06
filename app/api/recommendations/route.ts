import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { computeSuitability, type Scene } from '@/lib/scoring'

export const dynamic = 'force-dynamic'

// GET - Get personalized recommendations
export async function GET(request: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const userId = session.user.id as string

    // Get user's favorites and visit history
    const [favorites, visits] = await Promise.all([
      prisma.favorite.findMany({
        where: { userId },
        include: { shop: true },
      }),
      prisma.visitHistory.findMany({
        where: { userId },
        include: { shop: true },
        orderBy: { visitedAt: 'desc' },
        take: 20, // Last 20 visits
      }),
    ])

    // Analyze user preferences from favorites
    const favoriteShops = favorites.map((f) => f.shop)
    let userPreferences: {
      prefersQuiet: boolean
      prefersNaturalLight: boolean
      prefersLargeTables: boolean
      prefersOutlets: boolean
      prefersFastWifi: boolean
      preferredPriceLevel: number
      preferredScenes: Scene[]
    } = {
      prefersQuiet: false,
      prefersNaturalLight: false,
      prefersLargeTables: false,
      prefersOutlets: false,
      prefersFastWifi: false,
      preferredPriceLevel: 3,
      preferredScenes: [],
    }

    if (favoriteShops.length > 0) {
      const features = favoriteShops.map((shop) => shop.features as any)
      const avgNoise = features.reduce((sum, f) => sum + f.noise, 0) / features.length
      const avgLighting = features.reduce((sum, f) => sum + f.lighting, 0) / features.length
      const avgSeating = features.reduce((sum, f) => sum + f.seating, 0) / features.length
      const avgOutlets = features.reduce((sum, f) => sum + f.outlets, 0) / features.length
      const avgWifi = features.reduce((sum, f) => sum + f.wifi, 0) / features.length
      const avgPriceLevel =
        favoriteShops.reduce((sum, shop) => sum + shop.priceLevel, 0) / favoriteShops.length

      userPreferences = {
        prefersQuiet: avgNoise <= 2.5,
        prefersNaturalLight: avgLighting >= 4,
        prefersLargeTables: avgSeating >= 4,
        prefersOutlets: avgOutlets >= 4,
        prefersFastWifi: avgWifi >= 4,
        preferredPriceLevel: Math.round(avgPriceLevel),
        preferredScenes: ['Study', 'Remote Work', 'Date', 'Meeting'], // All scenes for now
      }
    }

    // Get visited shop IDs to exclude
    const visitedShopIds = new Set([
      ...favorites.map((f) => f.shopId),
      ...visits.map((v) => v.shopId),
    ])

    // Get all approved shops
    const allShops = await prisma.shop.findMany({
      where: {
        status: 'approved',
        id: {
          notIn: Array.from(visitedShopIds), // Exclude already visited/favorited shops
        },
      },
    })

    // Calculate recommendation scores for each shop
    const shopScores = allShops.map((shop) => {
      const features = shop.features as any
      let score = 0
      let matchCount = 0

      // Match based on preferences
      if (userPreferences.prefersQuiet && features.noise <= 2.5) {
        score += 20
        matchCount++
      }
      if (userPreferences.prefersNaturalLight && features.lighting >= 4) {
        score += 20
        matchCount++
      }
      if (userPreferences.prefersLargeTables && features.seating >= 4) {
        score += 15
        matchCount++
      }
      if (userPreferences.prefersOutlets && features.outlets >= 4) {
        score += 15
        matchCount++
      }
      if (userPreferences.prefersFastWifi && features.wifi >= 4) {
        score += 15
        matchCount++
      }

      // Price level match
      if (Math.abs(shop.priceLevel - userPreferences.preferredPriceLevel) <= 1) {
        score += 10
      }

      // Rating boost
      score += shop.rating * 5

      // Calculate suitability scores for different scenes
      const suitabilityScores: Record<Scene, number> = {
        Study: computeSuitability('Study', features, shop.rating).score,
        'Remote Work': computeSuitability('Remote Work', features, shop.rating).score,
        Date: computeSuitability('Date', features, shop.rating).score,
        Meeting: computeSuitability('Meeting', features, shop.rating).score,
      }

      return {
        shop,
        score,
        matchCount,
        suitabilityScores,
      }
    })

    // Sort by score and get top recommendations
    const topRecommendations = shopScores
      .sort((a, b) => b.score - a.score)
      .slice(0, 20) // Top 20 recommendations

    // Group by scene
    const recommendationsByScene: Record<Scene, typeof topRecommendations> = {
      Study: [],
      'Remote Work': [],
      Date: [],
      Meeting: [],
    }

    topRecommendations.forEach((rec) => {
      // Find best scene for this shop
      const bestScene = Object.entries(rec.suitabilityScores).reduce((a, b) =>
        b[1] > a[1] ? b : a
      )[0] as Scene

      if (recommendationsByScene[bestScene].length < 5) {
        recommendationsByScene[bestScene].push(rec)
      }
    })

    // Fill remaining slots with top shops for each scene
    Object.keys(recommendationsByScene).forEach((scene) => {
      const sceneKey = scene as Scene
      if (recommendationsByScene[sceneKey].length < 3) {
        const sceneShops = shopScores
          .filter((rec) => !recommendationsByScene[sceneKey].some((r) => r.shop.id === rec.shop.id))
          .sort((a, b) => b.suitabilityScores[sceneKey] - a.suitabilityScores[sceneKey])
          .slice(0, 3 - recommendationsByScene[sceneKey].length)

        recommendationsByScene[sceneKey].push(...sceneShops)
      }
    })

    // Format response
    const recommendations = Object.entries(recommendationsByScene).map(([scene, shops]) => ({
      scene: scene as Scene,
      shops: shops.map((rec) => ({
        ...rec.shop,
        suitability: {
          score: rec.suitabilityScores[scene as Scene],
          breakdown: [],
        },
        recommendationScore: rec.score,
        matchCount: rec.matchCount,
      })),
    }))

    return NextResponse.json({
      recommendations,
      userPreferences,
      stats: {
        favoritesCount: favorites.length,
        visitsCount: visits.length,
      },
    })
  } catch (error) {
    console.error('Error generating recommendations:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}


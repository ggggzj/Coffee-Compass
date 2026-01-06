import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { prisma } from '@/lib/prisma'
import { computeSuitability, type Scene } from '@/lib/scoring'

export const dynamic = 'force-dynamic'

const querySchema = z.object({
  city: z.enum(['Los Angeles', 'San Francisco', 'New York']).optional(),
  scene: z.enum(['Study', 'Remote Work', 'Date', 'Meeting']).optional(),
  sort: z.enum(['Distance', 'Rating', 'Suitability']).optional(),
  bounds: z.string().optional(), // format: minLng,minLat,maxLng,maxLat
  page: z.string().optional().transform((val) => (val ? parseInt(val, 10) : 1)),
  pageSize: z.string().optional().transform((val) => (val ? parseInt(val, 10) : 20)),
})

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const params = querySchema.parse({
      city: searchParams.get('city') || undefined,
      scene: searchParams.get('scene') || undefined,
      sort: searchParams.get('sort') || undefined,
      bounds: searchParams.get('bounds') || undefined,
      page: searchParams.get('page') || undefined,
      pageSize: searchParams.get('pageSize') || undefined,
    })

    // Parse bounds if provided
    let bounds: { minLng: number; minLat: number; maxLng: number; maxLat: number } | null = null
    if (params.bounds) {
      const [minLng, minLat, maxLng, maxLat] = params.bounds.split(',').map(Number)
      bounds = { minLng, minLat, maxLng, maxLat }
    }

    // Build where clause
    const where: any = {}
    if (params.city) {
      where.city = params.city
    }
    if (bounds) {
      where.latitude = {
        gte: bounds.minLat,
        lte: bounds.maxLat,
      }
      where.longitude = {
        gte: bounds.minLng,
        lte: bounds.maxLng,
      }
    }

    // Get total count for pagination
    const total = await prisma.shop.count({ where })

    // Fetch shops (fetch more than needed for sorting, then paginate)
    const shops = await prisma.shop.findMany({
      where,
    })

    // Calculate map center for distance calculation
    let mapCenter: { lat: number; lng: number } | null = null
    if (bounds) {
      mapCenter = {
        lat: (bounds.minLat + bounds.maxLat) / 2,
        lng: (bounds.minLng + bounds.maxLng) / 2,
      }
    } else if (params.city) {
      // Use city center if no bounds
      const cityCenters: Record<string, { lat: number; lng: number }> = {
        'Los Angeles': { lat: 34.0522, lng: -118.2437 },
        'San Francisco': { lat: 37.7749, lng: -122.4194 },
        'New York': { lat: 40.7128, lng: -74.006 },
      }
      mapCenter = cityCenters[params.city] || null
    }

    // Helper function to calculate distance in meters (Haversine formula)
    const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
      const R = 6371000 // Earth radius in meters
      const dLat = ((lat2 - lat1) * Math.PI) / 180
      const dLon = ((lon2 - lon1) * Math.PI) / 180
      const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos((lat1 * Math.PI) / 180) *
          Math.cos((lat2 * Math.PI) / 180) *
          Math.sin(dLon / 2) *
          Math.sin(dLon / 2)
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
      return R * c
    }

    // Helper function to determine if shop is open (mock implementation)
    const isShopOpen = (): boolean => {
      const hour = new Date().getHours()
      // Mock: shops open 7 AM - 9 PM
      return hour >= 7 && hour < 21
    }

    // Compute suitability scores and add distance/open status
    const shopsWithScores = shops.map((shop) => {
      const features = shop.features as any
      let suitability = null

      if (params.scene) {
        suitability = computeSuitability(params.scene as Scene, features, shop.rating)
      }

      let distance: number | undefined
      if (mapCenter) {
        distance = calculateDistance(mapCenter.lat, mapCenter.lng, shop.latitude, shop.longitude)
      }

      return {
        ...shop,
        suitability,
        distance,
        isOpen: isShopOpen(),
      }
    })

    // Sort shops
    let sortedShops = shopsWithScores
    if (params.sort === 'Rating') {
      sortedShops = [...shopsWithScores].sort((a, b) => b.rating - a.rating)
    } else if (params.sort === 'Suitability' && params.scene) {
      sortedShops = [...shopsWithScores].sort((a, b) => {
        const scoreA = a.suitability?.score || 0
        const scoreB = b.suitability?.score || 0
        return scoreB - scoreA
      })
    } else if (params.sort === 'Distance' && mapCenter) {
      sortedShops = [...shopsWithScores].sort((a, b) => {
        const distA = a.distance || Infinity
        const distB = b.distance || Infinity
        return distA - distB
      })
    }

    // Apply pagination after sorting
    const paginatedShops = sortedShops.slice(
      (params.page - 1) * params.pageSize,
      params.page * params.pageSize
    )

    return NextResponse.json({
      shops: paginatedShops,
      pagination: {
        page: params.page,
        pageSize: params.pageSize,
        total,
        totalPages: Math.ceil(total / params.pageSize),
      },
    })
  } catch (error) {
    console.error('Error fetching shops:', error)
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: 'Invalid query parameters', details: error.errors }, { status: 400 })
    }
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


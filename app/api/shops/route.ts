import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { prisma } from '@/lib/prisma'
import { computeSuitability, type Scene } from '@/lib/scoring'

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

    // Compute suitability scores if scene is provided
    const shopsWithScores = shops.map((shop) => {
      const features = shop.features as any
      let suitability = null

      if (params.scene) {
        suitability = computeSuitability(params.scene as Scene, features, shop.rating)
      }

      return {
        ...shop,
        suitability,
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
    }
    // Distance sorting would require calculating distance from a center point
    // For MVP, we'll skip it or use a simple lat/lng comparison

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


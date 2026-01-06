import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { computeSuitability, type Scene } from '@/lib/scoring'

export const dynamic = 'force-dynamic'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const shop = await prisma.shop.findUnique({
      where: { id: params.id },
    })

    if (!shop) {
      return NextResponse.json({ error: 'Shop not found' }, { status: 404 })
    }

    // Check if scene is provided in query params
    const searchParams = request.nextUrl.searchParams
    const scene = searchParams.get('scene') as Scene | null

    let suitability = null
    if (scene) {
      const features = shop.features as any
      suitability = computeSuitability(scene, features, shop.rating)
    }

    return NextResponse.json({
      ...shop,
      suitability,
    })
  } catch (error) {
    console.error('Error fetching shop:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


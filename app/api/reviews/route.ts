import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { z } from 'zod'

const reviewSchema = z.object({
  shopId: z.string().uuid(),
  ratings: z.object({
    noise: z.number().min(1).max(5),
    outlets: z.number().min(1).max(5),
    wifi: z.number().min(1).max(5),
    seating: z.number().min(1).max(5),
    lighting: z.number().min(1).max(5),
    privacy: z.number().min(1).max(5),
    busyness: z.number().min(1).max(5),
  }),
  text: z.string().optional(),
})

// GET - Get reviews (optionally filtered by shopId or userId)
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const shopId = searchParams.get('shopId')
    const userId = searchParams.get('userId')

    const where: any = {}
    if (shopId) where.shopId = shopId
    if (userId) where.userId = userId

    const reviews = await prisma.review.findMany({
      where,
      include: {
        user: {
          select: {
            id: true,
            name: true,
            image: true,
          },
        },
        shop: {
          select: {
            id: true,
            name: true,
          },
        },
      },
      orderBy: {
        createdAt: 'desc',
      },
    })

    return NextResponse.json({ reviews })
  } catch (error) {
    console.error('Error fetching reviews:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// POST - Create review
export async function POST(request: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { shopId, ratings, text } = reviewSchema.parse(body)

    // Check if shop exists
    const shop = await prisma.shop.findUnique({
      where: { id: shopId },
    })

    if (!shop) {
      return NextResponse.json({ error: 'Shop not found' }, { status: 404 })
    }

    // Check if user already reviewed this shop
    const existing = await prisma.review.findUnique({
      where: {
        shopId_userId: {
          shopId,
          userId: session.user.id as string,
        },
      },
    })

    if (existing) {
      return NextResponse.json(
        { error: 'You have already reviewed this shop' },
        { status: 400 }
      )
    }

    const review = await prisma.review.create({
      data: {
        shopId,
        userId: session.user.id as string,
        ratings,
        text,
      },
      include: {
        user: {
          select: {
            id: true,
            name: true,
            image: true,
          },
        },
        shop: {
          select: {
            id: true,
            name: true,
          },
        },
      },
    })

    // Update shop rating (average of all reviews)
    const allReviews = await prisma.review.findMany({
      where: { shopId },
      select: { ratings: true },
    })

    const avgRating =
      allReviews.reduce((sum, r) => {
        const ratings = r.ratings as any
        const avg =
          (ratings.noise +
            ratings.outlets +
            ratings.wifi +
            ratings.seating +
            ratings.lighting +
            ratings.privacy) /
          6
        return sum + avg
      }, 0) / allReviews.length

    await prisma.shop.update({
      where: { id: shopId },
      data: { rating: avgRating },
    })

    return NextResponse.json({ review }, { status: 201 })
  } catch (error) {
    console.error('Error creating review:', error)
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 }
      )
    }
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}


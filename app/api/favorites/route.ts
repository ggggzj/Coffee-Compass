import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { z } from 'zod'

const favoriteSchema = z.object({
  shopId: z.string().uuid(),
})

// GET - Get user's favorites
export async function GET(request: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const favorites = await prisma.favorite.findMany({
      where: {
        userId: session.user.id as string,
      },
      include: {
        shop: true,
      },
      orderBy: {
        createdAt: 'desc',
      },
    })

    return NextResponse.json({ favorites })
  } catch (error) {
    console.error('Error fetching favorites:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// POST - Add favorite
export async function POST(request: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { shopId } = favoriteSchema.parse(body)

    // Check if shop exists
    const shop = await prisma.shop.findUnique({
      where: { id: shopId },
    })

    if (!shop) {
      return NextResponse.json({ error: 'Shop not found' }, { status: 404 })
    }

    // Check if already favorited
    const existing = await prisma.favorite.findUnique({
      where: {
        shopId_userId: {
          shopId,
          userId: session.user.id as string,
        },
      },
    })

    if (existing) {
      return NextResponse.json(
        { error: 'Already favorited' },
        { status: 400 }
      )
    }

    const favorite = await prisma.favorite.create({
      data: {
        shopId,
        userId: session.user.id as string,
      },
      include: {
        shop: true,
      },
    })

    return NextResponse.json({ favorite }, { status: 201 })
  } catch (error) {
    console.error('Error adding favorite:', error)
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

// DELETE - Remove favorite
export async function DELETE(request: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const shopId = searchParams.get('shopId')

    if (!shopId) {
      return NextResponse.json(
        { error: 'shopId is required' },
        { status: 400 }
      )
    }

    await prisma.favorite.deleteMany({
      where: {
        shopId,
        userId: session.user.id as string,
      },
    })

    return NextResponse.json({ message: 'Favorite removed' })
  } catch (error) {
    console.error('Error removing favorite:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}


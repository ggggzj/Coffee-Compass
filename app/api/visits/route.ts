import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { z } from 'zod'

const visitSchema = z.object({
  shopId: z.string().uuid(),
})

// GET - Get user's visit history
export async function GET(request: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const visits = await prisma.visitHistory.findMany({
      where: {
        userId: session.user.id as string,
      },
      include: {
        shop: true,
      },
      orderBy: {
        visitedAt: 'desc',
      },
      take: 50, // Limit to last 50 visits
    })

    return NextResponse.json({ visits })
  } catch (error) {
    console.error('Error fetching visit history:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// POST - Record a visit
export async function POST(request: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { shopId } = visitSchema.parse(body)

    // Check if shop exists
    const shop = await prisma.shop.findUnique({
      where: { id: shopId },
    })

    if (!shop) {
      return NextResponse.json({ error: 'Shop not found' }, { status: 404 })
    }

    const visit = await prisma.visitHistory.create({
      data: {
        shopId,
        userId: session.user.id as string,
      },
      include: {
        shop: true,
      },
    })

    return NextResponse.json({ visit }, { status: 201 })
  } catch (error) {
    console.error('Error recording visit:', error)
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


import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { z } from 'zod'

export const dynamic = 'force-dynamic'

const submitSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  address: z.string().min(1, 'Address is required'),
  city: z.enum(['Los Angeles', 'San Francisco', 'New York']),
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  priceLevel: z.number().min(1).max(4),
  tags: z.array(z.string()).optional(),
  features: z.object({
    noise: z.number().min(1).max(5),
    outlets: z.number().min(1).max(5),
    wifi: z.number().min(1).max(5),
    seating: z.number().min(1).max(5),
    lighting: z.number().min(1).max(5),
    privacy: z.number().min(1).max(5),
  }),
})

// POST - Submit a new shop
export async function POST(request: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const data = submitSchema.parse(body)

    // Check if shop already exists (by name and address)
    const existing = await prisma.shop.findFirst({
      where: {
        name: data.name,
        address: data.address,
        city: data.city,
      },
    })

    if (existing) {
      return NextResponse.json(
        { error: 'A shop with this name and address already exists' },
        { status: 400 }
      )
    }

    // Create shop submission
    const submission = await prisma.shopSubmission.create({
      data: {
        submittedBy: session.user.id as string,
        name: data.name,
        address: data.address,
        city: data.city,
        latitude: data.latitude,
        longitude: data.longitude,
        priceLevel: data.priceLevel,
        tags: data.tags || [],
        features: data.features,
        status: 'pending',
      },
    })

    return NextResponse.json(
      {
        message: 'Shop submitted successfully. It will be reviewed by an admin.',
        submission,
      },
      { status: 201 }
    )
  } catch (error) {
    console.error('Error submitting shop:', error)
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


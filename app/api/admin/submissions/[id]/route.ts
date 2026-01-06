import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { z } from 'zod'

const updateSchema = z.object({
  status: z.enum(['pending', 'approved', 'rejected']),
})

// PATCH - Update submission status
export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await auth()
    if (!session?.user?.id || (session.user as any).role !== 'admin') {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { status } = updateSchema.parse(body)

    const submission = await prisma.shopSubmission.findUnique({
      where: { id: params.id },
    })

    if (!submission) {
      return NextResponse.json({ error: 'Submission not found' }, { status: 404 })
    }

    // If approving, create the shop
    if (status === 'approved' && submission.status !== 'approved') {
      const shop = await prisma.shop.create({
        data: {
          name: submission.name,
          address: submission.address,
          city: submission.city,
          latitude: submission.latitude,
          longitude: submission.longitude,
          priceLevel: submission.priceLevel,
          tags: submission.tags,
          features: submission.features as any,
          status: 'approved',
        },
      })

      // Update submission with shop ID
      await prisma.shopSubmission.update({
        where: { id: params.id },
        data: {
          status: 'approved',
          shopId: shop.id,
        },
      })

      return NextResponse.json({
        message: 'Shop approved and created',
        submission: {
          ...submission,
          status: 'approved',
          shopId: shop.id,
        },
        shop,
      })
    }

    // Otherwise, just update status
    const updated = await prisma.shopSubmission.update({
      where: { id: params.id },
      data: { status },
    })

    return NextResponse.json({ submission: updated })
  } catch (error) {
    console.error('Error updating submission:', error)
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


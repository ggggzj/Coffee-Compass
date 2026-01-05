'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'

interface Review {
  id: string
  shopId: string
  userId: string
  ratings: {
    noise: number
    outlets: number
    wifi: number
    seating: number
    lighting: number
    privacy: number
    busyness: number
  }
  text?: string
  createdAt: string
  shop: {
    id: string
    name: string
  }
  user: {
    id: string
    name: string | null
    image: string | null
  }
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

export default function ReviewsList() {
  const { data: session } = useSession()
  const [reviews, setReviews] = useState<Review[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!session) {
      setIsLoading(false)
      return
    }

    fetch(`/api/reviews?userId=${session.user?.id}`)
      .then((res) => res.json())
      .then((data) => {
        setReviews(data.reviews || [])
        setIsLoading(false)
      })
      .catch((error) => {
        console.error('Error fetching reviews:', error)
        setIsLoading(false)
      })
  }, [session])

  const getRatingLabel = (value: number): string => {
    if (value <= 1) return 'Poor'
    if (value <= 2) return 'Fair'
    if (value <= 3) return 'Good'
    if (value <= 4) return 'Very Good'
    return 'Excellent'
  }

  if (!session) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">My Reviews</h2>
        <p className="text-gray-500 text-center py-8">
          Please sign in to view your reviews
        </p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">My Reviews</h2>
        <div className="space-y-6">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="animate-pulse border-b border-gray-100 pb-6">
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/4 mb-4"></div>
              <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">My Reviews</h2>
      {reviews.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No reviews yet</p>
      ) : (
        <div className="space-y-6">
          {reviews.map((review) => (
            <div key={review.id} className="border-b border-gray-100 last:border-0 pb-6 last:pb-0">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{review.shop.name}</h3>
                  <p className="text-sm text-gray-500">{formatDate(review.createdAt)}</p>
                </div>
              </div>

              {review.text && (
                <p className="text-gray-700 mb-4">{review.text}</p>
              )}

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div>
                  <span className="text-gray-600">Noise:</span>
                  <span className="ml-2 font-medium">{review.ratings.noise}/5</span>
                  <span className="ml-1 text-gray-500">({getRatingLabel(review.ratings.noise)})</span>
                </div>
                <div>
                  <span className="text-gray-600">Outlets:</span>
                  <span className="ml-2 font-medium">{review.ratings.outlets}/5</span>
                </div>
                <div>
                  <span className="text-gray-600">WiFi:</span>
                  <span className="ml-2 font-medium">{review.ratings.wifi}/5</span>
                </div>
                <div>
                  <span className="text-gray-600">Seating:</span>
                  <span className="ml-2 font-medium">{review.ratings.seating}/5</span>
                </div>
                <div>
                  <span className="text-gray-600">Lighting:</span>
                  <span className="ml-2 font-medium">{review.ratings.lighting}/5</span>
                </div>
                <div>
                  <span className="text-gray-600">Privacy:</span>
                  <span className="ml-2 font-medium">{review.ratings.privacy}/5</span>
                </div>
                <div>
                  <span className="text-gray-600">Busyness:</span>
                  <span className="ml-2 font-medium">{review.ratings.busyness}/5</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}


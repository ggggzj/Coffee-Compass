'use client'

import { useEffect, useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSession } from 'next-auth/react'
// Icons as simple SVG components
const XIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    strokeWidth={1.5}
    stroke="currentColor"
    className={className}
  >
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
  </svg>
)

const HeartIcon = ({ className, filled }: { className?: string; filled?: boolean }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill={filled ? 'currentColor' : 'none'}
    viewBox="0 0 24 24"
    strokeWidth={1.5}
    stroke="currentColor"
    className={className}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.312-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"
    />
  </svg>
)

interface ShopDrawerProps {
  shopId: string
  scene: string
  onClose: () => void
}

async function fetchShop(shopId: string, scene: string) {
  const params = new URLSearchParams()
  params.set('scene', scene)
  const response = await fetch(`/api/shops/${shopId}?${params.toString()}`)
  if (!response.ok) {
    throw new Error('Failed to fetch shop')
  }
  return response.json()
}

async function fetchReviews(shopId: string) {
  const response = await fetch(`/api/reviews?shopId=${shopId}`)
  if (!response.ok) {
    throw new Error('Failed to fetch reviews')
  }
  return response.json()
}

async function checkFavorite(shopId: string) {
  const response = await fetch('/api/favorites')
  if (!response.ok) return false
  const data = await response.json()
  return data.favorites?.some((fav: any) => fav.shopId === shopId) || false
}

async function toggleFavorite(shopId: string, isFavorite: boolean) {
  if (isFavorite) {
    await fetch(`/api/favorites?shopId=${shopId}`, { method: 'DELETE' })
  } else {
    await fetch('/api/favorites', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ shopId }),
    })
  }
}

async function recordVisit(shopId: string) {
  await fetch('/api/visits', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ shopId }),
  })
}

export default function ShopDrawer({ shopId, scene, onClose }: ShopDrawerProps) {
  const { data: session } = useSession()
  const queryClient = useQueryClient()
  const [isFavorite, setIsFavorite] = useState(false)
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [reviewForm, setReviewForm] = useState({
    noise: 3,
    outlets: 3,
    wifi: 3,
    seating: 3,
    lighting: 3,
    privacy: 3,
    busyness: 3,
    text: '',
  })
  const drawerRef = useRef<HTMLDivElement>(null)

  const { data: shop, isLoading } = useQuery({
    queryKey: ['shop', shopId, scene],
    queryFn: () => fetchShop(shopId, scene),
  })

  const { data: reviewsData } = useQuery({
    queryKey: ['reviews', shopId],
    queryFn: () => fetchReviews(shopId),
    enabled: !!shopId,
  })

  const reviews = reviewsData?.reviews || []
  const userReview = reviews.find((r: any) => r.userId === session?.user?.id)

  // Check favorite status
  useEffect(() => {
    if (shop && session) {
      checkFavorite(shop.id).then(setIsFavorite)
    }
  }, [shop, session])

  // Record visit when drawer opens
  useEffect(() => {
    if (shop && session) {
      recordVisit(shop.id).catch(console.error)
    }
  }, [shop, session])

  const favoriteMutation = useMutation({
    mutationFn: () => toggleFavorite(shopId, isFavorite),
    onSuccess: () => {
      setIsFavorite(!isFavorite)
      queryClient.invalidateQueries({ queryKey: ['favorites'] })
    },
  })

  const reviewMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/reviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          shopId,
          ratings: {
            noise: reviewForm.noise,
            outlets: reviewForm.outlets,
            wifi: reviewForm.wifi,
            seating: reviewForm.seating,
            lighting: reviewForm.lighting,
            privacy: reviewForm.privacy,
            busyness: reviewForm.busyness,
          },
          text: reviewForm.text || undefined,
        }),
      })
      if (!response.ok) throw new Error('Failed to submit review')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews', shopId] })
      queryClient.invalidateQueries({ queryKey: ['shop', shopId] })
      setShowReviewForm(false)
      setReviewForm({
        noise: 3,
        outlets: 3,
        wifi: 3,
        seating: 3,
        lighting: 3,
        privacy: 3,
        busyness: 3,
        text: '',
      })
    },
  })

  const handleToggleFavorite = () => {
    if (!session) {
      window.location.href = '/auth/signin'
      return
    }
    favoriteMutation.mutate()
  }

  const handleSubmitReview = (e: React.FormEvent) => {
    e.preventDefault()
    if (!session) {
      window.location.href = '/auth/signin'
      return
    }
    reviewMutation.mutate()
  }

  // Handle click outside to close drawer (only on client)
  useEffect(() => {
    if (typeof window === 'undefined') return

    const handleClickOutside = (event: MouseEvent) => {
      if (drawerRef.current && !drawerRef.current.contains(event.target as Node)) {
        onClose()
      }
    }

    // Use a small delay to avoid immediate triggers during hydration
    const timeoutId = setTimeout(() => {
      document.addEventListener('mousedown', handleClickOutside)
    }, 100)

    return () => {
      clearTimeout(timeoutId)
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [onClose])

  if (isLoading) {
    return (
      <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl z-50 overflow-y-auto">
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!shop) {
    return null
  }

  const priceSymbols = '$'.repeat(shop.priceLevel)
  const features = shop.features as any
  const suitability = shop.suitability

  return (
    <div
      ref={drawerRef}
      className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl z-50 overflow-y-auto"
    >
      <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-900">Coffee Shop Details</h2>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
        >
          <XIcon className="w-5 h-5" />
        </button>
      </div>

      <div className="p-6 space-y-6">
        {/* Placeholder Images */}
        <div className="grid grid-cols-2 gap-2 -mx-6 -mt-6">
          <div className="h-48 bg-gradient-to-br from-amber-100 to-amber-200 flex items-center justify-center">
            <span className="text-amber-600 text-sm">Coffee Shop Image</span>
          </div>
          <div className="h-48 bg-gradient-to-br from-amber-50 to-amber-100 flex items-center justify-center">
            <span className="text-amber-600 text-sm">Interior View</span>
          </div>
        </div>

        <div>
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-2xl font-bold text-gray-900">{shop.name}</h3>
            {session && (
              <button
                onClick={handleToggleFavorite}
                disabled={favoriteMutation.isPending}
                className={`p-2 rounded-full transition-colors ${
                  isFavorite
                    ? 'text-red-500 hover:bg-red-50'
                    : 'text-gray-400 hover:bg-gray-100'
                } disabled:opacity-50`}
                title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
              >
                <HeartIcon className="w-6 h-6" filled={isFavorite} />
              </button>
            )}
          </div>
          <p className="text-gray-600">{shop.address}</p>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <span className="text-yellow-500 text-xl">★</span>
            <span className="text-lg font-semibold text-gray-900">{shop.rating.toFixed(1)}</span>
          </div>
          <div className="text-gray-600 text-lg">{priceSymbols}</div>
        </div>

        {shop.tags && shop.tags.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Tags</h4>
            <div className="flex flex-wrap gap-2">
              {shop.tags.map((tag: string) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {suitability && (
          <div className="border-t border-gray-200 pt-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">
              Suitability Score: {suitability.score}/100
            </h4>
            <p className="text-sm text-gray-600 mb-4">
              Scene: <span className="font-medium">{scene}</span>
            </p>

            <div className="space-y-3">
              <h5 className="text-sm font-medium text-gray-700">Score Breakdown:</h5>
              {suitability.breakdown.map((item: any, index: number) => (
                <div key={index} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-700 capitalize">{item.feature}</span>
                    <span className="text-gray-600">
                      {item.contribution.toFixed(1)}% (Weight: {(item.weight * 100).toFixed(0)}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${item.contribution}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="border-t border-gray-200 pt-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Facility Details</h4>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-600">Noise:</span>
              <span className="ml-2 font-medium">{features.noise}/5</span>
            </div>
            <div>
              <span className="text-gray-600">Outlets:</span>
              <span className="ml-2 font-medium">{features.outlets}/5</span>
            </div>
            <div>
              <span className="text-gray-600">WiFi:</span>
              <span className="ml-2 font-medium">{features.wifi}/5</span>
            </div>
            <div>
              <span className="text-gray-600">Seating:</span>
              <span className="ml-2 font-medium">{features.seating}/5</span>
            </div>
            <div>
              <span className="text-gray-600">Lighting:</span>
              <span className="ml-2 font-medium">{features.lighting}/5</span>
            </div>
            <div>
              <span className="text-gray-600">Privacy:</span>
              <span className="ml-2 font-medium">{features.privacy}/5</span>
            </div>
          </div>
        </div>

        {/* Reviews Section */}
        <div className="border-t border-gray-200 pt-6">
          <div className="flex justify-between items-center mb-4">
            <h4 className="text-lg font-semibold text-gray-900">
              Reviews ({reviews.length})
            </h4>
            {session && !userReview && (
              <button
                onClick={() => setShowReviewForm(!showReviewForm)}
                className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
              >
                {showReviewForm ? 'Cancel' : 'Write Review'}
              </button>
            )}
          </div>

          {/* Review Form */}
          {showReviewForm && session && (
            <form onSubmit={handleSubmitReview} className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h5 className="font-medium text-gray-900 mb-4">Your Review</h5>
              <div className="space-y-3 mb-4">
                {[
                  { key: 'noise', label: 'Noise Level' },
                  { key: 'outlets', label: 'Outlets' },
                  { key: 'wifi', label: 'WiFi Quality' },
                  { key: 'seating', label: 'Seating' },
                  { key: 'lighting', label: 'Lighting' },
                  { key: 'privacy', label: 'Privacy' },
                  { key: 'busyness', label: 'Busyness' },
                ].map(({ key, label }) => (
                  <div key={key} className="flex items-center justify-between">
                    <label className="text-sm text-gray-700">{label}:</label>
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map((value) => (
                        <button
                          key={value}
                          type="button"
                          onClick={() =>
                            setReviewForm({ ...reviewForm, [key]: value })
                          }
                          className={`w-8 h-8 rounded ${
                            (reviewForm[key as keyof typeof reviewForm] as number) >= value
                              ? 'bg-yellow-400 text-yellow-900'
                              : 'bg-gray-200 text-gray-400'
                          } transition-colors`}
                        >
                          ★
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              <textarea
                value={reviewForm.text}
                onChange={(e) =>
                  setReviewForm({ ...reviewForm, text: e.target.value })
                }
                placeholder="Write your review..."
                className="w-full p-3 border border-gray-300 rounded-md text-sm mb-3"
                rows={3}
              />
              <button
                type="submit"
                disabled={reviewMutation.isPending}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {reviewMutation.isPending ? 'Submitting...' : 'Submit Review'}
              </button>
            </form>
          )}

          {/* Reviews List */}
          {reviews.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No reviews yet</p>
          ) : (
            <div className="space-y-4">
              {reviews.map((review: any) => (
                <div
                  key={review.id}
                  className="border-b border-gray-100 pb-4 last:border-0"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-medium text-gray-900">
                        {review.user.name || 'Anonymous'}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(review.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  {review.text && (
                    <p className="text-gray-700 text-sm mb-3">{review.text}</p>
                  )}
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                    <div>Noise: {review.ratings.noise}/5</div>
                    <div>Outlets: {review.ratings.outlets}/5</div>
                    <div>WiFi: {review.ratings.wifi}/5</div>
                    <div>Seating: {review.ratings.seating}/5</div>
                    <div>Lighting: {review.ratings.lighting}/5</div>
                    <div>Privacy: {review.ratings.privacy}/5</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}


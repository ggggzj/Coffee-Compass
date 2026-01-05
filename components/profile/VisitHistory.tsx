'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import type { Shop } from '@/types/shop'

interface Visit {
  id: string
  shopId: string
  visitedAt: string
  shop: Shop
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  return date.toLocaleDateString()
}

export default function VisitHistory() {
  const { data: session } = useSession()
  const [visits, setVisits] = useState<Visit[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!session) {
      setIsLoading(false)
      return
    }

    fetch('/api/visits')
      .then((res) => res.json())
      .then((data) => {
        setVisits(data.visits || [])
        setIsLoading(false)
      })
      .catch((error) => {
        console.error('Error fetching visit history:', error)
        setIsLoading(false)
      })
  }, [session])

  if (!session) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Visit History</h2>
        <p className="text-gray-500 text-center py-8">
          Please sign in to view your visit history
        </p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Visit History</h2>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse py-2 border-b border-gray-100">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Visit History</h2>
      {visits.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No visit history</p>
      ) : (
        <div className="space-y-3">
          {visits.map((visit) => (
            <div
              key={visit.id}
              className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0"
            >
              <div>
                <p className="font-medium text-gray-900">{visit.shop.name}</p>
                <p className="text-sm text-gray-500">{formatDate(visit.visitedAt)}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}


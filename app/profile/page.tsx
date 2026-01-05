'use client'

import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Navigation from '@/components/Navigation'
import ProfileHeader from '@/components/profile/ProfileHeader'
import FavoritesList from '@/components/profile/FavoritesList'
import VisitHistory from '@/components/profile/VisitHistory'
import ReviewsList from '@/components/profile/ReviewsList'
import PreferenceCard from '@/components/profile/PreferenceCard'
import WeeklyRecommendations from '@/components/profile/WeeklyRecommendations'

export default function ProfilePage() {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin')
    }
  }, [status, router])

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  if (!session) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-900">CoffeeCompass</h1>
          <Navigation />
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ProfileHeader />
        
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            <FavoritesList />
            <VisitHistory />
            <ReviewsList />
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            <PreferenceCard />
            <WeeklyRecommendations />
          </div>
        </div>
      </div>
    </div>
  )
}


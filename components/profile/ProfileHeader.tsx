'use client'

export default function ProfileHeader() {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center gap-4">
        <div className="w-20 h-20 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
          JD
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">John Doe</h1>
          <p className="text-gray-600">Coffee enthusiast since 2023</p>
          <div className="flex gap-4 mt-2 text-sm text-gray-500">
            <span>12 Favorites</span>
            <span>•</span>
            <span>8 Reviews</span>
            <span>•</span>
            <span>24 Visits</span>
          </div>
        </div>
      </div>
    </div>
  )
}


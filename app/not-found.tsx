import Link from 'next/link'
import Navigation from '@/components/Navigation'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-900">CoffeeCompass</h1>
          <Navigation />
        </div>
      </div>
      <div className="flex items-center justify-center min-h-[calc(100vh-80px)]">
        <div className="text-center">
          <h2 className="text-6xl font-bold text-gray-900 mb-4">404</h2>
          <div className="w-px h-16 bg-gray-300 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600 mb-8">This page could not be found.</p>
          <Link
            href="/"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Go back home
          </Link>
        </div>
      </div>
    </div>
  )
}


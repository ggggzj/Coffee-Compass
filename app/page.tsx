'use client'

import { useState, useEffect, useCallback } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import MapPane from '@/components/MapPane'
import ResultsList from '@/components/ResultsList'
import FilterBar from '@/components/FilterBar'
import ShopDrawer from '@/components/ShopDrawer'
import Navigation from '@/components/Navigation'
import { useDebounce } from '@/hooks/useDebounce'

export default function Home() {
  const searchParams = useSearchParams()
  const router = useRouter()

  // Initialize state from URL params, but only on client side to avoid hydration mismatch
  const [city, setCity] = useState<string>('Los Angeles')
  const [scene, setScene] = useState<string>('Study')
  const [sort, setSort] = useState<string>('Suitability')
  const [selectedShopId, setSelectedShopId] = useState<string | null>(null)
  const [mapBounds, setMapBounds] = useState<string | null>(null)
  const [hoveredShopId, setHoveredShopId] = useState<string | null>(null)
  const [isMounted, setIsMounted] = useState(false)

  // Initialize from URL params only after mount to avoid hydration mismatch
  useEffect(() => {
    setIsMounted(true)
    setCity(searchParams.get('city') || 'Los Angeles')
    setScene(searchParams.get('scene') || 'Study')
    setSort(searchParams.get('sort') || 'Suitability')
    setSelectedShopId(searchParams.get('shop') || null)
    setMapBounds(searchParams.get('bounds') || null)
  }, [searchParams])

  // Debounce map bounds updates
  const debouncedMapBounds = useDebounce(mapBounds, 400)

  // Update URL params when filters change
  useEffect(() => {
    const params = new URLSearchParams()
    if (city) params.set('city', city)
    if (scene) params.set('scene', scene)
    if (sort) params.set('sort', sort)
    if (selectedShopId) params.set('shop', selectedShopId)
    if (debouncedMapBounds) params.set('bounds', debouncedMapBounds)
    router.replace(`/?${params.toString()}`, { scroll: false })
  }, [city, scene, sort, selectedShopId, debouncedMapBounds, router])

  const handleMapBoundsChange = useCallback((bounds: string) => {
    setMapBounds(bounds)
  }, [])

  const handleShopClick = useCallback((shopId: string) => {
    setSelectedShopId(shopId)
  }, [])

  const handleCloseDrawer = useCallback(() => {
    setSelectedShopId(null)
  }, [])

  // Prevent hydration mismatch by not rendering until mounted
  if (!isMounted) {
    return (
      <div className="flex flex-col h-screen">
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex gap-6 items-center">
          <div className="h-8 bg-gray-200 rounded w-32 animate-pulse"></div>
          <div className="h-8 bg-gray-200 rounded w-32 animate-pulse"></div>
          <div className="h-8 bg-gray-200 rounded w-32 animate-pulse"></div>
        </div>
        <div className="flex flex-1 overflow-hidden">
          <div className="w-1/2 overflow-y-auto border-r border-gray-200 bg-gray-50"></div>
          <div className="w-1/2 bg-gray-100"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen">
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-900">CoffeeCompass</h1>
          <Navigation />
        </div>
      </div>
      <FilterBar
        city={city}
        scene={scene}
        sort={sort}
        onCityChange={setCity}
        onSceneChange={setScene}
        onSortChange={setSort}
      />
      <div className="flex flex-1 overflow-hidden">
        <div className="w-1/2 overflow-y-auto border-r border-gray-200">
          <ResultsList
            city={city}
            scene={scene}
            sort={sort}
            bounds={debouncedMapBounds}
            onShopClick={handleShopClick}
            onShopHover={setHoveredShopId}
            hoveredShopId={hoveredShopId}
          />
        </div>
        <div className="w-1/2">
          <MapPane
            city={city}
            onBoundsChange={handleMapBoundsChange}
            selectedShopId={selectedShopId}
            hoveredShopId={hoveredShopId}
            onShopClick={handleShopClick}
            initialBounds={debouncedMapBounds}
          />
        </div>
      </div>
      {selectedShopId && (
        <ShopDrawer shopId={selectedShopId} scene={scene} onClose={handleCloseDrawer} />
      )}
    </div>
  )
}


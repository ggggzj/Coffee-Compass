'use client'

import { useState, useEffect, useCallback } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import MapPane from '@/components/MapPane'
import ResultsList from '@/components/ResultsList'
import FilterBar from '@/components/FilterBar'
import ShopDrawer from '@/components/ShopDrawer'
import { useDebounce } from '@/hooks/useDebounce'

export default function Home() {
  const searchParams = useSearchParams()
  const router = useRouter()

  const [city, setCity] = useState<string>(searchParams.get('city') || 'Los Angeles')
  const [scene, setScene] = useState<string>(searchParams.get('scene') || 'Study')
  const [sort, setSort] = useState<string>(searchParams.get('sort') || 'Suitability')
  const [selectedShopId, setSelectedShopId] = useState<string | null>(
    searchParams.get('shop') || null
  )
  const [mapBounds, setMapBounds] = useState<string | null>(null)
  const [hoveredShopId, setHoveredShopId] = useState<string | null>(null)

  // Debounce map bounds updates
  const debouncedMapBounds = useDebounce(mapBounds, 400)

  // Update URL params when filters change
  useEffect(() => {
    const params = new URLSearchParams()
    if (city) params.set('city', city)
    if (scene) params.set('scene', scene)
    if (sort) params.set('sort', sort)
    if (selectedShopId) params.set('shop', selectedShopId)
    router.replace(`/?${params.toString()}`, { scroll: false })
  }, [city, scene, sort, selectedShopId, router])

  const handleMapBoundsChange = useCallback((bounds: string) => {
    setMapBounds(bounds)
  }, [])

  const handleShopClick = useCallback((shopId: string) => {
    setSelectedShopId(shopId)
  }, [])

  const handleCloseDrawer = useCallback(() => {
    setSelectedShopId(null)
  }, [])

  return (
    <div className="flex flex-col h-screen">
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
          />
        </div>
      </div>
      {selectedShopId && (
        <ShopDrawer shopId={selectedShopId} scene={scene} onClose={handleCloseDrawer} />
      )}
    </div>
  )
}


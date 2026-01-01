'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import Map, { Marker, ViewStateChangeEvent } from 'react-map-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { useQuery } from '@tanstack/react-query'

interface MapPaneProps {
  city: string
  onBoundsChange: (bounds: string) => void
  selectedShopId: string | null
  hoveredShopId: string | null
  onShopClick: (shopId: string) => void
}

// City center coordinates
const CITY_CENTERS: Record<string, [number, number]> = {
  'Los Angeles': [-118.2437, 34.0522],
  'San Francisco': [-122.4194, 37.7749],
  'New York': [-74.006, 40.7128],
}

async function fetchShopsForMap(city: string) {
  const params = new URLSearchParams()
  params.set('city', city)
  params.set('pageSize', '100')

  const response = await fetch(`/api/shops?${params.toString()}`)
  if (!response.ok) {
    throw new Error('Failed to fetch shops')
  }
  return response.json()
}

export default function MapPane({
  city,
  onBoundsChange,
  selectedShopId,
  hoveredShopId,
  onShopClick,
}: MapPaneProps) {
  const mapRef = useRef<any>(null)
  const [viewState, setViewState] = useState({
    longitude: CITY_CENTERS[city]?.[0] || -118.2437,
    latitude: CITY_CENTERS[city]?.[1] || 34.0522,
    zoom: 12,
  })

  const { data } = useQuery({
    queryKey: ['shops-map', city],
    queryFn: () => fetchShopsForMap(city),
  })

  const shops = data?.shops || []

  // Update map center when city changes
  useEffect(() => {
    const center = CITY_CENTERS[city]
    if (center) {
      setViewState((prev) => ({
        ...prev,
        longitude: center[0],
        latitude: center[1],
      }))
    }
  }, [city])

  // Handle map move/zoom and update bounds
  const handleMoveEnd = useCallback(() => {
    if (!mapRef.current) return

    const map = mapRef.current.getMap()
    const bounds = map.getBounds()
    const sw = bounds.getSouthWest()
    const ne = bounds.getNorthEast()

    const boundsString = `${sw.lng},${sw.lat},${ne.lng},${ne.lat}`
    onBoundsChange(boundsString)
  }, [onBoundsChange])

  const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN

  if (!mapboxToken) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <p className="text-red-600 mb-2">Missing Mapbox Token</p>
          <p className="text-sm text-gray-600">Please set NEXT_PUBLIC_MAPBOX_TOKEN in .env file</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full h-full">
      <Map
        ref={mapRef}
        {...viewState}
        onMove={(evt: ViewStateChangeEvent) => setViewState(evt.viewState)}
        onMoveEnd={handleMoveEnd}
        mapboxAccessToken={mapboxToken}
        style={{ width: '100%', height: '100%' }}
        mapStyle="mapbox://styles/mapbox/streets-v12"
      >
        {shops.map((shop: any) => {
          const isSelected = selectedShopId === shop.id
          const isHovered = hoveredShopId === shop.id

          return (
            <Marker
              key={shop.id}
              longitude={shop.longitude}
              latitude={shop.latitude}
              anchor="bottom"
              onClick={() => onShopClick(shop.id)}
            >
              <div
                className={`cursor-pointer transition-all ${
                  isSelected
                    ? 'scale-125 z-10'
                    : isHovered
                    ? 'scale-110 z-5'
                    : 'scale-100'
                }`}
              >
                <div
                  className={`w-6 h-6 rounded-full border-2 ${
                    isSelected
                      ? 'bg-blue-600 border-blue-800'
                      : isHovered
                      ? 'bg-blue-400 border-blue-600'
                      : 'bg-red-500 border-red-700'
                  }`}
                />
              </div>
            </Marker>
          )
        })}
      </Map>
    </div>
  )
}


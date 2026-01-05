'use client'

import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import Map, { Marker, ViewStateChangeEvent } from 'react-map-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { useQuery } from '@tanstack/react-query'
import Supercluster from 'supercluster'

interface MapPaneProps {
  city: string
  onBoundsChange: (bounds: string) => void
  selectedShopId: string | null
  hoveredShopId: string | null
  onShopClick: (shopId: string) => void
  initialBounds?: string | null
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
  initialBounds,
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

  // Setup marker clustering
  const clusterer = useMemo(() => {
    return new Supercluster({
      radius: 50,
      maxZoom: 14,
    })
  }, [])

  const points = useMemo(() => {
    return shops.map((shop: any) => ({
      type: 'Feature' as const,
      properties: {
        cluster: false,
        shopId: shop.id,
      },
      geometry: {
        type: 'Point' as const,
        coordinates: [shop.longitude, shop.latitude],
      },
    }))
  }, [shops])

  const clusters = useMemo(() => {
    if (points.length === 0) return []
    clusterer.load(points)
    
    // Calculate bounding box from current view
    const bbox: [number, number, number, number] = [
      viewState.longitude - 0.1, // minLng
      viewState.latitude - 0.1,  // minLat
      viewState.longitude + 0.1, // maxLng
      viewState.latitude + 0.1,  // maxLat
    ]
    
    return clusterer.getClusters(bbox, Math.floor(viewState.zoom))
  }, [points, viewState, clusterer])

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
        {clusters.map((cluster: any) => {
          const [longitude, latitude] = cluster.geometry.coordinates
          const { cluster: isCluster, point_count } = cluster.properties

          if (isCluster) {
            return (
              <Marker
                key={`cluster-${cluster.id}`}
                longitude={longitude}
                latitude={latitude}
                anchor="center"
              >
                <div className="cursor-pointer bg-blue-600 text-white rounded-full border-2 border-blue-800 flex items-center justify-center font-semibold text-sm min-w-[30px] h-[30px] px-2">
                  {point_count}
                </div>
              </Marker>
            )
          }

          const shopId = cluster.properties.shopId
          const shop = shops.find((s: any) => s.id === shopId)
          if (!shop) return null

          const isSelected = selectedShopId === shop.id
          const isHovered = hoveredShopId === shop.id

          return (
            <Marker
              key={shop.id}
              longitude={longitude}
              latitude={latitude}
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


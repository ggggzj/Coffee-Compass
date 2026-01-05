'use client'

import { useState, useRef, useEffect } from 'react'

interface FilterBarProps {
  city: string
  scene: string
  sort: string
  onCityChange: (city: string) => void
  onSceneChange: (scene: string) => void
  onSortChange: (sort: string) => void
}

const PRESET_CITIES = ['Los Angeles', 'San Francisco', 'New York']

export default function FilterBar({
  city,
  scene,
  sort,
  onCityChange,
  onSceneChange,
  onSortChange,
}: FilterBarProps) {
  const [isCustomCity, setIsCustomCity] = useState(!PRESET_CITIES.includes(city))
  const [customCity, setCustomCity] = useState(isCustomCity ? city : '')
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!PRESET_CITIES.includes(city)) {
      setIsCustomCity(true)
      setCustomCity(city)
    }
  }, [city])

  const handleCitySelectChange = (value: string) => {
    if (value === 'custom') {
      setIsCustomCity(true)
      setTimeout(() => inputRef.current?.focus(), 0)
    } else {
      setIsCustomCity(false)
      onCityChange(value)
    }
  }

  const handleCustomCityChange = (value: string) => {
    setCustomCity(value)
    onCityChange(value)
  }

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4 flex gap-6 items-center flex-wrap">
      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-gray-700">Location:</label>
        {isCustomCity ? (
          <div className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              value={customCity}
              onChange={(e) => handleCustomCityChange(e.target.value)}
              placeholder="Enter city name"
              className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-48"
            />
            <button
              onClick={() => {
                setIsCustomCity(false)
                onCityChange('Los Angeles')
              }}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Use preset
            </button>
          </div>
        ) : (
          <select
            value={city}
            onChange={(e) => handleCitySelectChange(e.target.value)}
            className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {PRESET_CITIES.map((presetCity) => (
              <option key={presetCity} value={presetCity}>
                {presetCity}
              </option>
            ))}
            <option value="custom">Custom location...</option>
          </select>
        )}
      </div>

      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-gray-700">Scene:</label>
        <select
          value={scene}
          onChange={(e) => onSceneChange(e.target.value)}
          className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="Study">Study</option>
          <option value="Remote Work">Remote Work</option>
          <option value="Date">Date</option>
          <option value="Meeting">Meeting</option>
        </select>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-gray-700">Sort:</label>
        <select
          value={sort}
          onChange={(e) => onSortChange(e.target.value)}
          className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="Distance">Distance</option>
          <option value="Rating">Rating</option>
          <option value="Suitability">Suitability</option>
        </select>
      </div>
    </div>
  )
}


'use client'

interface FilterBarProps {
  city: string
  scene: string
  sort: string
  onCityChange: (city: string) => void
  onSceneChange: (scene: string) => void
  onSortChange: (sort: string) => void
}

export default function FilterBar({
  city,
  scene,
  sort,
  onCityChange,
  onSceneChange,
  onSortChange,
}: FilterBarProps) {
  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4 flex gap-6 items-center">
      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-gray-700">City:</label>
        <select
          value={city}
          onChange={(e) => onCityChange(e.target.value)}
          className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="Los Angeles">Los Angeles</option>
          <option value="San Francisco">San Francisco</option>
          <option value="New York">New York</option>
        </select>
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


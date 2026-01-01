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
        <label className="text-sm font-medium text-gray-700">城市:</label>
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
        <label className="text-sm font-medium text-gray-700">场景:</label>
        <select
          value={scene}
          onChange={(e) => onSceneChange(e.target.value)}
          className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="Study">学习</option>
          <option value="Remote Work">远程工作</option>
          <option value="Date">约会</option>
          <option value="Meeting">会议</option>
        </select>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-gray-700">排序:</label>
        <select
          value={sort}
          onChange={(e) => onSortChange(e.target.value)}
          className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="Distance">距离</option>
          <option value="Rating">评分</option>
          <option value="Suitability">适用性</option>
        </select>
      </div>
    </div>
  )
}


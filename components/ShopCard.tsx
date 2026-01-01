'use client'

interface ShopCardProps {
  shop: {
    id: string
    name: string
    address: string
    rating: number
    priceLevel: number
    suitability?: {
      score: number
    } | null
  }
  scene: string
  onClick: () => void
  onHover: () => void
  onLeave: () => void
  isHovered: boolean
}

export default function ShopCard({
  shop,
  scene,
  onClick,
  onHover,
  onLeave,
  isHovered,
}: ShopCardProps) {
  const priceSymbols = '$'.repeat(shop.priceLevel)

  return (
    <div
      onClick={onClick}
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
      className={`p-4 border rounded-lg cursor-pointer transition-all ${
        isHovered
          ? 'border-blue-500 shadow-lg bg-blue-50'
          : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
      }`}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-lg text-gray-900">{shop.name}</h3>
        {shop.suitability && (
          <div className="flex items-center gap-1">
            <span className="text-xs font-medium text-gray-600">适用性</span>
            <span className="text-lg font-bold text-blue-600">{shop.suitability.score}</span>
          </div>
        )}
      </div>
      <p className="text-sm text-gray-600 mb-2">{shop.address}</p>
      <div className="flex items-center gap-4 text-sm">
        <div className="flex items-center gap-1">
          <span className="text-yellow-500">★</span>
          <span className="text-gray-700">{shop.rating.toFixed(1)}</span>
        </div>
        <div className="text-gray-600">{priceSymbols}</div>
      </div>
    </div>
  )
}


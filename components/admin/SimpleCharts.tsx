'use client'

import type { AdminMetrics } from '@/types/admin'

// Mock metrics data
const mockMetrics: AdminMetrics = {
  dau: [120, 135, 142, 128, 150, 165, 178],
  dauLabels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  searchToClickRate: 0.42,
  favoriteRate: 0.18,
  apiLatency: 145,
  errorRate: 0.02,
}

export default function SimpleCharts() {
  const metrics = mockMetrics
  const maxDau = Math.max(...metrics.dau)

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Daily Active Users (Last 7 Days)</h2>
      <div className="flex items-end justify-between gap-2 h-64">
        {metrics.dau.map((value, index) => {
          const height = (value / maxDau) * 100
          return (
            <div key={index} className="flex-1 flex flex-col items-center">
              <div className="w-full flex flex-col items-center justify-end h-full">
                <div
                  className="w-full bg-blue-600 rounded-t-lg transition-all hover:bg-blue-700"
                  style={{ height: `${height}%` }}
                  title={`${value} users`}
                />
              </div>
              <div className="mt-2 text-xs text-gray-600">{metrics.dauLabels[index]}</div>
              <div className="mt-1 text-xs font-semibold text-gray-900">{value}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}


'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

interface Report {
  id: string
  type: 'review' | 'shop' | 'user'
  targetId: string
  targetName: string
  reason: string
  reportedBy: string
  reportedAt: string
  createdAt: string
  status: 'pending' | 'resolved' | 'dismissed'
  user: {
    id: string
    name: string | null
    email: string | null
  }
}

function getStatusColor(status: Report['status']): string {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'resolved':
      return 'bg-green-100 text-green-800'
    case 'dismissed':
      return 'bg-gray-100 text-gray-800'
  }
}

function getTypeColor(type: Report['type']): string {
  switch (type) {
    case 'review':
      return 'bg-blue-100 text-blue-800'
    case 'shop':
      return 'bg-purple-100 text-purple-800'
    case 'user':
      return 'bg-red-100 text-red-800'
  }
}

async function fetchReports(status?: string) {
  const url = status ? `/api/admin/reports?status=${status}` : '/api/admin/reports'
  const response = await fetch(url)
  if (!response.ok) throw new Error('Failed to fetch reports')
  const data = await response.json()
  return data.reports || []
}

async function updateReportStatus(id: string, status: Report['status']) {
  const response = await fetch(`/api/admin/reports/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  })
  if (!response.ok) throw new Error('Failed to update report')
  return response.json()
}

export default function ReportsTable() {
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'resolved' | 'dismissed'>('all')

  const { data: reports = [], isLoading } = useQuery({
    queryKey: ['admin-reports', statusFilter],
    queryFn: () => fetchReports(statusFilter === 'all' ? undefined : statusFilter),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: Report['status'] }) =>
      updateReportStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-reports'] })
    },
  })

  const handleStatusChange = (reportId: string, newStatus: Report['status']) => {
    updateMutation.mutate({ id: reportId, status: newStatus })
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm">
      <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">Reports & Review Management</h2>
        <select
          value={statusFilter}
          onChange={(e) =>
            setStatusFilter(e.target.value as 'all' | 'pending' | 'resolved' | 'dismissed')
          }
          className="px-3 py-1 border border-gray-300 rounded-md text-sm"
        >
          <option value="all">All Status</option>
          <option value="pending">Pending</option>
          <option value="resolved">Resolved</option>
          <option value="dismissed">Dismissed</option>
        </select>
      </div>
      <div className="overflow-x-auto">
        {reports.length === 0 ? (
          <div className="p-6 text-center text-gray-500">No reports found</div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Target
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Reason
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Reported By
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {reports.map((report: Report) => (
                <tr key={report.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getTypeColor(
                        report.type
                      )}`}
                    >
                      {report.type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{report.targetName}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{report.reason}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">
                      {report.user?.name || report.user?.email || 'Unknown'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(
                        report.status
                      )}`}
                    >
                      {report.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end gap-2">
                      {report.status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleStatusChange(report.id, 'resolved')}
                            disabled={updateMutation.isPending}
                            className="text-green-600 hover:text-green-900 disabled:opacity-50"
                          >
                            Resolve
                          </button>
                          <button
                            onClick={() => handleStatusChange(report.id, 'dismissed')}
                            disabled={updateMutation.isPending}
                            className="text-gray-600 hover:text-gray-900 disabled:opacity-50"
                          >
                            Dismiss
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}


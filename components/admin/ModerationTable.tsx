'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { ShopStatus } from '@/types/admin'

interface Submission {
  id: string
  name: string
  address: string
  city: string
  latitude: number
  longitude: number
  priceLevel: number
  tags: string[]
  features: any
  status: ShopStatus
  submittedAt: string
  createdAt: string
  user: {
    id: string
    name: string | null
    email: string | null
  }
  shop: any | null
}

function getStatusColor(status: ShopStatus): string {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'approved':
      return 'bg-green-100 text-green-800'
    case 'rejected':
      return 'bg-red-100 text-red-800'
  }
}

async function fetchSubmissions() {
  const response = await fetch('/api/admin/submissions')
  if (!response.ok) throw new Error('Failed to fetch submissions')
  const data = await response.json()
  return data.submissions || []
}

async function updateSubmissionStatus(id: string, status: ShopStatus) {
  const response = await fetch(`/api/admin/submissions/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  })
  if (!response.ok) throw new Error('Failed to update submission')
  return response.json()
}

export default function ModerationTable() {
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState<ShopStatus | 'all'>('all')

  const { data: submissions = [], isLoading } = useQuery({
    queryKey: ['admin-submissions', statusFilter],
    queryFn: async () => {
      const all = await fetchSubmissions()
      return statusFilter === 'all' ? all : all.filter((s: Submission) => s.status === statusFilter)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: ShopStatus }) =>
      updateSubmissionStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-submissions'] })
    },
  })

  const handleStatusChange = (submissionId: string, newStatus: ShopStatus) => {
    if (confirm(`Are you sure you want to ${newStatus} this submission?`)) {
      updateMutation.mutate({ id: submissionId, status: newStatus })
    }
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
        <h2 className="text-xl font-semibold text-gray-900">Shop Moderation</h2>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as ShopStatus | 'all')}
          className="px-3 py-1 border border-gray-300 rounded-md text-sm"
        >
          <option value="all">All Status</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>
      <div className="overflow-x-auto">
        {submissions.length === 0 ? (
          <div className="p-6 text-center text-gray-500">No submissions found</div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Shop Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Submitted By
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Submitted
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {submissions.map((submission: Submission) => (
                <tr key={submission.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{submission.name}</div>
                    <div className="text-sm text-gray-500">{submission.address}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{submission.city}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {submission.user.name || submission.user.email || 'Unknown'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(
                        submission.status
                      )}`}
                    >
                      {submission.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(submission.submittedAt || submission.createdAt).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end gap-2">
                      {submission.status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleStatusChange(submission.id, 'approved')}
                            disabled={updateMutation.isPending}
                            className="text-green-600 hover:text-green-900 disabled:opacity-50"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleStatusChange(submission.id, 'rejected')}
                            disabled={updateMutation.isPending}
                            className="text-red-600 hover:text-red-900 disabled:opacity-50"
                          >
                            Reject
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


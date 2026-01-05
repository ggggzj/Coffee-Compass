'use client'

import AdminLayout from '@/components/admin/AdminLayout'
import ModerationTable from '@/components/admin/ModerationTable'
import ReportsTable from '@/components/admin/ReportsTable'
import MetricsCards from '@/components/admin/MetricsCards'
import SimpleCharts from '@/components/admin/SimpleCharts'

export default function AdminPage() {
  return (
    <AdminLayout>
      <div className="space-y-6">
        <MetricsCards />
        <SimpleCharts />
        <ModerationTable />
        <ReportsTable />
      </div>
    </AdminLayout>
  )
}


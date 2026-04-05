"use client"

import { Suspense } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { KpiCards } from "@/components/dashboard/kpi-cards"
import { RevenueChart } from "@/components/dashboard/revenue-chart"
import { TenantDashboard } from "@/components/dashboard/tenant-dashboard"
import { useAuthStore } from "@/store/auth"
import type { OwnerDashboardResponse } from "@/hooks/use-dashboard"

function ChartSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-64 w-full" />
      </CardContent>
    </Card>
  )
}

// Mock data for fallback
const mockData: OwnerDashboardResponse = {
  total_bookings: 42,
  total_revenue: 125000,
  occupancy_rate: 78.5,
  active_bookings: 12,
  monthly_revenue: [
    { month: "2024-01", revenue: 15000 },
    { month: "2024-02", revenue: 22000 },
    { month: "2024-03", revenue: 18000 },
    { month: "2024-04", revenue: 25000 },
    { month: "2024-05", revenue: 28000 },
    { month: "2024-06", revenue: 17000 },
  ],
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const isTenant = user?.role === "tenant"

  if (isTenant) {
    return <TenantDashboard />
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Обзор</h1>
      <KpiCards data={mockData} />
      <Suspense fallback={<ChartSkeleton />}>
        <Card>
          <CardHeader>
            <CardTitle>Доход по месяцам</CardTitle>
          </CardHeader>
          <CardContent>
            <RevenueChart data={mockData.monthly_revenue} />
          </CardContent>
        </Card>
      </Suspense>
    </div>
  )
}

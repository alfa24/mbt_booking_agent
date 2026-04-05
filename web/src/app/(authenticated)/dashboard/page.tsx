import { Suspense } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { KpiCards } from "@/components/dashboard/kpi-cards"
import { RevenueChart } from "@/components/dashboard/revenue-chart"
import type { OwnerDashboardResponse } from "@/hooks/use-dashboard"

async function getDashboard(): Promise<OwnerDashboardResponse> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
  
  try {
    const res = await fetch(`${apiUrl}/dashboard/owner`, { 
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
      },
    })
    
    if (!res.ok) {
      throw new Error("Failed to fetch dashboard")
    }
    
    return res.json()
  } catch (_error) {
    // Return mock data if API is unavailable
    return {
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
  }
}

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

export default async function DashboardPage() {
  const data = await getDashboard()

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Обзор</h1>
      <KpiCards data={data} />
      <Suspense fallback={<ChartSkeleton />}>
        <Card>
          <CardHeader>
            <CardTitle>Доход по месяцам</CardTitle>
          </CardHeader>
          <CardContent>
            <RevenueChart data={data.monthly_revenue} />
          </CardContent>
        </Card>
      </Suspense>
    </div>
  )
}

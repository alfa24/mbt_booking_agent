"use client"

import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"

export interface MonthlyRevenue {
  month: string
  revenue: number
}

export interface OwnerDashboardResponse {
  total_bookings: number
  total_revenue: number
  occupancy_rate: number
  active_bookings: number
  monthly_revenue: MonthlyRevenue[]
}

export interface HouseStatsResponse {
  occupancy_rate: number
  total_revenue: number
  total_bookings: number
}

async function fetchOwnerDashboard(): Promise<OwnerDashboardResponse> {
  const response = await api.get("dashboard/owner")
  return response.json<OwnerDashboardResponse>()
}

async function fetchHouseStats(houseId: number): Promise<HouseStatsResponse> {
  const response = await api.get(`dashboard/houses/${houseId}/stats`)
  return response.json<HouseStatsResponse>()
}

export function useOwnerDashboard() {
  return useQuery({
    queryKey: ["dashboard", "owner"],
    queryFn: fetchOwnerDashboard,
  })
}

export function useHouseStats(houseId: number) {
  return useQuery({
    queryKey: ["dashboard", "house", houseId, "stats"],
    queryFn: () => fetchHouseStats(houseId),
    enabled: !!houseId,
  })
}

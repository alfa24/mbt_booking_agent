"use client"

import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"

export interface RevenueByHouse {
  house_id: number
  house_name: string
  revenue: number
}

export interface BookingsByMonth {
  month: string
  count: number
}

export interface LeaderboardResponse {
  bookings_by_month: BookingsByMonth[]
  revenue_by_house: RevenueByHouse[]
}

export interface LeaderboardFilters {
  period?: string
}

async function fetchLeaderboard(filters?: LeaderboardFilters): Promise<LeaderboardResponse> {
  const searchParams = new URLSearchParams()
  
  if (filters?.period) searchParams.append("period", filters.period)

  const queryString = searchParams.toString()
  const url = queryString ? `dashboard/leaderboard?${queryString}` : "dashboard/leaderboard"
  
  const response = await api.get(url)
  return response.json<LeaderboardResponse>()
}

export function useLeaderboard(filters?: LeaderboardFilters) {
  return useQuery({
    queryKey: ["leaderboard", filters],
    queryFn: () => fetchLeaderboard(filters),
  })
}

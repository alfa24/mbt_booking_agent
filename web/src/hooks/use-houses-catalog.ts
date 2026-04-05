"use client"

import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"

export interface House {
  id: number
  owner_id: number
  name: string
  description: string | null
  capacity: number
  is_active: boolean
  created_at: string
}

interface PaginatedHousesResponse {
  items: House[]
  total: number
  limit: number
  offset: number
}

async function fetchActiveHouses(): Promise<House[]> {
  const searchParams = new URLSearchParams({ is_active: "true" })
  const response = await api.get(`houses?${searchParams.toString()}`)
  const data = await response.json<PaginatedHousesResponse>()
  return data.items
}

export function useHousesCatalog() {
  return useQuery({
    queryKey: ["houses", "catalog"],
    queryFn: fetchActiveHouses,
  })
}

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

export interface OccupiedDate {
  check_in: string
  check_out: string
  booking_id: number
}

export interface HouseCalendarResponse {
  house_id: number
  occupied_dates: OccupiedDate[]
}

async function fetchHouseById(id: number): Promise<House> {
  const response = await api.get(`houses/${id}`)
  return response.json<House>()
}

async function fetchHouseCalendar(id: number): Promise<HouseCalendarResponse> {
  const response = await api.get(`houses/${id}/calendar`)
  return response.json<HouseCalendarResponse>()
}

export function useHouseDetails(id: number) {
  return useQuery({
    queryKey: ["houses", id],
    queryFn: () => fetchHouseById(id),
    enabled: !!id,
  })
}

export function useHouseCalendar(id: number) {
  return useQuery({
    queryKey: ["houses", id, "calendar"],
    queryFn: () => fetchHouseCalendar(id),
    enabled: !!id,
  })
}

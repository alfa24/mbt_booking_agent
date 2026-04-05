
"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/auth"

export type BookingStatus = "pending" | "confirmed" | "cancelled" | "completed"

export interface GuestInfo {
  tariff_id: number
  count: number
}

export interface Booking {
  id: number
  house_id: number
  tenant_id: number
  check_in: string
  check_out: string
  guests_planned: GuestInfo[]
  guests_actual: GuestInfo[] | null
  total_amount: number | null
  status: BookingStatus
  created_at: string
}

export interface CreateBookingRequest {
  house_id: number
  check_in: string
  check_out: string
  guests: GuestInfo[]
}

interface PaginatedBookingsResponse {
  items: Booking[]
  total: number
  limit: number
  offset: number
}

async function fetchUserBookings(userId: number): Promise<Booking[]> {
  const searchParams = new URLSearchParams({ user_id: String(userId) })
  const response = await api.get(`bookings?${searchParams.toString()}`)
  const data = await response.json<PaginatedBookingsResponse>()
  return data.items
}

async function createBooking(data: CreateBookingRequest, tenantId: number): Promise<Booking> {
  const response = await api.post("bookings", {
    json: data,
    searchParams: { tenant_id: tenantId },
  })
  return response.json<Booking>()
}

async function cancelBooking(id: number, tenantId: number): Promise<void> {
  await api.delete(`bookings/${id}`, { searchParams: { tenant_id: tenantId } })
}

export function useUserBookings(userId: number | undefined) {
  return useQuery({
    queryKey: ["bookings", "user", userId],
    queryFn: () => fetchUserBookings(userId!),
    enabled: !!userId,
  })
}

export function useCreateBooking() {
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  const tenantId = user?.id

  return useMutation({
    mutationFn: (data: CreateBookingRequest) => {
      if (!tenantId) throw new Error("User not authenticated")
      return createBooking(data, tenantId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookings"] })
      queryClient.invalidateQueries({ queryKey: ["houses"] })
      toast.success("Бронирование успешно создано")
    },
    onError: () => {
      toast.error("Не удалось создать бронирование")
    },
  })
}

export function useCancelBooking() {
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  const tenantId = user?.id

  return useMutation({
    mutationFn: (id: number) => {
      if (!tenantId) throw new Error("User not authenticated")
      return cancelBooking(id, tenantId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookings"] })
      toast.success("Бронирование отменено")
    },
    onError: () => {
      toast.error("Не удалось отменить бронирование")
    },
  })
}

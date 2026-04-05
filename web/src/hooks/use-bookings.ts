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

export interface UpdateBookingRequest {
  check_in?: string
  check_out?: string
  guests?: GuestInfo[]
  status?: BookingStatus
}

export interface BookingFilters {
  house_id?: number
  status?: BookingStatus
  check_in_from?: string
  check_in_to?: string
  check_out_from?: string
  check_out_to?: string
}

interface PaginatedBookingsResponse {
  items: Booking[]
  total: number
  limit: number
  offset: number
}

async function fetchBookings(filters?: BookingFilters): Promise<Booking[]> {
  const searchParams = new URLSearchParams()
  
  if (filters?.house_id) searchParams.append("house_id", String(filters.house_id))
  if (filters?.status) searchParams.append("status", filters.status)
  if (filters?.check_in_from) searchParams.append("check_in_from", filters.check_in_from)
  if (filters?.check_in_to) searchParams.append("check_in_to", filters.check_in_to)
  if (filters?.check_out_from) searchParams.append("check_out_from", filters.check_out_from)
  if (filters?.check_out_to) searchParams.append("check_out_to", filters.check_out_to)

  const queryString = searchParams.toString()
  const url = queryString ? `bookings?${queryString}` : "bookings"
  
  const response = await api.get(url)
  const data = await response.json<PaginatedBookingsResponse>()
  return data.items
}

async function updateBooking({
  id,
  data,
  tenantId,
}: {
  id: number
  data: UpdateBookingRequest
  tenantId: number
}): Promise<Booking> {
  const response = await api.patch(`bookings/${id}`, {
    json: data,
    searchParams: { tenant_id: tenantId },
  })
  return response.json<Booking>()
}

async function cancelBooking(id: number, tenantId: number): Promise<void> {
  await api.delete(`bookings/${id}`, { searchParams: { tenant_id: tenantId } })
}

async function createBooking(data: CreateBookingRequest, tenantId: number): Promise<Booking> {
  const response = await api.post("bookings", {
    json: data,
    searchParams: { tenant_id: tenantId },
  })
  return response.json<Booking>()
}

export function useBookings(filters?: BookingFilters) {
  return useQuery({
    queryKey: ["bookings", filters],
    queryFn: () => fetchBookings(filters),
  })
}

export function useUpdateBooking() {
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  const tenantId = user?.id

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateBookingRequest }) => {
      if (!tenantId) throw new Error("User not authenticated")
      return updateBooking({ id, data, tenantId })
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["bookings"] })
      queryClient.invalidateQueries({ queryKey: ["bookings", variables.id] })
      toast.success("Бронирование успешно обновлено")
    },
    onError: () => {
      toast.error("Не удалось обновить бронирование")
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
      toast.success("Бронирование успешно создано")
    },
    onError: () => {
      toast.error("Не удалось создать бронирование")
    },
  })
}

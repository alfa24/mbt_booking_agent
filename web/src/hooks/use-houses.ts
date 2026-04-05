"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
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

export interface CreateHouseRequest {
  name: string
  description?: string
  capacity: number
  is_active?: boolean
}

export interface UpdateHouseRequest {
  name?: string
  description?: string
  capacity?: number
  is_active?: boolean
}

interface PaginatedHousesResponse {
  items: House[]
  total: number
  limit: number
  offset: number
}

async function fetchHouses(): Promise<House[]> {
  const response = await api.get("houses")
  const data = await response.json<PaginatedHousesResponse>()
  return data.items
}

async function createHouse(data: CreateHouseRequest): Promise<House> {
  const response = await api.post("houses", { json: data })
  return response.json<House>()
}

async function updateHouse({
  id,
  data,
}: {
  id: number
  data: UpdateHouseRequest
}): Promise<House> {
  const response = await api.patch(`houses/${id}`, { json: data })
  return response.json<House>()
}

async function deleteHouse(id: number): Promise<void> {
  await api.delete(`houses/${id}`)
}

export function useHouses() {
  return useQuery({
    queryKey: ["houses"],
    queryFn: fetchHouses,
  })
}

export function useCreateHouse() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createHouse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["houses"] })
      toast.success("Дом успешно создан")
    },
    onError: () => {
      toast.error("Не удалось создать дом")
    },
  })
}

export function useUpdateHouse() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateHouse,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["houses"] })
      queryClient.invalidateQueries({ queryKey: ["houses", variables.id] })
      toast.success("Дом успешно обновлен")
    },
    onError: () => {
      toast.error("Не удалось обновить дом")
    },
  })
}

export function useDeleteHouse() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteHouse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["houses"] })
      toast.success("Дом успешно удален")
    },
    onError: () => {
      toast.error("Не удалось удалить дом")
    },
  })
}

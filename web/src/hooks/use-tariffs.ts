"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { api } from "@/lib/api"

export interface Tariff {
  id: number
  name: string
  amount: number
  created_at: string
}

export interface CreateTariffRequest {
  name: string
  amount: number
}

export interface UpdateTariffRequest {
  name?: string
  amount?: number
}

async function fetchTariffs(): Promise<Tariff[]> {
  const response = await api.get("tariffs")
  return response.json<Tariff[]>()
}

async function createTariff(data: CreateTariffRequest): Promise<Tariff> {
  const response = await api.post("tariffs", { json: data })
  return response.json<Tariff>()
}

async function updateTariff({
  id,
  data,
}: {
  id: number
  data: UpdateTariffRequest
}): Promise<Tariff> {
  const response = await api.patch(`tariffs/${id}`, { json: data })
  return response.json<Tariff>()
}

async function deleteTariff(id: number): Promise<void> {
  await api.delete(`tariffs/${id}`)
}

export function useTariffs() {
  return useQuery({
    queryKey: ["tariffs"],
    queryFn: fetchTariffs,
  })
}

export function useCreateTariff() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createTariff,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tariffs"] })
      toast.success("Тариф успешно создан")
    },
    onError: () => {
      toast.error("Не удалось создать тариф")
    },
  })
}

export function useUpdateTariff() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateTariff,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["tariffs"] })
      queryClient.invalidateQueries({ queryKey: ["tariffs", variables.id] })
      toast.success("Тариф успешно обновлен")
    },
    onError: () => {
      toast.error("Не удалось обновить тариф")
    },
  })
}

export function useDeleteTariff() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteTariff,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tariffs"] })
      toast.success("Тариф успешно удален")
    },
    onError: () => {
      toast.error("Не удалось удалить тариф")
    },
  })
}

"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { api } from "@/lib/api"

export interface ConsumableNote {
  id: number
  house_id: number
  created_by: number
  name: string
  comment: string | null
  created_at: string
}

export interface CreateNoteRequest {
  house_id: number
  name: string
  comment?: string
  created_by: number
}

export interface UpdateNoteRequest {
  name?: string
  comment?: string
}

interface PaginatedConsumableNotesResponse {
  items: ConsumableNote[]
  total: number
  limit: number
  offset: number
}

async function fetchConsumableNotes(houseId?: number): Promise<ConsumableNote[]> {
  const url = houseId ? `consumable-notes?house_id=${houseId}` : "consumable-notes"
  const response = await api.get(url)
  const data = await response.json<PaginatedConsumableNotesResponse>()
  return data.items
}

async function createNote(data: CreateNoteRequest): Promise<ConsumableNote> {
  const response = await api.post("consumable-notes", { json: data })
  return response.json<ConsumableNote>()
}

async function updateNote({
  id,
  data,
}: {
  id: number
  data: UpdateNoteRequest
}): Promise<ConsumableNote> {
  const response = await api.patch(`consumable-notes/${id}`, { json: data })
  return response.json<ConsumableNote>()
}

async function deleteNote(id: number): Promise<void> {
  await api.delete(`consumable-notes/${id}`)
}

export function useConsumableNotes(houseId?: number) {
  return useQuery({
    queryKey: ["consumable-notes", houseId],
    queryFn: () => fetchConsumableNotes(houseId),
  })
}

export function useCreateNote() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createNote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["consumable-notes"] })
      toast.success("Заметка успешно создана")
    },
    onError: () => {
      toast.error("Не удалось создать заметку")
    },
  })
}

export function useUpdateNote() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateNote,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["consumable-notes"] })
      queryClient.invalidateQueries({ queryKey: ["consumable-notes", variables.id] })
      toast.success("Заметка успешно обновлена")
    },
    onError: () => {
      toast.error("Не удалось обновить заметку")
    },
  })
}

export function useDeleteNote() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteNote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["consumable-notes"] })
      toast.success("Заметка успешно удалена")
    },
    onError: () => {
      toast.error("Не удалось удалить заметку")
    },
  })
}

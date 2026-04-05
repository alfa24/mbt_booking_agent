"use client"

import { useState } from "react"
import { format } from "date-fns"
import { ru } from "date-fns/locale"
import { Pencil, Plus, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  useConsumableNotes,
  useDeleteNote,
  type ConsumableNote,
} from "@/hooks/use-consumables"
import { useHouses } from "@/hooks/use-houses"
import { ConsumableFormDialog } from "./consumable-form-dialog"

export function ConsumablesList() {
  const { data: houses } = useHouses()
  const { data: notes, isLoading } = useConsumableNotes()
  const deleteNote = useDeleteNote()
  const [selectedHouse, setSelectedHouse] = useState<string>("all")
  const [editingNote, setEditingNote] = useState<ConsumableNote | null>(null)
  const [isCreateOpen, setIsCreateOpen] = useState(false)

  const filteredNotes =
    selectedHouse === "all"
      ? notes
      : notes?.filter((note) => note.house_id === Number(selectedHouse))

  const groupedNotes = filteredNotes?.reduce(
    (acc, note) => {
      const houseName = houses?.find((h) => h.id === note.house_id)?.name || `Дом #${note.house_id}`
      if (!acc[houseName]) acc[houseName] = []
      acc[houseName].push(note)
      return acc
    },
    {} as Record<string, ConsumableNote[]>
  )

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4">
          <div>
            <CardTitle>Заметки по расходникам</CardTitle>
            <CardDescription>Заметки о необходимых расходных материалах</CardDescription>
          </div>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="size-4" data-icon />
            Добавить заметку
          </Button>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Select value={selectedHouse} onValueChange={setSelectedHouse}>
              <SelectTrigger className="w-64">
                <SelectValue placeholder="Все дома" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все дома</SelectItem>
                {houses?.map((house) => (
                  <SelectItem key={house.id} value={String(house.id)}>
                    {house.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex flex-col gap-6">
            {filteredNotes?.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">Нет заметок</p>
            ) : (
              Object.entries(groupedNotes || {}).map(([houseName, houseNotes]) => (
                <div key={houseName} className="flex flex-col gap-3">
                  <h3 className="font-semibold text-lg">{houseName}</h3>
                  <div className="flex flex-col gap-3">
                    {houseNotes.map((note) => (
                      <Card key={note.id}>
                        <CardContent className="flex items-start justify-between p-4">
                          <div className="flex flex-col gap-1">
                            <span className="font-medium">{note.name}</span>
                            {note.comment && (
                              <span className="text-sm text-muted-foreground">
                                {note.comment}
                              </span>
                            )}
                            <span className="text-xs text-muted-foreground">
                              {format(new Date(note.created_at), "dd MMMM yyyy", { locale: ru })}
                            </span>
                          </div>
                          <div className="flex gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => setEditingNote(note)}
                            >
                              <Pencil className="size-4" data-icon />
                              <span className="sr-only">Редактировать</span>
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => deleteNote.mutate(note.id)}
                              disabled={deleteNote.isPending}
                            >
                              <Trash2 className="size-4" data-icon />
                              <span className="sr-only">Удалить</span>
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      <ConsumableFormDialog
        open={isCreateOpen}
        onOpenChange={setIsCreateOpen}
      />

      <ConsumableFormDialog
        note={editingNote}
        open={!!editingNote}
        onOpenChange={(open) => !open && setEditingNote(null)}
      />
    </>
  )
}

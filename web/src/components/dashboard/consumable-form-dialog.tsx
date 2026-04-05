"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  useCreateNote,
  useUpdateNote,
  type ConsumableNote,
} from "@/hooks/use-consumables"
import { useHouses } from "@/hooks/use-houses"
import { useAuthStore } from "@/store/auth"

interface ConsumableFormDialogProps {
  note?: ConsumableNote | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ConsumableFormDialog({
  note,
  open,
  onOpenChange,
}: ConsumableFormDialogProps) {
  const { data: houses } = useHouses()
  const { user } = useAuthStore()
  const createNote = useCreateNote()
  const updateNote = useUpdateNote()

  const [houseId, setHouseId] = useState("")
  const [name, setName] = useState("")
  const [comment, setComment] = useState("")

  const isEditing = !!note
  const isPending = createNote.isPending || updateNote.isPending

  useEffect(() => {
    if (note) {
      setHouseId(String(note.house_id))
      setName(note.name)
      setComment(note.comment || "")
    } else {
      setHouseId("")
      setName("")
      setComment("")
    }
  }, [note, open])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (isEditing && note) {
      updateNote.mutate(
        { id: note.id, data: { name, comment: comment || undefined } },
        { onSuccess: () => onOpenChange(false) }
      )
    } else {
      if (!user?.id) return
      createNote.mutate(
        {
          house_id: Number(houseId),
          name,
          comment: comment || undefined,
          created_by: user.id,
        },
        { onSuccess: () => onOpenChange(false) }
      )
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>
              {isEditing ? "Редактировать заметку" : "Добавить заметку"}
            </DialogTitle>
            <DialogDescription>
              {isEditing
                ? "Измените информацию о заметке"
                : "Заполните информацию о новой заметке"}
            </DialogDescription>
          </DialogHeader>

          <div className="flex flex-col gap-4 py-4">
            {!isEditing && (
              <div className="flex flex-col gap-2">
                <Label htmlFor="house">Дом</Label>
                <Select value={houseId} onValueChange={setHouseId} required>
                  <SelectTrigger id="house">
                    <SelectValue placeholder="Выберите дом" />
                  </SelectTrigger>
                  <SelectContent>
                    {houses?.map((house) => (
                      <SelectItem key={house.id} value={String(house.id)}>
                        {house.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div className="flex flex-col gap-2">
              <Label htmlFor="name">Название</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Например: Моющее средство"
                required
              />
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="comment">Комментарий</Label>
              <Textarea
                id="comment"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Дополнительная информация"
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isPending}
            >
              Отмена
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? "Сохранение..." : "Сохранить"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

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
  useCreateHouse,
  useUpdateHouse,
  type House,
} from "@/hooks/use-houses"

interface HouseFormDialogProps {
  house?: House | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function HouseFormDialog({
  house,
  open,
  onOpenChange,
}: HouseFormDialogProps) {
  const createHouse = useCreateHouse()
  const updateHouse = useUpdateHouse()

  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [capacity, setCapacity] = useState("")

  const isEditing = !!house
  const isPending = createHouse.isPending || updateHouse.isPending

  useEffect(() => {
    if (house) {
      setName(house.name)
      setDescription(house.description || "")
      setCapacity(String(house.capacity))
    } else {
      setName("")
      setDescription("")
      setCapacity("")
    }
  }, [house, open])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const parsedCapacity = Number(capacity)
    if (!Number.isFinite(parsedCapacity) || parsedCapacity <= 0) {
      return
    }

    const data = {
      name,
      description: description || undefined,
      capacity: parsedCapacity,
    }

    if (isEditing && house) {
      updateHouse.mutate(
        { id: house.id, data },
        { onSuccess: () => onOpenChange(false) }
      )
    } else {
      createHouse.mutate(data, { onSuccess: () => onOpenChange(false) })
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>
              {isEditing ? "Редактировать дом" : "Добавить дом"}
            </DialogTitle>
            <DialogDescription>
              {isEditing
                ? "Измените информацию о доме"
                : "Заполните информацию о новом доме"}
            </DialogDescription>
          </DialogHeader>

          <div className="flex flex-col gap-4 py-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="name">Название</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Например: Старый дом"
                required
              />
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="description">Описание</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Описание дома"
                rows={3}
              />
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="capacity">Вместимость (человек)</Label>
              <Input
                id="capacity"
                type="number"
                min={1}
                value={capacity}
                onChange={(e) => setCapacity(e.target.value)}
                placeholder="Например: 6"
                required
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

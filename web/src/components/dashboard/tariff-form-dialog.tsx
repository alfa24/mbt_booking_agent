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
import {
  useCreateTariff,
  useUpdateTariff,
  type Tariff,
} from "@/hooks/use-tariffs"

interface TariffFormDialogProps {
  tariff?: Tariff | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function TariffFormDialog({
  tariff,
  open,
  onOpenChange,
}: TariffFormDialogProps) {
  const createTariff = useCreateTariff()
  const updateTariff = useUpdateTariff()

  const [name, setName] = useState("")
  const [amount, setAmount] = useState("")

  const isEditing = !!tariff
  const isPending = createTariff.isPending || updateTariff.isPending

  useEffect(() => {
    if (tariff) {
      setName(tariff.name)
      setAmount(String(tariff.amount))
    } else {
      setName("")
      setAmount("")
    }
  }, [tariff, open])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const parsedAmount = Number(amount)
    if (!Number.isFinite(parsedAmount) || parsedAmount < 0) {
      return
    }

    const data = {
      name,
      amount: parsedAmount,
    }

    if (isEditing && tariff) {
      updateTariff.mutate(
        { id: tariff.id, data },
        { onSuccess: () => onOpenChange(false) }
      )
    } else {
      createTariff.mutate(data, { onSuccess: () => onOpenChange(false) })
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>
              {isEditing ? "Редактировать тариф" : "Добавить тариф"}
            </DialogTitle>
            <DialogDescription>
              {isEditing
                ? "Измените информацию о тарифе"
                : "Заполните информацию о новом тарифе"}
            </DialogDescription>
          </DialogHeader>

          <div className="flex flex-col gap-4 py-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="name">Название</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Например: Взрослый"
                required
              />
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="amount">Цена за ночь (₽)</Label>
              <Input
                id="amount"
                type="number"
                min={0}
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Например: 1500"
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

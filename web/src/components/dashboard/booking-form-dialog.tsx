"use client"

import { useState } from "react"
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
import { useCreateBooking, type GuestInfo } from "@/hooks/use-bookings"
import { useTariffs } from "@/hooks/use-tariffs"
import { useAuthStore } from "@/store/auth"
import type { House } from "@/hooks/use-houses"

interface BookingFormDialogProps {
  house: House | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function BookingFormDialog({
  house,
  open,
  onOpenChange,
}: BookingFormDialogProps) {
  const createBooking = useCreateBooking()
  const { data: tariffs } = useTariffs()
  const { user } = useAuthStore()

  const [checkIn, setCheckIn] = useState("")
  const [checkOut, setCheckOut] = useState("")
  const [guestCounts, setGuestCounts] = useState<Record<number, number>>({})

  const isPending = createBooking.isPending

  const handleGuestCountChange = (tariffId: number, count: string) => {
    const numCount = parseInt(count) || 0
    setGuestCounts((prev) => ({
      ...prev,
      [tariffId]: numCount,
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!house || !user) return

    const guests: GuestInfo[] = Object.entries(guestCounts)
      .filter(([, count]) => count > 0)
      .map(([tariff_id, count]) => ({
        tariff_id: Number(tariff_id),
        count,
      }))

    if (guests.length === 0) {
      return
    }

    createBooking.mutate(
      {
        house_id: house.id,
        check_in: checkIn,
        check_out: checkOut,
        guests,
      },
      {
        onSuccess: () => {
          setCheckIn("")
          setCheckOut("")
          setGuestCounts({})
          onOpenChange(false)
        },
      }
    )
  }

  const handleClose = () => {
    setCheckIn("")
    setCheckOut("")
    setGuestCounts({})
    onOpenChange(false)
  }

  if (!house) return null

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Забронировать {house.name}</DialogTitle>
            <DialogDescription>
              Выберите даты и укажите состав группы
            </DialogDescription>
          </DialogHeader>

          <div className="flex flex-col gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-2">
                <Label htmlFor="check_in">Заезд</Label>
                <Input
                  id="check_in"
                  type="date"
                  value={checkIn}
                  onChange={(e) => setCheckIn(e.target.value)}
                  required
                />
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="check_out">Выезд</Label>
                <Input
                  id="check_out"
                  type="date"
                  value={checkOut}
                  onChange={(e) => setCheckOut(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="flex flex-col gap-3">
              <Label>Состав группы</Label>
              {tariffs?.map((tariff) => (
                <div key={tariff.id} className="flex items-center gap-3">
                  <Label htmlFor={`tariff-${tariff.id}`} className="flex-1 text-sm font-normal">
                    {tariff.name} ({tariff.amount} ₽/ночь)
                  </Label>
                  <Input
                    id={`tariff-${tariff.id}`}
                    type="number"
                    min={0}
                    value={guestCounts[tariff.id] || ""}
                    onChange={(e) => handleGuestCountChange(tariff.id, e.target.value)}
                    className="w-20"
                    placeholder="0"
                  />
                </div>
              ))}
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isPending}
            >
              Отмена
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? "Создание..." : "Забронировать"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

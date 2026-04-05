"use client"

import { format } from "date-fns"
import { ru } from "date-fns/locale"
import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import {
  useUpdateBooking,
  useCancelBooking,
  type Booking,
  type BookingStatus,
} from "@/hooks/use-bookings"
import { useHouses } from "@/hooks/use-houses"
import { useTariffs } from "@/hooks/use-tariffs"

interface BookingDetailDialogProps {
  booking: Booking | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

const statusLabels: Record<BookingStatus, string> = {
  pending: "Ожидает",
  confirmed: "Подтверждено",
  cancelled: "Отменено",
  completed: "Завершено",
}

const statusVariants: Record<BookingStatus, "default" | "secondary" | "outline" | "destructive"> = {
  pending: "secondary",
  confirmed: "default",
  cancelled: "destructive",
  completed: "outline",
}

export function BookingDetailDialog({
  booking,
  open,
  onOpenChange,
}: BookingDetailDialogProps) {
  const { data: houses } = useHouses()
  const { data: tariffs } = useTariffs()
  const updateBooking = useUpdateBooking()
  const cancelBooking = useCancelBooking()

  if (!booking) return null

  const house = houses?.find((h) => h.id === booking.house_id)

  const handleConfirm = () => {
    updateBooking.mutate(
      { id: booking.id, data: { status: "confirmed" } },
      { onSuccess: () => onOpenChange(false) }
    )
  }

  const handleCancel = () => {
    cancelBooking.mutate(booking.id, { onSuccess: () => onOpenChange(false) })
  }

  const canConfirm = booking.status === "pending"
  const canCancel = booking.status === "pending" || booking.status === "confirmed"

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle>Бронирование #{booking.id}</SheetTitle>
          <SheetDescription>
            Подробная информация о бронировании
          </SheetDescription>
        </SheetHeader>

        <div className="flex flex-col gap-6 py-6">
          <div className="flex flex-col gap-2">
            <span className="text-sm text-muted-foreground">Статус</span>
            <Badge variant={statusVariants[booking.status]}>
              {statusLabels[booking.status]}
            </Badge>
          </div>

          <div className="flex flex-col gap-2">
            <span className="text-sm text-muted-foreground">Дом</span>
            <span className="font-medium">{house?.name || `Дом #${booking.house_id}`}</span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-2">
              <span className="text-sm text-muted-foreground">Заезд</span>
              <span className="font-medium">
                {format(new Date(booking.check_in), "dd MMMM yyyy", { locale: ru })}
              </span>
            </div>
            <div className="flex flex-col gap-2">
              <span className="text-sm text-muted-foreground">Выезд</span>
              <span className="font-medium">
                {format(new Date(booking.check_out), "dd MMMM yyyy", { locale: ru })}
              </span>
            </div>
          </div>

          <Separator />

          <div className="flex flex-col gap-2">
            <span className="text-sm text-muted-foreground">Гости (план)</span>
            <div className="flex flex-col gap-1">
              {booking.guests_planned.map((guest, index) => {
                const tariff = tariffs?.find((t) => t.id === guest.tariff_id)
                return (
                  <span key={index} className="text-sm">
                    {tariff?.name || `Тариф #${guest.tariff_id}`}: {guest.count} чел.
                  </span>
                )
              })}
            </div>
          </div>

          {booking.total_amount !== null && (
            <>
              <Separator />
              <div className="flex flex-col gap-2">
                <span className="text-sm text-muted-foreground">Итоговая сумма</span>
                <span className="text-xl font-bold">
                  {new Intl.NumberFormat("ru-RU", {
                    style: "currency",
                    currency: "RUB",
                  }).format(booking.total_amount)}
                </span>
              </div>
            </>
          )}

          <Separator />

          <div className="flex flex-col gap-2">
            <span className="text-sm text-muted-foreground">Создано</span>
            <span className="text-sm">
              {format(new Date(booking.created_at), "dd MMMM yyyy HH:mm", { locale: ru })}
            </span>
          </div>

          <div className="flex gap-2 mt-4">
            {canConfirm && (
              <Button
                className="flex-1"
                onClick={handleConfirm}
                disabled={updateBooking.isPending}
              >
                Подтвердить
              </Button>
            )}
            {canCancel && (
              <Button
                variant="destructive"
                className="flex-1"
                onClick={handleCancel}
                disabled={cancelBooking.isPending}
              >
                Отменить
              </Button>
            )}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}

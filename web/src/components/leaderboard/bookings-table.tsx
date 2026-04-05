"use client"

import { format } from "date-fns"
import { ru } from "date-fns/locale"
import { Eye } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { type Booking, type BookingStatus } from "@/hooks/use-bookings"
import { type House } from "@/hooks/use-houses"
import { BookingDetailDialog } from "@/components/dashboard/booking-detail-dialog"
import { useState } from "react"

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

interface BookingsTableProps {
  bookings: Booking[] | undefined
  houses: House[] | undefined
  isLoading: boolean
}

export function LeaderboardBookingsTable({ bookings, houses, isLoading }: BookingsTableProps) {
  const [viewingBooking, setViewingBooking] = useState<Booking | null>(null)

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Бронирования</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Дом</TableHead>
                <TableHead>Заезд</TableHead>
                <TableHead>Выезд</TableHead>
                <TableHead>Статус</TableHead>
                <TableHead className="text-right">Сумма</TableHead>
                <TableHead className="text-right">Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {bookings?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground">
                    Нет бронирований
                  </TableCell>
                </TableRow>
              ) : (
                bookings?.map((booking) => (
                  <TableRow key={booking.id}>
                    <TableCell className="font-medium">#{booking.id}</TableCell>
                    <TableCell>
                      {houses?.find((h) => h.id === booking.house_id)?.name ||
                        `Дом #${booking.house_id}`}
                    </TableCell>
                    <TableCell>
                      {format(new Date(booking.check_in), "dd MMM yyyy", { locale: ru })}
                    </TableCell>
                    <TableCell>
                      {format(new Date(booking.check_out), "dd MMM yyyy", { locale: ru })}
                    </TableCell>
                    <TableCell>
                      <Badge variant={statusVariants[booking.status]}>
                        {statusLabels[booking.status]}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {booking.total_amount
                        ? new Intl.NumberFormat("ru-RU", {
                            style: "currency",
                            currency: "RUB",
                            maximumFractionDigits: 0,
                          }).format(booking.total_amount)
                        : "—"}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setViewingBooking(booking)}
                      >
                        <Eye className="size-4" data-icon />
                        <span className="sr-only">Просмотр</span>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <BookingDetailDialog
        booking={viewingBooking}
        open={!!viewingBooking}
        onOpenChange={(open) => !open && setViewingBooking(null)}
      />
    </>
  )
}

"use client"

import { useState } from "react"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useBookings, type Booking, type BookingStatus } from "@/hooks/use-bookings"
import { useHouses, type House } from "@/hooks/use-houses"
import { BookingDetailDialog } from "./booking-detail-dialog"

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

export function BookingsTable() {
  const { data: houses } = useHouses()
  const [selectedHouse, setSelectedHouse] = useState<string>("all")
  const [selectedStatus, setSelectedStatus] = useState<string>("all")
  const [viewingBooking, setViewingBooking] = useState<Booking | null>(null)

  const filters = {
    house_id: selectedHouse !== "all" ? Number(selectedHouse) : undefined,
    status: selectedStatus !== "all" ? (selectedStatus as BookingStatus) : undefined,
  }

  const { data: bookings, isLoading } = useBookings(filters)

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
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
          <div className="flex flex-wrap gap-4 mb-4">
            <Select value={selectedHouse} onValueChange={setSelectedHouse}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Все дома" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все дома</SelectItem>
                {houses?.map((house: House) => (
                  <SelectItem key={house.id} value={String(house.id)}>
                    {house.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Все статусы" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все статусы</SelectItem>
                <SelectItem value="pending">Ожидает</SelectItem>
                <SelectItem value="confirmed">Подтверждено</SelectItem>
                <SelectItem value="completed">Завершено</SelectItem>
                <SelectItem value="cancelled">Отменено</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Дом</TableHead>
                <TableHead>Заезд</TableHead>
                <TableHead>Выезд</TableHead>
                <TableHead>Статус</TableHead>
                <TableHead className="text-right">Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {bookings?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground">
                    Нет бронирований
                  </TableCell>
                </TableRow>
              ) : (
                bookings?.map((booking) => (
                  <TableRow key={booking.id}>
                    <TableCell className="font-medium">#{booking.id}</TableCell>
                    <TableCell>
                      {houses?.find((h: House) => h.id === booking.house_id)?.name ||
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

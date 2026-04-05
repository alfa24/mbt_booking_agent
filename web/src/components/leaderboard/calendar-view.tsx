"use client"

import { useState, useMemo } from "react"
import {
  format,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  startOfWeek,
  endOfWeek,
  isSameMonth,
  addMonths,
  subMonths,
} from "date-fns"
import { ru } from "date-fns/locale"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import { type Booking, type BookingStatus } from "@/hooks/use-bookings"
import { type House } from "@/hooks/use-houses"
import { cn } from "@/lib/utils"

const statusVariants: Record<BookingStatus, "default" | "secondary" | "outline" | "destructive"> = {
  pending: "secondary",
  confirmed: "default",
  cancelled: "destructive",
  completed: "outline",
}

interface CalendarViewProps {
  bookings: Booking[] | undefined
  houses: House[] | undefined
}

export function CalendarView({ bookings, houses }: CalendarViewProps) {
  const [currentMonth, setCurrentMonth] = useState(new Date())

  const days = useMemo(() => {
    const start = startOfWeek(startOfMonth(currentMonth), { locale: ru })
    const end = endOfWeek(endOfMonth(currentMonth), { locale: ru })
    return eachDayOfInterval({ start, end })
  }, [currentMonth])

  const activeHouses = useMemo(() => {
    return houses?.filter((h) => h.is_active) ?? []
  }, [houses])

  const getBookingsForDayAndHouse = (day: Date, houseId: number) => {
    return bookings?.filter((booking) => {
      const checkIn = new Date(booking.check_in)
      const checkOut = new Date(booking.check_out)
      const dayStart = new Date(day.setHours(0, 0, 0, 0))
      const dayEnd = new Date(day.setHours(23, 59, 59, 999))
      return (
        booking.house_id === houseId &&
        checkIn <= dayEnd &&
        checkOut >= dayStart &&
        booking.status !== "cancelled"
      )
    })
  }

  const weekDays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Календарь бронирований</CardTitle>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={() => setCurrentMonth((prev) => subMonths(prev, 1))}
          >
            <ChevronLeft className="size-4" data-icon />
          </Button>
          <span className="text-sm font-medium min-w-32 text-center">
            {format(currentMonth, "LLLL yyyy", { locale: ru })}
          </span>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setCurrentMonth((prev) => addMonths(prev, 1))}
          >
            <ChevronRight className="size-4" data-icon />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="w-full">
          <div className="min-w-[800px]">
            {/* Header with days */}
            <div className="grid" style={{ gridTemplateColumns: `120px repeat(${days.length}, minmax(40px, 1fr))` }}>
              <div className="p-2 font-medium text-sm border-b">Дом</div>
              {days.map((day, index) => (
                <div
                  key={day.toISOString()}
                  className={cn(
                    "p-2 text-center text-xs border-b",
                    !isSameMonth(day, currentMonth) && "text-muted-foreground bg-muted/50",
                    index % 7 === 5 && "bg-muted/30",
                    index % 7 === 6 && "bg-muted/30"
                  )}
                >
                  <div className="font-medium">{format(day, "d")}</div>
                  <div className="text-[10px] text-muted-foreground">{weekDays[index % 7]}</div>
                </div>
              ))}
            </div>

            {/* Rows for each house */}
            {activeHouses.map((house) => (
              <div
                key={house.id}
                className="grid border-b last:border-b-0"
                style={{ gridTemplateColumns: `120px repeat(${days.length}, minmax(40px, 1fr))` }}
              >
                <div className="p-2 text-sm font-medium truncate border-r bg-muted/20">
                  {house.name}
                </div>
                {days.map((day) => {
                  const dayBookings = getBookingsForDayAndHouse(day, house.id)
                  const hasBooking = dayBookings && dayBookings.length > 0
                  const mainBooking = hasBooking ? dayBookings[0] : null

                  return (
                    <div
                      key={`${house.id}-${day.toISOString()}`}
                      className={cn(
                        "p-1 min-h-12 border-r last:border-r-0 relative",
                        !isSameMonth(day, currentMonth) && "bg-muted/30",
                        hasBooking && "bg-primary/5"
                      )}
                    >
                      {mainBooking && (
                        <Badge
                          variant={statusVariants[mainBooking.status]}
                          className="text-[10px] px-1 py-0 h-auto w-full justify-center truncate"
                        >
                          #{mainBooking.id}
                        </Badge>
                      )}
                      {dayBookings && dayBookings.length > 1 && (
                        <div className="absolute -top-1 -right-1 size-4 bg-primary text-primary-foreground rounded-full text-[10px] flex items-center justify-center">
                          {dayBookings.length}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            ))}
          </div>
          <ScrollBar orientation="horizontal" />
        </ScrollArea>

        {/* Legend */}
        <div className="flex flex-wrap gap-4 mt-4 text-sm">
          <div className="flex items-center gap-2">
            <Badge variant="default" className="text-xs">Подтверждено</Badge>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-xs">Ожидает</Badge>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">Завершено</Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

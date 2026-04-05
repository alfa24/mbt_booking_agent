"use client"

import { format } from "date-fns"
import { ru } from "date-fns/locale"
import { Calendar, Home, Clock } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { useBookings, type BookingStatus } from "@/hooks/use-bookings"
import { useHouses } from "@/hooks/use-houses"
import { useAuthStore } from "@/store/auth"

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

export function TenantDashboard() {
  const { user } = useAuthStore()
  const { data: bookings, isLoading: isLoadingBookings } = useBookings()
  const { data: houses, isLoading: isLoadingHouses } = useHouses()

  const myBookings = bookings?.filter((b) => b.tenant_id === user?.id) || []
  const activeBookings = myBookings.filter((b) => b.status === "confirmed" || b.status === "pending")
  const upcomingBooking = activeBookings
    .filter((b) => new Date(b.check_in) >= new Date())
    .sort((a, b) => new Date(a.check_in).getTime() - new Date(b.check_in).getTime())[0]

  if (isLoadingBookings || isLoadingHouses) {
    return (
      <div className="flex flex-col gap-6">
        <h1 className="text-2xl font-bold">Мой кабинет</h1>
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-16" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Мой кабинет</h1>
      
      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Всего бронирований</CardTitle>
            <Calendar className="size-4 text-muted-foreground" data-icon />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{myBookings.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Активные брони</CardTitle>
            <Clock className="size-4 text-muted-foreground" data-icon />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeBookings.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Доступные дома</CardTitle>
            <Home className="size-4 text-muted-foreground" data-icon />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{houses?.filter((h) => h.is_active).length || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Upcoming Booking */}
      {upcomingBooking && (
        <Card>
          <CardHeader>
            <CardTitle>Ближайшее бронирование</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="font-medium">
                  {houses?.find((h) => h.id === upcomingBooking.house_id)?.name || `Дом #${upcomingBooking.house_id}`}
                </span>
                <Badge variant={statusVariants[upcomingBooking.status]}>
                  {statusLabels[upcomingBooking.status]}
                </Badge>
              </div>
              <div className="text-sm text-muted-foreground">
                Заезд: {format(new Date(upcomingBooking.check_in), "dd MMMM yyyy", { locale: ru })}
              </div>
              <div className="text-sm text-muted-foreground">
                Выезд: {format(new Date(upcomingBooking.check_out), "dd MMMM yyyy", { locale: ru })}
              </div>
              {upcomingBooking.total_amount && (
                <div className="text-sm font-medium">
                  Сумма: {upcomingBooking.total_amount.toLocaleString()} ₽
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Bookings */}
      <Card>
        <CardHeader>
          <CardTitle>История бронирований</CardTitle>
        </CardHeader>
        <CardContent>
          {myBookings.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">
              У вас пока нет бронирований
            </p>
          ) : (
            <div className="flex flex-col gap-3">
              {myBookings.slice(0, 5).map((booking) => (
                <div
                  key={booking.id}
                  className="flex items-center justify-between border-b pb-3 last:border-0"
                >
                  <div className="flex flex-col gap-1">
                    <span className="font-medium">
                      {houses?.find((h) => h.id === booking.house_id)?.name || `Дом #${booking.house_id}`}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {format(new Date(booking.check_in), "dd MMM", { locale: ru })} - {format(new Date(booking.check_out), "dd MMM yyyy", { locale: ru })}
                    </span>
                  </div>
                  <Badge variant={statusVariants[booking.status]}>
                    {statusLabels[booking.status]}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

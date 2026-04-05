"use client"

import Link from "next/link"
import { Calendar, Home, XCircle, CheckCircle, Clock, Ban } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useAuthStore } from "@/store/auth"
import { useUserBookings, useCancelBooking, type Booking, type BookingStatus } from "@/hooks/use-tenant-bookings"
import { format, parseISO } from "date-fns"
import { ru } from "date-fns/locale"

const statusLabels: Record<BookingStatus, string> = {
  pending: "Ожидает подтверждения",
  confirmed: "Подтверждено",
  cancelled: "Отменено",
  completed: "Завершено",
}

const statusIcons: Record<BookingStatus, React.ReactNode> = {
  pending: <Clock className="size-4" />,
  confirmed: <CheckCircle className="size-4" />,
  cancelled: <Ban className="size-4" />,
  completed: <CheckCircle className="size-4" />,
}

const statusVariants: Record<BookingStatus, "default" | "secondary" | "destructive" | "outline"> = {
  pending: "secondary",
  confirmed: "default",
  cancelled: "destructive",
  completed: "outline",
}

function BookingCard({ booking, onCancel }: { booking: Booking; onCancel?: (id: number) => void }) {
  const canCancel = booking.status === "pending" || booking.status === "confirmed"

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-lg">Бронирование #{booking.id}</CardTitle>
            <CardDescription>
              Создано {format(parseISO(booking.created_at), "d MMMM yyyy", { locale: ru })}
            </CardDescription>
          </div>
          <Badge variant={statusVariants[booking.status]} className="flex items-center gap-1">
            {statusIcons[booking.status]}
            {statusLabels[booking.status]}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-2 text-sm">
          <Home className="size-4 text-muted-foreground" />
          <span>Дом #{booking.house_id}</span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <Calendar className="size-4 text-muted-foreground" />
          <span>
            {format(parseISO(booking.check_in), "d MMMM", { locale: ru })} — {format(parseISO(booking.check_out), "d MMMM yyyy", { locale: ru })}
          </span>
        </div>
        {booking.total_amount !== null && (
          <div className="text-sm">
            <span className="text-muted-foreground">Сумма: </span>
            <strong>{booking.total_amount.toLocaleString('ru-RU')} ₽</strong>
          </div>
        )}
        {canCancel && onCancel && (
          <Button 
            variant="outline" 
            size="sm" 
            className="w-full mt-2"
            onClick={() => onCancel(booking.id)}
          >
            <XCircle className="size-4 mr-2" />
            Отменить бронирование
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

export default function TenantBookingsPage() {
  const { user } = useAuthStore()
  const { data: bookings, isLoading } = useUserBookings(user?.id)
  const cancelMutation = useCancelBooking()

  const handleCancel = (id: number) => {
    if (confirm("Вы уверены, что хотите отменить бронирование?")) {
      cancelMutation.mutate(id)
    }
  }

  const filterBookings = (status: BookingStatus | "all") => {
    if (!bookings) return []
    if (status === "all") return bookings
    return bookings.filter((b) => b.status === status)
  }

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <h1 className="text-2xl font-bold">Мои бронирования</h1>
        <div className="grid gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-48" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  const allBookings = filterBookings("all")

  if (allBookings.length === 0) {
    return (
      <div className="flex flex-col gap-6">
        <h1 className="text-2xl font-bold">Мои бронирования</h1>
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground mb-4">У вас пока нет бронирований</p>
            <Button asChild>
              <Link href="/tenant/houses">Найти дом</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Мои бронирования</h1>
        <Button asChild>
          <Link href="/tenant/bookings/new">Новое бронирование</Link>
        </Button>
      </div>

      <Tabs defaultValue="all" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="all">Все</TabsTrigger>
          <TabsTrigger value="pending">Ожидают</TabsTrigger>
          <TabsTrigger value="confirmed">Подтверждены</TabsTrigger>
          <TabsTrigger value="completed">Завершены</TabsTrigger>
          <TabsTrigger value="cancelled">Отменены</TabsTrigger>
        </TabsList>
        
        <TabsContent value="all" className="mt-4">
          <div className="grid gap-4">
            {filterBookings("all").map((booking) => (
              <BookingCard 
                key={booking.id} 
                booking={booking} 
                onCancel={handleCancel}
              />
            ))}
          </div>
        </TabsContent>
        
        <TabsContent value="pending" className="mt-4">
          <div className="grid gap-4">
            {filterBookings("pending").map((booking) => (
              <BookingCard 
                key={booking.id} 
                booking={booking} 
                onCancel={handleCancel}
              />
            ))}
            {filterBookings("pending").length === 0 && (
              <p className="text-center text-muted-foreground py-8">Нет ожидающих бронирований</p>
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="confirmed" className="mt-4">
          <div className="grid gap-4">
            {filterBookings("confirmed").map((booking) => (
              <BookingCard 
                key={booking.id} 
                booking={booking} 
                onCancel={handleCancel}
              />
            ))}
            {filterBookings("confirmed").length === 0 && (
              <p className="text-center text-muted-foreground py-8">Нет подтвержденных бронирований</p>
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="completed" className="mt-4">
          <div className="grid gap-4">
            {filterBookings("completed").map((booking) => (
              <BookingCard key={booking.id} booking={booking} />
            ))}
            {filterBookings("completed").length === 0 && (
              <p className="text-center text-muted-foreground py-8">Нет завершенных бронирований</p>
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="cancelled" className="mt-4">
          <div className="grid gap-4">
            {filterBookings("cancelled").map((booking) => (
              <BookingCard key={booking.id} booking={booking} />
            ))}
            {filterBookings("cancelled").length === 0 && (
              <p className="text-center text-muted-foreground py-8">Нет отмененных бронирований</p>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

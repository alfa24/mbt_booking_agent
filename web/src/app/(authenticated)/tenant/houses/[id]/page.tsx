"use client"

import Link from "next/link"
import { useRouter, useParams } from "next/navigation"
import { Users, Calendar, ArrowLeft, Home } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { useHouseDetails, useHouseCalendar } from "@/hooks/use-house-details"
import { format, parseISO, isWithinInterval } from "date-fns"
import { ru } from "date-fns/locale"

export default function HouseDetailsPage() {
  const params = useParams()
  const router = useRouter()
  
  // Handle params safely - useParams may return empty object on first render
  const id = params?.id ? (Array.isArray(params.id) ? params.id[0] : params.id) : undefined
  const houseId = id ? parseInt(id, 10) : NaN
  
  const { data: house, isLoading: isLoadingHouse } = useHouseDetails(houseId)
  const { data: calendar, isLoading: isLoadingCalendar } = useHouseCalendar(houseId)

  const isLoading = isLoadingHouse || isLoadingCalendar
  
  // Wait for params to be available
  if (!params || !id) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton className="h-8 w-64" />
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-full" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-32 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton className="h-8 w-64" />
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-full" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-32 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!house) {
    return (
      <div className="flex flex-col gap-6">
        <h1 className="text-2xl font-bold">Дом не найден</h1>
        <Button variant="outline" asChild>
          <Link href="/tenant/houses">
            <ArrowLeft className="size-4 mr-2" />
            Вернуться к списку
          </Link>
        </Button>
      </div>
    )
  }

  const occupiedDates = calendar?.occupied_dates || []

  // Generate next 3 months for calendar view
  const generateCalendarDays = () => {
    const days = []
    const today = new Date()
    const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
    const endOfThreeMonths = new Date(today.getFullYear(), today.getMonth() + 3, 0)
    
    for (let d = new Date(startOfMonth); d <= endOfThreeMonths; d.setDate(d.getDate() + 1)) {
      const dateStr = format(d, "yyyy-MM-dd")
      const isOccupied = occupiedDates.some((range) => {
        const checkIn = parseISO(range.check_in)
        const checkOut = parseISO(range.check_out)
        return isWithinInterval(d, { start: checkIn, end: checkOut })
      })
      days.push({ date: new Date(d), dateStr, isOccupied })
    }
    return days
  }

  const calendarDays = generateCalendarDays()
  const months = Array.from(new Set(calendarDays.map(d => format(d.date, "MMMM yyyy", { locale: ru }))))

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" asChild>
          <Link href="/tenant/houses">
            <ArrowLeft className="size-4" />
          </Link>
        </Button>
        <h1 className="text-2xl font-bold">{house.name}</h1>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Home className="size-5" />
              Информация о доме
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <p className="text-muted-foreground">
              {house.description || "Описание отсутствует"}
            </p>
            <div className="flex items-center gap-2 text-sm">
              <Users className="size-4 text-muted-foreground" />
              <span>Вместимость: <strong>{house.capacity} человек</strong></span>
            </div>
            <Badge variant={house.is_active ? "default" : "secondary"}>
              {house.is_active ? "Доступен для бронирования" : "Недоступен"}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Забронировать</CardTitle>
            <CardDescription>
              Выберите даты и оформите бронирование
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              className="w-full"
              onClick={() => router.push(`/tenant/bookings/new?houseId=${house.id}`)}
            >
              <Calendar className="size-4 mr-2" />
              Забронировать
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="size-5" />
            Календарь занятости
          </CardTitle>
          <CardDescription>
            Красным отмечены занятые даты
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-3">
            {months.map((month) => (
              <div key={month} className="space-y-2">
                <h3 className="font-semibold capitalize">{month}</h3>
                <div className="grid grid-cols-7 gap-1 text-center text-xs">
                  {["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"].map((day) => (
                    <div key={day} className="p-1 text-muted-foreground font-medium">
                      {day}
                    </div>
                  ))}
                  {calendarDays
                    .filter((d) => format(d.date, "MMMM yyyy", { locale: ru }) === month)
                    .map((day, idx) => {
                      const dayOfWeek = day.date.getDay() || 7
                      const offset = idx === 0 ? dayOfWeek - 1 : 0
                      
                      return (
                        <>
                          {idx === 0 && offset > 0 && 
                            Array.from({ length: offset }).map((_, i) => (
                              <div key={`empty-${i}`} />
                            ))
                          }
                          <div
                            key={day.dateStr}
                            className={`p-1 rounded text-xs ${
                              day.isOccupied
                                ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                                : "bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                            }`}
                            title={day.isOccupied ? "Занято" : "Свободно"}
                          >
                            {format(day.date, "d")}
                          </div>
                        </>
                      )
                    })}
                </div>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-4 mt-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-green-50 border border-green-200 dark:bg-green-900/30" />
              <span>Свободно</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-red-100 border border-red-200 dark:bg-red-900/30" />
              <span>Занято</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

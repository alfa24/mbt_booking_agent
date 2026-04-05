"use client"

import { useState, useEffect, useMemo } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import Link from "next/link"
import { ArrowLeft, Calendar, Users, Plus, Minus, Home } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { useHousesCatalog } from "@/hooks/use-houses-catalog"
import { useTariffs } from "@/hooks/use-tariffs"
import { useCreateBooking } from "@/hooks/use-tenant-bookings"
import { format, addDays, parseISO, isBefore } from "date-fns"

interface GuestSelection {
  tariff_id: number
  count: number
}

export default function NewBookingPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const preselectedHouseId = searchParams.get("houseId")

  const { data: houses, isLoading: isLoadingHouses } = useHousesCatalog()
  const { data: tariffs, isLoading: isLoadingTariffs } = useTariffs()
  const createMutation = useCreateBooking()

  const [selectedHouseId, setSelectedHouseId] = useState<string>(preselectedHouseId || "")
  const [checkIn, setCheckIn] = useState<string>("")
  const [checkOut, setCheckOut] = useState<string>("")
  const [guests, setGuests] = useState<GuestSelection[]>([])


  // Calculate total cost
  const totalCost = useMemo(() => {
    if (!checkIn || !checkOut || guests.length === 0 || !tariffs) return 0
    
    const start = parseISO(checkIn)
    const end = parseISO(checkOut)
    const nights = Math.max(0, Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)))
    
    if (nights <= 0) return 0

    return guests.reduce((total, guest) => {
      const tariff = tariffs.find((t) => t.id === guest.tariff_id)
      if (!tariff) return total
      return total + tariff.amount * guest.count * nights
    }, 0)
  }, [checkIn, checkOut, guests, tariffs])

  // Add guest row
  const addGuest = () => {
    if (tariffs && tariffs.length > 0) {
      setGuests([...guests, { tariff_id: tariffs[0].id, count: 1 }])
    }
  }

  // Remove guest row
  const removeGuest = (index: number) => {
    setGuests(guests.filter((_, i) => i !== index))
  }

  // Update guest
  const updateGuest = (index: number, field: keyof GuestSelection, value: number) => {
    const newGuests = [...guests]
    newGuests[index] = { ...newGuests[index], [field]: value }
    setGuests(newGuests)
  }

  // Initialize with one guest row when tariffs load
  useEffect(() => {
    if (tariffs && tariffs.length > 0 && guests.length === 0) {
      setGuests([{ tariff_id: tariffs[0].id, count: 1 }])
    }
  }, [tariffs, guests.length])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedHouseId || !checkIn || !checkOut || guests.length === 0) {
      return
    }

    // Filter out guests with count 0
    const validGuests = guests.filter((g) => g.count > 0)
    
    if (validGuests.length === 0) {
      return
    }

    createMutation.mutate(
      {
        house_id: parseInt(selectedHouseId, 10),
        check_in: checkIn,
        check_out: checkOut,
        guests: validGuests,
      },
      {
        onSuccess: () => {
          router.push("/tenant/bookings")
        },
      }
    )
  }

  const isLoading = isLoadingHouses || isLoadingTariffs

  // Set minimum date to today
  const minDate = format(new Date(), "yyyy-MM-dd")

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton className="h-8 w-64" />
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-48" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" asChild>
          <Link href="/tenant/houses">
            <ArrowLeft className="size-4" />
          </Link>
        </Button>
        <h1 className="text-2xl font-bold">Новое бронирование</h1>
      </div>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Детали бронирования</CardTitle>
            <CardDescription>
              Выберите дом, даты и количество гостей
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* House Selection */}
            <div className="space-y-2">
              <Label htmlFor="house">
                <Home className="size-4 inline mr-2" />
                Дом
              </Label>
              <Select value={selectedHouseId} onValueChange={setSelectedHouseId}>
                <SelectTrigger id="house">
                  <SelectValue placeholder="Выберите дом" />
                </SelectTrigger>
                <SelectContent>
                  {houses?.map((house) => (
                    <SelectItem key={house.id} value={house.id.toString()}>
                      {house.name} (до {house.capacity} чел.)
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="check-in">
                  <Calendar className="size-4 inline mr-2" />
                  Дата заезда
                </Label>
                <Input
                  id="check-in"
                  type="date"
                  min={minDate}
                  value={checkIn}
                  onChange={(e) => {
                    setCheckIn(e.target.value)
                    // Reset check-out if it's before new check-in
                    if (checkOut && isBefore(parseISO(checkOut), parseISO(e.target.value))) {
                      setCheckOut("")
                    }
                  }}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="check-out">
                  <Calendar className="size-4 inline mr-2" />
                  Дата выезда
                </Label>
                <Input
                  id="check-out"
                  type="date"
                  min={checkIn ? format(addDays(parseISO(checkIn), 1), "yyyy-MM-dd") : minDate}
                  value={checkOut}
                  onChange={(e) => setCheckOut(e.target.value)}
                  required
                  disabled={!checkIn}
                />
              </div>
            </div>

            {/* Guests */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label>
                  <Users className="size-4 inline mr-2" />
                  Гости
                </Label>
                <Button type="button" variant="outline" size="sm" onClick={addGuest}>
                  <Plus className="size-4 mr-1" />
                  Добавить
                </Button>
              </div>

              {guests.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  Добавьте хотя бы одного гостя
                </p>
              )}

              {guests.map((guest, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Select
                    value={guest.tariff_id.toString()}
                    onValueChange={(value) => updateGuest(index, "tariff_id", parseInt(value))}
                  >
                    <SelectTrigger className="flex-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {tariffs?.map((tariff) => (
                        <SelectItem key={tariff.id} value={tariff.id.toString()}>
                          {tariff.name} ({(tariff.amount / 100).toFixed(2)} ₽/ночь)
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  
                  <div className="flex items-center gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      className="size-8"
                      onClick={() => updateGuest(index, "count", Math.max(0, guest.count - 1))}
                    >
                      <Minus className="size-4" />
                    </Button>
                    <span className="w-8 text-center">{guest.count}</span>
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      className="size-8"
                      onClick={() => updateGuest(index, "count", guest.count + 1)}
                    >
                      <Plus className="size-4" />
                    </Button>
                  </div>

                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="size-8 text-destructive"
                    onClick={() => removeGuest(index)}
                  >
                    <Minus className="size-4" />
                  </Button>
                </div>
              ))}
            </div>

            {/* Total */}
            {totalCost > 0 && (
              <div className="pt-4 border-t">
                <div className="flex items-center justify-between text-lg">
                  <span>Итого:</span>
                  <strong className="text-xl">{(totalCost / 100).toFixed(2)} ₽</strong>
                </div>
                {checkIn && checkOut && (
                  <p className="text-sm text-muted-foreground mt-1">
                    {Math.ceil((parseISO(checkOut).getTime() - parseISO(checkIn).getTime()) / (1000 * 60 * 60 * 24))} ночей
                  </p>
                )}
              </div>
            )}

            {/* Submit */}
            <div className="flex gap-4 pt-4">
              <Button 
                type="submit" 
                className="flex-1"
                disabled={createMutation.isPending || !selectedHouseId || !checkIn || !checkOut || guests.length === 0}
              >
                {createMutation.isPending ? "Создание..." : "Забронировать"}
              </Button>
              <Button type="button" variant="outline" asChild>
                <Link href="/tenant/houses">Отмена</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}

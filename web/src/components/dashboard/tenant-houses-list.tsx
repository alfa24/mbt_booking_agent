"use client"

import { useState } from "react"
import { Calendar, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { useHouses, type House } from "@/hooks/use-houses"
import { BookingFormDialog } from "./booking-form-dialog"

export function TenantHousesList() {
  const { data: houses, isLoading } = useHouses()
  const [selectedHouse, setSelectedHouse] = useState<House | null>(null)
  const [isBookingOpen, setIsBookingOpen] = useState(false)

  const handleBook = (house: House) => {
    setSelectedHouse(house)
    setIsBookingOpen(true)
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-32 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  const activeHouses = houses?.filter((h) => h.is_active) || []

  return (
    <>
      <div className="flex flex-col gap-6">
        <h1 className="text-2xl font-bold">Доступные дома</h1>
        
        {activeHouses.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              Нет доступных домов для бронирования
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {activeHouses.map((house) => (
              <Card key={house.id} className="flex flex-col">
                <CardHeader>
                  <CardTitle>{house.name}</CardTitle>
                  <CardDescription>
                    {house.description || "Нет описания"}
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-1">
                  <div className="flex flex-col gap-4">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Users className="size-4" data-icon />
                      <span>Вместимость: {house.capacity} человек</span>
                    </div>
                    <Button 
                      className="w-full mt-auto" 
                      onClick={() => handleBook(house)}
                    >
                      <Calendar className="size-4 mr-2" data-icon />
                      Забронировать
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      <BookingFormDialog
        house={selectedHouse}
        open={isBookingOpen}
        onOpenChange={setIsBookingOpen}
      />
    </>
  )
}

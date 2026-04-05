"use client"

import Link from "next/link"
import { Users, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { useHousesCatalog } from "@/hooks/use-houses-catalog"

export default function TenantHousesPage() {
  const { data: houses, isLoading } = useHousesCatalog()

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <h1 className="text-2xl font-bold">Доступные дома</h1>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
                <Skeleton className="h-4 w-full" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-24" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (!houses || houses.length === 0) {
    return (
      <div className="flex flex-col gap-6">
        <h1 className="text-2xl font-bold">Доступные дома</h1>
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            Нет доступных домов для бронирования
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Доступные дома</h1>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {houses.map((house) => (
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
                  <Users className="size-4" />
                  <span>Вместимость: {house.capacity} человек</span>
                </div>
                <Button 
                  variant="outline" 
                  className="w-full mt-auto"
                  asChild
                >
                  <Link href={`/tenant/houses/${house.id}`}>
                    Подробнее
                    <ArrowRight className="size-4 ml-2" />
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

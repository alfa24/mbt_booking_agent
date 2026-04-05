"use client"

import { useState } from "react"
import { Pencil, Plus } from "lucide-react"
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
import { Skeleton } from "@/components/ui/skeleton"
import { useHouses, type House } from "@/hooks/use-houses"
import { HouseFormDialog } from "./house-form-dialog"

export function HousesTable() {
  const { data: houses, isLoading } = useHouses()
  const [editingHouse, setEditingHouse] = useState<House | null>(null)
  const [isCreateOpen, setIsCreateOpen] = useState(false)

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
        <CardHeader className="flex flex-row items-center justify-between gap-4">
          <CardTitle>Дома</CardTitle>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="size-4" data-icon />
            Добавить дом
          </Button>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Название</TableHead>
                <TableHead>Описание</TableHead>
                <TableHead>Вместимость</TableHead>
                <TableHead>Статус</TableHead>
                <TableHead className="text-right">Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {houses?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground">
                    Нет домов
                  </TableCell>
                </TableRow>
              ) : (
                houses?.map((house) => (
                  <TableRow key={house.id}>
                    <TableCell className="font-medium">{house.name}</TableCell>
                    <TableCell className="max-w-xs truncate">
                      {house.description || "—"}
                    </TableCell>
                    <TableCell>{house.capacity} чел.</TableCell>
                    <TableCell>
                      {house.is_active ? (
                        <span className="text-green-600">Активен</span>
                      ) : (
                        <span className="text-muted-foreground">Неактивен</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setEditingHouse(house)}
                        >
                          <Pencil className="size-4" data-icon />
                          <span className="sr-only">Редактировать</span>
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <HouseFormDialog
        open={isCreateOpen}
        onOpenChange={setIsCreateOpen}
      />

      <HouseFormDialog
        house={editingHouse}
        open={!!editingHouse}
        onOpenChange={(open) => !open && setEditingHouse(null)}
      />
    </>
  )
}

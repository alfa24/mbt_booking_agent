"use client"

import { useState } from "react"
import { Pencil, Plus, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { useTariffs, useDeleteTariff, type Tariff } from "@/hooks/use-tariffs"
import { TariffFormDialog } from "./tariff-form-dialog"

export function TariffsList() {
  const { data: tariffs, isLoading } = useTariffs()
  const deleteTariff = useDeleteTariff()
  const [editingTariff, setEditingTariff] = useState<Tariff | null>(null)
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
              <Skeleton key={i} className="h-24 w-full" />
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
          <div>
            <CardTitle>Тарифы</CardTitle>
            <CardDescription>Цены за ночь для разных категорий гостей</CardDescription>
          </div>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="size-4" data-icon />
            Добавить тариф
          </Button>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4">
            {tariffs?.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">Нет тарифов</p>
            ) : (
              tariffs?.map((tariff) => (
                <Card key={tariff.id}>
                  <CardContent className="flex items-center justify-between p-4">
                    <div className="flex flex-col gap-1">
                      <span className="font-medium">{tariff.name}</span>
                      <span className="text-sm text-muted-foreground">
                        {new Intl.NumberFormat("ru-RU", {
                          style: "currency",
                          currency: "RUB",
                        }).format(tariff.amount)} / ночь
                      </span>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setEditingTariff(tariff)}
                      >
                        <Pencil className="size-4" data-icon />
                        <span className="sr-only">Редактировать</span>
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => deleteTariff.mutate(tariff.id)}
                        disabled={deleteTariff.isPending}
                      >
                        <Trash2 className="size-4" data-icon />
                        <span className="sr-only">Удалить</span>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      <TariffFormDialog
        open={isCreateOpen}
        onOpenChange={setIsCreateOpen}
      />

      <TariffFormDialog
        tariff={editingTariff}
        open={!!editingTariff}
        onOpenChange={(open) => !open && setEditingTariff(null)}
      />
    </>
  )
}
